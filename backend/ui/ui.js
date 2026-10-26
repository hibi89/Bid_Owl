'use strict';
// No external resources and no HTML interpolation of user-supplied bid content.
const $ = (id) => document.getElementById(id);
const state = {page: 1, pages: 1, seq: 0, focus: null, items: [], favorites: new Set()};
const themes = new Set(['cloud','obsidian','midnight','graphite','emerald','sand','iris']);
const key = (bid) => JSON.stringify([bid.source_id, bid.bid_no]);
const money = (n) => Number.isSafeInteger(n) ? n.toLocaleString('ko-KR') : '정보 없음';
const date = (v) => {if (!v) return '정보 없음'; const d = new Date(v); return Number.isNaN(d.getTime()) ? '날짜 확인 필요' : d.toLocaleString('ko-KR',{year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});};
const node = (tag, className, content) => {const el=document.createElement(tag); if(className) el.className=className; if(content!==undefined) el.textContent=String(content); return el;};
function loadPreferences(){
  try{const current=localStorage.getItem('bidowl-theme'); if(themes.has(current)) $('theme').value=current;
    const parsed=JSON.parse(localStorage.getItem('bidowl-favorites')||'[]'); if(Array.isArray(parsed)) state.favorites=new Set(parsed.filter(x=>typeof x==='string').slice(0,20000));}
  catch{state.favorites=new Set();}
  document.body.dataset.theme=$('theme').value;
}
function saveFavorites(){try{localStorage.setItem('bidowl-favorites', JSON.stringify([...state.favorites]));}catch{note('브라우저 저장 기능이 비활성화되어 관심 공고가 다음 실행에 유지되지 않을 수 있습니다.',true);}}
async function request(path,options={}){const response=await fetch(path, {cache:'no-store',...options}); const result=await response.json(); if(!response.ok) throw Error(result.error||'조회 실패'); return result;}
function note(message,error=false){$('notice').textContent=message; $('notice').classList.toggle('error',error);}
function badge(value){return node('span','badge '+value,value);}
function params(){const query=new URLSearchParams();for(const id of ['search','category','status','deadline','profile']){const val=$(id).value.trim();if(val) query.set(id==='search'?'q':id,val);}query.set('page',String(state.page));query.set('page_size','30');return query;}
function favoritePairs(){
  if(state.favorites.size>1000)throw Error('관심 공고 조회는 최대 1,000건까지 지원합니다. 기존 저장값을 정리해 주세요.');
  return [...state.favorites].map(value=>{
    let pair;try{pair=JSON.parse(value);}catch{throw Error('저장된 관심 공고 식별자가 올바르지 않습니다.');}
    if(!Array.isArray(pair)||pair.length!==2||pair.some(s=>typeof s!=='string'||!s.trim()||s.length>300))throw Error('저장된 관심 공고 식별자가 올바르지 않습니다.');
    return pair;
  });
}
function findBids(){
  const query=params();
  if(!$('only-favorites').checked)return request('/api/bids?'+query.toString());
  return request('/api/bids/favorites',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({favorites:favoritePairs(),filters:Object.fromEntries(query)})
  });
}
function rowFor(item){
  const tr=node('tr'); const favCell=node('td');const fav=node('button','favorite'+(state.favorites.has(key(item))?' active':''),state.favorites.has(key(item))?'★':'☆');
  fav.type='button';fav.setAttribute('aria-label',state.favorites.has(key(item))?'관심 공고 해제':'관심 공고 등록');fav.setAttribute('aria-pressed',String(state.favorites.has(key(item))));
  fav.addEventListener('click',()=>{const id=key(item);if(state.favorites.has(id))state.favorites.delete(id);else if(state.favorites.size>=1000){note('관심 공고 저장 상한은 1,000건입니다.',true);return;}else state.favorites.add(id);saveFavorites();loadBids();});favCell.append(fav);tr.append(favCell);
  const first=node('td');const link=node('button','bid-link',item.title||'(제목 없음)');link.type='button';link.addEventListener('click',()=>openDetail(item,link));first.append(link,node('div','subline',item.agency+' · '+item.source_id+' / '+item.bid_no));tr.append(first);
  tr.append(node('td','',item.category),node('td','mono',date(item.deadline)));
  const eligibility=node('td');eligibility.append(badge(item.status));
  if(item.review_reason) eligibility.append(node('div','subline',item.review_reason));
  if(item.expired) eligibility.append(node('div','subline','마감 지남'));
  tr.append(eligibility,node('td','mono',money(item.budget)));return tr;
}
async function loadBids(){
  const seq=++state.seq;note('조회 중…');
  try{const data=await findBids();if(seq!==state.seq)return;
    const totalPages=Math.max(1,Math.ceil(data.total/data.page_size));
    if(state.page>totalPages){state.page=totalPages;return loadBids();}
    const body=$('results');body.replaceChildren();state.items=data.items;state.pages=Math.max(1,Math.ceil(data.total/data.page_size));
    for(const item of data.items) body.append(rowFor(item));
    if(!data.items.length){const cell=node('td','', '조건에 맞는 공고가 없습니다.');cell.colSpan=6;const tr=node('tr');tr.append(cell);body.append(tr);}
    $('count').textContent=data.total.toLocaleString('ko-KR')+'건';$('refreshed').textContent=date(data.generated_at);
    $('page').textContent=state.page+' / '+state.pages;$('prev').disabled=state.page<=1;$('next').disabled=state.page>=state.pages;
    const category=$('category');const selection=category.value;category.replaceChildren(new Option('전체 분야',''));
    for(const item of data.categories) category.add(new Option(item,item));category.value=selection;
    note($('only-favorites').checked?'저장된 전체 공고에서 관심 항목을 검색·필터·페이지 이동합니다.':'실시간 API가 아닌 PC의 저장 DB 조회 결과입니다.');
  }catch(err){if(seq!==state.seq)return;note('조회 오류: '+err.message,true);$('results').replaceChildren();$('count').textContent='오류';}
}
function definition(container,label,value){container.append(node('dt','',label),node('dd','',value===null||value===undefined?'정보 없음':String(value)));}
async function openDetail(item,button){state.focus=button;$('drawer').hidden=false;$('overlay').hidden=false;document.body.classList.add('drawer-open');$('detail-content').replaceChildren(node('p','','근거를 조회하고 있습니다.'));$('drawer').focus();
  try{const query=new URLSearchParams({source_id:item.source_id,bid_no:item.bid_no,profile:$('profile').value});const data=await request('/api/detail?'+query.toString());
    const host=$('detail-content');host.replaceChildren();host.append(node('h2','',data.bid.title));const dl=node('dl');
    for(const [label,val] of [['공고번호',data.bid.bid_no],['기관',data.bid.agency],['분야',data.bid.category],['예산',money(data.bid.budget)+' 원'],['마감',date(data.bid.deadline)],['데이터 기준',date(data.bid.data_as_of)],['평가 시점',date(data.bid.checked_at)],['선택된 회사',data.bid.profile_id],['공고 원문 정보',data.bid.source_ref],['저장본 버전',data.bid.bid_version]])definition(dl,label,val);host.append(dl);
    const statusline=node('div','');statusline.append(badge(data.bid.status));statusline.append(node('span','subline','  · 최신 평가 기준 표시'));host.append(statusline);
    if(!data.evidence_is_current)host.append(node('p','warn',data.bid.review_reason+' · 과거 평가를 PASS로 간주하지 않습니다.'));
    host.append(node('h3','','조건별 판정 근거'));
    if(!data.rules.length)host.append(node('p','','저장된 세부 평가가 없습니다. CLI에서 해당 공고·프로필을 평가해야 합니다.'));
    for(const rule of data.rules){const box=node('section','rule');const heading=node('div');heading.append(badge(rule.status),node('strong','', '  '+rule.rule_id+' · '+rule.kind));box.append(heading,node('p','',rule.explanation),node('div','subline',rule.reason_code));
      if(rule.source_text)box.append(node('div','source',rule.source_text));if(rule.source_locator)box.append(node('div','subline','출처 위치: '+rule.source_locator));host.append(box);}
    host.append(node('p','disclaimer',data.notice));
  }catch(err){$('detail-content').replaceChildren(node('p','warn','근거 조회 오류: '+err.message));}
}
function closeDetail(){$('drawer').hidden=true;$('overlay').hidden=true;document.body.classList.remove('drawer-open');if(state.focus?.isConnected)state.focus.focus();}
async function loadProfiles(){try{const data=await request('/api/profiles');for(const p of data.profiles)$('profile').add(new Option(p.profile_id+' (v'+p.version+')',p.profile_id));}catch{note('회사 프로필 목록 조회 실패',true);}}
let delay;
for(const id of ['category','status','deadline','profile','only-favorites'])$(id).addEventListener('change',()=>{state.page=1;loadBids();});
$('search').addEventListener('input',()=>{clearTimeout(delay);delay=setTimeout(()=>{state.page=1;loadBids();},230);});
$('prev').addEventListener('click',()=>{if(state.page>1){state.page--;loadBids();}});
$('next').addEventListener('click',()=>{if(state.page<state.pages){state.page++;loadBids();}});
$('theme').addEventListener('change',()=>{const val=$('theme').value;if(themes.has(val)){document.body.dataset.theme=val;try{localStorage.setItem('bidowl-theme',val);}catch{}}});
$('close').addEventListener('click',closeDetail);$('overlay').addEventListener('click',closeDetail);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('drawer').hidden)closeDetail();if(e.key==='Tab'&&!$('drawer').hidden){const x=$('drawer').querySelectorAll('button:not([disabled]),a[href],input,select');if(!x.length)return;const first=x[0],last=x[x.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}});
loadPreferences();loadProfiles().then(loadBids);