# -*- coding: utf-8 -*-
"""tavily.py 的确定性测试：不触网，api_call 全部被替换。"""

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import sys
import unittest

PKG = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = PKG / "scripts" / "tavily.py"

spec = importlib.util.spec_from_file_location("tavily_web_script", SCRIPT)
mod = module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def run_main(argv, key="tvly-testkey1234", captured_call=None, responses=None):
    """运行 main(argv)，注入假密钥；返回 (exit_code, stdout, captured calls)。"""
    saved = os.environ.get("TAVILY_API_KEY")
    os.environ["TAVILY_API_KEY"] = key

    calls = []

    def fake_api_call(endpoint, payload=None, api_key=None, method=None, timeout=120):
        calls.append((endpoint, payload, method))
        if captured_call is not None:
            captured_call.append((endpoint, payload, method))
        if responses:
            status, data = responses.pop(0)
            return status, data
        return 200, {"ok": True}

    original = module.api_call
    module.api_call = fake_api_call
    buf = io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(buf):
            code = module.main(argv)
    except SystemExit as e:
        code = e.code
    finally:
        module.api_call = original
        if saved is None:
            os.environ.pop("TAVILY_API_KEY", None)
        else:
            os.environ["TAVILY_API_KEY"] = saved
    return code, buf.getvalue(), calls


class NoKeyTests(unittest.TestCase):
    def test_missing_key_exits_2_with_guide(self):
        saved = os.environ.pop("TAVILY_API_KEY", None)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                with self.assertRaises(SystemExit) as ctx:
                    module.main(["search", "x"])
            self.assertEqual(ctx.exception.code, 2)
        finally:
            if saved is not None:
                os.environ["TAVILY_API_KEY"] = saved
        out = buf.getvalue()
        self.assertIn("TAVILY_API_KEY", out)
        self.assertIn("export", out)

    def test_blank_key_exits_2(self):
        saved = os.environ.get("TAVILY_API_KEY")
        os.environ["TAVILY_API_KEY"] = "   "
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as ctx:
                    module.main(["search", "x"])
            self.assertEqual(ctx.exception.code, 2)
        finally:
            if saved is None:
                os.environ.pop("TAVILY_API_KEY", None)
            else:
                os.environ["TAVILY_API_KEY"] = saved


