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
    pub port: u16,
    pub host: String,
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
pub fn open_history_folder(pm: State<ProcessManager>, task_id: Option<String>) -> Result<(), String> {
    let base_data_history = pm.get_data_dir().join("history");
    let base_project_history = pm.get_project_root().join("history");

    let target_dir = if let Some(ref tid) = task_id {
        let tid = tid.trim();
        if !tid.is_empty() {
            let data_task_dir = base_data_history.join(tid);
            let proj_task_dir = base_project_history.join(tid);
            if data_task_dir.exists() {
                data_task_dir
            } else if proj_task_dir.exists() {
                proj_task_dir
            } else if base_data_history.exists() {
                base_data_history
            } else {
                base_project_history
            }
        } else if base_data_history.exists() {
            base_data_history
        } else {
            base_project_history
        }
    } else if base_data_history.exists() {
        base_data_history
    } else {
        base_project_history
    };

    open_directory(&target_dir)
}

#[tauri::command]
pub fn open_config_file(pm: State<ProcessManager>, file_type: String) -> Result<(), String> {
    let data_dir = pm.get_data_dir();
    let project_root = pm.get_project_root();

    let target_file = match file_type.as_str() {
        "env" => {
            let data_env = data_dir.join(".env");
            let root_env = project_root.join(".env");
            if data_env.exists() {
                data_env
            } else if root_env.exists() {
                root_env
            } else {
                let _ = std::fs::create_dir_all(&data_dir);
                let root_example = project_root.join(".env.example");
                if root_example.exists() {
                    let _ = std::fs::copy(&root_example, &data_env);
                } else {
                    let _ = std::fs::write(&data_env, "# RedInk Configuration
REDINK_PORT=12398
REDINK_LOG_LEVEL=INFO
");
                }
                data_env
            }
        }
        "text_providers" => {
            let data_file = data_dir.join("text_providers.yaml");
            let root_file = project_root.join("text_providers.yaml");
            if data_file.exists() {
                data_file
            } else if root_file.exists() {
                root_file
            } else {
                let _ = std::fs::create_dir_all(&data_dir);
                let root_example = project_root.join("text_providers.yaml.example");
                if root_example.exists() {
                    let _ = std::fs::copy(&root_example, &data_file);
                }
                data_file
            }
        }
        "image_providers" => {
            let data_file = data_dir.join("image_providers.yaml");
            let root_file = project_root.join("image_providers.yaml");
            if data_file.exists() {
                data_file
            } else if root_file.exists() {
                root_file
            } else {
                let _ = std::fs::create_dir_all(&data_dir);
                let root_example = project_root.join("image_providers.yaml.example");
                if root_example.exists() {
                    let _ = std::fs::copy(&root_example, &data_file);
                }
                data_file
            }
        }
        "search_providers" => {
            let data_file = data_dir.join("search_providers.yaml");
            let root_file = project_root.join("search_providers.yaml");
            if data_file.exists() {
                data_file
            } else if root_file.exists() {
                root_file
            } else {
                let _ = std::fs::create_dir_all(&data_dir);
                let root_example = project_root.join("search_providers.yaml.example");
                if root_example.exists() {
                    let _ = std::fs::copy(&root_example, &data_file);
                }
                data_file
            }
        }
        _ => return Err(format!("未知的配置文件类型: {}", file_type)),
    };

    open_file(&target_file)
}

#[tauri::command]
pub fn open_external_url(url: String) -> Result<(), String> {
    open_url(&url)
}

#[tauri::command]
pub fn get_platform_info(pm: State<ProcessManager>) -> PlatformInfo {
    let auth_token = std::env::var("REDINK_AUTH_TOKEN")
        .ok()
        .filter(|s| !s.trim().is_empty());
    PlatformInfo {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        app_name: env!("CARGO_PKG_NAME").to_string(),
        auth_token,
        port: pm.get_port(),
        host: pm.get_host(),
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

fn open_file(path: &Path) -> Result<(), String> {
    if !path.exists() {
        return Err(format!("配置文件不存在: {:?}", path));
    }

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        let path_str = path.to_string_lossy().to_string();
        let mut cmd = if path.file_name().map(|n| n.to_string_lossy().starts_with(".env")).unwrap_or(false) {
            let mut c = Command::new("notepad.exe");
            c.arg(&path_str);
            c
        } else {
            let mut c = Command::new("cmd");
            c.args(["/c", "start", "", &path_str]);
            c
        };
        cmd.creation_flags(0x08000000);
        cmd.spawn().map_err(|e| format!("打开文件失败: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        let status = Command::new("open")
            .arg("-t")
            .arg(path)
            .status()
            .map_err(|e| format!("调用 open 打开文件失败: {}", e))?;
        if !status.success() {
            return Err(format!("打开文件失败，退出码: {:?}", status.code()));
        }
    }

    #[cfg(target_os = "linux")]
    {
        let status = Command::new("xdg-open")
            .arg(path)
            .status()
            .map_err(|e| format!("调用 xdg-open 打开文件失败: {}", e))?;
        if !status.success() {
            return Err(format!("打开文件失败，退出码: {:?}", status.code()));
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
