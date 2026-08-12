#!/usr/bin/env python3
"""Validate logo SVG files against a conservative, static-safe profile."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_ELEMENTS = {
    "svg", "g", "defs", "title", "desc", "path", "rect", "circle",
    "ellipse", "line", "polyline", "polygon", "linearGradient",
    "radialGradient", "stop", "clipPath", "mask", "symbol", "use",
    "text", "tspan",
}
RAW_FORBIDDEN = re.compile(
    rb"<!\s*(?:DOCTYPE|ENTITY)\b|<\?(?!xml(?:\s|$))",
    re.IGNORECASE,
)
DANGEROUS_SCHEME = re.compile(r"^\s*(?:javascript|data)\s*:", re.IGNORECASE)
URL_REFERENCE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
VIEWBOX_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
VIEWBOX = re.compile(rf"^\s*{VIEWBOX_NUMBER}(?:[\s,]+{VIEWBOX_NUMBER}){{3}}\s*$")


@dataclass(frozen=True)
class ValidationResult:
    path: Path
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def namespace(name: str) -> str | None:
    if name.startswith("{") and "}" in name:
        return name[1:].split("}", 1)[0]
    return None


def collect_paths(inputs: list[Path]) -> tuple[list[Path], list[str]]:
    paths: set[Path] = set()
    errors: list[str] = []
    for item in inputs:
        if not item.exists():
            errors.append(f"{item}: path does not exist")
        elif item.is_dir():
            paths.update(path for path in item.rglob("*.svg") if path.is_file())
        elif item.is_file():
            paths.add(item)
        else:
            errors.append(f"{item}: unsupported path type")
    if not paths and not errors:
        errors.append("no SVG files found")
    return sorted(paths), errors


def validate_svg(path: Path, max_bytes: int = MAX_BYTES) -> ValidationResult:
    errors: list[str] = []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return ValidationResult(path, (f"cannot read file: {exc}",))

    if len(raw) > max_bytes:
        errors.append(f"file exceeds {max_bytes} bytes")
        return ValidationResult(path, tuple(errors))
    if RAW_FORBIDDEN.search(raw):
        errors.append("contains a forbidden DTD, entity, or processing instruction")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"is not valid UTF-8: {exc}")
        return ValidationResult(path, tuple(errors))

    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        errors.append(f"invalid XML: {exc}")
        return ValidationResult(path, tuple(errors))

    if local_name(root.tag) != "svg" or namespace(root.tag) != SVG_NS:
        errors.append(f"root must be {{{SVG_NS}}}svg")
    view_box = root.attrib.get("viewBox", "")
    if not VIEWBOX.fullmatch(view_box):
        errors.append("root must have a four-number viewBox")

    for required in ("title", "desc"):
        matches = [child for child in root if local_name(child.tag) == required]
        if not matches:
            errors.append(f"root must contain a direct {required} element")
        elif len(matches) > 1:
            errors.append(f"root must not contain multiple direct {required} elements")
        elif not "".join(matches[0].itertext()).strip():
            errors.append(f"{required} element must not be empty")

    ids: set[str] = set()
    references: list[tuple[str, str]] = []
    for element in root.iter():
        tag_ns = namespace(element.tag)
        tag = local_name(element.tag)
        if tag_ns != SVG_NS:
            errors.append(f"element {tag!r} uses a non-SVG namespace")
        if tag not in ALLOWED_ELEMENTS:
            errors.append(f"element {tag!r} is not allowed")

        element_id = element.attrib.get("id")
        if element_id:
            if element_id in ids:
                errors.append(f"duplicate id: {element_id}")
            ids.add(element_id)

        for raw_name, value in element.attrib.items():
            attr = local_name(raw_name)
            attr_ns = namespace(raw_name)
            if attr.lower().startswith("on"):
                errors.append(f"event attribute {attr!r} is not allowed on {tag}")
            if attr_ns not in {None, XLINK_NS}:
                errors.append(f"attribute {attr!r} uses an unknown namespace")
            if attr == "style":
                errors.append(f"style attribute is not allowed on {tag}; use presentation attributes")
            if DANGEROUS_SCHEME.search(value):
                errors.append(f"dangerous URI scheme is not allowed in {attr} on {tag}")
            if attr == "href":
                if not value.startswith("#") or len(value) == 1:
                    errors.append(f"external href is not allowed on {tag}")
                else:
                    references.append((tag, value[1:]))
            if attr in {"aria-labelledby", "aria-describedby"}:
                for target in value.split():
                    references.append((tag, target))
            for match in URL_REFERENCE.finditer(value):
                target = match.group(2).strip()
                if not target.startswith("#") or len(target) == 1:
                    errors.append(f"external url() reference is not allowed on {tag}")
                else:
                    references.append((tag, target[1:]))

    for tag, target in references:
        if target not in ids:
            errors.append(f"{tag} references missing id: {target}")

    return ValidationResult(path, tuple(dict.fromkeys(errors)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate static logo SVG files without external dependencies."
    )
    parser.add_argument("paths", nargs="+", type=Path, help="SVG files or directories")
    parser.add_argument(
        "--max-bytes", type=int, default=MAX_BYTES, help=f"maximum file size (default: {MAX_BYTES})"
    )
    args = parser.parse_args(argv)

    if args.max_bytes <= 0:
        parser.error("--max-bytes must be positive")
    paths, input_errors = collect_paths(args.paths)
    for error in input_errors:
        print(f"FAIL {error}", file=sys.stderr)

    failed = bool(input_errors)
    for path in paths:
        result = validate_svg(path, args.max_bytes)
        if result.ok:
            print(f"PASS {path}")
            continue
        failed = True
        print(f"FAIL {path}", file=sys.stderr)
        for error in result.errors:
            print(f"  - {error}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
