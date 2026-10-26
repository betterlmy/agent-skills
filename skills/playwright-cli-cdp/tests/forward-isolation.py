#!/usr/bin/env python3
"""Verify two already-started disposable instances. Leaves browsers attached.

Usage: python3 tests/forward-isolation.py a.json b.json [--simulate-focus]
Only use fresh test profiles: navigates their pages and writes synthetic storage.
"""
import argparse
import concurrent.futures
import http.server
import json
from pathlib import Path
import subprocess
import threading

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('instances', nargs=2, type=Path)
parser.add_argument('--simulate-focus', action='store_true',
                    help='Explicitly emulate page focus; does not validate desktop focus')
args = parser.parse_args()
instances = [json.loads(path.read_text()) for path in args.instances]
for field in ('session', 'endpoint', 'profile'):
    assert len({instance[field] for instance in instances}) == 2, field
wrapper = Path(__file__).resolve().parents[1] / 'scripts/playwright-cdp.sh'


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'''<!doctype html><title>CDP isolation test</title>
<label>Value <input id="value"></label>
<button onclick="document.querySelector('#result').textContent=document.querySelector('#value').value">Apply</button>
<output id="result"></output>'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *unused):
        pass


def cli(instance, *command):
    result = subprocess.run(['bash', str(wrapper), '-s=' + instance['session'], *command],
                            capture_output=True, text=True, timeout=30)
    if result.returncode or '### Error' in result.stdout:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}'


def exercise(pair):
    name, instance = pair
    cli(instance, 'attach', '--cdp=' + instance['endpoint'])
    cli(instance, 'goto', base + '/' + name)
    if args.simulate_focus:
        cli(instance, 'run-code', '''async page => {
          const cdp = await page.context().newCDPSession(page);
          await cdp.send('Emulation.setFocusEmulationEnabled', {enabled: true});
          return await page.evaluate(() => document.visibilityState);
        }''')
    else:
        cli(instance, 'run-code', 'async page => { await page.bringToFront(); }')
    cli(instance, 'fill', '#value', name)
    cli(instance, 'click', "getByRole('button', { name: 'Apply' })")
    cli(instance, 'run-code', '''async page => {
      await page.evaluate(value => {
        localStorage.setItem('cdp-isolation-test', value);
        document.cookie = 'cdp_isolation_test=' + value + '; path=/';
      }, %s);
    }''' % json.dumps(name))


try:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        list(pool.map(exercise, zip('ab', instances)))
    for name, instance in zip('ab', instances):
        raw = cli(instance, '--raw', 'eval', '''JSON.stringify({
          url: location.pathname,
          result: document.querySelector('#result').textContent,
          local: localStorage.getItem('cdp-isolation-test'),
          cookie: document.cookie
        })''')
        actual = json.loads(raw.strip())
        if isinstance(actual, str):
            actual = json.loads(actual)
        assert actual == dict(url='/' + name, result=name, local=name,
                              cookie='cdp_isolation_test=' + name), actual
    cli(instances[0], 'goto', base + '/a-next')
    assert json.loads(cli(instances[1], '--raw', 'eval', 'location.pathname').strip()) == '/b'
    print(json.dumps(dict(passed=True, instances=instances,
                          focus_simulated=args.simulate_focus,
                          checks=['unique resources', 'concurrent attach/navigation/fill/locator click',
                                  'same-origin cookie/localStorage isolation', 'independent navigation'])))
finally:
    server.shutdown()
    server.server_close()
