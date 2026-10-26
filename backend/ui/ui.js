'use strict';
// No external resources and no HTML interpolation of user-supplied bid content.
const $ = (id) => document.getElementById(id);
const state = {page: 1, pages: 1, seq: 0, drawerSeq: 0, focus: null, items: [], favorites: new Set()};
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
    if(data.items.some(item=>item.source_id==='BIDOWL_SYNTHETIC_DEMO'))$('demo-indicator').hidden=false;
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
async function openDetail(item,button){const token=++state.drawerSeq;state.focus=button;$('drawer').hidden=false;$('overlay').hidden=false;document.body.classList.add('drawer-open');$('detail-content').replaceChildren(node('p','','근거를 조회하고 있습니다.'));$('drawer').focus();
  try{const query=new URLSearchParams({source_id:item.source_id,bid_no:item.bid_no,profile:$('profile').value});const data=await request('/api/detail?'+query.toString());
    if(token!==state.drawerSeq||$('drawer').hidden)return;
    const host=$('detail-content');host.replaceChildren();const heading=node('h2','',data.bid.title);heading.id='detail-title';host.append(heading);const dl=node('dl');
    for(const [label,val] of [['공고번호',data.bid.bid_no],['기관',data.bid.agency],['분야',data.bid.category],['예산',money(data.bid.budget)+' 원'],['마감',date(data.bid.deadline)],['데이터 기준',date(data.bid.data_as_of)],['평가 시점',date(data.bid.checked_at)],['선택된 회사',data.bid.profile_id],['공고 원문 정보',data.bid.source_ref],['저장본 버전',data.bid.bid_version]])definition(dl,label,val);host.append(dl);
    const statusline=node('div','');statusline.append(badge(data.bid.status));statusline.append(node('span','subline','  · 저장본 판정 / 버전 일치 여부 확인'));host.append(statusline);
    if(!data.evidence_is_current)host.append(node('p','warn',data.bid.review_reason+' · 과거 평가를 PASS로 간주하지 않습니다.'));
    host.append(node('h3','','조건별 판정 근거'));
    if(!data.rules.length)host.append(node('p','','저장된 세부 평가가 없습니다. CLI에서 해당 공고·프로필을 평가해야 합니다.'));
    for(const rule of data.rules){const box=node('section','rule');const heading=node('div');heading.append(badge(rule.status),node('strong','', '  '+rule.rule_id+' · '+rule.kind));box.append(heading,node('p','',rule.explanation),node('div','subline',rule.reason_code));
      if(rule.source_text)box.append(node('div','source',rule.source_text));if(rule.source_locator)box.append(node('div','subline','출처 위치: '+rule.source_locator));host.append(box);}
    if(Number.isSafeInteger(data.bid.assessment_id)&&data.bid.assessment_id>0){
      const snapshotId=data.bid.assessment_id;
      host.append(node('h3','','저장된 평가 보고서'));
      host.append(node('p','subline','평가 ID '+snapshotId+' · 조회 중인 평가의 과거 스냅샷으로 출력합니다. DB와 평가 기록은 바뀌지 않습니다.'));
      const href='/api/report?'+new URLSearchParams({assessment_id:String(snapshotId)});
      const download=node('a','report-download','Excel (.xlsx) 직접 다운로드');
      download.href=href;download.download='bidowl_review_'+String(snapshotId).padStart(8,'0')+'.xlsx';
      host.append(download);
      if(!data.evidence_is_current)host.append(node('p','warn','이 평가는 과거 버전입니다. 출력 보고서의 PASS/FAIL은 현재 참가 자격을 뜻하지 않습니다.'));
      const command='python report_existing.py --db "DB_PATH" --assessment-id '+snapshotId+' --output "NEW_REPORT_DIR" --format both';
      host.append(node('pre','command',command),node('p','subline','backend 폴더에서 실행하세요. DB_PATH와 새 출력 폴더 경로를 실제 로컬 경로로 바꿔야 합니다.'));
    }else{
      host.append(node('p','subline','저장된 평가 기록이 없어 보고서를 출력할 수 없습니다. 먼저 로컬 CLI에서 공고를 평가해야 합니다.'));
    }
    host.append(node('p','disclaimer',data.notice));
  }catch(err){if(token===state.drawerSeq&&!$('drawer').hidden)$('detail-content').replaceChildren(node('p','warn','근거 조회 오류: '+err.message));}
}

