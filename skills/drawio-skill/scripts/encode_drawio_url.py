#!/usr/bin/env python3
"""Encode a .drawio XML file into a diagrams.net viewer URL.

Used as the browser fallback when the draw.io desktop CLI is unavailable.
Produces a client-side URL — the diagram XML is encoded in the URL
fragment (after `#`), so nothing is uploaded to any server.

Usage: python3 encode_drawio_url.py <path/to/input.drawio>
"""
import base64
import argparse
import urllib.parse
import zlib
import xml.etree.ElementTree as ET
from pathlib import Path


def encode(xml: str) -> str:
    # Raw deflate (no zlib header) — diagrams.net uses mxGraph's raw inflate
    c = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed = c.compress(xml.encode("utf-8")) + c.flush()
    # Standard base64 (atob rejects url-safe -/_); strip newlines
    encoded = base64.b64encode(compressed).decode("utf-8").replace("\n", "")
    return (
        "https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&edit=_blank#R"
        + urllib.parse.quote(encoded, safe="")
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="input .drawio file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        xml = args.path.read_text(encoding="utf-8")
        root = ET.fromstring(xml)
    except (OSError, UnicodeError, ET.ParseError) as error:
        raise SystemExit(str(error)) from error
    if root.tag != "mxfile":
        raise SystemExit("input root must be <mxfile>")
    print(encode(xml))
