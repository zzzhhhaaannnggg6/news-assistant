#!/bin/zsh
set -euo pipefail

PLIST="/Users/li/Library/LaunchAgents/com.li.codex.mobile-news.plist"
LABEL="com.li.codex.mobile-news"

if /bin/launchctl print "gui/$(id -u)/${LABEL}" >/dev/null 2>&1; then
  /bin/launchctl bootout "gui/$(id -u)" "${PLIST}" >/dev/null 2>&1 || true
  /usr/bin/osascript -e 'display notification "移动版新闻助手已经停止。" with title "新闻助手 Mobile"' >/dev/null 2>&1 || true
  /bin/echo "Stopped mobile app server."
else
  /bin/echo "Mobile app server is not running."
fi
