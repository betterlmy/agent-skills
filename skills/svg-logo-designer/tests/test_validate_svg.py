from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_svg.py"
SPEC = importlib.util.spec_from_file_location("validate_svg", SCRIPT)
assert SPEC and SPEC.loader
validate_svg = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_svg
SPEC.loader.exec_module(validate_svg)


VALID = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <title id="logo-title">A&amp;B logo</title>
  <desc id="logo-desc">Two circles</desc>
  <defs><linearGradient id="brand-gradient"><stop offset="0" stop-color="#000"/></linearGradient></defs>
  <circle cx="30" cy="50" r="20" fill="url(#brand-gradient)"/>
  <circle cx="70" cy="50" r="20" fill="#fff"/>
</svg>
"""


class ValidateSvgTests(unittest.TestCase):
    def validate(self, content: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "logo.svg"
            path.write_text(content, encoding="utf-8")
            return validate_svg.validate_svg(path)

    def test_accepts_static_accessible_svg(self):
        self.assertTrue(self.validate(VALID).ok)

    def test_rejects_unescaped_user_text(self):
        result = self.validate(VALID.replace("A&amp;B", "A&B"))
        self.assertIn("invalid XML", result.errors[0])

    def test_rejects_script_and_event_handler(self):
        unsafe = VALID.replace(
            "<circle cx=\"30\"", "<script>alert(1)</script><circle onload=\"alert(1)\" cx=\"30\""
        )
        result = self.validate(unsafe)
        self.assertTrue(any("script" in error for error in result.errors))
        self.assertTrue(any("event attribute" in error for error in result.errors))

    def test_rejects_external_reference(self):
        unsafe = VALID.replace("fill=\"#fff\"", "fill=\"url(https://example.com/x.svg#paint)\"")
        self.assertTrue(any("external url()" in error for error in self.validate(unsafe).errors))

    def test_rejects_data_uri_but_allows_colon_in_description(self):
        unsafe = VALID.replace("fill=\"#fff\"", "fill=\"data:image/svg+xml;base64,PHN2Zz4=\"")
        self.assertTrue(any("dangerous URI scheme" in error for error in self.validate(unsafe).errors))
        self.assertTrue(self.validate(VALID.replace("Two circles", "Data: two circles")).ok)

    def test_rejects_processing_instruction_and_empty_description(self):
        unsafe = VALID.replace(
            "<svg ", "<?xml-stylesheet href=\"https://example.com/theme.css\"?><svg ", 1
        ).replace("Two circles", "")
        result = self.validate(unsafe)
        self.assertTrue(any("forbidden" in error for error in result.errors))
        self.assertTrue(any("desc element must not be empty" in error for error in result.errors))

    def test_rejects_missing_and_duplicate_ids(self):
        unsafe = VALID.replace("id=\"logo-desc\"", "id=\"logo-title\"").replace(
            "url(#brand-gradient)", "url(#missing)"
        )
        result = self.validate(unsafe)
        self.assertTrue(any("duplicate id" in error for error in result.errors))
        self.assertTrue(any("missing id" in error for error in result.errors))

    def test_command_entrypoint_reports_pass_and_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "valid.svg").write_text(VALID, encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(validate_svg.main([str(root)]), 0)
            self.assertIn("PASS", stdout.getvalue())

            (root / "invalid.svg").write_text(VALID.replace("A&amp;B", "A&B"), encoding="utf-8")
            stderr = io.StringIO()
            stdout = io.StringIO()
            with redirect_stderr(stderr), redirect_stdout(stdout):
                self.assertEqual(validate_svg.main([str(root)]), 1)
            self.assertIn("invalid XML", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
