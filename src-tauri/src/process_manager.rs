use log::{error, info, warn};
use serde::Serialize;
use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::{Arc, Mutex};
use std::time::Duration;

#[derive(Debug, Clone, Serialize)]
pub struct BackendStatus {
    pub is_running: bool,
    pub host: String,
    pub port: u16,
    pub pid: Option<u32>,
    pub message: String,
    pub error: Option<String>,
}

#[derive(Debug, Clone)]
pub struct PythonInterpreter {
    pub path: PathBuf,
    pub is_uv: bool,
}

#[derive(Clone)]
pub struct ProcessManager {
    child: Arc<Mutex<Option<Child>>>,
    last_error: Arc<Mutex<Option<String>>>,
    project_root: PathBuf,
    host: String,
    port: u16,
}

impl ProcessManager {
    pub fn new(host: String, port: u16) -> Self {
        let project_root = Self::detect_project_root();
        info!("[ProcessManager] Resolved project root: {:?}", project_root);

        Self {
            child: Arc::new(Mutex::new(None)),
            last_error: Arc::new(Mutex::new(None)),
            project_root,
            host,
            port,
        }
    }

    /// 获取增强型 PATH 环境变量（补全 macOS/Linux 从 GUI 启动时缺失的终端常用路径）
    pub fn get_enhanced_path() -> String {
        let current_path = std::env::var("PATH").unwrap_or_default();
        #[cfg(not(target_os = "windows"))]
        {
            if let Some(home) = Self::get_user_home() {
                let extra_paths = [
                    home.join(".local").join("bin"),
                    home.join(".cargo").join("bin"),
                    home.join(".local").join("share").join("mise").join("shims"),
                    PathBuf::from("/opt/homebrew/bin"),
                    PathBuf::from("/usr/local/bin"),
                ];
                let mut path_elements: Vec<String> = extra_paths
                    .iter()
                    .filter(|p| p.exists() && !current_path.contains(&p.to_string_lossy().to_string()))
                    .map(|p| p.to_string_lossy().to_string())
                    .collect();
                if !path_elements.is_empty() {
                    path_elements.push(current_path);
                    return path_elements.join(":");
                }
            }
        }
        current_path
    }

    pub fn get_user_home() -> Option<PathBuf> {
        #[cfg(target_os = "windows")]
        {
            std::env::var("USERPROFILE").ok().map(PathBuf::from)
        }
        #[cfg(not(target_os = "windows"))]
        {
            std::env::var("HOME").ok().map(PathBuf::from)
        }
    }

    /// 自动推断项目根目录路径（支持开发环境与跨平台打包安装环境）
    pub fn detect_project_root() -> PathBuf {
        // 1. 优先使用显式指定的环境变量
        if let Ok(env_root) = std::env::var("REDINK_ROOT") {
            let p = PathBuf::from(env_root);
            if p.join("backend").join("app.py").exists() {
                return p;
            }
        }

        // 2. 检查当前工作目录（排除系统根目录 /）
        if let Ok(cwd) = std::env::current_dir() {
            if cwd != PathBuf::from("/") {
                if cwd.join("backend").join("app.py").exists() {
                    return cwd;
                }
                if let Some(parent) = cwd.parent() {
                    if parent != PathBuf::from("/") && parent.join("backend").join("app.py").exists() {
                        return parent.to_path_buf();
                    }
                }
            }
        }

        // 3. 检查当前可执行文件所在目录及其祖先目录
        if let Ok(mut exe) = std::env::current_exe() {
            for _ in 0..5 {
                if exe.pop() {
                    if exe.join("backend").join("app.py").exists() {
                        return exe;
                    }
                    // macOS app bundle: Contents/Resources
                    if exe.join("Resources").join("backend").join("app.py").exists() {
                        return exe.join("Resources");
                    }
                    if exe.join("resources").join("backend").join("app.py").exists() {
                        return exe.join("resources");
                    }
                } else {
                    break;
                }
            }
        }

        // 4. 启发式探测用户主目录下的常见开发工作区（解决 macOS 从访达启动不继承终端环境变量的问题）
        if let Some(home) = Self::get_user_home() {
            let candidates = [
                home.join("workspace").join("xiaohongshu-redink"),
                home.join("workspace").join("RedInk"),
                home.join("Projects").join("xiaohongshu-redink"),
                home.join("Development").join("xiaohongshu-redink"),
            ];
            for cand in candidates {
                if cand.join("backend").join("app.py").exists() {
                    info!("[ProcessManager] Found project root via heuristic: {:?}", cand);
                    return cand;
                }
            }
        }

        // 5. 降级安全处理：避免降级到系统只读根目录 /
        if let Ok(cwd) = std::env::current_dir() {
            if cwd != PathBuf::from("/") {
                return cwd;
            }
        }

        if let Some(home) = Self::get_user_home() {
            home.join(".redink")
        } else {
            PathBuf::from(".")
        }
    }

