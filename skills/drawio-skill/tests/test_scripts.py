from __future__ import annotations

import base64
import sys
import tempfile
import unittest
import urllib.parse
import zlib
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import repair_png  # noqa: E402
import validate_drawio  # noqa: E402


VALID_GRAPH = """<mxGraphModel><root>
<mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="2" vertex="1" parent="1"><mxGeometry x="0" y="0" width="10" height="10" as="geometry"/></mxCell>
<mxCell id="3" vertex="1" parent="1"><mxGeometry x="20" y="0" width="10" height="10" as="geometry"/></mxCell>
<mxCell id="4" edge="1" parent="1" source="2" target="3"><mxGeometry relative="1" as="geometry"/></mxCell>
</root></mxGraphModel>"""


def compressed_page(graph: str) -> str:
    quoted = urllib.parse.quote(graph, safe="~()*!.'")
    compressor = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    payload = compressor.compress(quoted.encode()) + compressor.flush()
    return base64.b64encode(payload).decode()


class ValidateDrawioTests(unittest.TestCase):
    def validate_text(self, text: str) -> int:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "diagram.drawio"
            path.write_text(text, encoding="utf-8")
            return validate_drawio.validate(path)

    def test_accepts_uncompressed_page(self) -> None:
        xml = f'<mxfile><diagram name="Page-1">{VALID_GRAPH}</diagram></mxfile>'
        self.assertEqual(self.validate_text(xml), 0)

    def test_accepts_compressed_page(self) -> None:
        xml = f'<mxfile><diagram name="Page-1">{compressed_page(VALID_GRAPH)}</diagram></mxfile>'
        self.assertEqual(self.validate_text(xml), 0)

    def test_rejects_edge_without_geometry(self) -> None:
        graph = VALID_GRAPH.replace(
            '<mxCell id="4" edge="1" parent="1" source="2" target="3"><mxGeometry relative="1" as="geometry"/></mxCell>',
            '<mxCell id="4" edge="1" parent="1" source="2" target="3"/>',
        )
        xml = f'<mxfile><diagram name="Page-1">{graph}</diagram></mxfile>'
        self.assertEqual(self.validate_text(xml), 1)


class RepairPngTests(unittest.TestCase):
    def test_valid_png_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.png"
            original = repair_png.PNG_SIGNATURE + repair_png.IEND
            path.write_bytes(original)
            self.assertFalse(repair_png.repair(path))
            self.assertEqual(path.read_bytes(), original)

    def test_known_truncation_is_repaired(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "truncated.png"
            path.write_bytes(repair_png.PNG_SIGNATURE + b"payload\x00\x00\x00\x00")
            self.assertTrue(repair_png.repair(path))
            self.assertTrue(path.read_bytes().endswith(repair_png.IEND))

    def test_unknown_corruption_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.png"
            path.write_bytes(repair_png.PNG_SIGNATURE + b"broken")
            with self.assertRaises(ValueError):
                repair_png.repair(path)


if __name__ == "__main__":
    unittest.main()
