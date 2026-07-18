#!/usr/bin/env python3
"""对 AGENTS.md 做确定性静态审计，不修改目标文件。"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


VAGUE_PATTERNS = (
    r"遵循(?:相关)?最佳实践",
    r"注意(?:代码)?质量",
    r"适当(?:地)?(?:运行)?测试",
    r"保持代码质量",
    r"follow best practices",
    r"ensure (?:high )?quality",
    r"test as appropriate",
)

PRIVATE_PATH_PATTERNS = (
    r"/home/[^/\s`]+(?:/[^\s`]*)?",
    r"/Users/[^/\s`]+(?:/[^\s`]*)?",
    r"[A-Za-z]:\\Users\\[^\\\s`]+(?:\\[^\s`]*)?",
)

SECRET_PATTERNS = (
    ("私钥头", r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ("AWS Access Key", r"\bAKIA[0-9A-Z]{16}\b"),
    ("GitHub Token", r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    (
        "疑似明文凭据",
        r"(?i)\b(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*[\"']?(?!\$\{|<|\*|x{3,}|example|changeme)[A-Za-z0-9_./+=-]{12,}",
    ),
)

DANGEROUS_PATTERNS = (
    r"\brm\s+-rf\s+(?:/|~|\$HOME)\b",
    r"\bgit\s+push\s+(?:--force|-f)\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\s+-[a-zA-Z]*f",
    r"\bDROP\s+DATABASE\b",
)

DRIFT_SUBJECT_PATTERN = re.compile(
    r"项目结构|目录结构|技术栈|工具链|构建(?:或|和|与)?测试命令|构建命令|测试命令|生成流程|开发约束|"
    r"project structure|directory structure|tech(?:nology)? stack|toolchain|build (?:or |and )?test commands?|development constraints?",
    re.IGNORECASE,
)
DRIFT_CHANGE_PATTERN = re.compile(r"变更|变化|调整|新增|删除|change|update", re.IGNORECASE)
DRIFT_ACTION_PATTERN = re.compile(r"同步|更新|维护|sync|update|keep.*current", re.IGNORECASE)

NEGATION_MARKERS = (
    "禁止",
    "不要",
    "不得",
    "不可",
    "严禁",
    "never",
    "do not",
    "don't",
    "must not",
    "prohibit",
)


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str
    line: int | None = None

    def render(self, path: Path) -> str:
        location = f"{path}:{self.line}" if self.line is not None else str(path)
        return f"{self.severity:<5} {location} {self.message}"


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def first_match(text: str, pattern: str, flags: int = 0) -> tuple[int, str] | None:
    match = re.search(pattern, text, flags)
    if not match:
        return None
    return line_for_offset(text, match.start()), match.group(0)


def has_drift_sync_rule(text: str) -> bool:
    paragraphs = re.split(r"\n\s*\n", text)
    return any(
        re.search(r"AGENTS\.md", paragraph, re.IGNORECASE)
        and DRIFT_SUBJECT_PATTERN.search(paragraph)
        and DRIFT_CHANGE_PATTERN.search(paragraph)
        and DRIFT_ACTION_PATTERN.search(paragraph)
        for paragraph in paragraphs
    )


def audit_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()

    if not text.strip():
        return [Finding("ERROR", "文件为空")]

    if not re.search(r"(?m)^#{1,6}\s+\S", text):
        findings.append(Finding("ERROR", "缺少 Markdown 标题"))

    for marker in ("```", "~~~"):
        marker_lines = [i for i, line in enumerate(lines, 1) if line.lstrip().startswith(marker)]
        if len(marker_lines) % 2:
            findings.append(Finding("ERROR", f"未闭合的 {marker} 代码块", marker_lines[-1]))

    if len(lines) > 240:
        findings.append(Finding("WARN", f"文件共 {len(lines)} 行，可能包含过多背景或重复规则"))

    for pattern in VAGUE_PATTERNS:
        match = first_match(text, pattern, re.IGNORECASE)
        if match:
            line, value = match
            findings.append(Finding("WARN", f"发现模糊表述：{value!r}；请改为可执行规则", line))

    for pattern in PRIVATE_PATH_PATTERNS:
        match = first_match(text, pattern)
        if match:
            line, value = match
            findings.append(Finding("WARN", f"发现疑似用户私有绝对路径：{value!r}", line))

    for label, pattern in SECRET_PATTERNS:
        match = first_match(text, pattern)
        if match:
            line, _ = match
            findings.append(Finding("ERROR", f"发现{label}，不得在 AGENTS.md 中保存凭据", line))

    for index, line_text in enumerate(lines, 1):
        lowered = line_text.lower()
        if any(re.search(pattern, line_text, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS):
            if not any(marker in lowered for marker in NEGATION_MARKERS):
                findings.append(Finding("WARN", "发现未明确作为禁令的危险命令，请人工确认", index))

    headings = [
        re.sub(r"\s+", " ", match.group(1).strip().lower())
        for line in lines
        if (match := re.match(r"^#{1,6}\s+(.+?)\s*$", line))
    ]
    duplicate_headings = [heading for heading, count in Counter(headings).items() if count > 1]
    for heading in duplicate_headings:
        first_line = next(
            i for i, line in enumerate(lines, 1)
            if re.match(r"^#{1,6}\s+(.+?)\s*$", line)
            and re.sub(r"\s+", " ", re.match(r"^#{1,6}\s+(.+?)\s*$", line).group(1).strip().lower()) == heading
        )
        findings.append(Finding("WARN", f"重复标题：{heading!r}", first_line))

    for index, line_text in enumerate(lines, 1):
        if re.search(r"\b(?:TODO|TBD|FIXME)\b|待补充|待确认", line_text, re.IGNORECASE):
            findings.append(Finding("WARN", "发现占位或待确认内容，请确认是否应保留", index))

    if not has_drift_sync_rule(text):
        findings.append(
            Finding(
                "WARN",
                "未发现防漂移规则：项目结构、技术栈、命令或开发约束变化时，应同步更新适用作用域的 AGENTS.md",
            )
        )

    if not findings:
        findings.append(Finding("OK", "未发现确定性的静态问题"))

    return findings


def audit_file(path: Path) -> list[Finding]:
    if not path.exists():
        return [Finding("ERROR", "文件不存在")]
    if not path.is_file():
        return [Finding("ERROR", "目标不是普通文件")]
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Finding("ERROR", "文件不是有效的 UTF-8 文本")]
    findings = audit_text(text)
    if path.name != "AGENTS.md":
        findings.insert(0, Finding("WARN", "目标文件名不是 AGENTS.md"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="静态审计 AGENTS.md，不修改目标文件")
    parser.add_argument("path", type=Path, help="待审计的 AGENTS.md 路径")
    parser.add_argument("--strict", action="store_true", help="将警告也视为失败")
    args = parser.parse_args()

    path = args.path.expanduser().resolve()
    findings = audit_file(path)
    for finding in findings:
        print(finding.render(path))

    if any(finding.severity == "ERROR" for finding in findings):
        return 1
    if args.strict and any(finding.severity == "WARN" for finding in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
