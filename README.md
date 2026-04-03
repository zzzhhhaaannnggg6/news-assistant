# Local Daily News Assistant

This setup runs a daily deep-dive news digest locally with `codex --search exec`.

## What it does

- Runs once per day at 08:00 Asia/Shanghai time
- Searches the web for the last 24 hours of important updates
- Produces a Chinese deep-dive digest in Markdown and styled HTML
- Opens the latest HTML report in Google Chrome
- If the Mac was off or you were not logged in at 08:00, it will push the report the next time the LaunchAgent loads after 08:00
- Interprets `CS` as `computer science / information security`, not Counter-Strike
- If generation times out or fails, it now opens a status page instead of failing silently
- Stores reports locally and keeps `latest.md` and `latest.html` copies
- If GitHub sync is configured, mobile digest data can be published for cross-network access without affecting the desktop workflow

## Files

- `daily_news_prompt.md`: prompt template used by Codex
- `run_news_digest.sh`: manual runner and scheduled entrypoint
- `render_news_html.py`: Markdown to styled HTML renderer
- `export_digest_data.py`: exports the latest digest to a mobile-friendly data bundle
- `reports/`: generated daily reports
- `html/`: generated daily HTML reports
- `mobile_app/`: Android / HarmonyOS 4 friendly mobile web app
- `logs/`: runner logs
- `state/`: delivery state for Chrome auto-open
- `sources/`: optional scratch space for future source bundles

## Manual run

```sh
/Users/li/.codex/news_assistant/run_news_digest.sh --now
```

## Output

- Latest report: `/Users/li/.codex/news_assistant/latest.md`
- Latest HTML report: `/Users/li/.codex/news_assistant/latest.html`
- Daily archive: `/Users/li/.codex/news_assistant/reports/YYYY-MM-DD.md`
- Daily HTML archive: `/Users/li/.codex/news_assistant/html/YYYY-MM-DD.html`
- Mobile app entry: `/Users/li/.codex/news_assistant/mobile_app/index.html`

## launchd

- Agent label: `com.li.codex.daily-news`
- Agent file: `/Users/li/Library/LaunchAgents/com.li.codex.daily-news.plist`

Useful commands:

```sh
launchctl bootstrap "gui/$(id -u)" /Users/li/Library/LaunchAgents/com.li.codex.daily-news.plist
launchctl bootout "gui/$(id -u)" /Users/li/Library/LaunchAgents/com.li.codex.daily-news.plist
launchctl kickstart -k "gui/$(id -u)/com.li.codex.daily-news"
launchctl print "gui/$(id -u)/com.li.codex.daily-news"
```
