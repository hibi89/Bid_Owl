const CACHE='bid-insight-v12-editorial';
const CORE=['./','index.html','styles.css','editorial.css','app.js','data.js','manifest.webmanifest','icon.svg','assets/bid-hero.png','assets/bid-smartcity.png','assets/bid-digital.png','assets/bid-green.png','assets/bid-construction.png','assets/bid-ai.png','assets/bid-safety.png'];

self.addEventListener('install',e=>{
  e.waitUntil(
    caches.open(CACHE)
      .then(c=>c.addAll(CORE))
      .then(()=>self.skipWaiting())
  );
});

self.addEventListener('activate',e=>{
  e.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const url=new URL(e.request.url);
  if(url.origin!==self.location.origin) return;

  const networkFirst=()=>{
    return fetch(e.request,{cache:'no-store'}).then(resp=>{
      if(resp && resp.ok){
        const copy=resp.clone();
        caches.open(CACHE).then(c=>c.put(e.request,copy));
      }
      return resp;
    }).catch(()=>caches.match(e.request).then(r=>r||caches.match('./')));
  };

  // HTML navigation and core app assets must prefer the newest deployment.
  if(e.request.mode==='navigate' ||
     e.request.destination==='style' ||
     e.request.destination==='script' ||
     /\.(?:css|js|json|webmanifest)$/.test(url.pathname)){
    e.respondWith(networkFirst());
    return;
  }

  // Heavy/static media can stay cache-first.
  e.respondWith(
    caches.match(e.request).then(cached=>{
      if(cached) return cached;
      return fetch(e.request).then(resp=>{
        if(resp && resp.ok){
          const copy=resp.clone();
          caches.open(CACHE).then(c=>c.put(e.request,copy));
        }
        return resp;
      });
    })
  );
});
