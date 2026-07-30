#!/usr/bin/env python3
"""Static audit for agent skill folders."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


MAX_DESCRIPTION = 1024
MAX_SKILL_MD_LINES = 140
SKIP_DIRS = {".git", "__pycache__", "dist", "node_modules"}
AMBIGUOUS_SKILL_NAMES = {"commit"}
CLI_MENTION = re.compile(r"\bcli\b", re.IGNORECASE)
CLI_CONTRACT_MARKER = "<!-- cli-compatibility-contract:v1 -->"
TRIGGER_WORDING = re.compile(
    r"\b(?:"
    r"use(?:\s+this\s+skill)?\s+(?:when|for)"
    r"|this\s+skill\s+(?:(?:should\s+)?be|is)\s+used\s+(?:when|for)"
    r")\b",
    re.IGNORECASE,
)


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
    raw_lines = match.group(1).splitlines()
    index = 0
    while index < len(raw_lines):
        raw_line = raw_lines[index]
        line = raw_line.strip()
        if not line or line.startswith("#"):
            index += 1
            continue
        if raw_line[:1].isspace():
            index += 1
            continue
        if ":" not in line:
            issues.append(warn(f"frontmatter line is not key/value: {raw_line}"))
            index += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if re.fullmatch(r"[|>][-+]?", value):
            block_lines: list[str] = []
            index += 1
            while index < len(raw_lines):
                block_line = raw_lines[index]
                if block_line and not block_line[:1].isspace():
                    break
                block_lines.append(block_line.strip())
                index += 1
            separator = " " if value.startswith(">") else "\n"
            frontmatter[key] = separator.join(block_lines).strip()
            continue
        frontmatter[key] = value.strip('"').strip("'")
        index += 1
    return frontmatter, issues


def is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def package_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        relative = path.relative_to(skill_dir)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.is_file() or path.is_symlink():
            files.append(path)
    return sorted(files)


def sibling_skill_names(skill_dir: Path) -> list[str]:
    names: list[str] = []
    for sibling in skill_dir.parent.iterdir():
        sibling_md = sibling / "SKILL.md"
        if sibling == skill_dir or not sibling_md.is_file():
            continue
        try:
            sibling_text = sibling_md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        frontmatter, _ = parse_frontmatter(sibling_text)
        name = frontmatter.get("name", "")
        if name:
            names.append(name)
    return sorted(set(names))


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def cross_skill_reference_results(skill_dir: Path) -> list[str]:
    results: list[str] = []
    names = sibling_skill_names(skill_dir)
    if not names:
        return results

    for path in package_files(skill_dir):
        if path.is_symlink():
            continue
        text = read_text(path)
        if text is None:
            continue
        relative = path.relative_to(skill_dir)
        for line_number, line in enumerate(text.splitlines(), 1):
            for name in names:
                escaped = re.escape(name)
                if name in AMBIGUOUS_SKILL_NAMES:
                    patterns = (
                        rf"\${escaped}(?![a-z0-9-])",
                        rf"\bskill\b[^\n]{{0,40}}`?{escaped}`?",
                        rf"`?{escaped}`?[^\n]{{0,40}}\bskill\b",
                        rf"(?:^|[/.])skills/{escaped}(?:/|$)",
                    )
                else:
                    patterns = (rf"(?<![a-z0-9-]){escaped}(?![a-z0-9-])",)
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns):
                    results.append(
                        fail(f"cross-skill reference to '{name}': {relative}:{line_number}")
                    )
    return results


def external_link_results(skill_dir: Path) -> list[str]:
    results: list[str] = []
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    root = skill_dir.resolve()

    for path in package_files(skill_dir):
        relative = path.relative_to(skill_dir)
        if path.is_symlink():
            target = path.resolve(strict=False)
            if not is_within(target, root):
                results.append(fail(f"symlink points outside skill package: {relative} -> {target}"))
            continue

        text = read_text(path)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for match in link_pattern.finditer(line):
                raw_target = match.group(1).strip().strip("<>")
                target_text = raw_target.split(maxsplit=1)[0]
                parsed = urlparse(target_text)
                if parsed.scheme or target_text.startswith("#"):
                    continue
                target_path = unquote(target_text.split("#", 1)[0])
                if not target_path:
                    continue
                resolved = (path.parent / target_path).resolve(strict=False)
                if not is_within(resolved, root):
                    results.append(
                        fail(f"link points outside skill package: {relative}:{line_number} -> {target_text}")
                    )
    return results


def cli_compatibility_results(
    skill_dir: Path,
    skill_text: str,
    frontmatter: dict[str, str],
) -> list[str]:
    results: list[str] = []
    declared = frontmatter.get("external-cli", "").lower() == "true"

    if CLI_MENTION.search(skill_text) and not declared:
        results.append(warn("SKILL.md 提到 CLI，但 frontmatter 未声明 external-cli: true"))
        return results
    if not declared:
        return results

    contract_value = frontmatter.get("cli-compatibility", "")
    if not contract_value:
        return [fail("external-cli Skill 缺少 cli-compatibility frontmatter")]

    contract_path = (skill_dir / contract_value).resolve(strict=False)
    root = skill_dir.resolve()
    if not is_within(contract_path, root):
        return [fail(f"cli-compatibility 指向 Skill 包外: {contract_value}")]
    if not contract_path.is_file():
        return [fail(f"cli-compatibility 文件不存在: {contract_value}")]
    if contract_value not in skill_text:
        results.append(fail(f"SKILL.md 未链接 cli-compatibility 文件: {contract_value}"))

    contract_text = read_text(contract_path)
    if contract_text is None:
        return results + [fail(f"cli-compatibility 文件不是可读 UTF-8: {contract_value}")]

    required_fragments = (
        CLI_CONTRACT_MARKER,
        "本机验证版本",
        "## 关键能力",
        "## 版本不一致时",
    )
    for fragment in required_fragments:
        if fragment not in contract_text:
            results.append(fail(f"cli-compatibility 文件缺少必需内容: {fragment}"))
    if not results:
        results.append(ok("外部 CLI 兼容性契约完整"))
    return results


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
        elif not TRIGGER_WORDING.search(description):
            results.append(warn('description should include concrete "Use when..." or "Use for..." trigger contexts'))
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

    results.extend(cross_skill_reference_results(skill_dir))
    results.extend(external_link_results(skill_dir))
    results.extend(cli_compatibility_results(skill_dir, text, frontmatter))

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
