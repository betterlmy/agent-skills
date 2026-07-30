#!/usr/bin/env python3
"""PowerShell wrapper 的跨平台回归测试；本机无 PowerShell 时跳过。"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


WRAPPER = Path(__file__).resolve().parents[1] / "scripts" / "codegraph.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


@unittest.skipUnless(POWERSHELL, "当前环境没有 PowerShell")
class CodeGraphPowerShellWrapperTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.fake_bin = self.root / "fake-codegraph.ps1"
        self.fake_bin.write_text(
            "$args | ForEach-Object { Write-Output $_ }\n",
            encoding="utf-8",
        )

    def run_wrapper(self, *args: str) -> list[str]:
        env = os.environ.copy()
        env["CODEGRAPH_BIN"] = str(self.fake_bin)
        command = [
            str(POWERSHELL), "-NoProfile", "-File", str(WRAPPER), *args,
        ]
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            env=env,
            cwd=self.root,
        )
        return result.stdout.splitlines()

    def test_status_defaults_to_json(self) -> None:
        self.assertEqual(
            ["status", "--json", "project path"],
            self.run_wrapper("status", "project path"),
        )

    def test_subcommand_help_does_not_require_project_or_symbol(self) -> None:
        self.assertEqual(["impact", "--help"], self.run_wrapper("impact", "--help"))
        self.assertEqual(["--help"], self.run_wrapper("raw", "--help"))

    def test_explore_and_node_preserve_spaces(self) -> None:
        self.assertEqual(
            ["explore", "--path", "project path", "auth flow"],
            self.run_wrapper("explore", "project path", "auth flow"),
        )
        self.assertEqual(
            ["node", "--path", "project path", "--file", "src/a file.ts"],
            self.run_wrapper("node", "project path", "--file", "src/a file.ts"),
        )

    def test_no_json_and_affected_arguments_are_forwarded(self) -> None:
        self.assertEqual(
            ["files", "--path", "project path", "--format", "tree"],
            self.run_wrapper("files", "project path", "--format", "tree", "--no-json"),
        )
        self.assertEqual(
            ["affected", "--path", "project path", "src/a file.ts", "--json"],
            self.run_wrapper("affected", "project path", "src/a file.ts"),
        )

    @unittest.skipUnless(shutil.which("git"), "当前环境没有 Git")
    def test_init_enforces_git_ignore_rule(self) -> None:
        project = self.root / "git project"
        project.mkdir()
        subprocess.run(["git", "-C", str(project), "init", "-q"], check=True)

        env = os.environ.copy()
        env["CODEGRAPH_BIN"] = str(self.fake_bin)
        command = [
            str(POWERSHELL), "-NoProfile", "-File", str(WRAPPER),
            "init", str(project),
        ]
        rejected = subprocess.run(command, capture_output=True, text=True, env=env)
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("未忽略 .codegraph/", rejected.stderr)

        (project / ".gitignore").write_text(".codegraph/\n", encoding="utf-8")
        accepted = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(["init", str(project)], accepted.stdout.splitlines())


if __name__ == "__main__":
    unittest.main()
