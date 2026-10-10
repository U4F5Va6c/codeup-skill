"""假 HTTP 验证格式、凭据边界和不确定写入，不访问云效。"""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener


SCRIPT = Path(__file__).resolve().parents[1] / "skills/codeup/scripts/projex_comment.py"
spec = importlib.util.spec_from_file_location("projex_comment", SCRIPT)
comment = importlib.util.module_from_spec(spec)
# 包检查只扫描可分发源文件，测试加载脚本时不产生字节码缓存。
exec(compile(SCRIPT.read_text(encoding="utf-8"), str(SCRIPT), "exec"), comment.__dict__)


class CommentTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.body = Path(temp.name) / "comment.md"
        self.content = "## 中文标题\n\n- [x] **通过**\n\n[链接](https://example.com)\n`$() <>&`\n"
        self.body.write_text(self.content, encoding="utf-8")
        self.env = {comment.TOKEN_ENV: "fake-secret-token", comment.ORG_ENV: "test-org"}
        self.opener = Mock()
        self.opener.open.return_value = io.BytesIO(b'{"id":"123"}')

    def run_comment(self, workitem="test-id"):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, self.env, clear=True), \
                patch.object(comment.urllib.request, "build_opener", return_value=self.opener), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = comment.main(["--id", workitem, "--body-file", str(self.body)])
        output = stdout.getvalue() + stderr.getvalue()
        self.assertNotIn("fake-secret-token", output)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_preserves_markdown_and_uses_injected_identity(self):
        code, stdout, stderr = self.run_comment()
        self.assertEqual((code, json.loads(stdout), stderr), (0, {"id": "123"}, ""))
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.full_url, comment.ENDPOINT + "/oapi/v1/projex/organizations/test-org/workitems/test-id/comments")
        self.assertEqual(request.method, "POST")
        self.assertEqual(json.loads(request.data), {"content": self.content, "formatType": "MARKDOWN"})
        self.assertEqual(request.get_header("X-yunxiao-token"), self.env[comment.TOKEN_ENV])
        self.opener.open.assert_called_once()

    def test_rejects_missing_credentials_and_other_endpoint_before_network(self):
        for key, value in ((comment.TOKEN_ENV, ""), (comment.TOKEN_ENV, "bad\ntoken"),
                           (comment.ORG_ENV, ""), (comment.ORG_ENV, "../other"),
                           ("ALIBABA_CLOUD_YUNXIAO_API_BASE_URL", "https://region.invalid")):
            with self.subTest(key=key, value=value):
                original = dict(self.env)
                self.env[key] = value
                self.assertEqual(self.run_comment()[0], 2)
                self.env = original
        self.opener.open.assert_not_called()

    def test_bad_target_or_file_does_not_post(self):
        self.assertEqual(self.run_comment("../wrong?target")[0], 2)
        self.body.write_text(" \n")
        self.assertEqual(self.run_comment()[0], 2)
        self.body.write_bytes(b"\xff")
        self.assertEqual(self.run_comment()[0], 2)
        self.body.unlink()
        self.assertEqual(self.run_comment()[0], 2)
        self.opener.open.assert_not_called()

    def test_http_errors_do_not_retry_or_echo_response(self):
        for status, expected in ((401, 1), (403, 1), (429, 1), (408, 3), (500, 3), (302, 3)):
            with self.subTest(status=status):
                self.opener.reset_mock()
                self.opener.open.side_effect = HTTPError(comment.ENDPOINT, status,
                    "fake-secret-token", {}, io.BytesIO(b"fake-secret-token"))
                code, stdout, stderr = self.run_comment()
                self.assertEqual(code, expected)
                self.assertEqual(stdout, "")
                self.assertIn(str(status), stderr)
                self.opener.open.assert_called_once()

    def test_unknown_result_requires_readback_without_retry(self):
        for error in (TimeoutError("fake-secret-token"), URLError("fake-secret-token")):
            self.opener.reset_mock()
            self.opener.open.side_effect = error
            self.assertEqual(self.run_comment()[0], 3)
            self.opener.open.assert_called_once()
        self.opener.open.side_effect = None
        for body in (b"invalid json", b"{}", b'{"id":null}', b"[]", b"\xff"):
            self.opener.reset_mock()
            self.opener.open.return_value = io.BytesIO(body)
            self.assertEqual(self.run_comment()[0], 3)
            self.opener.open.assert_called_once()

    def test_redirect_cannot_forward_pat(self):
        opener = build_opener(comment.NoRedirect())
        request = Request(comment.ENDPOINT, headers={"x-yunxiao-token": "fake-secret-token"})
        with self.assertRaises(HTTPError) as caught:
            opener.error("https", request, io.BytesIO(), 302, "redirect",
                         {"location": "https://other.invalid"})
        caught.exception.close()


if __name__ == "__main__":
    unittest.main()
