#!/usr/bin/env python3
"""Export a transparent, font-outlined SVG for PowerPoint/Office."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_drawio(explicit: str | None) -> str:
    if explicit:
        candidate = shutil.which(explicit) or explicit
        if Path(candidate).is_file() or shutil.which(candidate):
            return candidate
        raise SystemExit(f"draw.io executable not found: {explicit}")

    for name in ("draw.io", "drawio"):
        candidate = shutil.which(name)
        if candidate:
            return candidate

    mac_path = Path("/Applications/draw.io.app/Contents/MacOS/draw.io")
    if mac_path.is_file():
        return str(mac_path)

    raise SystemExit("draw.io executable not found on PATH")


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def drawio_pdf_command(
    drawio: str, source: Path, output: Path, border: int, page: int
) -> list[str]:
    command = [
        drawio,
        "-x",
        "-f",
        "pdf",
        "--crop",
        "-b",
        str(border),
        "-p",
        str(page),
        "-o",
        str(output),
        str(source),
    ]

    if platform.system() == "Linux":
        command.append("--disable-gpu")
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            command.append("--no-sandbox")
        xvfb = shutil.which("xvfb-run")
        if xvfb:
            command = [
                xvfb,
                "-a",
                "--server-args=-screen 0 1920x1080x24",
                *command,
            ]

    return command


def is_pdf_page_background(group: ET.Element) -> bool:
    if local_name(group.tag) != "g" or not group.get("clip-path", "").startswith(
        "url(#clip-"
    ):
        return False

    descendants = list(group)
    if len(descendants) != 1 or local_name(descendants[0].tag) != "path":
        return False

    path = descendants[0]
    fill = "".join(path.get("fill", "").lower().split())
    opacity = path.get("fill-opacity", "1")
    return fill == "rgb(100%,100%,100%)" and opacity == "1"


def make_transparent_and_validate(raw_svg: Path, output_svg: Path) -> bool:
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xlink", XLINK_NS)
    tree = ET.parse(raw_svg)
    root = tree.getroot()

    if local_name(root.tag) != "svg":
        raise SystemExit("pdftocairo output root is not <svg>")

    removed_background = False
    for child in list(root):
        if is_pdf_page_background(child):
            root.remove(child)
            removed_background = True
            break

    forbidden = {"text", "foreignObject"}
    found = sorted(
        {local_name(element.tag) for element in root.iter()} & forbidden
    )
    if found:
        raise SystemExit(
            "PPT-safe SVG still contains unsupported text nodes: " + ", ".join(found)
        )

    output_svg.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_svg, encoding="utf-8", xml_declaration=False)
    if not output_svg.read_bytes().startswith(b"<svg"):
        raise SystemExit("output does not start with <svg>")

    return removed_background


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export Draw.io to a transparent SVG with text converted to glyph paths "
            "for PowerPoint/Office compatibility."
        )
    )
    parser.add_argument("input", type=Path, help="input .drawio file")
    parser.add_argument("output", type=Path, help="output .svg file")
    parser.add_argument("--drawio", help="draw.io executable name or absolute path")
    parser.add_argument("--border", type=int, default=10, help="diagram border in pixels")
    parser.add_argument("--page", type=int, default=1, help="1-based page index")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.input.resolve()
    output = args.output.resolve()

    if not source.is_file():
        raise SystemExit(f"input file not found: {source}")
    if source.suffix.lower() != ".drawio":
        raise SystemExit("input file must use the .drawio extension")
    if output.suffix.lower() != ".svg":
        raise SystemExit("output file must use the .svg extension")
    if args.border < 0 or args.page < 1:
        raise SystemExit("--border must be >= 0 and --page must be >= 1")

    drawio = find_drawio(args.drawio)
    pdftocairo = shutil.which("pdftocairo")
    if not pdftocairo:
        raise SystemExit("pdftocairo not found; install Poppler first")

    with tempfile.TemporaryDirectory(prefix="drawio-ppt-svg-") as temp_dir:
        temp = Path(temp_dir)
        pdf = temp / "diagram.pdf"
        raw_svg = temp / "diagram.svg"

        run(drawio_pdf_command(drawio, source, pdf, args.border, args.page))
        run([pdftocairo, "-svg", str(pdf), str(raw_svg)])
        removed = make_transparent_and_validate(raw_svg, output)

    status = "removed PDF page background" if removed else "no PDF page background found"
    print(f"Exported PPT-safe SVG: {output} ({status})")


if __name__ == "__main__":
    main()
