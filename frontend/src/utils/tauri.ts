import { isTauriEnvironment } from '../api';

export interface BackendStatus {
  is_running: boolean;
  host: string;
  port: number;
  pid?: number | null;
  message: string;
  error?: string | null;
}

export interface PlatformInfo {
  os: string;
  arch: string;
  version: string;
  app_name: string;
  auth_token?: string | null;
}

export { isTauriEnvironment };

export async function getBackendStatus(): Promise<BackendStatus | null> {
  if (!isTauriEnvironment()) return null;
  try {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke<BackendStatus>('get_backend_status');
  } catch (e) {
    console.error('Failed to get backend status from Tauri:', e);
    return null;
  }
}

export async function restartBackend(): Promise<BackendStatus | null> {
  if (!isTauriEnvironment()) return null;
  try {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke<BackendStatus>('restart_backend');
  } catch (e) {
    console.error('Failed to restart backend via Tauri:', e);
    throw e;
  }
}

export async function openDataFolder(): Promise<void> {
  if (!isTauriEnvironment()) return;
  const { invoke } = await import('@tauri-apps/api/core');
  await invoke('open_data_folder');
}

export async function openLogsFolder(): Promise<void> {
  if (!isTauriEnvironment()) return;
  const { invoke } = await import('@tauri-apps/api/core');
  await invoke('open_logs_folder');
}

export async function openExternalUrl(url: string): Promise<void> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('open_external_url', { url });
      return;
    } catch (e) {
      console.warn('Failed to open external url via Tauri, falling back to window.open', e);
    }
  }
  window.open(url, '_blank');
}

export async function getPlatformInfo(): Promise<PlatformInfo | null> {
  if (!isTauriEnvironment()) return null;
  try {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke<PlatformInfo>('get_platform_info');
  } catch (e) {
    return null;
  }
}