    #[allow(dead_code)]
    pub fn get_project_root(&self) -> PathBuf {
        self.project_root.clone()
    }

    pub fn get_data_dir(&self) -> PathBuf {
        // 如果项目根目录有效存在且不是系统根目录 /，且处于开发目录模式
        if self.project_root != PathBuf::from("/") && self.project_root.join("backend").join("app.py").exists() {
            let candidate = self.project_root.join("data");
            // 确保不是在 /Applications 只读 app bundle 内
            if !self.project_root.to_string_lossy().contains(".app/Contents") {
                return candidate;
            }
        }

        // 桌面端规范：写入用户应用数据目录
        if let Some(home) = Self::get_user_home() {
            #[cfg(target_os = "macos")]
            return home.join("Library").join("Application Support").join("RedInk").join("data");
            #[cfg(target_os = "windows")]
            return home.join("AppData").join("Roaming").join("RedInk").join("data");
            #[cfg(target_os = "linux")]
            return home.join(".local").join("share").join("redink").join("data");
        }

        self.project_root.join("data")
    }

    pub fn get_logs_dir(&self) -> PathBuf {
        // macOS 上 tauri_plugin_log 默认输出目录
        #[cfg(target_os = "macos")]
        if let Some(home) = Self::get_user_home() {
            let standard_log = home.join("Library").join("Logs").join("com.redink.desktop");
            if standard_log.exists() {
                return standard_log;
            }
        }

        if self.project_root != PathBuf::from("/") && self.project_root.join("backend").join("app.py").exists() {
            if !self.project_root.to_string_lossy().contains(".app/Contents") {
                return self.project_root.join("logs");
            }
        }

        if let Some(home) = Self::get_user_home() {
            #[cfg(target_os = "macos")]
            return home.join("Library").join("Logs").join("com.redink.desktop");
            #[cfg(not(target_os = "macos"))]
            return home.join(".redink").join("logs");
        }

        self.project_root.join("logs")
    }

