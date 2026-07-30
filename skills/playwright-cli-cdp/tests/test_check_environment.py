#!/usr/bin/env python3
"""环境检查脚本的版本漂移与关键能力回归测试。"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-environment.sh"


class CheckEnvironmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.chrome = self.root / "chrome"
        self.write_executable(self.chrome, "#!/usr/bin/env bash\nexit 0\n")
        self.write_executable(self.root / "curl", "#!/usr/bin/env bash\nexit 0\n")

    @staticmethod
    def write_executable(path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)

    def run_check(
        self,
        version: str = "0.1.17",
        missing_capability: str = "",
    ) -> subprocess.CompletedProcess[str]:
        help_lines = [
            "  attach [name]",
            "  snapshot [target]",
            "  run-code [code]",
            "  tracing-start",
            "  video-start [filename]",
        ]
        help_text = "\\n".join(
            line
            for line in help_lines
            if not missing_capability or missing_capability not in line
        )
        self.write_executable(
            self.root / "playwright-cli",
            "#!/usr/bin/env bash\n"
            f"if [[ \"${{1:-}}\" == \"--version\" ]]; then printf '%s\\n' '{version}'; exit 0; fi\n"
            f"if [[ \"${{1:-}}\" == \"--help\" ]]; then printf '%b\\n' '{help_text}'; exit 0; fi\n"
            "exit 0\n",
        )
        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{self.root}:{env.get('PATH', '')}",
                "CHROME_BIN": str(self.chrome),
                "CDP_TIMEOUT_SECONDS": "1",
            }
        )
        return subprocess.run(
            ["/bin/bash", str(SCRIPT)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
            cwd=self.root,
        )

    def test_verified_version_and_capabilities_pass(self) -> None:
        result = self.run_check()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("与本机验证版本", result.stdout)

    def test_version_drift_warns_but_capabilities_allow_continue(self) -> None:
        result = self.run_check(version="0.2.0")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("与本机验证版本 0.1.17 不同", result.stdout)

    def test_missing_required_capability_fails(self) -> None:
        result = self.run_check(missing_capability="run-code")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("缺少必需能力: run-code", result.stdout)


if __name__ == "__main__":
    unittest.main()
