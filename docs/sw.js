// Ouverture instantanée : tout est servi depuis le cache du téléphone, puis rafraîchi en
// arrière-plan (« stale-while-revalidate »). Quand de nouvelles séances arrivent, on prévient
// la page, qui se met à jour toute seule. Hors ligne, l'appli marche avec la dernière copie.
const CACHE = "seances-v8";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "data/showtimes.json"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

// Version d'une réponse : ETag (GitHub Pages en fournit un), sinon date et taille.
const version = res => res && (res.headers.get("etag") || `${res.headers.get("last-modified")}|${res.headers.get("content-length")}`);

self.addEventListener("fetch", e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return;
  const isData = url.pathname.endsWith("/data/showtimes.json");
  const key = req.mode === "navigate" ? "./" : url.pathname + (isData ? "" : url.search);
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(key, { ignoreSearch: req.mode === "navigate" || isData });
    const network = fetch(req, isData ? { cache: "no-cache" } : undefined).then(async res => {
      if (res.ok) {
        await cache.put(key, res.clone());
        if (isData && cached && version(cached) !== version(res)) {
          for (const c of await self.clients.matchAll()) c.postMessage({ type: "data-updated" });
        }
      }
      return res;
    });
    e.waitUntil(network.catch(() => {}));
    return cached || network;
  })());
});
