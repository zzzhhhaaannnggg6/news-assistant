#!/opt/homebrew/bin/python3
from __future__ import annotations

import argparse
import http.server
import json
import os
import socket
import subprocess
from pathlib import Path


BASE_DIR = Path("/Users/li/.codex/news_assistant")
MOBILE_DIR = BASE_DIR / "mobile_app"
STATE_DIR = BASE_DIR / "state"
LOG_DIR = BASE_DIR / "logs"
EXPORT_SCRIPT = BASE_DIR / "export_digest_data.py"
LATEST_MD = BASE_DIR / "latest.md"
DATA_JSON = MOBILE_DIR / "data" / "latest.json"
DATA_JS = MOBILE_DIR / "data" / "latest.js"
SERVER_INFO = STATE_DIR / "mobile_server.json"


def export_latest_digest() -> None:
    subprocess.run(
        [
            "/opt/homebrew/bin/python3",
            str(EXPORT_SCRIPT),
            "--input",
            str(LATEST_MD),
            "--json-output",
            str(DATA_JSON),
            "--js-output",
            str(DATA_JS),
        ],
        check=True,
    )


def local_ips() -> list[str]:
    ips: list[str] = []
    for interface in ("en0", "en1"):
        try:
            result = subprocess.run(
                ["/usr/sbin/ipconfig", "getifaddr", interface],
                capture_output=True,
                text=True,
                check=True,
            )
            ip = result.stdout.strip()
            if ip and ip not in ips:
                ips.append(ip)
        except subprocess.CalledProcessError:
            continue
    if not ips:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                ip = sock.getsockname()[0]
                if ip and ip not in ips:
                    ips.append(ip)
        except OSError:
            pass
    if "127.0.0.1" not in ips:
        ips.insert(0, "127.0.0.1")
    return ips


def write_server_info(port: int, ips: list[str]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SERVER_INFO.write_text(
        json.dumps(
            {
                "port": port,
                "ips": ips,
                "urls": [f"http://{ip}:{port}/index.html" for ip in ips],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    MOBILE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    export_latest_digest()

    ips = local_ips()
    write_server_info(args.port, ips)

    os.chdir(MOBILE_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler) as httpd:
        print("News Assistant Mobile server is running.")
        for ip in ips:
            print(f"URL: http://{ip}:{args.port}/index.html")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
