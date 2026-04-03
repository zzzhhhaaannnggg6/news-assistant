#!/bin/zsh
set -euo pipefail

BASE_DIR="/Users/li/.codex/news_assistant"
STATE_DIR="${BASE_DIR}/state"
LOG_DIR="${BASE_DIR}/logs"
INFO_FILE="${STATE_DIR}/mobile_server.json"
PORT="${NEWS_MOBILE_PORT:-8787}"
PLIST="/Users/li/Library/LaunchAgents/com.li.codex.mobile-news.plist"
LABEL="com.li.codex.mobile-news"

/bin/mkdir -p "${STATE_DIR}" "${LOG_DIR}"

/bin/mkdir -p "$(dirname "${PLIST}")"
/bin/sleep 1
/bin/launchctl bootout "gui/$(id -u)" "${PLIST}" >/dev/null 2>&1 || true
/bin/launchctl bootstrap "gui/$(id -u)" "${PLIST}"
/bin/launchctl kickstart -k "gui/$(id -u)/${LABEL}"
/bin/sleep 2

if [ -f "${INFO_FILE}" ]; then
  /bin/cat "${INFO_FILE}"
fi

/usr/bin/osascript -e 'display notification "移动版新闻助手已经启动。" with title "新闻助手 Mobile"' >/dev/null 2>&1 || true
/usr/bin/open "http://127.0.0.1:${PORT}/index.html"