function field(form,label,value,type='text'){
  const box=node('label','profile-field',label); const control=node('input');
  control.type=type;control.value=value===null||value===undefined?'':String(value);
  if(type==='text')control.maxLength=300;
  box.append(control);form.append(box);return control;
}
function listField(form,label,current){
  const box=node('label','profile-field',label);
  const mode=node('select');mode.setAttribute('aria-label',label+' 입력 상태');
  for(const [text,val] of [['정보 없음 (UNKNOWN)','unknown'],['없음이 확인됨','empty'],['목록 입력','values']])mode.add(new Option(text,val));
  const value=node('input');value.type='text';value.placeholder='쉼표로 구분하여 입력';value.maxLength=8192;
  mode.value=current===null?'unknown':current.length?'values':'empty';
  if(Array.isArray(current))value.value=current.join(', ');
  const change=()=>{value.disabled=mode.value!=='values';};mode.addEventListener('change',change);change();
  box.append(mode,value);form.append(box);return {mode,value};
}
function profileList(field){
  if(field.mode.value==='unknown')return null;
  if(field.mode.value==='empty')return [];
  const items=field.value.value.split(',').map(x=>x.trim()).filter(Boolean);
  if(!items.length||items.length>100||items.some(x=>x.length>300)||new Set(items).size!==items.length){
    throw Error('목록은 중복 없는 1~100개 항목을 쉼표로 구분해 입력하세요.');
  }
  return items;
}
function profileNumber(input,name){
  const value=input.value.trim();if(!value)return null;
  if(!/^(0|[1-9][0-9]*)$/.test(value))throw Error(name+'은 음수가 아닌 정수여야 합니다.');
  const parsed=Number(value);
  if(!Number.isSafeInteger(parsed))throw Error(name+'의 숫자가 너무 큽니다.');
  return parsed;
}
async function openProfileEditor(button,creating=false){
  const token=++state.drawerSeq;
  const id=$('profile').value;
  if(!creating&&!id){note('먼저 편집할 회사 프로필을 선택하세요.',true);$('profile').focus();return;}
  state.focus=button;$('drawer').hidden=false;$('overlay').hidden=false;document.body.classList.add('drawer-open');
  $('detail-content').replaceChildren(node('p','','저장된 회사 프로필을 읽고 있습니다.'));$('drawer').focus();
  try{
    const data=creating?
      {profile:{profile_id:'',region:null,categories:null,licenses:null,staff_count:null,experience_total_krw:null},version:0}:
      await request('/api/profile?'+new URLSearchParams({profile_id:id}).toString());
    if(token!==state.drawerSeq||$('drawer').hidden)return;
    const p=data.profile,host=$('detail-content');host.replaceChildren();
    const heading=node('h2','',creating?'새 회사 프로필 입력 파일':'회사 프로필 편집 파일');heading.id='detail-title';host.append(heading);
    host.append(node('p','warn','이 화면에서는 SQLite를 직접 수정하지 않습니다. JSON을 내려받은 뒤 로컬 명령으로 변경을 적용해야 합니다. 먼저 미리보기 결과를 확인하세요.'));
    const form=node('form','profile-form');
    const pid=creating?field(form,'새 회사 프로필 ID',p.profile_id):
      node('p','', '프로필 ID: '+p.profile_id+' · 현재 버전 '+data.version);
    if(!creating)form.append(pid);
    const region=field(form,'사업장 소재지',p.region);
    const categories=listField(form,'업종 / 카테고리',p.categories);
    const licenses=listField(form,'면허 / 자격',p.licenses);
    const staff=field(form,'인력 수',p.staff_count,'text');
    const experience=field(form,'실적 합계 (KRW)',p.experience_total_krw,'text');
    const message=node('p','subline','정보가 불명확하면 빈칸 또는 정보 없음으로 유지하세요. 임의로 PASS를 만들지 마세요.');
    form.append(message);
    const download=node('button','','편집 JSON 내려받기');download.type='submit';form.append(download);
    const result=node('p','', '');result.setAttribute('role','status');form.append(result);
    form.addEventListener('submit',(event)=>{
      event.preventDefault();
      try{
        const rawRegion=region.value.trim();
        const chosenId=creating?pid.value.trim():p.profile_id;
        if(!chosenId||chosenId.length>300)throw Error('회사 프로필 ID를 1~300자로 입력하세요.');
        const profile={profile_id:chosenId,region:rawRegion||null,
          categories:profileList(categories),licenses:profileList(licenses),
          staff_count:profileNumber(staff,'인력 수'),experience_total_krw:profileNumber(experience,'실적 합계')};
        const content=JSON.stringify(profile,null,2);
        const filename='bidowl_profile_'+chosenId.replace(/[^a-zA-Z0-9_-]/g,'_').slice(0,60)+'.json';
        const href=URL.createObjectURL(new Blob([content],{type:'application/json;charset=utf-8'}));
        const a=node('a');a.href=href;a.download=filename;document.body.append(a);a.click();a.remove();
        setTimeout(()=>URL.revokeObjectURL(href),1000);
        result.textContent='JSON 파일을 생성했습니다. 파일을 저장한 후 아래 명령으로 미리보기 및 적용을 진행하세요.';
      }catch(err){result.textContent='입력 오류: '+err.message;}
    });
    host.append(form,node('h3','','로컬 명령으로 적용하기'));
    const command='python profile_workflow.py --db "DB_PATH" --profile-file "'+
      'DOWNLOADED_JSON" '+(creating?'--create':'--expected-version '+data.version)+' --reassess';
    const apply=command+' --apply --backup "NEW_BACKUP_PATH.sqlite3"';
    host.append(node('p','','① 먼저 미리보기 (DB 수정 없음)'),node('pre','command',command),
      node('p','','② 결과 확인 후 명시적으로 적용 (백업 필수)'),node('pre','command',apply),
      node('p','disclaimer','파일은 PC에만 저장됩니다. 명령의 DB_PATH/다운로드 경로/새 백업 경로를 실제 경로로 바꿔 실행하세요. 오류나 도중 중단 시 백업을 보존하세요.'));
  }catch(err){if(token===state.drawerSeq&&!$('drawer').hidden)$('detail-content').replaceChildren(node('p','warn','프로필 조회 실패: '+err.message));}
}

