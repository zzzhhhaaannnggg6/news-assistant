#!/bin/zsh
set -euo pipefail

APP_DIR="/Users/li/.codex/news_assistant/android_app"

if [ -z "${JAVA_HOME:-}" ]; then
  /bin/echo "JAVA_HOME is not set."
fi

if [ -z "${ANDROID_HOME:-}" ] && [ -z "${ANDROID_SDK_ROOT:-}" ]; then
  /bin/echo "ANDROID_HOME or ANDROID_SDK_ROOT is not set."
fi

/bin/echo "This project is scaffolded, but this machine still needs a working Android SDK and Gradle wrapper/bootstrap path to produce an APK."
/bin/echo "Project directory: ${APP_DIR}"
