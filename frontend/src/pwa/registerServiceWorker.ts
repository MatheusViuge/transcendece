export function registerServiceWorker() {
  if (import.meta.env.DEV || !("serviceWorker" in navigator)) return;

  window.addEventListener("load", () => {
    void navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {
      window.dispatchEvent(new CustomEvent("pwa:registration-error"));
    });
  });
}
