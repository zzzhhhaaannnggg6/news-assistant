#!/opt/homebrew/bin/python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--timeout-seconds", required=True, type=int)
    parser.add_argument("--reasoning-effort", default="low")
    parser.add_argument("--search", action="store_true")
    args = parser.parse_args()

    prompt = Path(args.prompt_file).read_text()
    command = ["/opt/homebrew/bin/codex"]
    if args.search:
        command.append("--search")
    command.extend(
        [
            "exec",
            "-c",
            f'model_reasoning_effort="{args.reasoning_effort}"',
            "--skip-git-repo-check",
            "--color",
            "never",
            "-C",
            args.workdir,
            "-o",
            args.output_file,
            "-",
        ]
    )

    try:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            timeout=args.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(
            f"codex generation timed out after {args.timeout_seconds} seconds",
            file=sys.stderr,
        )
        return 124

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
