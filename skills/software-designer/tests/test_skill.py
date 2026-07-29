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
        self.assertIn("## 12. 设计依据", template)

    def test_skill_defines_non_blocking_unknowns_and_recommendations(self):
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("当前交付互不兼容", skill_text)
        self.assertIn("技术中立设计", skill_text)
        self.assertIn("**建议**", skill_text)
        self.assertIn("理由、代价和需要确认的责任角色", skill_text)

    def test_formation_method_does_not_replace_document_semantics(self):
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        standard = (SKILL_DIR / "references/document-standard.md").read_text(
            encoding="utf-8"
        )
        reverse = (SKILL_DIR / "references/reverse-engineering.md").read_text(
            encoding="utf-8"
        )
        template = (
            SKILL_DIR / "templates/software-design-document.md"
        ).read_text(encoding="utf-8")
        example = (
            SKILL_DIR / "examples/student-management-system.md"
        ).read_text(encoding="utf-8")

        self.assertIn("文档语义不随形成方式改变", skill_text)
        self.assertIn("不得用分析任务代替系统目的", skill_text)
        self.assertIn("不得用“分析代码”", standard)
        self.assertIn("识别系统背景与建设目标", reverse)
        self.assertIn("不要描述本次分析、逆向或文档编写任务", template)
        self.assertIn("| 形成方式 |", template)
        self.assertIn("| 事实基准 |", template)
        self.assertNotIn("| 设计模式 |", template)
        self.assertIn("| 形成方式 |", example)

    def test_template_separates_test_presence_from_execution_result(self):
        template = (SKILL_DIR / "templates/software-design-document.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("证据状态/执行结果", template)
        self.assertIn("测试存在/本次通过/未运行", template)

if __name__ == "__main__":
    unittest.main()
