# News Assistant

一个可跨网络使用的每日新闻助手。

## 下载与使用

- 最新 APK 直接下载：
  [news-assistant-latest.apk](https://github.com/zzzhhhaaannnggg6/news-assistant/releases/download/mobile-latest/news-assistant-latest.apk)
- 最新版本页面：
  [Latest Release](https://github.com/zzzhhhaaannnggg6/news-assistant/releases/tag/mobile-latest)
- 所有版本：
  [Releases](https://github.com/zzzhhhaaannnggg6/news-assistant/releases)
- 手机网页版：
  [https://zzzhhhaaannnggg6.github.io/news-assistant/](https://zzzhhhaaannnggg6.github.io/news-assistant/)

## 给普通用户的最短说明

1. 如果你想安装 App，直接下载上面的“最新 APK”到安卓手机并安装。
2. 如果你暂时不想安装，直接打开上面的手机网页版即可。
3. 电脑端仍然保留本地 `08:00` 自动弹出 HTML 简报的机制，和手机端是分开的。

## 这是什么

- 每天生成一份中文深度新闻简报
- 重点覆盖：国际形势、游戏、商业洞见、数码圈、计算机 / 信息安全
- 手机端可以跨 Wi‑Fi 使用
- 电脑端继续走本地 HTML 推送，不依赖手机端

## 当前版本说明

- `mobile-latest` 会始终指向当前可下载的最新 APK
- GitHub 首页里的下载链接会固定跳到最新安装包
- 如果手机拦截安装，请在系统里允许“安装未知应用”
- 手机网页版和 APK 读取的是同一套日报数据

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
