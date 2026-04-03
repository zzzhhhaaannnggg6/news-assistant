#!/opt/homebrew/bin/python3
from __future__ import annotations

import argparse
import html
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
FEED_LANG = "en-US"
FEED_REGION = "US"


TOPIC_FEEDS = {
    "WORLD": "https://news.google.com/rss/headlines/section/topic/WORLD?hl={hl}&gl={gl}&ceid={gl}:en",
    "BUSINESS": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl={hl}&gl={gl}&ceid={gl}:en",
    "TECHNOLOGY": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl={hl}&gl={gl}&ceid={gl}:en",
}


SECTION_QUERIES = [
    (
        "International Situation",
        [
            ("World Topic", TOPIC_FEEDS["WORLD"].format(hl=FEED_LANG, gl=FEED_REGION), 8),
            (
                "Policy Search",
                "https://news.google.com/rss/search?q="
                + quote_plus("diplomacy sanctions military election policy when:1d")
                + f"&hl={FEED_LANG}&gl={FEED_REGION}&ceid={FEED_REGION}:en",
                8,
            ),
        ],
    ),
    (
        "Gaming",
        [
            (
                "League of Legends Esports",
                "https://news.google.com/rss/search?q="
                + quote_plus('"League of Legends esports" OR LCK OR LPL OR MSI OR Worlds when:1d')
                + f"&hl={FEED_LANG}&gl={FEED_REGION}&ceid={FEED_REGION}:en",
                8,
            ),
            (
                "Valorant Esports",
                "https://news.google.com/rss/search?q="
                + quote_plus('"Valorant esports" OR VCT OR "Valorant Champions Tour" when:1d')
                + f"&hl={FEED_LANG}&gl={FEED_REGION}&ceid={FEED_REGION}:en",
                8,
            ),
            (
                "Honkai Star Rail",
                "https://news.google.com/rss/search?q="
                + quote_plus('"Honkai Star Rail" OR "Honkai: Star Rail" when:1d')
                + f"&hl={FEED_LANG}&gl={FEED_REGION}&ceid={FEED_REGION}:en",
                8,
            ),
        ],
    ),
    (
        "Business Insight",
        [
            ("Business Topic", TOPIC_FEEDS["BUSINESS"].format(hl=FEED_LANG, gl=FEED_REGION), 8),
            (
                "AI and Semiconductors",
                "https://news.google.com/rss/search?q="
                + quote_plus("AI semiconductor earnings funding acquisition partnership when:1d")
                + f"&hl={FEED_LANG}&gl={FEED_REGION}&ceid={FEED_REGION}:en",
                8,
            ),
        ],
    ),
    (
        "Consumer Tech",
        [
            ("Technology Topic", TOPIC_FEEDS["TECHNOLOGY"].format(hl=FEED_LANG, gl=FEED_REGION), 8),
            (
                "Devices and Chips",
                "https://news.google.com/rss/search?q="
                + quote_plus("smartphone PC laptop chip AI hardware consumer electronics when:1d")
                + f"&hl={FEED_LANG}&gl={FEED_REGION}&ceid={FEED_REGION}:en",
                8,
            ),
        ],
    ),
    (
        "CS Scene",
        [
            (
                "Counter-Strike",
                "https://news.google.com/rss/search?q="
                + quote_plus('"Counter-Strike 2" OR CS2 OR HLTV OR ESL OR BLAST when:1d')
                + f"&hl={FEED_LANG}&gl={FEED_REGION}&ceid={FEED_REGION}:en",
                8,
            ),
        ],
    ),
]


SOURCE_BLACKLIST = {
    "Polymarket",
    "Esports.net",
    "Action Network",
    "Sports Illustrated",
    "Odds Shark",
    "OddsJam",
    "Sportsbook Review",
    "Doc's Sports",
    "PickDawgz",
    "Rotowire",
    "Covers",
    "SportyTrader",
}


