"""Local contract check against the installed Matt Pocock skills.

The engineering skills look up tracker-doc sections by their English heading.
The ProjeX template uses Chinese headings, so every seed section must appear in
SECTIONS and its Chinese heading must exist: an upstream addition fails here
instead of silently going unmapped. Skipped where the skills are not
installed (e.g. CI); point MATT_SKILLS_DIR elsewhere if needed.
"""

import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills" / "codeup" / "assets" / "issue-tracker.md"
SKILLS = Path(os.environ.get("MATT_SKILLS_DIR", Path.home() / ".agents" / "skills"))
SEED = SKILLS / "setup-matt-pocock-skills" / "issue-tracker-github.md"

# Matt seed heading -> heading in the ProjeX template
SECTIONS = {
    "Conventions": "真相来源与操作",
    "Pull requests as a triage surface": "MR 作为分诊入口",
    'When a skill says "publish to the issue tracker"': "发布到工作项追踪",
    'When a skill says "fetch the relevant ticket"': "读取相关工作项",
    "Wayfinding operations": "Wayfinder 操作",
}


def section(text, heading):
    match = re.search(rf"(?ms)^## {re.escape(heading)}.*?$(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


@unittest.skipUnless(SEED.is_file(), "setup-matt-pocock-skills is not installed")
class MattContractTests(unittest.TestCase):
    def test_template_maps_every_seed_section(self):
        ours = TEMPLATE.read_text()
        for heading in re.findall(r"(?m)^## (.+)$", SEED.read_text()):
            with self.subTest(heading=heading):
                self.assertIn(heading, SECTIONS)
                self.assertRegex(ours, rf"(?m)^## {re.escape(SECTIONS[heading])}$")

    def test_wayfinding_operations_are_all_mapped(self):
        seed = section(SEED.read_text(), "Wayfinding operations")
        ours = section(TEMPLATE.read_text(), SECTIONS["Wayfinding operations"])
        operations = re.findall(r"(?m)^- \*\*(.+?)\*\*", seed)
        self.assertTrue(operations)
        for name in operations:
            with self.subTest(operation=name):
                self.assertRegex(ours, rf"(?m)^- \*\*[^*]*（{re.escape(name)}）\*\*")


if __name__ == "__main__":
    unittest.main()