    /// 跨平台搜索可用的 Python 解释器
    pub fn find_python(&self) -> Result<PythonInterpreter, String> {
        let root = &self.project_root;

        // 1. 检查内置绿色便携运行包 (runtime/)
        #[cfg(target_os = "windows")]
        let embedded_python = root.join("runtime").join("python.exe");
        #[cfg(not(target_os = "windows"))]
        let embedded_python = root.join("runtime").join("bin").join("python3");

        if embedded_python.exists() {
            info!("Found embedded Python runtime: {:?}", embedded_python);
            return Ok(PythonInterpreter {
                path: embedded_python,
                is_uv: false,
            });
        }

        // 2. 检查项目专属虚拟环境 (.venv)
        #[cfg(target_os = "windows")]
        let venv_python = root.join(".venv").join("Scripts").join("python.exe");
        #[cfg(not(target_os = "windows"))]
        let venv_python = root.join(".venv").join("bin").join("python3");

        if venv_python.exists() {
            info!("Found .venv Python runtime: {:?}", venv_python);
            return Ok(PythonInterpreter {
                path: venv_python,
                is_uv: false,
            });
        }

        // 3. 检查备用虚拟环境 (venv)
        #[cfg(target_os = "windows")]
        let alt_venv = root.join("venv").join("Scripts").join("python.exe");
        #[cfg(not(target_os = "windows"))]
        let alt_venv = root.join("venv").join("bin").join("python3");

        if alt_venv.exists() {
            info!("Found venv Python runtime: {:?}", alt_venv);
            return Ok(PythonInterpreter {
                path: alt_venv,
                is_uv: false,
            });
        }

        // 4. 检查常见安装路径下的 uv
        #[cfg(not(target_os = "windows"))]
        if let Some(home) = Self::get_user_home() {
            let direct_uvs = [
                home.join(".local").join("bin").join("uv"),
                home.join(".cargo").join("bin").join("uv"),
                PathBuf::from("/opt/homebrew/bin/uv"),
                PathBuf::from("/usr/local/bin/uv"),
            ];
            for uv_path in direct_uvs {
                if uv_path.exists() {
                    info!("Found uv at direct path: {:?}", uv_path);
                    return Ok(PythonInterpreter {
                        path: uv_path,
                        is_uv: true,
                    });
                }
            }
        }

        // 5. 检查系统 PATH 中是否安装了 uv
        if Self::check_command_exists("uv") {
            info!("Found uv in PATH, will use `uv run python`");
            return Ok(PythonInterpreter {
                path: PathBuf::from("uv"),
                is_uv: true,
            });
        }

        // 6. 检查系统 PATH 中的 python3 / python
        #[cfg(not(target_os = "windows"))]
        if Self::check_command_exists("python3") {
            return Ok(PythonInterpreter {
                path: PathBuf::from("python3"),
                is_uv: false,
            });
        }

        if Self::check_command_exists("python") {
            return Ok(PythonInterpreter {
                path: PathBuf::from("python"),
                is_uv: false,
            });
        }

        Err("未在系统中找到可用的 Python 环境（请安装 Python 3.9+ 或 uv，或配置内置 runtime 目录）".to_string())
    }

    fn check_command_exists(cmd: &str) -> bool {
        #[cfg(target_os = "windows")]
        let mut test_cmd = {
            let mut c = Command::new("where");
            c.arg(cmd);
            use std::os::windows::process::CommandExt;
            c.creation_flags(0x08000000);
            c
        };

        #[cfg(not(target_os = "windows"))]
        let mut test_cmd = {
            let mut c = Command::new("which");
            c.arg(cmd);
            c.env("PATH", Self::get_enhanced_path());
            c
        };

        test_cmd.output().map(|out| out.status.success()).unwrap_or(false)
    }

    /// 检测本地健康检查端点
    pub fn check_health(host: &str, port: u16) -> bool {
        let url = format!("http://{}:{}/api/health", host, port);
        match ureq::get(&url).timeout(Duration::from_millis(1500)).call() {
            Ok(resp) => resp.status() == 200,
            Err(_) => false,
        }
    }

    /// 获取当前服务运行状态
    pub fn get_status(&self) -> BackendStatus {
        let running = Self::check_health(&self.host, self.port);
        let pid = {
            let lock = self.child.lock().unwrap();
            lock.as_ref().map(|c| c.id())
        };

        let message = if running {
            if pid.is_some() {
                "本地后端引擎正在稳定运行".to_string()
            } else {
                "已连接到现有本地服务实例".to_string()
            }
        } else {
            "本地后端引擎未启动".to_string()
        };

        let error = {
            let lock = self.last_error.lock().unwrap();
            lock.clone()
        };

        BackendStatus {
            is_running: running,
            host: self.host.clone(),
            port: self.port,
            pid,
            message,
            error,
        }
    }

    /// 启动 Python 后端服务（无终端黑框）
    pub fn start(&self) -> Result<(), String> {
        let res = self.start_inner();
        if let Err(ref e) = res {
            let mut lock = self.last_error.lock().unwrap();
            *lock = Some(e.clone());
        } else {
            let mut lock = self.last_error.lock().unwrap();
            *lock = None;
        }
        res
    }

