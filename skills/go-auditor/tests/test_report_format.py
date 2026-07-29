from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
REPORT_FORMAT = SKILL_DIR / "references" / "report-format.md"


class ReportFormatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REPORT_FORMAT.read_text(encoding="utf-8")

    def test_summary_uses_type_by_severity_matrix(self) -> None:
        self.assertIn("问题类型 × 严重度", self.text)
        self.assertIn("| 问题类型 | 阻断级 | 应修复 | 可优化 | 小计 |", self.text)

    def test_findings_are_type_first_then_severity(self) -> None:
        self.assertIn("先按问题类型分类，类型内部再按严重度分级", self.text)
        self.assertIn("禁止先汇总全部阻断级", self.text)
        self.assertIn("#### 阻断级", self.text)
        self.assertIn("#### 应修复", self.text)
        self.assertIn("#### 可优化", self.text)

    def test_zero_unreviewed_and_not_applicable_are_distinct(self) -> None:
        self.assertIn("`0` 只表示该类型已经审计且没有确认问题", self.text)
        self.assertIn("未检查写“未审计”", self.text)
        self.assertIn("与当前范围无关写“不适用”", self.text)

    def test_summary_is_decision_oriented_and_findings_show_confirmation(self) -> None:
        self.assertIn("摘要面向决策者", self.text)
        self.assertIn("最先处理的三项", self.text)
        self.assertIn("证据与确认状态", self.text)
        self.assertIn("仓库外可达性未知", self.text)

    def test_final_report_is_not_an_append_only_draft(self) -> None:
        self.assertIn("正式报告只能在候选回读、去重、分类和定级后整体收口", self.text)
        self.assertIn("不得把 append-only 草稿直接当作最终报告", self.text)


if __name__ == "__main__":
    unittest.main()
