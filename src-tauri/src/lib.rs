mod commands;
mod process_manager;
mod tray;

use log::{error, info};
use process_manager::ProcessManager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let host = std::env::var("REDINK_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port = std::env::var("REDINK_PORT")
        .ok()
        .and_then(|p| p.parse::<u16>().ok())
        .unwrap_or(12398);

    let pm = ProcessManager::new(host, port);
    let pm_for_setup = pm.clone();
    let pm_for_exit = pm.clone();

    tauri::Builder::default()
        .manage(pm)
        .plugin(
            tauri_plugin_log::Builder::default()
                .level(log::LevelFilter::Info)
                .build(),
        )
        .setup(move |app| {
            info!("Initializing RedInk Desktop...");

            // 初始化系统托盘
            if let Err(err) = tray::setup_tray(app.handle()) {
                error!("Failed to setup system tray: {}", err);
            }

            // 在后台异步启动本地 Python 后端引擎（不阻塞主界面渲染）
            let pm_thread = pm_for_setup.clone();
            std::thread::spawn(move || {
                info!("Starting background Python engine...");
                if let Err(e) = pm_thread.start() {
                    error!("Backend startup failed: {}", e);
                } else {
                    info!("Backend engine initialized successfully");
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::get_backend_status,
            commands::restart_backend,
            commands::open_data_folder,
            commands::open_logs_folder,
            commands::open_history_folder,
            commands::open_external_url,
            commands::get_platform_info,
        ])
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(move |_app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                info!("Application exit requested, terminating backend child processes...");
                pm_for_exit.stop();
            }
        });
}
