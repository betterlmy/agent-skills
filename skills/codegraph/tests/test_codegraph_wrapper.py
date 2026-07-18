#!/usr/bin/env python3
"""Bash wrapper 的参数、安全边界和兼容性回归测试。"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


WRAPPER = Path(__file__).resolve().parents[1] / "scripts" / "codegraph.sh"


class CodeGraphWrapperTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.fake_bin = self.root / "codegraph"
        self.write_executable(
            self.fake_bin,
            "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\"\n",
        )

    @staticmethod
    def write_executable(path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)

    def run_wrapper(
        self,
        *args: str,
        check: bool = True,
        env_overrides: dict[str, str] | None = None,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CODEGRAPH_BIN"] = str(self.fake_bin)
        if env_overrides:
            env.update(env_overrides)
        return subprocess.run(
            ["/bin/bash", str(WRAPPER), *args],
            check=check,
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd or self.root,
        )

    def output(self, *args: str) -> list[str]:
        return self.run_wrapper(*args).stdout.splitlines()

    def test_wrapper_works_outside_skill_directory(self) -> None:
        project = self.root / "unrelated project"
        project.mkdir()
        self.assertEqual(["--version"], self.run_wrapper("check", cwd=project).stdout.splitlines())

    def test_default_json_commands_without_optional_arguments(self) -> None:
        cases = {
            ("status", "."): ["status", "--json", "."],
            ("query", ".", "TargetSymbol"): ["query", "--path", ".", "--json", "TargetSymbol"],
            ("files", "."): ["files", "--path", ".", "--json"],
            ("callers", ".", "TargetSymbol"): ["callers", "--path", ".", "--json", "TargetSymbol"],
            ("callees", ".", "TargetSymbol"): ["callees", "--path", ".", "--json", "TargetSymbol"],
            ("impact", ".", "TargetSymbol"): ["impact", "--path", ".", "--json", "TargetSymbol"],
            ("affected", "."): ["affected", "--path", ".", "--json"],
        }
        for arguments, expected in cases.items():
            with self.subTest(arguments=arguments):
                self.assertEqual(expected, self.output(*arguments))

    def test_explore_and_node_forward_native_text_commands(self) -> None:
        self.assertEqual(
            ["explore", "--path", "project path", "auth flow", "--max-files", "8"],
            self.output("explore", "project path", "auth flow", "--max-files", "8"),
        )
        self.assertEqual(
            ["node", "--path", "project path", "--file", "src/file name.ts", "--limit", "20"],
            self.output("node", "project path", "--file", "src/file name.ts", "--limit", "20"),
        )

    def test_options_and_paths_with_spaces_are_preserved(self) -> None:
        self.assertEqual(
            [
                "affected", "--path", "project path", "--depth", "3", "--filter",
                "**/* test.*", "--json", "src/a file.ts", "src/b file.ts",
            ],
            self.output(
                "affected", "project path", "src/a file.ts", "src/b file.ts",
                "--depth", "3", "--filter", "**/* test.*",
            ),
        )

    def test_no_json_preserves_human_readable_output(self) -> None:
        self.assertEqual(
            ["files", "--path", ".", "--format", "tree"],
            self.output("files", ".", "--format", "tree", "--no-json"),
        )

    def test_simple_commands_forward_project_last(self) -> None:
        project = self.root / "plain-project"
        project.mkdir()
        cases = {
            ("init", str(project), "--verbose"): ["init", "--verbose", str(project)],
            ("uninit", str(project), "--force"): ["uninit", "--force", str(project)],
            ("index", str(project), "--quiet"): ["index", "--quiet", str(project)],
            ("sync", str(project), "--quiet"): ["sync", "--quiet", str(project)],
            ("unlock", str(project)): ["unlock", str(project)],
        }
        for arguments, expected in cases.items():
            with self.subTest(arguments=arguments):
                self.assertEqual(expected, self.output(*arguments))

    def test_init_rejects_git_project_without_ignore_rule(self) -> None:
        project = self.root / "git-project"
        project.mkdir()
        subprocess.run(["git", "-C", str(project), "init", "-q"], check=True)

        result = self.run_wrapper("init", str(project), check=False)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("未忽略 .codegraph/", result.stderr)

    def test_init_accepts_git_project_with_ignore_rule(self) -> None:
        project = self.root / "git-project"
        project.mkdir()
        subprocess.run(["git", "-C", str(project), "init", "-q"], check=True)
        (project / ".gitignore").write_text(".codegraph/\n", encoding="utf-8")

        self.assertEqual(
            ["init", str(project)],
            self.output("init", str(project)),
        )

    def test_missing_arguments_return_actionable_error(self) -> None:
        for arguments, message in (
            (("query", "."), "query 缺少 search 参数"),
            (("explore", "."), "explore 缺少 query 参数"),
            (("node", "."), "node 需要 symbol"),
            (("unlock", ".", "extra"), "unlock 不接受额外参数"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_wrapper(*arguments, check=False)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(message, result.stderr)

    def test_native_upgrade_is_preferred_when_available(self) -> None:
        self.assertEqual(["upgrade", "--check"], self.output("upgrade", "--check"))

    def test_upgrade_fallback_uses_npm_when_native_command_is_missing(self) -> None:
        fallback_bin = self.root / "old-codegraph"
        self.write_executable(
            fallback_bin,
            """#!/usr/bin/env bash
if [[ "${1:-}" == "upgrade" && "${2:-}" == "--help" ]]; then exit 1; fi
if [[ "${1:-}" == "--version" ]]; then printf '0.1.0\\n'; exit 0; fi
printf '%s\\n' "$@"
""",
        )
        fake_npm = self.root / "npm"
        self.write_executable(fake_npm, "#!/usr/bin/env bash\nprintf 'npm:%s\\n' \"$@\"\n")
        path = f"{self.root}:{os.environ.get('PATH', '')}"

        result = self.run_wrapper(
            "upgrade", "2.0.0",
            env_overrides={"CODEGRAPH_BIN": str(fallback_bin), "PATH": path},
        )

        self.assertEqual(["npm:i", "npm:-g", "npm:@colbymchenry/codegraph@2.0.0"], result.stdout.splitlines())

    def test_upgrade_fallback_reports_missing_npm(self) -> None:
        fallback_bin = self.root / "old-codegraph"
        self.write_executable(
            fallback_bin,
            "#!/bin/bash\n[[ \"${1:-}\" == upgrade ]] && exit 1\nprintf '0.1.0\\n'\n",
        )
        empty_path = self.root / "empty-path"
        empty_path.mkdir()

        result = self.run_wrapper(
            "upgrade", "--check", check=False,
            env_overrides={"CODEGRAPH_BIN": str(fallback_bin), "PATH": str(empty_path)},
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("找不到 npm", result.stderr)


if __name__ == "__main__":
    unittest.main()
