#!/opt/homebrew/bin/python3
from __future__ import annotations

import argparse
import html
import re
from datetime import datetime
from pathlib import Path


LABEL_CLASS_MAP = {
    "一句话判断": "verdict",
    "发生了什么": "event",
    "背景": "background",
    "为什么重要": "importance",
    "关键事实": "facts",
    "接下来观察": "watch",
    "来源": "sources",
    "说明": "note",
}


CSS = """
:root {
  --bg: #f6efe3;
  --bg-strong: #efe1c4;
  --panel: rgba(255, 252, 246, 0.92);
  --panel-strong: rgba(255, 248, 236, 0.96);
  --ink: #1e1a16;
  --muted: #6d6258;
  --line: rgba(80, 58, 33, 0.12);
  --accent: #b4512d;
  --accent-2: #165c67;
  --accent-3: #a27b18;
  --shadow: 0 20px 60px rgba(86, 61, 36, 0.10);
}

* { box-sizing: border-box; }

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(180, 81, 45, 0.18), transparent 28%),
    radial-gradient(circle at top right, rgba(22, 92, 103, 0.14), transparent 26%),
    linear-gradient(180deg, #f9f3e9 0%, var(--bg) 48%, #f4ead8 100%);
  font-family: "Iowan Old Style", "Palatino Linotype", "Songti SC", "Noto Serif SC", serif;
}

a {
  color: inherit;
  text-decoration: none;
}

.page {
  width: min(1320px, calc(100vw - 32px));
  margin: 24px auto 48px;
}

.hero {
  position: relative;
  overflow: hidden;
  padding: 40px 44px 34px;
  border: 1px solid var(--line);
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(255,255,255,0.78), rgba(255,246,232,0.90)),
    linear-gradient(135deg, rgba(180,81,45,0.10), rgba(22,92,103,0.08));
  box-shadow: var(--shadow);
}

.hero::after {
  content: "";
  position: absolute;
  inset: auto -80px -110px auto;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(180,81,45,0.24), transparent 65%);
  pointer-events: none;
}

.eyebrow {
  margin: 0 0 12px;
  font-family: "Avenir Next Condensed", "DIN Alternate", "Helvetica Neue", sans-serif;
  font-size: 12px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--accent-2);
}

.hero h1 {
  margin: 0;
  max-width: 850px;
  font-size: clamp(2.1rem, 4vw, 4rem);
  line-height: 1.02;
  letter-spacing: -0.04em;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(80, 58, 33, 0.10);
  color: var(--muted);
  font-family: "Avenir Next", "PingFang SC", sans-serif;
  font-size: 13px;
}

.layout {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 24px;
  margin-top: 22px;
}

.toc {
  position: sticky;
  top: 20px;
  align-self: start;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 22px;
  background: rgba(255, 251, 244, 0.82);
  box-shadow: 0 18px 40px rgba(86, 61, 36, 0.06);
  backdrop-filter: blur(10px);
}

.toc-title {
  margin: 0 0 12px;
  font-family: "Avenir Next Condensed", "DIN Alternate", sans-serif;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
}

.toc ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.toc li + li {
  margin-top: 8px;
}

.toc a {
  display: block;
  padding: 10px 12px;
  border-radius: 14px;
  color: var(--muted);
  font-family: "Avenir Next", "PingFang SC", sans-serif;
  font-size: 14px;
  transition: background 160ms ease, color 160ms ease, transform 160ms ease;
}

.toc a:hover {
  color: var(--ink);
  background: rgba(180,81,45,0.10);
  transform: translateX(2px);
}

.content {
  min-width: 0;
}

.news-section {
  margin-bottom: 22px;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--panel);
  box-shadow: 0 14px 36px rgba(86, 61, 36, 0.06);
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 18px;
}

.section-kicker {
  margin: 0;
  font-family: "Avenir Next Condensed", "DIN Alternate", sans-serif;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent);
}

.news-section h2 {
  margin: 0;
  font-size: clamp(1.5rem, 2.3vw, 2.15rem);
  letter-spacing: -0.03em;
}

.news-section > p {
  margin: 0 0 14px;
  font-size: 1.02rem;
  line-height: 1.8;
  color: var(--ink);
}

.story-card {
  margin-top: 18px;
  padding: 20px 20px 18px;
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.82), rgba(255,248,238,0.88));
  border: 1px solid rgba(80, 58, 33, 0.08);
}

.story-card h3 {
  margin: 0 0 12px;
  font-size: 1.28rem;
  line-height: 1.35;
}

.story-list,
.top-list,
.watch-list {
  margin: 0;
  padding-left: 0;
}

.story-list {
  list-style: none;
}

.story-list li,
.watch-list li {
  margin: 10px 0 0;
  padding: 0;
}

.meta-row {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.meta-label {
  font-family: "Avenir Next Condensed", "DIN Alternate", sans-serif;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
}

.meta-content {
  min-width: 0;
  line-height: 1.76;
}

.meta-row--verdict .meta-content {
  font-weight: 700;
  color: var(--accent-2);
}

.meta-row--facts .meta-content {
  color: var(--accent);
}

.meta-row--sources .meta-content {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.meta-row--sources a {
  display: inline-flex;
  align-items: center;
  padding: 9px 12px;
  border-radius: 999px;
  background: rgba(22, 92, 103, 0.08);
  border: 1px solid rgba(22, 92, 103, 0.16);
  color: var(--accent-2);
  font-family: "Avenir Next", "PingFang SC", sans-serif;
  font-size: 13px;
}

.meta-row--sources a:hover {
  background: rgba(22, 92, 103, 0.14);
}

.top-list {
  padding-left: 28px;
}

.top-list li {
  margin: 0 0 12px;
  padding: 16px 18px;
  border-radius: 18px;
  background: var(--panel-strong);
  border: 1px solid rgba(80, 58, 33, 0.08);
  line-height: 1.72;
}

.watch-list {
  padding-left: 0;
  list-style: none;
}

.watch-list li {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(162, 123, 24, 0.08);
  border: 1px solid rgba(162, 123, 24, 0.15);
  line-height: 1.7;
}

.muted-note {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(80, 58, 33, 0.05);
  color: var(--muted);
}

strong {
  font-weight: 700;
}

code {
  padding: 2px 6px;
  border-radius: 8px;
  background: rgba(80, 58, 33, 0.08);
  font-family: "SFMono-Regular", "Menlo", monospace;
  font-size: 0.92em;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .toc {
    position: static;
  }

  .meta-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}

@media (max-width: 640px) {
  .page {
    width: min(100vw - 20px, 100%);
    margin-top: 10px;
  }

  .hero,
  .news-section {
    padding: 18px;
    border-radius: 22px;
  }

  .story-card {
    padding: 16px;
  }

  .top-list {
    padding-left: 22px;
  }
}
"""


