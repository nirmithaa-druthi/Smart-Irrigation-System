const CACHE_NAME = "smart-irrigation-v1";

const APP_SHELL = [
  "/",
  "/manifest.json"
];

// Install
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );

  self.skipWaiting();
});

// Activate
self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

// Existing offline/cache behavior
self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});

// =========================================================
// WEB PUSH NOTIFICATIONS
// =========================================================

self.addEventListener("push", (event) => {
  let data = {
    title: "Smart Irrigation Alert",
    body: "You have a new irrigation alert.",
  };

  if (event.data) {
    try {
      data = event.data.json();
    } catch {
      data.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/icons/icon-192.png",
      badge: "/icons/icon-192.png",
      tag: "smart-irrigation-alert",
      data: {
        url: "/alerts",
      },
    })
  );
});

// Notification click
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  event.waitUntil(
    self.clients.matchAll({
      type: "window",
      includeUncontrolled: true,
    }).then((clientList) => {

      for (const client of clientList) {
        if ("focus" in client) {
          client.navigate("/alerts");
          return client.focus();
        }
      }

      return self.clients.openWindow("/alerts");
    })
  );
});