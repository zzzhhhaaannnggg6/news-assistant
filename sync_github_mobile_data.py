#!/opt/homebrew/bin/python3
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = BASE_DIR / "state" / "github_sync_config.json"


def gh_request(method: str, url: str, token: str, data: dict | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "codex-news-assistant",
    }
    payload = None if data is None else json.dumps(data).encode("utf-8")
    request = urllib.request.Request(url, method=method, headers=headers, data=payload)
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def build_tree_entries(repo_root: Path, files: list[str], owner: str, repo: str, token: str) -> list[dict]:
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    entries: list[dict] = []
    for relative in files:
        content = (repo_root / relative).read_text()
        blob = gh_request(
            "POST",
            api_base + "/git/blobs",
            token,
            {"content": content, "encoding": "utf-8"},
        )
        entries.append(
            {
                "path": relative,
                "mode": "100644",
                "type": "blob",
                "sha": blob["sha"],
            }
        )
    return entries


def sync_files(owner: str, repo: str, token: str, message: str) -> str:
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    ref = gh_request("GET", api_base + "/git/ref/heads/main", token)
    base_commit = ref["object"]["sha"]
    commit = gh_request("GET", api_base + f"/git/commits/{base_commit}", token)
    base_tree = commit["tree"]["sha"]

    files = [
        "mobile_app/data/latest.json",
        "mobile_app/data/latest.js",
        "android_app/app/src/main/assets/app/data/latest.json",
        "android_app/app/src/main/assets/app/data/latest.js",
    ]
    tree = gh_request(
        "POST",
        api_base + "/git/trees",
        token,
        {
            "base_tree": base_tree,
            "tree": build_tree_entries(BASE_DIR, files, owner, repo, token),
        },
    )
    new_commit = gh_request(
        "POST",
        api_base + "/git/commits",
        token,
        {
            "message": message,
            "tree": tree["sha"],
            "parents": [base_commit],
        },
    )
    updated = gh_request(
        "PATCH",
        api_base + "/git/refs/heads/main",
        token,
        {"sha": new_commit["sha"], "force": False},
    )
    return updated["object"]["sha"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--message", default="Update mobile digest data")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text())
    sha = sync_files(
        owner=config["owner"],
        repo=config["repo"],
        token=config["token"],
        message=args.message,
    )
    print(sha)


if __name__ == "__main__":
    main()
