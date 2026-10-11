"""Local contract check against the installed Matt Pocock skills.

The engineering skills look up tracker-doc sections by heading. The ProjeX
template must keep every section of the setup skill's GitHub seed, so an
upstream addition fails here instead of silently going unmapped. Skipped where
the skills are not installed (e.g. CI); point MATT_SKILLS_DIR elsewhere if needed.
"""

import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills" / "codeup" / "assets" / "issue-tracker.md"
SKILLS = Path(os.environ.get("MATT_SKILLS_DIR", Path.home() / ".agents" / "skills"))
SEED = SKILLS / "setup-matt-pocock-skills" / "issue-tracker-github.md"


def section(text, heading):
    match = re.search(rf"(?ms)^## {re.escape(heading)}.*?$(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


@unittest.skipUnless(SEED.is_file(), "setup-matt-pocock-skills is not installed")
class MattContractTests(unittest.TestCase):
    def test_template_keeps_every_seed_section(self):
        ours = TEMPLATE.read_text()
        for heading in re.findall(r"(?m)^## (.+)$", SEED.read_text()):
            with self.subTest(heading=heading):
                self.assertRegex(ours, rf"(?m)^## {re.escape(heading)}")

    def test_wayfinding_operations_are_all_mapped(self):
        seed = section(SEED.read_text(), "Wayfinding operations")
        ours = section(TEMPLATE.read_text(), "Wayfinding operations")
        operations = re.findall(r"(?m)^- \*\*(.+?)\*\*", seed)
        self.assertTrue(operations)
        for name in operations:
            with self.subTest(operation=name):
                self.assertIn(f"- **{name}**", ours)


if __name__ == "__main__":
    unittest.main()
