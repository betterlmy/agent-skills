import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_skill.py"
SPEC = importlib.util.spec_from_file_location("audit_skill", SCRIPT)
assert SPEC and SPEC.loader
AUDIT_SKILL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT_SKILL)


def write_skill(root: Path, name: str, body: str = "") -> Path:
    skill_dir = root / name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Use when testing {name}.\n---\n\n{body}\n",
        encoding="utf-8",
    )
    return skill_dir


class ParseFrontmatterTest(unittest.TestCase):
    def test_parses_yaml_block_scalar_without_warnings(self) -> None:
        text = """---
name: alpha-tool
description: |
  Creates alpha output.
  Use when alpha output is requested.
allowed-tools:
  - Read
  - Bash
---
"""
        frontmatter, issues = AUDIT_SKILL.parse_frontmatter(text)

        self.assertEqual([], issues)
        self.assertIn("Use when", frontmatter["description"])


class IndependenceAuditTest(unittest.TestCase):
    def test_rejects_sibling_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            alpha = write_skill(root, "alpha-tool", "Run `beta-tool` for details.")
            write_skill(root, "beta-tool")

            results = AUDIT_SKILL.audit(alpha)

        self.assertTrue(any("cross-skill reference to 'beta-tool'" in item for item in results))

    def test_allows_self_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            alpha = write_skill(root, "alpha-tool", "Use `$alpha-tool` for this workflow.")
            write_skill(root, "beta-tool")

            results = AUDIT_SKILL.audit(alpha)

        self.assertFalse(any("cross-skill reference" in item for item in results))

    def test_does_not_treat_git_commit_as_sibling_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            alpha = write_skill(root, "alpha-tool", "Run git commit only after approval.")
            write_skill(root, "commit")

            results = AUDIT_SKILL.audit(alpha)

        self.assertFalse(any("cross-skill reference" in item for item in results))

    def test_rejects_markdown_link_outside_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            alpha = write_skill(root, "alpha-tool", "Read [shared](../shared.md).")
            (root / "shared.md").write_text("shared", encoding="utf-8")

            results = AUDIT_SKILL.audit(alpha)

        self.assertTrue(any("link points outside skill package" in item for item in results))

    def test_rejects_symlink_outside_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            alpha = write_skill(root, "alpha-tool")
            outside = root / "shared.md"
            outside.write_text("shared", encoding="utf-8")
            (alpha / "shared.md").symlink_to(outside)

            results = AUDIT_SKILL.audit(alpha)

        self.assertTrue(any("symlink points outside skill package" in item for item in results))


if __name__ == "__main__":
    unittest.main()
