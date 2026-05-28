#!/usr/bin/env python3
"""Static audit for agent skill folders."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


MAX_DESCRIPTION = 1024
MAX_SKILL_MD_LINES = 140


def fail(message: str) -> str:
    return f"FAIL {message}"


def warn(message: str) -> str:
    return f"WARN {message}"


def ok(message: str) -> str:
    return f"OK   {message}"


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    issues: list[str] = []
    if not text.startswith("---\n"):
        return {}, [fail("SKILL.md is missing YAML frontmatter")]

    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return {}, [fail("SKILL.md frontmatter delimiter is invalid")]

    frontmatter: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            issues.append(warn(f"frontmatter line is not key/value: {raw_line}"))
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter, issues


def audit(skill_dir: Path) -> list[str]:
    results: list[str] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return [fail(f"missing SKILL.md at {skill_md}")]

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    frontmatter, fm_issues = parse_frontmatter(text)
    results.extend(fm_issues)

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if not name:
        results.append(fail("frontmatter is missing name"))
    elif not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        results.append(fail(f"name is not lowercase hyphen-case: {name}"))
    else:
        results.append(ok("name is lowercase hyphen-case"))

    if name and skill_dir.name != name:
        results.append(warn(f"folder name '{skill_dir.name}' does not match skill name '{name}'"))

    if not description:
        results.append(fail("frontmatter is missing description"))
    else:
        if len(description) > MAX_DESCRIPTION:
            results.append(fail(f"description is {len(description)} chars; max is {MAX_DESCRIPTION}"))
        elif "Use when" not in description and "use when" not in description:
            results.append(warn('description should include concrete "Use when..." trigger contexts'))
        elif "<" in description or ">" in description:
            results.append(fail("description contains angle brackets"))
        else:
            results.append(ok("description has trigger-oriented wording"))

    if len(lines) > MAX_SKILL_MD_LINES:
        results.append(warn(f"SKILL.md has {len(lines)} lines; consider moving detail to references/"))
    else:
        results.append(ok(f"SKILL.md length is {len(lines)} lines"))

    if "TODO" in text or "[TODO" in text:
        results.append(fail("SKILL.md still contains TODO placeholders"))

    references_dir = skill_dir / "references"
    if references_dir.exists():
        refs = sorted(p for p in references_dir.iterdir() if p.is_file())
        for ref in refs:
            if ref.name not in text:
                results.append(warn(f"reference file is not mentioned from SKILL.md: references/{ref.name}"))
        nested = [p for p in references_dir.rglob("*") if p.is_file() and p.parent != references_dir]
        if nested:
            results.append(warn("references/ contains nested files; keep references one level deep unless necessary"))

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        scripts = sorted(p for p in scripts_dir.iterdir() if p.is_file())
        for script in scripts:
            if script.name not in text:
                results.append(warn(f"script is not mentioned from SKILL.md: scripts/{script.name}"))
            if os.access(script, os.X_OK):
                results.append(ok(f"script is executable: scripts/{script.name}"))
            elif script.suffix in {".py", ".sh"}:
                results.append(warn(f"script is not executable: scripts/{script.name}"))

    agents_yaml = skill_dir / "agents" / "openai.yaml"
    if agents_yaml.exists():
        agent_text = agents_yaml.read_text(encoding="utf-8")
        if "display_name:" in agent_text and "short_description:" in agent_text:
            results.append(ok("agents/openai.yaml has display and short description"))
        else:
            results.append(warn("agents/openai.yaml is missing display_name or short_description"))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a skill folder for production readiness.")
    parser.add_argument("skill_dir", help="Path to a skill directory")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    results = audit(skill_dir)
    for result in results:
        print(result)

    return 1 if any(result.startswith("FAIL") for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
