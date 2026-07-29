from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
RENDER_SCRIPT = SKILL_DIR / "scripts" / "render_scan_json.py"


class RenderScanJsonTests(unittest.TestCase):
    def test_rejects_incomplete_command_record_without_replacing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metadata = root / "metadata"
            events = root / "events"
            commands = root / "commands"
            output = root / "result.json"
            metadata.write_bytes(b"scope\0recursive:.\0")
            events.write_bytes("通过\0gofmt\0".encode("utf-8"))
            commands.write_bytes(b"incomplete\0")
            output.write_text('{"old": true}\n', encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    str(RENDER_SCRIPT),
                    "--output",
                    str(output),
                    "--root",
                    str(root),
                    "--module-mode",
                    "readonly",
                    "--goflags=-mod=readonly",
                    "--network",
                    "blocked",
                    "--package-count",
                    "1",
                    "--deleted",
                    "0",
                    "--metadata",
                    str(metadata),
                    "--events",
                    str(events),
                    "--commands",
                    str(commands),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertEqual({"old": True}, json.loads(output.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