class PayloadTests(unittest.TestCase):
    def test_search_payload(self):
        captured = []
        code, out, _ = run_main(
            ["search", "latest AI agent releases", "--depth", "advanced",
             "--topic", "news", "--days", "3", "--max-results", "8", "--include-answer"],
            captured_call=captured,
        )
        self.assertEqual(code, 0)
        endpoint, payload, method = captured[0]
        self.assertEqual(endpoint, "/search")
        self.assertIn(method, (None, "POST"))
        self.assertEqual(payload["query"], "latest AI agent releases")
        self.assertEqual(payload["search_depth"], "advanced")
        self.assertEqual(payload["topic"], "news")
        self.assertEqual(payload["days"], 3)
        self.assertEqual(payload["max_results"], 8)
        self.assertTrue(payload["include_answer"])
        parsed = json.loads(out)
        self.assertTrue(parsed["ok"])

    def test_search_defaults(self):
        captured = []
        run_main(["search", "q"], captured_call=captured)
        _, payload, _ = captured[0]
        self.assertEqual(payload["search_depth"], "basic")
        self.assertEqual(payload["topic"], "general")
        self.assertEqual(payload["max_results"], 5)
        self.assertNotIn("days", payload)
        self.assertNotIn("include_answer", payload)

    def test_extract_payload(self):
        captured = []
        run_main(
            ["extract", "https://a.example/1", "https://b.example/2", "--include-images"],
            captured_call=captured,
        )
        _, payload, _ = captured[0]
        self.assertEqual(captured[0][0], "/extract")
        self.assertEqual(payload["urls"], ["https://a.example/1", "https://b.example/2"])
        self.assertTrue(payload["include_images"])

    def test_map_payload(self):
        captured = []
        run_main(["map", "https://docs.example.com", "--max-depth", "2"], captured_call=captured)
        _, payload, _ = captured[0]
        self.assertEqual(captured[0][0], "/map")
        self.assertEqual(payload["url"], "https://docs.example.com")
        self.assertEqual(payload["max_depth"], 2)

    def test_crawl_payload(self):
        captured = []
        code, out, _ = run_main(
            ["crawl", "https://docs.example.com", "--max-depth", "2", "--max-breadth", "10"],
            captured_call=captured,
            responses=[(200, {"results": [{"url": "https://docs.example.com/p1"}]})],
        )
        self.assertEqual(code, 0)
        self.assertEqual(captured[0][0], "/crawl")
        self.assertEqual(captured[0][1]["url"], "https://docs.example.com")
        self.assertEqual(captured[0][1]["max_depth"], 2)
        self.assertEqual(captured[0][1]["max_breadth"], 10)
        parsed = json.loads(out)
        self.assertIn("results", parsed)

    def test_crawl_defaults(self):
        captured = []
        code, _, _ = run_main(
            ["crawl", "https://docs.example.com"],
            captured_call=captured,
            responses=[(200, {"results": []})],
        )
        self.assertEqual(code, 0)
        self.assertEqual(captured[0][0], "/crawl")
        self.assertEqual(captured[0][1]["url"], "https://docs.example.com")
        self.assertNotIn("max_depth", captured[0][1])
        self.assertNotIn("max_breadth", captured[0][1])

    def test_research_no_wait_payload(self):
        captured = []
        code, _, _ = run_main(
            ["research", "competitive landscape", "--model", "pro", "--no-wait"],
            captured_call=captured,
        )
        self.assertEqual(code, 0)
        endpoint, payload, _ = captured[0]
        self.assertEqual(endpoint, "/research")
        # 实测 /research 入参字段为 input（非 query）
        self.assertEqual(payload["input"], "competitive landscape")
        self.assertEqual(payload["model"], "pro")
        self.assertEqual(len(captured), 1)  # --no-wait 不轮询

    def test_research_status_get(self):
        captured = []
        code, _, _ = run_main(["research-status", "job-42"], captured_call=captured)
        self.assertEqual(code, 0)
        endpoint, _, method = captured[0]
        self.assertEqual(endpoint, "/research/job-42")
        self.assertEqual(method, "GET")
        self.assertEqual(len(captured), 1)


class MaskingTests(unittest.TestCase):
    def test_check_output_masks_key(self):
        out_key = "tvly-secret-abc9"
        _, out, _ = run_main(["check"], key=out_key)
        self.assertNotIn(out_key, out)
        self.assertIn("***abc9", out)


class ErrorPathTests(unittest.TestCase):
    def test_auth_error_exits_3(self):
        code, out, _ = run_main(
            ["search", "q"],
            responses=[(401, {"detail": "invalid key"})],
        )
        self.assertEqual(code, 3)
        self.assertIn("鉴权失败", out)
        self.assertNotIn("tvly-testkey1234", out)

    def test_rate_limit_exits_3_with_hint(self):
        code, out, _ = run_main(
            ["search", "q"],
            responses=[(429, {"message": "slow down"})],
        )
        self.assertEqual(code, 3)
        self.assertIn("限流", out)

    def test_network_error_exits_4(self):
        code, out, _ = run_main(
            ["search", "q"],
            responses=[(0, {"error": "network: refused"})],
        )
        self.assertEqual(code, 4)
        self.assertIn("network", out)

    def test_research_poll_completed(self):
        import time as _time
        original_sleep = _time.sleep
        _time.sleep = lambda *_: None
        try:
            code, out, calls = run_main(
                ["research-poll", "job-1", "--timeout", "60", "--interval", "1"],
                responses=[(200, {"status": "completed", "report": "done"})],
            )
        finally:
            _time.sleep = original_sleep
        self.assertEqual(code, 0)
        self.assertIn('"report": "done"', out)
        self.assertEqual(calls[0][0], "/research/job-1")


if __name__ == "__main__":
    unittest.main()
