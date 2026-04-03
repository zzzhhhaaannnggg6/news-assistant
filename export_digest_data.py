#!/opt/homebrew/bin/python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


LABEL_ORDER = [
    "一句话判断",
    "发生了什么",
    "背景",
    "为什么重要",
    "关键事实",
    "接下来观察",
    "来源",
    "说明",
]


def normalize_lines(lines: list[str]) -> list[str]:
    normalized: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        labeled = re.match(r"^-\s+(一句话判断|发生了什么|背景|为什么重要|关键事实|接下来观察|来源|说明)：\s*(.*)$", line)
        if labeled:
            label, body = labeled.groups()
            extras: list[str] = []
            probe = index + 1
            while probe < len(lines):
                nested = re.match(r"^\s+-\s+(.*)$", lines[probe])
                if not nested:
                    break
                extras.append(nested.group(1).strip())
                probe += 1
            if extras:
                separator = " " if label == "来源" else "；"
                suffix = separator.join(extras)
                body = f"{body}{separator if body else ''}{suffix}".strip()
                normalized.append(f"- {label}：{body}")
                index = probe
                continue
        normalized.append(line)
        index += 1
    return normalized


def parse_links(text: str) -> list[dict[str, str]]:
    return [
        {"label": match.group(1), "url": match.group(2)}
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text)
    ]


def parse_digest(md_text: str) -> dict:
    lines = normalize_lines(md_text.splitlines())
    digest = {
        "title": "",
        "greeting": "",
        "overview": "",
        "top3": [],
        "sections": [],
        "closing": "",
    }

    current_section: dict | None = None
    current_story: dict | None = None
    paragraph_buffer: list[str] = []
    in_top3 = False

    def flush_paragraph() -> None:
        nonlocal paragraph_buffer, current_section
        if not paragraph_buffer:
            return
        text = " ".join(item.strip() for item in paragraph_buffer).strip()
        if not text:
            paragraph_buffer = []
            return
        if current_section is None:
            if not digest["greeting"] and digest["title"]:
                digest["greeting"] = text
            else:
                digest["overview"] = text
        elif current_section["title"] == "今日总览":
            current_section.setdefault("notes", []).append(text)
            digest["overview"] = text
        elif current_section["title"] == "收尾总结":
            current_section.setdefault("notes", []).append(text)
            digest["closing"] = text
        elif current_story is None:
            current_section.setdefault("notes", []).append(text)
        else:
            current_story.setdefault("notes", []).append(text)
        paragraph_buffer = []

    def close_story() -> None:
        nonlocal current_story
        flush_paragraph()
        if current_story is not None and current_section is not None:
            current_section.setdefault("stories", []).append(current_story)
        current_story = None

    def close_section() -> None:
        nonlocal current_section, in_top3
        close_story()
        flush_paragraph()
        if current_section is not None:
            digest["sections"].append(current_section)
        current_section = None
        in_top3 = False

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            flush_paragraph()
            continue

        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if level == 1:
                digest["title"] = text
            elif level == 2:
                close_section()
                current_section = {"title": text, "stories": [], "notes": []}
                in_top3 = text == "今日 Top 3"
            elif level == 3:
                close_story()
                current_story = {"title": text, "items": [], "notes": []}
            continue

        ordered = re.match(r"^\d+\.\s+(.*)$", line)
        if ordered and in_top3:
            digest["top3"].append(ordered.group(1).strip())
            continue

        labeled = re.match(r"^-\s+(一句话判断|发生了什么|背景|为什么重要|关键事实|接下来观察|来源|说明)：\s*(.*)$", line)
        if labeled and current_story is not None:
            label, value = labeled.groups()
            entry = {"label": label, "text": value.strip()}
            if label == "来源":
                entry["links"] = parse_links(value)
            current_story["items"].append(entry)
            continue

        if line.endswith("No high-value update today.") or "No high-value update today." in line:
            if current_story is None and current_section is not None:
                current_section.setdefault("notes", []).append(line.strip())
            else:
                paragraph_buffer.append(line.strip())
            continue

        paragraph_buffer.append(line.strip())

    close_section()
    return digest


def write_outputs(digest: dict, json_path: Path, js_path: Path) -> None:
    payload = json.dumps(digest, ensure_ascii=False, indent=2)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(payload)
    js_path.write_text(f"window.__DIGEST__ = {payload};\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--js-output", required=True)
    args = parser.parse_args()

    digest = parse_digest(Path(args.input).read_text())
    write_outputs(digest, Path(args.json_output), Path(args.js_output))


if __name__ == "__main__":
    main()
