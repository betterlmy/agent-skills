import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_skill.py"
SPEC = importlib.util.spec_from_file_location("audit_skill", SCRIPT)
assert SPEC and SPEC.loader
AUDIT_SKILL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT_SKILL)


def write_skill(root: Path, name: str, body: str = "", description: str | None = None) -> Path:
    skill_dir = root / name
    skill_dir.mkdir()
    if description is None:
        description = f"Use when testing {name}."
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n",
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


class TriggerDescriptionAuditTest(unittest.TestCase):
    def test_accepts_common_use_when_phrasings(self) -> None:
        descriptions = (
            "Use when alpha output is requested.",
            "Use for alpha output tasks.",
            "Use this skill when alpha output is requested.",
            "This skill should be used when alpha output is requested.",
            "This skill is used for alpha output tasks.",
        )
        for description in descriptions:
            with self.subTest(description=description), tempfile.TemporaryDirectory() as temp_dir:
                skill = write_skill(Path(temp_dir), "alpha-tool", description=description)

                results = AUDIT_SKILL.audit(skill)

                self.assertFalse(any("trigger contexts" in item for item in results))

    def test_warns_when_description_has_no_trigger_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(
                Path(temp_dir),
                "alpha-tool",
                description="Creates alpha output.",
            )

            results = AUDIT_SKILL.audit(skill)

        self.assertTrue(any("trigger contexts" in item for item in results))


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


class CliCompatibilityAuditTest(unittest.TestCase):
    def test_warns_when_cli_is_mentioned_but_not_declared(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), "alpha-tool", "Use the Alpha CLI.")

            results = AUDIT_SKILL.audit(skill)

        self.assertTrue(any("未声明 external-cli" in item for item in results))

    def test_rejects_declared_cli_without_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), "alpha-tool")
            (skill / "SKILL.md").write_text(
                "---\nname: alpha-tool\ndescription: Use when testing alpha.\n"
                "external-cli: true\n---\n",
                encoding="utf-8",
            )

            results = AUDIT_SKILL.audit(skill)

        self.assertTrue(any("缺少 cli-compatibility frontmatter" in item for item in results))

    def test_accepts_complete_cli_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), "alpha-tool")
            references = skill / "references"
            references.mkdir()
            contract = references / "cli-compatibility.md"
            contract.write_text(
                "# CLI 兼容性\n\n<!-- cli-compatibility-contract:v1 -->\n\n"
                "| 本机验证版本 | `1.2.3` |\n\n"
                "## 关键能力\n\nRun help.\n\n"
                "## 版本不一致时\n\nWarn and probe.\n",
                encoding="utf-8",
            )
            (skill / "SKILL.md").write_text(
                "---\nname: alpha-tool\ndescription: Use when testing alpha.\n"
                "external-cli: true\n"
                "cli-compatibility: references/cli-compatibility.md\n---\n\n"
                "Read [CLI compatibility](references/cli-compatibility.md).\n",
                encoding="utf-8",
            )

            results = AUDIT_SKILL.audit(skill)

        self.assertTrue(any("兼容性契约完整" in item for item in results))
        self.assertFalse(any(item.startswith("FAIL") for item in results))


class InstructionAuditRegressionTest(unittest.TestCase):
    def test_npm_test_is_not_a_skill_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = write_skill(root, "develop", "Run `npm test`.")
            write_skill(root, "test")
            self.assertFalse(any("cross-skill reference" in x for x in AUDIT_SKILL.audit(skill)))
            (skill / "SKILL.md").write_text((skill / "SKILL.md").read_text() + "\nUse $test.\n")
            self.assertTrue(any("cross-skill reference" in x for x in AUDIT_SKILL.audit(skill)))

    def test_example_todo_is_not_unfinished_instruction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), "alpha", "Example: `<!-- TODO: image -->`.\n```text\n[TODO: example]\n```\n")
            self.assertFalse(any("TODO placeholders" in x for x in AUDIT_SKILL.audit(skill)))
            (skill / "SKILL.md").write_text((skill / "SKILL.md").read_text() + "\n[TODO: finish instructions]\n")
            self.assertTrue(any("TODO placeholders" in x for x in AUDIT_SKILL.audit(skill)))

    def test_plugin_boundary_allows_shared_but_rejects_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plugin = root / "plugin"
            plugin.mkdir()
            skill = write_skill(plugin, "alpha", "Read [shared](../shared.md).")
            (plugin / "shared.md").write_text("shared")
            self.assertFalse(any(x.startswith("FAIL") for x in AUDIT_SKILL.audit(skill, package_root=plugin)))
            (skill / "SKILL.md").write_text((skill / "SKILL.md").read_text() + "\n[escape](../../outside.md)\n")
            self.assertTrue(any("outside skill package" in x for x in AUDIT_SKILL.audit(skill, package_root=plugin)))

    def test_missing_local_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), "alpha", "Read [missing](references/missing.md).")
            self.assertTrue(any("missing local link" in x for x in AUDIT_SKILL.audit(skill)))

    def test_metadata_cli_fields_are_read(self) -> None:
        data, _ = AUDIT_SKILL.parse_frontmatter("---\nname: alpha\ndescription: Use when testing.\nmetadata:\n  external-cli: \"true\"\n  cli-compatibility: \"references/cli.md\"\n---\n")
        self.assertEqual("true", data.get("external-cli"))
        self.assertEqual("references/cli.md", data.get("cli-compatibility"))

    def test_code_examples_are_not_markdown_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), "alpha", "```cpp\nauto f = [](int x) { return x; };\n```\nInline `[](int x)` is code.\n")
            (skill / "example.py").write_text('sample = "[missing](missing.md)"')
            self.assertFalse(any("local link" in x for x in AUDIT_SKILL.audit(skill)))

    def test_development_filename_is_not_develop_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = write_skill(root, "test", "This Skill uses development-and-testing.md.")
            write_skill(root, "develop")
            self.assertFalse(any("cross-skill reference" in x for x in AUDIT_SKILL.audit(skill)))

    def test_binary_assets_and_oversized_text_are_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            asset = root / "large.pptx"
            asset.write_bytes(b"binary")
            self.assertIsNone(AUDIT_SKILL.read_text(asset))
            text = root / "large.md"
            text.write_bytes(b"x" * (AUDIT_SKILL.MAX_TEXT_BYTES + 1))
            self.assertIsNone(AUDIT_SKILL.read_text(text))


if __name__ == "__main__":
    unittest.main()
