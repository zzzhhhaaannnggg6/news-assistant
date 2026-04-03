#!/bin/zsh
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export TZ="Asia/Shanghai"

BASE_DIR="/Users/li/.codex/news_assistant"
PROMPT_FILE="${BASE_DIR}/daily_news_prompt.md"
PROMPT_RENDERED_FILE="${STATE_DIR:-${BASE_DIR}/state}/current_prompt.txt"
REPORT_DIR="${BASE_DIR}/reports"
HTML_DIR="${BASE_DIR}/html"
MOBILE_APP_DIR="${BASE_DIR}/mobile_app"
MOBILE_DATA_DIR="${MOBILE_APP_DIR}/data"
LOG_DIR="${BASE_DIR}/logs"
STATE_DIR="${BASE_DIR}/state"
LATEST_FILE="${BASE_DIR}/latest.md"
LATEST_HTML_FILE="${BASE_DIR}/latest.html"
STATUS_MD_FILE="${STATE_DIR}/latest_status.md"
STATUS_HTML_FILE="${STATE_DIR}/latest_status.html"
TMP_FILE="${REPORT_DIR}/.latest.tmp.md"
RUN_DATE="$([ -n "${NEWS_RUN_DATE_OVERRIDE:-}" ] && printf '%s' "${NEWS_RUN_DATE_OVERRIDE}" || /bin/date '+%Y-%m-%d')"
DAY_FILE="${REPORT_DIR}/${RUN_DATE}.md"
DAY_HTML_FILE="${HTML_DIR}/${RUN_DATE}.html"
CODEX_BIN="/opt/homebrew/bin/codex"
PYTHON_BIN="/opt/homebrew/bin/python3"
CHROME_APP="/Applications/Google Chrome.app"
LAST_OPENED_FILE="${STATE_DIR}/last_opened_date.txt"
MODE="${1:-scheduled}"
RUN_HOUR=8
RUN_MINUTE=0
GEN_TIMEOUT_SECONDS="${NEWS_GENERATION_TIMEOUT:-480}"

/bin/mkdir -p "${REPORT_DIR}" "${HTML_DIR}" "${BASE_DIR}/sources" "${LOG_DIR}" "${STATE_DIR}"
/bin/mkdir -p "${MOBILE_DATA_DIR}"

PROMPT="$(/usr/bin/sed "s/__RUN_DATE__/${RUN_DATE}/g" "${PROMPT_FILE}")"
/usr/bin/printf '%s\n' "${PROMPT}" > "${PROMPT_RENDERED_FILE}"
NOW_HM="$(/bin/date '+%H%M')"
TODAY_CUTOFF_EPOCH="$(/bin/date -j -f '%Y-%m-%d %H:%M:%S' "${RUN_DATE} ${RUN_HOUR}:00:00" '+%s')"
NOW_EPOCH="$(/bin/date '+%s')"

log_line() {
  /bin/echo "$(/bin/date '+%Y-%m-%d %H:%M:%S %Z') $1" >> "${LOG_DIR}/runner.log"
}

notify_user() {
  notify_title="$1"
  notify_body="$2"
  /usr/bin/osascript -e "display notification \"${notify_body}\" with title \"${notify_title}\"" >/dev/null 2>&1 || true
}

file_mtime() {
  if [ -f "$1" ]; then
    /usr/bin/stat -f '%m' "$1"
  else
    /bin/echo 0
  fi
}

latest_archive_html_uri() {
  "${PYTHON_BIN}" - <<'PY'
from pathlib import Path
run_date = Path("/Users/li/.codex/news_assistant/state/run_date_placeholder.txt").read_text().strip()
html_dir = Path("/Users/li/.codex/news_assistant/html")
candidates = sorted(
    [p for p in html_dir.glob("*.html") if p.name != f"{run_date}.html"],
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)
print(candidates[0].as_uri() if candidates else "")
PY
}

