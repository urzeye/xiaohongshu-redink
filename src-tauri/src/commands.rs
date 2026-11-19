use std::path::Path;
use std::process::Command;
use serde::Serialize;
use tauri::State;

use crate::process_manager::{BackendStatus, ProcessManager};

#[derive(Debug, Serialize)]
pub struct PlatformInfo {
    pub os: String,
    pub arch: String,
    pub version: String,
    pub app_name: String,
    pub auth_token: Option<String>,
}

#[tauri::command]
pub fn get_backend_status(pm: State<ProcessManager>) -> BackendStatus {
    pm.get_status()
}

#[tauri::command]
pub fn restart_backend(pm: State<ProcessManager>) -> Result<BackendStatus, String> {
    pm.restart()?;
    Ok(pm.get_status())
}

#[tauri::command]
pub fn open_data_folder(pm: State<ProcessManager>) -> Result<(), String> {
    let dir = pm.get_data_dir();
    open_directory(&dir)
}

#[tauri::command]
pub fn open_logs_folder(pm: State<ProcessManager>) -> Result<(), String> {
    let dir = pm.get_logs_dir();
    open_directory(&dir)
}

#[tauri::command]
pub fn open_external_url(url: String) -> Result<(), String> {
    open_url(&url)
}

#[tauri::command]
pub fn get_platform_info() -> PlatformInfo {
    let auth_token = std::env::var("REDINK_AUTH_TOKEN")
        .ok()
        .filter(|s| !s.trim().is_empty());
    PlatformInfo {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        app_name: env!("CARGO_PKG_NAME").to_string(),
        auth_token,
    }
}

fn open_directory(path: &Path) -> Result<(), String> {
    if !path.exists() {
        std::fs::create_dir_all(path)
            .map_err(|e| format!("创建目录失败 ({:?}): {}", path, e))?;
    }

    if !path.exists() {
        return Err(format!("目录不存在且无法自动创建: {:?}", path));
    }

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        let mut cmd = Command::new("explorer");
        cmd.arg(path);
        cmd.creation_flags(0x08000000);
        cmd.spawn().map_err(|e| format!("打开目录失败: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        let status = Command::new("open")
            .arg(path)
            .status()
            .map_err(|e| format!("调用 open 打开目录失败: {}", e))?;
        if !status.success() {
            return Err(format!("打开目录失败，系统退出码: {:?}", status.code()));
        }
    }

    #[cfg(target_os = "linux")]
    {
        let status = Command::new("xdg-open")
            .arg(path)
            .status()
            .map_err(|e| format!("调用 xdg-open 打开目录失败: {}", e))?;
        if !status.success() {
            return Err(format!("打开目录失败，系统退出码: {:?}", status.code()));
        }
    }

    Ok(())
}

fn open_url(url: &str) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        let mut cmd = Command::new("cmd");
        cmd.args(["/c", "start", "", url]);
        cmd.creation_flags(0x08000000);
        cmd.spawn().map_err(|e| format!("打开网页失败: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(url)
            .spawn()
            .map_err(|e| format!("打开网页失败: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(url)
            .spawn()
            .map_err(|e| format!("打开网页失败: {}", e))?;
    }

    Ok(())
}
