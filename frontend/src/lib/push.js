import { API } from "./api";
import { deviceId } from "./device";

const b64ToUint8 = (s) => {
  const pad = "=".repeat((4 - (s.length % 4)) % 4);
  const raw = atob((s + pad).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
};

export const pushSupported = () => "serviceWorker" in navigator && "PushManager" in window;

export const enablePush = async () => {
  if (!pushSupported()) {
    return { ok: false, message: "Su iPhone aggiungi prima l'app alla schermata Home, poi attiva le notifiche." };
  }
  const permission = await Notification.requestPermission();
  if (permission !== "granted") return { ok: false, message: "Notifiche negate dal browser." };

  let reg = await navigator.serviceWorker.getRegistration();
  if (!reg) {
    try { reg = await navigator.serviceWorker.register("/sw.js"); } catch (e) { return { ok: false, message: "Service worker non disponibile in preview. Pubblica l'app e riprova." }; }
  }
  const { public_key } = await fetch(`${API}/push/public-key`).then((r) => r.json());
  if (!public_key) return { ok: false, message: "Chiave VAPID mancante" };
  const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64ToUint8(public_key) });
  await fetch(`${API}/push/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...sub.toJSON(), device_id: deviceId() }),
  });
  localStorage.setItem("flashpulse-push-enabled", "1");
  return { ok: true };
};

export const disablePush = async () => {
  const reg = await navigator.serviceWorker.getRegistration();
  const sub = await reg?.pushManager.getSubscription();
  if (sub) {
    await fetch(`${API}/push/unsubscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ endpoint: sub.endpoint }),
    }).catch(() => {});
    await sub.unsubscribe().catch(() => {});
  }
  localStorage.setItem("flashpulse-push-enabled", "0");
  return { ok: true };
};

export const sendPushTest = async () => {
  return fetch(`${API}/push/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ device_id: deviceId() }),
  }).then((r) => r.json());
};

export const pushEnabledLocal = () =>
  localStorage.getItem("flashpulse-push-enabled") === "1" && (typeof Notification === "undefined" || Notification.permission === "granted");
