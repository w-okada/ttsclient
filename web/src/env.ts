declare global {
  interface Window {
    colab_server?: number;
    colab_server_port?: number;
    electronAPI?: unknown;
  }
}

export const isDesktopApp = (): boolean =>
  navigator.userAgent.includes("Electron");

export const isColabEnv = (): boolean =>
  window.colab_server === 1;

export const getServerBaseUrl = (): string => {
  if (window.colab_server_port) {
    return `https://localhost:${window.colab_server_port}`;
  }
  return "";
};

export const useFlatPath = (): boolean =>
  isColabEnv();

/**
 * Generates the correct proxy path for file access.
 * In Colab environments, all file access goes through /get_proxy.
 * In normal environments, files are accessed directly.
 */
export const getProxyPath = (path: string): string => {
  const base = getServerBaseUrl();
  if (useFlatPath()) {
    return `${base}/get_proxy?path=${encodeURIComponent(path)}`;
  }
  return `${base}/get_proxy?path=${encodeURIComponent(path)}`;
};
