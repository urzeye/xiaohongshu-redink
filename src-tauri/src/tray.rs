use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager,
};

pub fn setup_tray(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let show_i = MenuItem::with_id(app, "show", "显示主界面", true, None::<&str>)?;
    let browser_i = MenuItem::with_id(app, "open_browser", "在外部浏览器中打开 (12398)", true, None::<&str>)?;
    let data_i = MenuItem::with_id(app, "open_data", "打开本地数据目录", true, None::<&str>)?;
    let logs_i = MenuItem::with_id(app, "open_logs", "打开运行日志目录", true, None::<&str>)?;
    let restart_i = MenuItem::with_id(app, "restart", "重启本地引擎", true, None::<&str>)?;
    let quit_i = MenuItem::with_id(app, "quit", "退出 RedInk", true, None::<&str>)?;
    let sep1 = PredefinedMenuItem::separator(app)?;
    let sep2 = PredefinedMenuItem::separator(app)?;

    let menu = Menu::with_items(
        app,
        &[
            &show_i,
            &browser_i,
            &sep1,
            &data_i,
            &logs_i,
            &restart_i,
            &sep2,
            &quit_i,
        ],
    )?;

    let icon = match app.default_window_icon() {
        Some(i) => i.clone(),
        None => return Err("Window icon not available for tray".into()),
    };

    let _tray = TrayIconBuilder::new()
        .icon(icon)
        .menu(&menu)
        .show_menu_on_left_click(false)
        .tooltip("RedInk · 小红书创作引擎 (家庭宽带本地版)")
        .on_menu_event(|app, event| match event.id.as_ref() {
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.unminimize();
                    let _ = window.set_focus();
                }
            }
            "open_browser" => {
                let _ = crate::commands::open_external_url("http://127.0.0.1:12398".to_string());
            }
            "open_data" => {
                if let Some(pm) = app.try_state::<crate::process_manager::ProcessManager>() {
                    let _ = crate::commands::open_data_folder(pm);
                }
            }
            "open_logs" => {
                if let Some(pm) = app.try_state::<crate::process_manager::ProcessManager>() {
                    let _ = crate::commands::open_logs_folder(pm);
                }
            }
            "restart" => {
                if let Some(pm) = app.try_state::<crate::process_manager::ProcessManager>() {
                    let _ = pm.restart();
                }
            }
            "quit" => {
                if let Some(pm) = app.try_state::<crate::process_manager::ProcessManager>() {
                    pm.stop();
                }
                app.exit(0);
            }
            _ => {}
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.unminimize();
                    let _ = window.set_focus();
                }
            }
        })
        .build(app)?;

    Ok(())
}
