self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', () => self.clients.claim());
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('execute-api.amazonaws.com')) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
