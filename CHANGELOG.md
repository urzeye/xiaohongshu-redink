# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-11-18

### 🖥️ Desktop Application (Tauri v2)
- **Cross-Platform Desktop App**: Implemented native desktop application based on Tauri v2 for Windows (`.exe` / NSIS) and macOS (`.dmg` Universal Apple Silicon & Intel).
- **Zero-Friction Local Execution**: Runs directly in the user's home broadband environment to prevent account IP risk, eliminating manual Docker and Node.js setup requirements.
- **Process Lifecycle Management**: Seamlessly manages the local Python engine and `xiaohongshu-mcp` service without terminal black windows.
- **System Tray & Native Shortcuts**: Added system tray integration (minimize, quick show, restart engine) and native application menu support.

### 🚀 Publish Engine Improvements
- **Creator Center Session Auto-Sync**: Automatically synchronizes and injects `galaxy_creator_session_id` into `cookies.json` using the existing `web_session`, resolving creator center publish compatibility issues.
- **Creator Authorization Detection**: Real-time status detection for creator center authorization and real browser window opening for login authorization.
- **Silent Background Automation**: Upgraded to background silent publishing; eliminates unexpected browser popups and session flicker during routine checks.

### 🎨 Image Generation & Aspect Ratio Fixes
- **Dynamic Dimension Mapping**: Dynamically maps aspect ratio options (3:4, 1:1, 4:3, 9:16, 16:9) to standard pixel dimensions (e.g. 864x1152 for 3:4) across Volcano Ark and OpenAI-compatible APIs, resolving 1:1 square output limitations.

### 🛡️ Desktop & Web Stability
- **History Image Preview 401 Fix**: Injected authentication headers and tokens for image preview URLs, preventing 401 unauthorized errors on desktop.
- **Auto-Recovery for Missing History Images**: Automatically recovers missing history thumbnails or images from task directories without breaking history views.
- **Polling & Navigation Resilience**: Improved frontend long-polling resilience, tag copying, and menu navigation.

## [0.3.5] - 2026-03-05

### ✨ New Features / Visual Updates

- **Brand Identity**: Completely redesigned the core application logo. Replaced old visuals with an elegant, romantic skeuomorphic design featuring an intricate crystal starry night rose without distracting textual elements, improving the app's overall aesthetics.
- Favicon and top banner logo (144x144, 2048x2048 PNGs) have been successfully updated.

### 🎨 UI Improvements

- **Result View Enhancements**: Refined the user interface for displaying operation results.
  - Adjusted result tag colors to a crisp, professional blue tone.
  - Re-themed the progress bar to drift away from standard error red, providing a calmer, non-distracting appropriate color scheme.
