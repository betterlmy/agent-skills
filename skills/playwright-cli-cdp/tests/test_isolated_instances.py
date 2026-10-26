"""Deterministic launcher and wrapper regressions; no real browser required."""
import http.server
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VersionHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({'webSocketDebuggerUrl': 'ws://127.0.0.1/devtools/browser/test'}).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class IsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), VersionHandler)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.port = self.server.server_port
        # Exercise the native Unix branch even when tests run under WSL.
        self.executable('grep', '#!/bin/bash\nexit 1\n')
        self.executable('chrome', '''#!/bin/bash
for arg in "$@"; do
  case "$arg" in --user-data-dir=*) profile="${arg#*=}";; esac
done
[[ "${MOCK_TIMEOUT:-}" != 1 ]] || exit 0
printf '%s\\n' "$MOCK_PORT" > "$profile/DevToolsActivePort"
sleep .1
printf '%s\\n%s\\n' "$MOCK_PORT" "${MOCK_BROWSER_PATH:-/devtools/browser/test}" > "$profile/DevToolsActivePort"
''')
        self.executable('playwright-cli', '#!/bin/bash\nprintf "%s\\n" "$PLAYWRIGHT_MCP_OUTPUT_DIR"\n')
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(('CDP_', 'PLAYWRIGHT_'))}
        self.env.update(PATH=f'{self.base}:{os.environ["PATH"]}', HOME=str(self.base),
                        TMPDIR=str(self.base), CHROME_BIN=str(self.base / 'chrome'),
                        MOCK_PORT=str(self.port), CDP_TIMEOUT_SECONDS='1')

    def executable(self, name, content):
        path = self.base / name
        path.write_text(content)
        path.chmod(0o755)

    def launch(self, **overrides):
        return subprocess.run(['bash', str(ROOT / 'scripts/open-chrome-remote.sh')],
                              env={**self.env, **overrides}, capture_output=True, text=True, timeout=5)

    def test_dynamic_port_and_partial_file(self):
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        instance = json.loads(result.stdout)
        self.assertEqual(instance['endpoint'], f'http://127.0.0.1:{self.port}')
        self.assertTrue(instance['session'].startswith('agent-'))
        self.assertEqual(Path(instance['profile']).name, instance['session'])

    def test_existing_profile_is_rejected(self):
        result = self.launch(CDP_USER_DATA_DIR=str(self.base))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_occupied_fixed_port_is_not_adopted(self):
        result = self.launch(CDP_PORT=str(self.port))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_timeout_retains_profile_and_reports_failure(self):
        result = self.launch(MOCK_TIMEOUT='1', CDP_SESSION='timeout-test')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('resources retained', result.stderr)
        self.assertTrue((self.base / '.cache/playwright-cli-cdp/profiles/timeout-test').is_dir())

    def test_mismatched_browser_identity_is_rejected(self):
        result = self.launch(MOCK_BROWSER_PATH='/devtools/browser/wrong')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_unsafe_host_and_session_are_rejected(self):
        for override in ({'CDP_HOST': '0.0.0.0'}, {'CDP_SESSION': '../unsafe'}, {'CDP_PORT': '65536'}):
            with self.subTest(override=override):
                self.assertNotEqual(self.launch(**override).returncode, 0)

    def test_wrapper_separates_session_outputs(self):
        outputs = []
        for session in ('task-a', 'task-b'):
            result = subprocess.run(['bash', str(ROOT / 'scripts/playwright-cdp.sh'),
                                     f'-s={session}', 'snapshot'], env=self.env,
                                    capture_output=True, text=True, check=True)
            outputs.append(result.stdout.strip())
            self.assertTrue(outputs[-1].endswith('/' + session))
        self.assertNotEqual(*outputs)

    def test_wrapper_rejects_session_path_traversal(self):
        result = subprocess.run(['bash', str(ROOT / 'scripts/playwright-cdp.sh'),
                                 '-s=../unsafe', 'snapshot'], env=self.env, capture_output=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
