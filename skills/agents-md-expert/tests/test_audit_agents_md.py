#!/usr/bin/env python3
"""audit_agents_md.py 的标准库单元测试。"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_agents_md.py"
SPEC = importlib.util.spec_from_file_location("audit_agents_md", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

SYNC_RULE = (
    "项目结构、技术栈、构建或测试命令、开发约束发生变化时，"
    "必须同步更新适用作用域的 AGENTS.md。"
)


class AuditAgentsMdTest(unittest.TestCase):
    def severities(self, text: str) -> list[str]:
        return [finding.severity for finding in MODULE.audit_text(text)]

    def test_clean_document(self) -> None:
        text = f"# 项目规则\n\n{SYNC_RULE}\n\n## 验证\n\n```bash\ngo test ./...\n```\n"
        findings = MODULE.audit_text(text)
        self.assertEqual(["OK"], [finding.severity for finding in findings])

    def test_second_level_heading_is_valid(self) -> None:
        text = f"## 项目规则\n\n{SYNC_RULE}\n"
        findings = MODULE.audit_text(text)
        self.assertEqual(["OK"], [finding.severity for finding in findings])

    def test_missing_drift_rule_is_warning(self) -> None:
        text = "# 项目规则\n\n必须运行已声明的检查命令。\n"
        findings = MODULE.audit_text(text)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("防漂移规则" in message for message in messages))

    def test_drift_rule_is_detected(self) -> None:
        self.assertTrue(MODULE.has_drift_sync_rule(f"# 项目规则\n\n{SYNC_RULE}\n"))

    def test_unclosed_fence_is_error(self) -> None:
        text = "# 项目规则\n\n```bash\ngo test ./...\n"
        self.assertIn("ERROR", self.severities(text))

    def test_secret_is_error(self) -> None:
        text = "# 项目规则\n\nTOKEN=abcdefghijklmnop123456\n"
        self.assertIn("ERROR", self.severities(text))

    def test_vague_rule_is_warning(self) -> None:
        text = "# 项目规则\n\n请遵循最佳实践。\n"
        self.assertIn("WARN", self.severities(text))

    def test_prohibited_dangerous_command_is_not_warning(self) -> None:
        text = "# 项目规则\n\n禁止执行 `git reset --hard`。\n"
        findings = MODULE.audit_text(text)
        messages = [finding.message for finding in findings]
        self.assertFalse(any("危险命令" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
