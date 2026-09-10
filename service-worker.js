const CACHE_NAME = 'cyberdoom-v2-autoplay';
const FILES_TO_CACHE = ['./', './index.html', './manifest.json', './autoplay.js', './autoplay.css', './icon-192.png', './icon-512.png'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(FILES_TO_CACHE)));
  // A new worker activates after existing game tabs close, avoiding a mixed-version run.
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys
    .filter(key => key.startsWith('cyberdoom-') && key !== CACHE_NAME)
    .map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  if(event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(caches.open(CACHE_NAME).then(async cache => {
    const cached = await cache.match(event.request);
    if(cached) return cached;
    try { return await fetch(event.request); }
    catch(error) {
      if(event.request.mode === 'navigate') return cache.match('./index.html');
      throw error;
    }
  }));
});
