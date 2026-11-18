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
    PlatformInfo {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        app_name: env!("CARGO_PKG_NAME").to_string(),
    }
}

fn open_directory(path: &Path) -> Result<(), String> {
    if !path.exists() {
        let _ = std::fs::create_dir_all(path);
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
        Command::new("open")
            .arg(path)
            .spawn()
            .map_err(|e| format!("打开目录失败: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(path)
            .spawn()
            .map_err(|e| format!("打开目录失败: {}", e))?;
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
