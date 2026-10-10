"""Offline distribution checks; no tenant access or model-behavior claims."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "codeup"


class PackageTests(unittest.TestCase):
    def test_entry_metadata(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\n"))
        metadata = text.split("---", 2)[1]
        self.assertRegex(metadata, r"(?m)^name: codeup$")
        self.assertRegex(metadata, r"(?m)^description: .+")
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())

    def test_relative_links_stay_in_distribution(self):
        for path in ROOT.rglob("*.md"):
            boundary = SKILL if path.is_relative_to(SKILL) else ROOT
            for link in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", path.read_text()):
                target = urlsplit(link)
                if target.scheme or target.netloc or not target.path:
                    continue
                resolved = (path.parent / unquote(target.path)).resolve()
                with self.subTest(file=path.relative_to(ROOT), link=link):
                    self.assertTrue(resolved.is_relative_to(boundary))
                    self.assertTrue(resolved.exists())

    def test_skill_contains_no_machine_paths(self):
        for path in SKILL.rglob("*"):
            if path.is_file():
                with self.subTest(file=path.relative_to(SKILL)):
                    self.assertNotRegex(path.read_text(), r"(?:/Users/|/home/|/var/folders/)")


if __name__ == "__main__":
    unittest.main()