write_status_page() {
  status_reason="$1"
  reason_line="$2"
  previous_uri="$3"
  previous_line="今天没有新的成稿可打开。"
  if [ -n "${previous_uri}" ]; then
    previous_line="上一份成功简报仍可打开：[查看上一份简报](${previous_uri})"
  fi
  /bin/cat > "${STATUS_MD_FILE}" <<EOF
# ${RUN_DATE} 深度新闻简报

喵，今天的自动推送已经触发，但生成过程出了问题，我先把状态告诉你。

## 今日总览
${reason_line}

## 生成状态
### ${status_reason}
- 一句话判断：这次不是“没触发”，而是日报生成流程没有在可接受时间内完成。
- 发生了什么：自动任务今天已经启动，但生成阶段超时或异常退出，因此没有形成新的完整日报。
- 背景：当前这套日报依赖 \`codex --search exec\` 做联网收束；如果搜索侧反复重连，进程就可能长时间卡住。
- 为什么重要：如果不做超时与兜底，结果就是你像今天 2026 年 4 月 3 日中午醒来时一样，什么都收不到。
- 关键事实：
  - 本次任务的硬超时已设置为 ${GEN_TIMEOUT_SECONDS} 秒。
  - 超时或失败时，系统现在会改为推送状态页，而不是静默卡住。
  - Chrome 自动打开逻辑仍会执行，因此至少会有一个明确结果页弹出。
- 接下来观察：我已经把执行链改成“超时即收口”；下一次定时或补推会按新逻辑运行。
- 来源：[运行日志](file:///Users/li/.codex/news_assistant/logs/runner.log) [错误输出](file:///Users/li/.codex/news_assistant/logs/launchd.stderr.log)

## 可打开的上一份简报
${previous_line}

## 收尾总结
这次确实是自动化做得不够稳，喵。我已经把“卡住就什么都没有”改成“卡住也会明确通知你”，后面至少不会再无声失败。
EOF
  "${PYTHON_BIN}" "${BASE_DIR}/render_news_html.py" --input "${STATUS_MD_FILE}" --output "${STATUS_HTML_FILE}"
  /bin/cp "${STATUS_MD_FILE}" "${LATEST_FILE}"
  /bin/cp "${STATUS_HTML_FILE}" "${LATEST_HTML_FILE}"
}

should_generate=0
if [ ! -f "${DAY_FILE}" ]; then
  should_generate=1
elif [ "${NOW_EPOCH}" -ge "${TODAY_CUTOFF_EPOCH}" ] && [ "$(file_mtime "${DAY_FILE}")" -lt "${TODAY_CUTOFF_EPOCH}" ]; then
  should_generate=1
fi

if [ "${MODE}" = "--scheduled" ] && [ "${NOW_HM}" -lt "0800" ]; then
  log_line "skipped early scheduled run before 08:00"
  exit 0
fi

/bin/echo "${RUN_DATE}" > "${STATE_DIR}/run_date_placeholder.txt"
log_line "starting ${MODE} run for ${RUN_DATE}"

generation_failed=0

if [ "${MODE}" = "--generate-only" ] || [ "${MODE}" = "--scheduled" ] || [ "${MODE}" = "--now" ]; then
  if [ "${should_generate}" -eq 1 ] || [ "${MODE}" = "--now" ]; then
    if "${PYTHON_BIN}" "${BASE_DIR}/run_codex_prompt.py" \
      --prompt-file "${PROMPT_RENDERED_FILE}" \
      --output-file "${TMP_FILE}" \
      --workdir /Users/li/.codex \
      --timeout-seconds "${GEN_TIMEOUT_SECONDS}" \
      --reasoning-effort low \
      --search; then
      /bin/mv "${TMP_FILE}" "${DAY_FILE}"
      /bin/cp "${DAY_FILE}" "${LATEST_FILE}"
      log_line "generated ${DAY_FILE}"
    else
      generation_failed=1
      /bin/rm -f "${TMP_FILE}"
      log_line "generation failed for ${RUN_DATE}"
    fi
  else
    /bin/cp "${DAY_FILE}" "${LATEST_FILE}"
    log_line "reused existing ${DAY_FILE}"
  fi
fi

if [ "${generation_failed}" -eq 0 ]; then
  "${PYTHON_BIN}" "${BASE_DIR}/render_news_html.py" --input "${DAY_FILE}" --output "${DAY_HTML_FILE}"
  /bin/cp "${DAY_HTML_FILE}" "${LATEST_HTML_FILE}"
  log_line "rendered ${DAY_HTML_FILE}"
  open_notification_text="今日简报已生成并准备打开。"
else
  previous_uri="$(latest_archive_html_uri)"
  write_status_page "自动生成超时或失败" "${RUN_DATE} 这次任务已经触发，但生成阶段没有在规定时间内完成，因此我先给你状态页而不是空白。" "${previous_uri}"
  log_line "rendered status page after failed generation"
  open_notification_text="今日日报生成超时，已打开状态页。"
fi

"${PYTHON_BIN}" "${BASE_DIR}/export_digest_data.py" \
  --input "${LATEST_FILE}" \
  --json-output "${MOBILE_DATA_DIR}/latest.json" \
  --js-output "${MOBILE_DATA_DIR}/latest.js"
log_line "exported mobile digest bundle"

if [ -f "${BASE_DIR}/sync_android_assets.py" ]; then
  "${PYTHON_BIN}" "${BASE_DIR}/sync_android_assets.py"
  log_line "synced android asset bundle"
fi

if [ -f "${STATE_DIR}/github_sync_config.json" ]; then
  if "${PYTHON_BIN}" "${BASE_DIR}/sync_github_mobile_data.py" --message "Update mobile digest data for ${RUN_DATE}"; then
    log_line "synced mobile digest to github"
  else
    log_line "failed to sync mobile digest to github"
  fi
fi

should_open=0
if [ "${MODE}" = "--now" ]; then
  should_open=1
elif [ "${MODE}" = "--scheduled" ]; then
  last_opened=""
  if [ -f "${LAST_OPENED_FILE}" ]; then
    last_opened="$(/bin/cat "${LAST_OPENED_FILE}")"
  fi
  if [ "${NOW_HM}" -ge "0800" ] && [ "${last_opened}" != "${RUN_DATE}" ]; then
    should_open=1
  fi
fi

if [ "${should_open}" -eq 1 ] && [ -d "${CHROME_APP}" ]; then
  LATEST_HTML_URI="$("${PYTHON_BIN}" - <<'PY'
from pathlib import Path
print(Path("/Users/li/.codex/news_assistant/latest.html").as_uri())
PY
)"
  /usr/bin/osascript <<EOF
tell application "Google Chrome"
  activate
  if (count of windows) = 0 then
    make new window
  end if
  set URL of active tab of front window to "${LATEST_HTML_URI}"
end tell
EOF
  /bin/echo "${RUN_DATE}" > "${LAST_OPENED_FILE}"
  log_line "opened ${LATEST_HTML_FILE} in Google Chrome"
  notify_user "每日新闻助手" "${open_notification_text}"
elif [ "${should_open}" -eq 1 ]; then
  notify_user "每日新闻助手" "${open_notification_text}"
fi
