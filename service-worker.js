const CACHE='bid-insight-v10';
const ASSETS=['./','index.html','styles.css','app.js','data.js','manifest.webmanifest','icon.svg','landing-desktop.png','landing-mobile.png'];

self.addEventListener('install',e=>{
  e.waitUntil(
    caches.open(CACHE)
      .then(c=>c.addAll(ASSETS))
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

  // 페이지 이동/F5는 항상 서버의 최신 라우팅을 먼저 확인한다.
  if(e.request.mode==='navigate'){
    e.respondWith(
      fetch(e.request)
        .then(resp=>resp)
        .catch(()=>caches.match('./'))
    );
    return;
  }

  // 정적 자산은 캐시 우선. 정상 응답만 캐시에 저장한다.
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
