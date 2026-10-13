// Canonical fleet shape: same-origin relative ("") everywhere EXCEPT behind a
// Tauri gate. Absolute backend URLs work from localhost tabs only; any other
// hostname (LAN name, Tailscale MagicDNS) dies on CORS while curl "proves"
// the backend is healthy.
declare global {
  interface Window {
    __TAURI__?: unknown;
    __TAURI_INTERNALS__?: unknown;
  }
}

function isTauri(): boolean {
  if (typeof window === "undefined") return false;
  return (
    window.__TAURI__ !== undefined ||
    window.__TAURI_INTERNALS__ !== undefined ||
    window.location.hostname === "tauri.localhost"
  );
}

export const API_BASE: string = isTauri() ? "http://127.0.0.1:10811" : "";
