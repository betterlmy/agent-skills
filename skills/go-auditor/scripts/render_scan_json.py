#!/usr/bin/env python3
"""把 scan.sh 的 NUL 分隔记录原子写为稳定 JSON。"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile


def read_nul(path: Path) -> list[str]:
    data = path.read_bytes().split(b"\0")
    if data and data[-1] == b"":
        data.pop()
    return [item.decode("utf-8", errors="replace") for item in data]


def grouped(values: list[str], size: int, source: str) -> list[list[str]]:
    if len(values) % size:
        raise ValueError(f"{source} 记录字段不完整")
    return [values[index : index + size] for index in range(0, len(values), size)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--module-mode", required=True)
    parser.add_argument("--goflags", required=True)
    parser.add_argument("--network", choices=("allowed", "blocked"), required=True)
    parser.add_argument("--package-count", required=True)
    parser.add_argument("--deleted", type=int, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--commands", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metadata: defaultdict[str, list[str]] = defaultdict(list)
    for kind, value in grouped(read_nul(args.metadata), 2, "metadata"):
        metadata[kind].append(value)

    events = [
        {"status": status, "message": message}
        for status, message in grouped(read_nul(args.events), 2, "event")
    ]
    commands = [
        {
            "check": check,
            "kind": kind,
            "command": command,
            "exit_code": int(exit_code),
            "elapsed_seconds": int(elapsed),
            "output_truncated": truncated == "1",
            "raw_output_file": raw_output or None,
        }
        for check, kind, command, exit_code, elapsed, truncated, raw_output in grouped(
            read_nul(args.commands), 7, "command"
        )
    ]
    package_count: int | None
    package_count = int(args.package_count) if args.package_count.isdigit() else None
    status_counts = Counter(event["status"] for event in events)
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": args.root,
        "environment": {
            "module_mode": args.module_mode,
            "goflags": args.goflags,
            "network": args.network,
        },
        "scope": {
            "labels": metadata["scope"],
            "go_files": metadata["file"],
            "package_patterns": metadata["pattern"],
            "resolved_package_count": package_count,
            "resolved_packages": metadata["package"],
            "diff_paths": metadata["diff"],
            "deleted_or_unscannable_diff_paths": args.deleted,
        },
        "events": events,
        "commands": commands,
        "summary": dict(sorted(status_counts.items())),
    }

    args.output.parent.mkdir(parents=False, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{args.output.name}.", suffix=".tmp", dir=args.output.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output_file:
            json.dump(result, output_file, ensure_ascii=False, indent=2)
            output_file.write("\n")
        os.replace(temporary_name, args.output)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
