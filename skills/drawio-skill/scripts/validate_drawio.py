#!/usr/bin/env python3
"""Validate structural invariants in an uncompressed Draw.io XML file."""

from __future__ import annotations

import argparse
import base64
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from collections import Counter
from pathlib import Path


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def read_graph_model(diagram: ET.Element) -> ET.Element:
    graph = diagram.find("mxGraphModel")
    if graph is not None:
        return graph

    encoded = (diagram.text or "").strip()
    if not encoded:
        raise ValueError("missing mxGraphModel content")

    try:
        compressed = base64.b64decode(encoded, validate=True)
        quoted_xml = zlib.decompress(compressed, -zlib.MAX_WBITS).decode("utf-8")
        graph = ET.fromstring(urllib.parse.unquote(quoted_xml))
    except (ValueError, zlib.error, UnicodeError, ET.ParseError) as error:
        raise ValueError(f"invalid compressed diagram: {error}") from error

    if graph.tag != "mxGraphModel":
        raise ValueError("decoded page root is not mxGraphModel")
    return graph


def validate(path: Path) -> int:
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError) as error:
        fail(str(error))
        return 1

    root = tree.getroot()
    if root.tag != "mxfile":
        fail("root element must be <mxfile>")
        return 1

    diagrams = root.findall("diagram")
    if not diagrams:
        fail("mxfile contains no <diagram> pages")
        return 1

    errors = 0
    total_cells = 0
    total_edges = 0

    for page_index, diagram in enumerate(diagrams, start=1):
        try:
            graph = read_graph_model(diagram)
        except ValueError as error:
            fail(f"page {page_index}: {error}")
            errors += 1
            continue

        cell_root = graph.find("root")
        if cell_root is None:
            fail(f"page {page_index}: missing mxGraphModel/root")
            errors += 1
            continue

        cells = cell_root.findall("mxCell")
        total_cells += len(cells)
        ids = [cell.get("id") for cell in cells]
        present_ids = {cell_id for cell_id in ids if cell_id}
        counts = Counter(cell_id for cell_id in ids if cell_id)

        if "0" not in present_ids or "1" not in present_ids:
            fail(f"page {page_index}: required root cells 0 and 1 are missing")
            errors += 1

        duplicates = sorted(cell_id for cell_id, count in counts.items() if count > 1)
        if duplicates:
            fail(f"page {page_index}: duplicate cell IDs: {', '.join(duplicates)}")
            errors += 1

        for cell in cells:
            cell_id = cell.get("id", "<missing-id>")
            parent = cell.get("parent")
            if parent and parent not in present_ids:
                fail(f"page {page_index}, cell {cell_id}: unknown parent {parent}")
                errors += 1

            if cell.get("edge") != "1":
                continue

            total_edges += 1
            geometry = cell.find("mxGeometry")
            if geometry is None or geometry.get("as") != "geometry":
                fail(f"page {page_index}, edge {cell_id}: missing mxGeometry")
                errors += 1
            elif geometry.get("relative") != "1":
                fail(f"page {page_index}, edge {cell_id}: mxGeometry must be relative=1")
                errors += 1

            for endpoint in ("source", "target"):
                ref = cell.get(endpoint)
                if ref and ref not in present_ids:
                    fail(f"page {page_index}, edge {cell_id}: unknown {endpoint} {ref}")
                    errors += 1

    if errors:
        fail(f"validation failed with {errors} issue(s)")
        return 1

    print(
        f"OK: {path} ({len(diagrams)} page(s), {total_cells} cell(s), "
        f"{total_edges} edge(s))"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="uncompressed .drawio XML file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(validate(args.path))