function closeDetail(){++state.drawerSeq;$('drawer').hidden=true;$('overlay').hidden=true;document.body.classList.remove('drawer-open');if(state.focus?.isConnected)state.focus.focus();}
async function loadProfiles(){try{const data=await request('/api/profiles');for(const p of data.profiles)$('profile').add(new Option(p.profile_id+' (v'+p.version+')',p.profile_id));}catch{note('회사 프로필 목록 조회 실패',true);}}
let delay;
for(const id of ['category','status','deadline','profile','only-favorites'])$(id).addEventListener('change',()=>{state.page=1;loadBids();});
$('search').addEventListener('input',()=>{clearTimeout(delay);delay=setTimeout(()=>{state.page=1;loadBids();},230);});
$('prev').addEventListener('click',()=>{if(state.page>1){state.page--;loadBids();}});
$('next').addEventListener('click',()=>{if(state.page<state.pages){state.page++;loadBids();}});
$('theme').addEventListener('change',()=>{const val=$('theme').value;if(themes.has(val)){document.body.dataset.theme=val;try{localStorage.setItem('bidowl-theme',val);}catch{}}});
$('edit-profile').addEventListener('click',()=>openProfileEditor($('edit-profile')));
$('create-profile').addEventListener('click',()=>openProfileEditor($('create-profile'),true));
$('close').addEventListener('click',closeDetail);$('overlay').addEventListener('click',closeDetail);
document.addEventListener('keydown',e=>{
  if($('drawer').hidden)return;
  if(e.key==='Escape'){e.preventDefault();closeDetail();return;}
  if(e.key!=='Tab')return;
  const controls=[...$('drawer').querySelectorAll('button:not([disabled]),a[href],input:not([disabled]),select:not([disabled])')].filter(el=>el.getClientRects().length);
  if(!controls.length){e.preventDefault();$('drawer').focus();return;}
  const first=controls[0],last=controls[controls.length-1];
  if(document.activeElement===$('drawer')||!$('drawer').contains(document.activeElement)){
    e.preventDefault();(e.shiftKey?last:first).focus();
  }else if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
  else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
});
loadPreferences();loadProfiles().then(loadBids);