    fn start_inner(&self) -> Result<(), String> {
        // 如果服务已经在健康运行，则直接复用
        if Self::check_health(&self.host, self.port) {
            info!("Backend already responding on {}:{}, skipping spawn", self.host, self.port);
            return Ok(());
        }

        let python = self.find_python()?;
        let app_py = self.project_root.join("backend").join("app.py");

        if !app_py.exists() {
            return Err(format!("找不到启动脚本 backend/app.py: {:?}", app_py));
        }

        info!("Spawning backend with {:?} at {:?}", python, app_py);

        let mut cmd = if python.is_uv {
            let mut c = Command::new(&python.path);
            c.arg("run").arg("python").arg("backend/app.py");
            c
        } else {
            let mut c = Command::new(&python.path);
            c.arg("backend/app.py");
            c
        };

        let data_dir = self.get_data_dir();
        let logs_dir = self.get_logs_dir();
        let _ = std::fs::create_dir_all(&data_dir);
        let _ = std::fs::create_dir_all(&logs_dir);

        cmd.current_dir(&self.project_root);
        cmd.env("PATH", Self::get_enhanced_path());
        cmd.env("PYTHONUNBUFFERED", "1");
        cmd.env("REDINK_ROOT", &self.project_root);
        cmd.env("REDINK_DATA_DIR", &data_dir);
        cmd.env("REDINK_LOGS_DIR", &logs_dir);
        cmd.env("REDINK_HOST", &self.host);
        cmd.env("REDINK_PORT", self.port.to_string());
        cmd.env("REDINK_DEBUG", "0");
        cmd.env("APP_ENV", "production");

        // 当运行于 macOS app bundle 只读资源目录时，重定向虚拟环境至用户数据目录
        if self.project_root.to_string_lossy().contains(".app/Contents") {
            let venv_dir = data_dir.join(".venv");
            cmd.env("UV_PROJECT_ENVIRONMENT", &venv_dir);
        }

        #[cfg(target_os = "windows")]
        {
            use std::os::windows::process::CommandExt;
            // 0x08000000: CREATE_NO_WINDOW (禁止弹出 cmd 控制台黑框)
            cmd.creation_flags(0x08000000);
        }

        let child = cmd
            .spawn()
            .map_err(|e| format!("启动 Python 进程失败: {}", e))?;

        let pid = child.id();
        info!("Spawned Python backend (PID: {})", pid);

        {
            let mut lock = self.child.lock().unwrap();
            *lock = Some(child);
        }

        // 轮询等待健康检查就绪（最多等待 30 秒）
        let start_time = std::time::Instant::now();
        let timeout = Duration::from_secs(30);

        while start_time.elapsed() < timeout {
            std::thread::sleep(Duration::from_millis(600));

            if Self::check_health(&self.host, self.port) {
                info!("Backend is ready and healthy at http://{}:{}", self.host, self.port);
                return Ok(());
            }

            // 检查子进程是否意外异常退出了
            let mut lock = self.child.lock().unwrap();
            if let Some(ref mut c) = *lock {
                match c.try_wait() {
                    Ok(Some(status)) => {
                        error!("Python backend exited unexpectedly with status: {}", status);
                        return Err(format!("Python 后端异常退出 (状态码: {})，请检查依赖或日志", status));
                    }
                    Ok(None) => {}
                    Err(e) => {
                        warn!("Error checking process status: {}", e);
                    }
                }
            }
        }

        Err(format!("等待服务启动超时（30秒内未在 {}:{} 探活成功）", self.host, self.port))
    }

    /// 停止 Python 后端子进程
    pub fn stop(&self) {
        let mut lock = self.child.lock().unwrap();
        if let Some(mut child) = lock.take() {
            info!("Terminating Python backend PID: {}", child.id());
            let _ = child.kill();
            let _ = child.wait();
            info!("Python backend terminated");
        }
    }

    /// 重启服务
    pub fn restart(&self) -> Result<(), String> {
        self.stop();
        std::thread::sleep(Duration::from_millis(800));
        self.start()
    }
}
