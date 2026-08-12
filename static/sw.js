const CACHE_NAME = 'charvak-v2';
const urlsToCache = ['/', '/static/css/style.css', '/static/js/main.js'];

self.addEventListener('install', event => {
    event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache)));
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(caches.keys().then(keys => 
        Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ));
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => response || fetch(event.request))
    );
});

// Push Notification Support
self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    const options = {
        body: data.body || 'New update from Charvak',
        icon: '/static/images/logo.png',
        badge: '/static/images/logo.png',
        data: { url: data.url || '/' }
    };
    event.waitUntil(self.registration.showNotification(data.title || 'Charvak IT Consulting', options));
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(clients.openWindow(event.notification.data.url));
});