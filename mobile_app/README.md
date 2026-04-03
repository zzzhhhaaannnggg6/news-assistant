# News Assistant Mobile

This is a mobile-first web app for the daily digest.

## What It Is

- A small installable PWA tuned for Android and HarmonyOS 4 browsers
- Reads digest data from `./data/latest.js`
- Optimized for narrow mobile screens

## Where To Look

- Entry file: `/Users/li/.codex/news_assistant/mobile_app/index.html`
- Latest data bundle: `/Users/li/.codex/news_assistant/mobile_app/data/latest.js`
- One-click launcher: `/Users/li/.codex/news_assistant/start_mobile_app.command`
- Stop launcher: `/Users/li/.codex/news_assistant/stop_mobile_app.command`

## Notes

- On Android or HarmonyOS 4, open the app in a modern browser and add it to the home screen.
- Because this machine does not currently have a Java or Android SDK toolchain installed, this mobile app is delivered as a PWA rather than a compiled APK.
- The easiest workflow is to start the local server on your Mac, then open the LAN URL on your phone while both devices are on the same Wi-Fi.