TITLE_BLACKLIST = (
    "odds",
    "betting",
    "prediction",
    "predictions",
    "best bets",
    "parlay",
    "wager",
    "fantasy",
    "picks",
    "tips",
)


def fetch_feed(url: str) -> ET.Element:
    result = subprocess.run(
        ["/usr/bin/curl", "-A", USER_AGENT, "-fsL", "--max-time", "15", url],
        check=True,
        capture_output=True,
    )
    return ET.fromstring(result.stdout)


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(value).split())


def extract_source(title: str, description: str) -> str:
    match = re.search(r"<font color=\"#6f6f6f\">(.*?)</font>", description)
    if match:
        return html.unescape(match.group(1)).strip()
    if " - " in title:
        return title.rsplit(" - ", 1)[-1].strip()
    return "Unknown"


def clean_title(title: str, source: str) -> str:
    suffix = f" - {source}"
    if title.endswith(suffix):
        return title[: -len(suffix)].strip()
    return title.strip()


def parse_date(value: str) -> datetime:
    try:
        dt = parsedate_to_datetime(value)
    except Exception:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def is_low_value(title: str, source: str) -> bool:
    lowered = title.lower()
    if any(keyword in lowered for keyword in TITLE_BLACKLIST):
        return True
    return source in SOURCE_BLACKLIST


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


@dataclass
class Item:
    section: str
    bucket: str
    title: str
    source: str
    published: datetime
    link: str


def iter_items(section: str, bucket: str, url: str, limit: int) -> Iterable[Item]:
    root = fetch_feed(url)
    items = root.findall("./channel/item")
    cutoff = datetime.now(timezone.utc) - timedelta(days=2)
    count = 0
    for raw in items:
        title = (raw.findtext("title") or "").strip()
        description = raw.findtext("description") or ""
        source = extract_source(title, description)
        title = clean_title(title, source)
        link = (raw.findtext("link") or "").strip()
        published = parse_date(raw.findtext("pubDate") or "")
        if not title or not link:
            continue
        if published < cutoff:
            continue
        if is_low_value(title, source):
            continue
        yield Item(section=section, bucket=bucket, title=title, source=source, published=published, link=link)
        count += 1
        if count >= limit:
            break


def collect_query(section: str, bucket: str, url: str, limit: int) -> list[Item]:
    try:
        return list(iter_items(section, bucket, url, limit))
    except Exception:
        return []


def collect() -> dict[str, list[Item]]:
    seen: set[str] = set()
    grouped: dict[str, list[Item]] = {section: [] for section, _queries in SECTION_QUERIES}
    futures = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        for section, queries in SECTION_QUERIES:
            for bucket, url, limit in queries:
                future = executor.submit(collect_query, section, bucket, url, limit)
                futures[future] = section
        for future in as_completed(futures):
            section = futures[future]
            for item in future.result():
                key = normalize_title(item.title)
                if key in seen:
                    continue
                seen.add(key)
                grouped[section].append(item)
    for section, _queries in SECTION_QUERIES:
        grouped[section].sort(key=lambda item: item.published, reverse=True)
        grouped[section] = grouped[section][:12]
    return grouped


def render(run_date: str, grouped: dict[str, list[Item]]) -> str:
    lines = [
        f"# Source Bundle for {run_date}",
        "",
        "Use this bundle as the primary source set for the daily digest.",
        "Each item below is a candidate signal collected from Google News RSS feeds.",
        "Prefer more authoritative sources when multiple items cover the same story.",
        "",
    ]
    for section, _queries in SECTION_QUERIES:
        lines.append(f"## {section}")
        items = grouped.get(section, [])
        if not items:
            lines.append("- No candidate items collected.")
            lines.append("")
            continue
        for item in items:
            lines.append(f"- Title: {item.title}")
            lines.append(f"  Source: {item.source}")
            lines.append(f"  Published: {item.published.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            lines.append(f"  Bucket: {item.bucket}")
            lines.append(f"  Link: {item.link}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = render(args.date, collect())
    output_path.write_text(bundle)


if __name__ == "__main__":
    main()
