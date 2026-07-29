from __future__ import annotations

import os
import json
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import textwrap
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SCAN_SCRIPT = SKILL_DIR / "scripts" / "scan.sh"


class ScanScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.repo = self.root / "repo"
        self.bin_dir = self.root / "bin"
        self.repo.mkdir()
        self.bin_dir.mkdir()
        (self.repo / "go.mod").write_text("module example.com/audit\n\ngo 1.22\n", encoding="utf-8")
        (self.repo / "main.go").write_text("package main\n\nfunc main() {}\n", encoding="utf-8")
        self._write_tool(
            "go",
            """
            if [ "$1" = "version" ]; then
              echo "go version go-test"
              exit 0
            fi
            if [ -n "${FAKE_ENV_LOG:-}" ]; then
              printf '%s|%s|%s|%s\n' "${GOPROXY-unset}" "${GOTOOLCHAIN-unset}" "${GOFLAGS-unset}" "${GOWORK-unset}" >>"$FAKE_ENV_LOG"
            fi
            if [ -n "${FAKE_COMMAND_LOG:-}" ]; then
              printf '%s\n' "$*" >>"$FAKE_COMMAND_LOG"
            fi
            if [ "$1" = "list" ]; then
              if [ -n "${FAKE_GO_LIST_ERROR:-}" ]; then
                printf '%s\n' "$FAKE_GO_LIST_ERROR" >&2
              elif [ -n "${FAKE_GO_LIST_OUTPUT:-}" ]; then
                printf '%b\n' "$FAKE_GO_LIST_OUTPUT"
              else
                printf '%s\n' 'example.com/audit'
              fi
              exit "${FAKE_GO_LIST_EXIT:-0}"
            fi
            if [ -n "${FAKE_GO_OUTPUT:-}" ]; then
              printf '%s\n' "$FAKE_GO_OUTPUT" >&2
            fi
            exit "${FAKE_GO_EXIT:-0}"
            """,
        )
        self._write_tool(
            "gofmt",
            """
            case "$2" in
              *bad.go) printf '%s\n' "$2" ;;
            esac
            """,
        )

    def _write_tool(self, name: str, body: str) -> None:
        tool = self.bin_dir / name
        tool.write_text(
            "#!/usr/bin/env bash\nset -u\n" + textwrap.dedent(body).lstrip(),
            encoding="utf-8",
        )
        tool.chmod(tool.stat().st_mode | stat.S_IXUSR)

    def _run(self, *args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}:/usr/bin:/bin"
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ["bash", str(SCAN_SCRIPT), *args, str(self.repo)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def _init_git(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is not installed")
        self._git("init", "-q")
        self._git("config", "user.email", "audit@example.com")
        self._git("config", "user.name", "Audit Test")
        self._git("add", ".")
        self._git("commit", "-qm", "initial")

    def test_recursively_reports_format_drift(self) -> None:
        nested = self.repo / "internal" / "service"
        nested.mkdir(parents=True)
        (nested / "bad.go").write_text("package service\n", encoding="utf-8")

        result = self._run()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("[发现问题] gofmt 格式：1/2 个文件存在漂移", result.stdout)
        self.assertIn("./internal/service/bad.go", result.stdout)

    def test_tool_diagnostic_is_reported_as_issue(self) -> None:
        result = self._run(extra_env={"FAKE_GO_EXIT": "7", "FAKE_GO_OUTPUT": "diagnostic"})

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("[发现问题] go vet ./...（退出码 7）", result.stdout)
        self.assertIn("[发现问题] go build ./...（退出码 7）", result.stdout)
        self.assertIn("发现问题：2", result.stdout)

    def test_tool_without_diagnostic_is_unclassified(self) -> None:
        result = self._run(extra_env={"FAKE_GO_EXIT": "7"})

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("[未分类失败] go vet ./... 无诊断退出（退出码 7）", result.stdout)
        self.assertIn("未分类失败：2", result.stdout)

    def test_zero_tests_is_reported_once_without_shell_error(self) -> None:
        result = self._run()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(1, result.stdout.count("_test.go 文件数：0"))
        self.assertNotIn("integer expression expected", result.stderr)

    def test_strict_mode_fails_when_optional_tools_are_missing(self) -> None:
        result = self._run("--strict")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("未运行：4", result.stdout)

    def test_default_go_commands_are_offline_and_module_readonly(self) -> None:
        env_log = self.root / "go-env.log"

        result = self._run(extra_env={"FAKE_ENV_LOG": str(env_log)})

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        lines = env_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(3, len(lines))
        for line in lines:
            self.assertEqual("off|local|-mod=readonly|off", line)

    def test_inherited_module_mode_cannot_disable_readonly(self) -> None:
        env_log = self.root / "go-env.log"

        result = self._run(
            extra_env={"FAKE_ENV_LOG": str(env_log), "GOFLAGS": "-trimpath -mod=mod"}
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("最终 GOFLAGS：-trimpath -mod=readonly", result.stdout)
        for line in env_log.read_text(encoding="utf-8").splitlines():
            self.assertIn("|-trimpath -mod=readonly|", line)

    def test_dangerous_inherited_go_flags_are_filtered(self) -> None:
        result = self._run(extra_env={"GOFLAGS": "-overlay=tmp.json -toolexec helper -trimpath"})

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("已过滤继承的 GOFLAGS 参数 -overlay=tmp.json", result.stdout)
        self.assertIn("已过滤继承的 GOFLAGS 参数 -toolexec 及其值", result.stdout)
        self.assertIn("最终 GOFLAGS：-trimpath -mod=readonly", result.stdout)

    def test_package_scope_does_not_recurse_into_subpackages(self) -> None:
        package_dir = self.repo / "internal" / "service"
        nested_dir = package_dir / "nested"
        nested_dir.mkdir(parents=True)
        (package_dir / "service.go").write_text("package service\n", encoding="utf-8")
        (nested_dir / "bad.go").write_text("package nested\n", encoding="utf-8")

        result = self._run("--package-dir", "internal/service")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("package:./internal/service", result.stdout)
        self.assertIn("当前 Go 文件：1", result.stdout)
        self.assertNotIn("nested/bad.go", result.stdout)

    def test_directory_scope_recurses(self) -> None:
        nested_dir = self.repo / "internal" / "service" / "nested"
        nested_dir.mkdir(parents=True)
        (nested_dir / "bad.go").write_text("package nested\n", encoding="utf-8")

        result = self._run("--target", "internal")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("recursive:./internal", result.stdout)
        self.assertIn("./internal/service/nested/bad.go", result.stdout)

    def test_file_scope_does_not_scan_unselected_files(self) -> None:
        (self.repo / "bad.go").write_text("package main\n", encoding="utf-8")

        result = self._run("--target", "main.go")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("file:./main.go", result.stdout)
        self.assertIn("当前 Go 文件：1", result.stdout)
        self.assertNotIn("./bad.go", result.stdout)

    def test_multiple_file_targets_expand_to_their_owning_packages(self) -> None:
        first_dir = self.repo / "internal" / "first"
        second_dir = self.repo / "internal" / "second"
        first_dir.mkdir(parents=True)
        second_dir.mkdir(parents=True)
        (first_dir / "first.go").write_text("package first\n", encoding="utf-8")
        (second_dir / "second.go").write_text("package second\n", encoding="utf-8")

        result = self._run(
            "--target",
            "internal/first/first.go",
            "--target",
            "internal/second/second.go",
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("当前 Go 文件：2", result.stdout)
        self.assertIn("Go package pattern 数量：2", result.stdout)

    def test_package_pattern_and_resolved_packages_are_distinct(self) -> None:
        result = self._run(
            extra_env={"FAKE_GO_LIST_OUTPUT": "example.com/audit\\nexample.com/audit/a\\nexample.com/audit/b"}
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Go package pattern 数量：1", result.stdout)
        self.assertIn("  - ./...", result.stdout)
        self.assertIn("已解析 Go package 数量：3", result.stdout)

    def test_dependency_probe_failure_is_reported_once_and_cascades(self) -> None:
        result = self._run(
            extra_env={
                "FAKE_GO_LIST_EXIT": "1",
                "FAKE_GO_LIST_ERROR": "module lookup disabled by GOPROXY=off",
            }
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual(1, result.stdout.count("module lookup disabled by GOPROXY=off"))
        self.assertIn("[前置条件未满足] package 解析失败", result.stdout)
        self.assertIn("[未运行] go vet ./...：package 前置解析未完成", result.stdout)
        self.assertIn("前置条件未满足：1", result.stdout)

    def test_rejects_scope_outside_target_root(self) -> None:
        outside_file = self.root / "outside.go"
        outside_file.write_text("package outside\n", encoding="utf-8")

        result = self._run("--target", str(outside_file))

        self.assertEqual(2, result.returncode)
        self.assertIn("位于目标根之外", result.stderr)

    def test_working_diff_combines_unstaged_staged_and_untracked_files(self) -> None:
        self._init_git()
        (self.repo / "main.go").write_text("package main\n\nfunc main() { println(1) }\n", encoding="utf-8")
        (self.repo / "staged.go").write_text("package main\n", encoding="utf-8")
        self._git("add", "staged.go")
        (self.repo / "untracked.go").write_text("package main\n", encoding="utf-8")

        result = self._run("--diff", "working")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("diff:working", result.stdout)
        self.assertIn("Diff Go 路径：3", result.stdout)
        self.assertIn("当前 Go 文件：3", result.stdout)

    def test_staged_diff_ignores_unstaged_and_untracked_files(self) -> None:
        self._init_git()
        (self.repo / "main.go").write_text("package main\n\nfunc main() { println(1) }\n", encoding="utf-8")
        (self.repo / "staged.go").write_text("package main\n", encoding="utf-8")
        self._git("add", "staged.go")
        (self.repo / "untracked.go").write_text("package main\n", encoding="utf-8")

        result = self._run("--diff", "staged")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("diff:staged", result.stdout)
        self.assertIn("Diff Go 路径：1", result.stdout)
        self.assertIn("当前 Go 文件：1", result.stdout)

    def test_revision_range_diff(self) -> None:
        self._init_git()
        (self.repo / "range.go").write_text("package main\n", encoding="utf-8")
        self._git("add", "range.go")
        self._git("commit", "-qm", "add range file")

        result = self._run("--diff-range", "HEAD~1..HEAD")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("diff-range:HEAD~1..HEAD", result.stdout)
        self.assertIn("Diff Go 路径：1", result.stdout)

    def test_invalid_revision_range_fails_preflight(self) -> None:
        self._init_git()

        result = self._run("--diff-range", "missing-ref...HEAD")

        self.assertEqual(2, result.returncode)
        self.assertIn("无法读取 Git diff", result.stderr)

    def test_diff_and_path_scope_are_mutually_exclusive(self) -> None:
        result = self._run("--diff", "working", "--target", "main.go")

        self.assertEqual(2, result.returncode)
        self.assertIn("不能与 --target", result.stderr)

    def test_empty_go_diff_does_not_expand_to_repository(self) -> None:
        self._init_git()

        result = self._run("--diff", "working")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Diff Go 路径：0", result.stdout)
        self.assertIn("当前 Go 文件：0", result.stdout)
        self.assertIn("Go package pattern 数量：0", result.stdout)

    def test_deleted_diff_path_is_reported_and_owning_package_is_checked(self) -> None:
        (self.repo / "deleted.go").write_text("package main\n", encoding="utf-8")
        self._init_git()
        (self.repo / "deleted.go").unlink()

        result = self._run("--diff", "working")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Diff Go 路径：1", result.stdout)
        self.assertIn("当前不存在或不可扫描的 Diff 路径：1", result.stdout)
        self.assertIn("Go package pattern 数量：1", result.stdout)

    def test_deleted_last_go_file_does_not_add_empty_package(self) -> None:
        package_dir = self.repo / "removed"
        package_dir.mkdir()
        (package_dir / "deleted.go").write_text("package removed\n", encoding="utf-8")
        self._init_git()
        (package_dir / "deleted.go").unlink()

        result = self._run("--diff", "working")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("当前不存在或不可扫描的 Diff 路径：1", result.stdout)
        self.assertIn("Go package pattern 数量：0", result.stdout)

    def test_ignored_go_file_is_excluded_from_recursive_scope(self) -> None:
        self._init_git()
        (self.repo / ".gitignore").write_text("generated/\n", encoding="utf-8")
        generated = self.repo / "generated"
        generated.mkdir()
        (generated / "ignored.go").write_text("package generated\n", encoding="utf-8")

        result = self._run()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("当前 Go 文件：1", result.stdout)
        self.assertNotIn("ignored.go", result.stdout)

    def test_dynamic_checks_are_disabled_by_default(self) -> None:
        command_log = self.root / "commands.log"

        result = self._run(extra_env={"FAKE_COMMAND_LOG": str(command_log)})

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        commands = command_log.read_text(encoding="utf-8").splitlines()
        self.assertFalse(any(command.startswith("test ") for command in commands))
        self.assertIn("测试、竞态与覆盖率默认不执行", result.stdout)

    def test_explicit_test_race_and_cover_use_selected_package_scope(self) -> None:
        command_log = self.root / "commands.log"

        result = self._run(
            "--test",
            "--race",
            "--cover",
            "--test-timeout",
            "30s",
            extra_env={"FAKE_COMMAND_LOG": str(command_log)},
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        commands = command_log.read_text(encoding="utf-8").splitlines()
        self.assertIn("test -timeout=30s ./...", commands)
        self.assertIn("test -race -timeout=30s ./...", commands)
        self.assertIn("test -cover -timeout=30s ./...", commands)
        self.assertIn("命令：env", result.stdout)

    def test_json_output_matches_text_scope_and_status(self) -> None:
        json_output = self.root / "scan.json"

        result = self._run(
            "--json-output",
            str(json_output),
            extra_env={"FAKE_GO_LIST_OUTPUT": "example.com/audit\\nexample.com/audit/sub"},
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(json_output.read_text(encoding="utf-8"))
        self.assertEqual(1, payload["schema_version"])
        self.assertEqual(["./..."], payload["scope"]["package_patterns"])
        self.assertEqual(2, payload["scope"]["resolved_package_count"])
        self.assertEqual(
            ["example.com/audit", "example.com/audit/sub"],
            payload["scope"]["resolved_packages"],
        )
        self.assertEqual(3, payload["summary"]["通过"])
        self.assertEqual(2, len(payload["commands"]))
        self.assertIn(f"JSON 输出：{json_output}", result.stdout)

    def test_explicit_output_directory_preserves_full_tool_outputs(self) -> None:
        output_directory = self.root / "logs"
        output_directory.mkdir()

        result = self._run(
            "--output-dir",
            str(output_directory),
            extra_env={"FAKE_GO_OUTPUT": "tool diagnostic", "FAKE_GO_EXIT": "1"},
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        output_files = sorted(output_directory.glob("*.log"))
        self.assertGreaterEqual(len(output_files), 4)
        self.assertTrue(
            any("tool diagnostic" in path.read_text(encoding="utf-8") for path in output_files)
        )
        self.assertIn("完整输出：", result.stdout)

    def test_output_directory_must_be_empty(self) -> None:
        output_directory = self.root / "logs"
        output_directory.mkdir()
        (output_directory / "existing.log").write_text("keep\n", encoding="utf-8")

        result = self._run("--output-dir", str(output_directory))

        self.assertEqual(2, result.returncode)
        self.assertIn("必须为空", result.stderr)
        self.assertEqual("keep\n", (output_directory / "existing.log").read_text(encoding="utf-8"))

    def test_rejects_non_module_root_before_running_tools(self) -> None:
        (self.repo / "go.mod").unlink()

        result = self._run()

        self.assertEqual(2, result.returncode)
        self.assertIn("没有 go.mod 或 go.work", result.stderr)

    @unittest.skipUnless(shutil.which("go"), "go is not installed")
    def test_real_go_fixture_expands_recursive_pattern_to_packages(self) -> None:
        first = self.repo / "first"
        second = self.repo / "second"
        first.mkdir()
        second.mkdir()
        (first / "first.go").write_text("package first\n", encoding="utf-8")
        (second / "second.go").write_text("package second\n", encoding="utf-8")
        environment = os.environ.copy()
        environment.pop("GOFLAGS", None)
        environment["GOCACHE"] = str(self.root / "go-cache")
        environment["GOMODCACHE"] = str(self.root / "go-mod-cache")
        environment["GOENV"] = "off"

        result = subprocess.run(
            ["bash", str(SCAN_SCRIPT), str(self.repo)],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Go package pattern 数量：1", result.stdout)
        self.assertIn("已解析 Go package 数量：3", result.stdout)


if __name__ == "__main__":
    unittest.main()