def slugify(text: str, index: int) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return base or f"section-{index}"


def render_inline(text: str) -> str:
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|`([^`]+)`")
    result = []
    last = 0
    for match in pattern.finditer(text):
        result.append(html.escape(text[last:match.start()]))
        label, url, bold_text, code_text = match.groups()
        if label is not None and url is not None:
            result.append(
                f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noreferrer">{html.escape(label)}</a>'
            )
        elif bold_text is not None:
            result.append(f"<strong>{html.escape(bold_text)}</strong>")
        elif code_text is not None:
            result.append(f"<code>{html.escape(code_text)}</code>")
        last = match.end()
    result.append(html.escape(text[last:]))
    return "".join(result)


def build_list_item(content: str, list_kind: str) -> str:
    match = re.match(r"^(一句话判断|发生了什么|背景|为什么重要|关键事实|接下来观察|来源|说明)：\s*(.*)$", content)
    if match:
        label, body = match.groups()
        class_name = LABEL_CLASS_MAP.get(label, "generic")
        return (
            f'<li class="meta-row meta-row--{class_name}">'
            f'<span class="meta-label">{html.escape(label)}</span>'
            f'<span class="meta-content">{render_inline(body)}</span>'
            f"</li>"
        )
    item_class = "watch-item" if list_kind == "watch-list" else "generic-item"
    return f'<li class="{item_class}">{render_inline(content)}</li>'


def render_markdown(md_text: str) -> tuple[str, list[tuple[str, str]]]:
    lines = normalize_lines(md_text.splitlines())
    html_parts: list[str] = []
    toc: list[tuple[str, str]] = []
    paragraph_buffer: list[str] = []
    current_list_kind: str | None = None
    section_open = False
    article_open = False
    section_title = ""
    section_index = 0

    def flush_paragraph() -> None:
        nonlocal paragraph_buffer
        if not paragraph_buffer:
            return
        text = " ".join(line.strip() for line in paragraph_buffer).strip()
        if text:
            css = "muted-note" if text.startswith("No high-value update today.") else ""
            class_attr = f' class="{css}"' if css else ""
            html_parts.append(f"<p{class_attr}>{render_inline(text)}</p>")
        paragraph_buffer = []

    def close_list() -> None:
        nonlocal current_list_kind
        if current_list_kind == "story-list":
            html_parts.append("</ul>")
        elif current_list_kind == "top-list":
            html_parts.append("</ol>")
        elif current_list_kind == "watch-list":
            html_parts.append("</ul>")
        current_list_kind = None

    def close_article() -> None:
        nonlocal article_open
        flush_paragraph()
        close_list()
        if article_open:
            html_parts.append("</article>")
            article_open = False

    def close_section() -> None:
        nonlocal section_open
        close_article()
        flush_paragraph()
        close_list()
        if section_open:
            html_parts.append("</section>")
            section_open = False

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            flush_paragraph()
            close_list()
            if level == 1:
                html_parts.append(f'<header class="hero"><p class="eyebrow">Daily News Assistant</p><h1>{render_inline(text)}</h1></header>')
            elif level == 2:
                close_section()
                section_index += 1
                section_title = text
                section_id = slugify(text, section_index)
                toc.append((section_id, text))
                html_parts.append(
                    f'<section class="news-section" id="{section_id}">'
                    f'<div class="section-header"><p class="section-kicker">Section {section_index:02d}</p>'
                    f'<h2>{render_inline(text)}</h2></div>'
                )
                section_open = True
            elif level == 3:
                close_article()
                html_parts.append(f'<article class="story-card"><h3>{render_inline(text)}</h3>')
                article_open = True
            continue

        ordered = re.match(r"^\d+\.\s+(.*)$", line)
        if ordered:
            flush_paragraph()
            if current_list_kind != "top-list":
                close_list()
                current_list_kind = "top-list"
                html_parts.append('<ol class="top-list">')
            html_parts.append(build_list_item(ordered.group(1).strip(), current_list_kind))
            continue

        unordered = re.match(r"^-+\s+(.*)$", line)
        if unordered:
            flush_paragraph()
            wanted = "watch-list" if "观察" in section_title else "story-list"
            if current_list_kind != wanted:
                close_list()
                current_list_kind = wanted
                tag = "ul"
                html_parts.append(f'<{tag} class="{wanted}">')
            html_parts.append(build_list_item(unordered.group(1).strip(), current_list_kind))
            continue

        paragraph_buffer.append(line.strip())

    close_section()
    return "\n".join(html_parts), toc


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
                joiner = " " if label == "来源" else "；"
                body = f"{body}{joiner if body else ''}{joiner.join(extras)}".strip()
                normalized.append(f"- {label}：{body}")
                index = probe
                continue
        normalized.append(line)
        index += 1
    return normalized


def wrap_document(title: str, body_html: str, toc: list[tuple[str, str]]) -> str:
    toc_items = "\n".join(
        f'<li><a href="#{html.escape(section_id)}">{html.escape(label)}</a></li>' for section_id, label in toc
    )
    rendered_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    hero_html = ""
    hero_match = re.match(r"\s*(<header class=\"hero\">.*?</header>)(.*)$", body_html, re.S)
    if hero_match:
        hero_html = hero_match.group(1)
        body_html = hero_match.group(2)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="page">
    {hero_html}
    <div class="hero-meta">
      <span class="hero-chip">Asia/Shanghai</span>
      <span class="hero-chip">08:00 自动投递</span>
      <span class="hero-chip">最后渲染：{html.escape(rendered_at)}</span>
    </div>
    <div class="layout">
      <aside class="toc">
        <p class="toc-title">Quick Jump</p>
        <ul>
          {toc_items}
        </ul>
      </aside>
      <main class="content">
        {body_html}
      </main>
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    md_text = input_path.read_text()
    body_html, toc = render_markdown(md_text)
    title = next((line[2:].strip() for line in md_text.splitlines() if line.startswith("# ")), "Deep News Digest")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(wrap_document(title, body_html, toc))


if __name__ == "__main__":
    main()
