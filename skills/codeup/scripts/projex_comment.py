#!/usr/bin/env python3
"""补齐中心版 CLI 的 Markdown 评论写入；凭据由调用方注入。"""

import argparse
import http.client
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request


ENDPOINT = "https://openapi-rdc.aliyuncs.com"
TOKEN_ENV = "ALIBABA_CLOUD_YUNXIAO_ACCESS_TOKEN"
ORG_ENV = "ALIBABA_CLOUD_YUNXIAO_ORGANIZATION_ID"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # PAT 只交给已核实的固定接入点。
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="工作项 API ID，不是展示编号")
    parser.add_argument("--body-file", required=True, type=Path, help="UTF-8 Markdown 文件")
    args = parser.parse_args(argv)

    try:
        if os.environ.get("ALIBABA_CLOUD_YUNXIAO_API_BASE_URL", "").rstrip("/") not in ("", ENDPOINT):
            raise ValueError("此脚本仅支持中心版默认接入点；Region 版需核对实例 API。")
        organization = os.environ.get(ORG_ENV, "")
        if not organization or not re.fullmatch(r"[A-Za-z0-9_-]+", organization):
            raise ValueError("请通过本机凭据入口注入有效的组织 ID。")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", args.id):
            raise ValueError("工作项 API ID 不能包含路径、查询参数或空白。")
        token = os.environ.get(TOKEN_ENV, "")
        if not token or any(not 33 <= ord(c) <= 126 for c in token):
            raise ValueError("请通过本机凭据入口注入有效 PAT。")
        try:
            content = args.body_file.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            raise ValueError("无法读取 UTF-8 Markdown 文件。") from None
        if not content.strip():
            raise ValueError("评论内容不能为空。")
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2

    request = urllib.request.Request(
        f"{ENDPOINT}/oapi/v1/projex/organizations/{organization}/workitems/{args.id}/comments",
        data=json.dumps({"content": content, "formatType": "MARKDOWN"}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-yunxiao-token": token},
        method="POST",
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=30) as response:
            result = json.load(response)
        comment_id = result.get("id") if isinstance(result, dict) else None
        if (type(comment_id) not in (str, int)
                or not re.fullmatch(r"[A-Za-z0-9_-]+", str(comment_id))):
            raise ValueError("missing comment id")
    except urllib.error.HTTPError as error:
        error.close()
        if 400 <= error.code < 500 and error.code != 408:
            print(f"创建被拒绝（HTTP {error.code}）；检查身份、权限、目标及参数。未自动重试。", file=sys.stderr)
            return 1
        print(f"创建结果不确定（HTTP {error.code}）；先回读评论，勿直接重试。", file=sys.stderr)
        return 3
    except (OSError, http.client.HTTPException, ValueError):
        print("创建结果不确定（网络异常或响应无有效 ID）；先回读评论，勿直接重试。", file=sys.stderr)
        return 3

    print(json.dumps({"id": str(comment_id)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
