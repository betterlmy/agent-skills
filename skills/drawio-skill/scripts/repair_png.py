#!/usr/bin/env python3
"""Repair the known truncated IEND form in Draw.io embedded PNG exports.

draw.io's CLI emits -e PNGs with the 4-byte IEND length field but missing
the 8 bytes of "IEND" type + CRC. Strict PNG decoders and vision APIs
(Anthropic included) reject the file with 400 "Could not process image".
SVG/PDF are unaffected.

Usage: python3 repair_png.py <path/to/diagram.drawio.png>

Idempotent: the endswith(IEND) guard makes this a no-op once draw.io
fixes the bug upstream, so it's safe to run unconditionally after every
-e PNG export.
"""
import argparse
import os
import tempfile
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IEND = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def repair(path: Path) -> bool:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"not a PNG file: {path}")
    if data.endswith(IEND):
        return False
    if not data.endswith(b"\x00\x00\x00\x00"):
        raise ValueError(
            "PNG is not the known Draw.io truncated-IEND form; refusing to modify it"
        )

    repaired = data[:-4] + IEND
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        temp.write(repaired)
        temp_path = Path(temp.name)
    os.replace(temp_path, path)
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="embedded Draw.io PNG")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        changed = repair(args.path)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    print(f"{'repaired' if changed else 'already valid'}: {args.path}")
