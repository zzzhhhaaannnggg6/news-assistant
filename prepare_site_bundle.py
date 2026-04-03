#!/opt/homebrew/bin/python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MOBILE_DIR = BASE_DIR / "mobile_app"


def write_config(target: Path, remote_url: str) -> None:
    target.write_text(
        "window.__MOBILE_CONFIG__ = {\n"
        f"  remoteDigestJsonUrl: {remote_url!r},\n"
        "  appMode: \"github\"\n"
        "};\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--remote-json-url", default="")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(MOBILE_DIR / "index.html", output_dir / "index.html")
    shutil.copy2(MOBILE_DIR / "styles.css", output_dir / "styles.css")
    shutil.copy2(MOBILE_DIR / "app.js", output_dir / "app.js")
    shutil.copy2(MOBILE_DIR / "manifest.webmanifest", output_dir / "manifest.webmanifest")
    shutil.copy2(MOBILE_DIR / "service-worker.js", output_dir / "service-worker.js")
    shutil.copy2(MOBILE_DIR / "icon.svg", output_dir / "icon.svg")
    write_config(output_dir / "config.js", args.remote_json_url)

    export_target_json = data_dir / "latest.json"
    export_target_js = data_dir / "latest.js"
    shutil.copy2(MOBILE_DIR / "data" / "latest.json", export_target_json)
    shutil.copy2(MOBILE_DIR / "data" / "latest.js", export_target_js)
    shutil.copy2(export_target_json, output_dir / "latest.json")


if __name__ == "__main__":
    main()
