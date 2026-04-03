#!/opt/homebrew/bin/python3
from __future__ import annotations

import shutil
import argparse
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MOBILE_DIR = BASE_DIR / "mobile_app"
TARGET_DIR = BASE_DIR / "android_app" / "app" / "src" / "main" / "assets" / "app"

INCLUDE = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.webmanifest",
    "icon.svg",
    "config.js",
    "data/latest.js",
    "data/latest.json",
]


def write_config(target: Path, remote_url: str) -> None:
    target.write_text(
        "window.__MOBILE_CONFIG__ = {\n"
        f"  remoteDigestJsonUrl: {remote_url!r},\n"
        "  appMode: \"android\"\n"
        "};\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-dir", default=str(TARGET_DIR))
    parser.add_argument("--remote-json-url", default="")
    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    for relative in INCLUDE:
        if relative == "config.js":
            continue
        source = MOBILE_DIR / relative
        target = target_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    write_config(target_dir / "config.js", args.remote_json_url)


if __name__ == "__main__":
    main()
