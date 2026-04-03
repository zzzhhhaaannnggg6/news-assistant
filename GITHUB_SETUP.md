# GitHub Setup

This project is prepared for a split deployment model:

- Desktop Mac workflow stays local and unchanged
- Mobile app and cross-network access are delivered through GitHub

## What GitHub Will Provide

1. GitHub Pages:
   - hosts the public mobile web version
   - hosts `latest.json` for cross-network syncing
2. GitHub Actions:
   - builds an Android APK in the cloud
   - uploads build artifacts
   - can publish release APK assets

## What You Need To Provide

- A GitHub repository to push this folder into
- If you want daily remote sync, credentials or an access path that lets this Mac push updated mobile data to that repository

## Recommended Repository Layout

Push the contents of `/Users/li/.codex/news_assistant` as the repository root.

## After Pushing

1. Enable GitHub Pages in the repository
2. Use GitHub Actions to build the APK
3. Optionally configure a token locally so the Mac can push updated mobile data every day

## Current Limitation

This Mac currently cannot resolve Android SDK and npm package hosts from the shell, so the actual APK build should run on GitHub Actions rather than locally.
