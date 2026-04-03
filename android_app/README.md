# News Assistant Android App

This is the separate Android APK project for the phone app.

## Goal

- Keep the desktop HTML push workflow unchanged
- Provide a separate Android APK that reads the same digest data model
- Support offline bundled content plus a future remote JSON feed for cross-network updates

## Current Status

- Project scaffolded locally
- Not yet compiled into an APK on this machine

## Why APK Build Is Blocked Right Now

- This machine currently cannot resolve Android SDK and npm package hosts from the shell
- Android SDK command line tools and npm dependencies could not be downloaded

## What This Project Expects

- A working Android SDK
- A JDK
- Internet access to Android and npm package registries, or preinstalled toolchains
- For cross-network live data: an internet-accessible static URL serving `latest.json`

## Remote Feed

The app is designed to read a remote digest JSON URL in the future.
That remote URL is configured in:

- `app/src/main/assets/app/config.js`

If that URL is empty, the app falls back to bundled local content.
