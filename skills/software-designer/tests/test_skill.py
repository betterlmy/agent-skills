import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


class SoftwareDesignerSkillTests(unittest.TestCase):
    def test_skill_entry_and_resources_exist(self):
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(skill_text, r"(?m)^name: software-designer$")
        for relative_path in (
            "references/document-standard.md",
            "references/reverse-engineering.md",
            "templates/software-design-document.md",
            "examples/student-management-system.md",
        ):
            self.assertTrue((SKILL_DIR / relative_path).is_file(), relative_path)
        self.assertIn("references/document-standard.md", skill_text)
        self.assertIn("references/reverse-engineering.md", skill_text)

    def test_example_contains_required_diagram_views(self):
        example = (SKILL_DIR / "examples/student-management-system.md").read_text(
            encoding="utf-8"
        )
        mermaid_blocks = re.findall(
            r"```mermaid\n(.*?)\n```", example, flags=re.DOTALL
        )
        self.assertEqual(3, len(mermaid_blocks))
        self.assertTrue(any(block.startswith("flowchart") for block in mermaid_blocks))
        self.assertTrue(any(block.startswith("erDiagram") for block in mermaid_blocks))
        self.assertTrue(any(block.startswith("sequenceDiagram") for block in mermaid_blocks))

    def test_template_has_traceability_and_evidence_sections(self):
        template = (SKILL_DIR / "templates/software-design-document.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("### 修订记录", template)
        self.assertIn("## 11. 追踪矩阵", template)
        self.assertIn("## 12. 代码证据", template)

    def test_skill_defines_non_blocking_unknowns_and_recommendations(self):
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("当前交付互不兼容", skill_text)
        self.assertIn("技术中立设计", skill_text)
        self.assertIn("**建议**", skill_text)
        self.assertIn("理由、代价和需要确认的责任角色", skill_text)

if __name__ == "__main__":
    unittest.main()
