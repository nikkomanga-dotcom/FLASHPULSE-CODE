/* FlashPulse app-shell service worker */
const CACHE = "flashpulse-shell-v1";
const SHELL = ["/", "/manifest.json"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // Never cache API or cross-origin
  if (url.pathname.startsWith("/api") || url.origin !== self.location.origin) return;

  // Navigation: network first, fallback to cached root
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req).catch(() => caches.match("/"))
    );
    return;
  }

  // Static assets: stale-while-revalidate
  event.respondWith(
    caches.match(req).then((hit) => {
      const net = fetch(req).then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => hit);
      return hit || net;
    })
  );
});

self.addEventListener("push", (event) => {
  const d = event.data ? event.data.json() : {};
  event.waitUntil(self.registration.showNotification(d.title || "FlashPulse", {
    body: d.body,
    icon: "/icons/icon-192.png",
    badge: "/icons/icon-192.png",
    tag: "flashpulse-alert",
    data: { url: d.url || "/" },
  }));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data?.url || "/"));
});
