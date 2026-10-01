(() => {
  'use strict';
  const DATA = window.PROJECT08_DATA;
  const bids = DATA.bids;
  const summary = DATA.summary;
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => [...root.querySelectorAll(sel)];
  const state = {view:'dashboard', search:'', category:'all', grade:'all', risk:'all', favOnly:false, recSort:'score', favorites:new Set(JSON.parse(localStorage.getItem('bidFavorites')||'[]'))};

  const esc = s => String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const gradeClass = g => g === '적극추천' ? 'recommend' : g === '검토' ? 'review' : 'pass';
  const riskClass = r => r === 'HIGH' ? 'high' : 'medium';
  const LEVEL_KO = {HIGH:'높음', MEDIUM:'중간', LOW:'낮음'};
  const fmtBillion = won => {
    if (!Number.isFinite(won)) return '-';
    const eok = won / 1e8;
    if (eok >= 10000) return `${(eok/10000).toFixed(2)}조`;
    if (eok >= 1000) return `${eok.toLocaleString('ko-KR',{maximumFractionDigits:0})}억`;
    return `${eok.toLocaleString('ko-KR',{maximumFractionDigits:1})}억`;
  };
  const fmtPct = n => Number.isFinite(n) ? `${n.toFixed(1)}%` : '-';
  const dday = n => Number.isFinite(n) ? (n === 0 ? 'D-DAY' : n > 0 ? `D-${n}` : `D+${Math.abs(n)}`) : '-';
  const truncate = (s,n=30) => !s ? '' : (s.length > n ? s.slice(0,n-1)+'…' : s);

  /* 공통 색상 토큰 — CSS variable 단일 소스 (도넛·legend·badge 동일 사용) */
  const cssVar = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const GRADE_COLOR = {
    recommend: cssVar('--grade-recommend') || '#16815c',
    review: cssVar('--grade-review') || '#b07714',
    pass: cssVar('--grade-pass') || '#5d6f7d'
  };

  /* 화면 표시용 한글 라벨 (내부 key는 노출하지 않음) */
  const QA_AREA_KO = {parsing:'원문 파싱 충실도', eligibility:'자격 판정 논리', screening_scoring:'스크리닝·스코어링', recommendation_grounding:'추천 근거 타당성', simulation_sanity:'시뮬레이션 일관성'};
  const ASSUMPTION_KO = {
    monthly_cost_per_person:{label:'1인당 월 인건비', desc:'투입 인원 1명이 한 달에 발생시키는 인건비 가정'},
    revenue_per_person_month:{label:'1인당 월 수행규모 가정', desc:'한 명이 한 달 동안 담당한다고 가정한 사업규모'},
    other_cost_ratio:{label:'기타원가 비율', desc:'인건비 외 출장·장비·제경비 등의 원가 비중'},
    project_fixed_cost:{label:'프로젝트 고정비', desc:'기간·인원과 무관하게 고정으로 발생하는 비용'},
    wage_escalation:{label:'임금상승 보정', desc:'12개월 초과 기간에 연 5% 비례 적용'},
    staff_clamp:{label:'예상 투입인력 범위', desc:'시뮬레이션에서 허용되는 투입 인력의 상·하한'}
  };
  const DET_ITEMS = ['필수 필드 존재 여부','예산 값 양수 여부','수행기간 값 양수 여부','날짜 형식 정상 여부','D-Day 재계산 일치 여부','마감임박(3일 이내) 판정 일치 여부','마감 경과 여부 일치','최소 수주액 기준 판정 일치','자격조건 개수/구조 정상 여부','즉시 제외 사유 규칙 일치 여부','점수 합산 공식 일치 여부','등급 판정 일치 여부','즉시 제외 사유와 등급 상호작용 일치 여부','총원가 계산 일치 여부','예상이익 계산 일치 여부','마진율 계산 일치 여부','시뮬레이션 판단 중요도 판정 일치 여부'];

  function setView(view, opts={}) {
    state.view = view;
    $$('.view').forEach(el => el.classList.toggle('active', el.id === `view-${view}`));
    $$('[data-view]').forEach(btn => btn.classList.toggle('active', btn.dataset.view === view));
    window.scrollTo({top:0,behavior:'smooth'});
    if (view === 'search') renderSearch();
    if (view === 'recommend') renderRecommendationGrid();
    if (view === 'risk') renderRisk();
    if (view === 'simulation') renderSimulation();
    if (view === 'quality') renderQuality();
    if (opts.silent !== true) {
      if (view === 'dashboard') history.replaceState(null,'',location.pathname+location.search);
      else location.hash = view;
    }
  }

  function renderKPIs() {
    const cards = [
      {label:'적극추천', value:`${summary.grade_counts['적극추천']}건`, note:'지금 바로 검토할 핵심 기회', icon:'★', cls:'lead', jump:'recommend', jumpTitle:'추천 공고로 이동'},
      {label:'검토 필요', value:`${summary.grade_counts['검토']}건`, note:'담당자 확인 또는 보완 필요', icon:'▣', cls:'amber', jump:'search', jumpTitle:'공고 탐색에서 담당자 검토 필요 공고만 보기', gradeJump:'검토'},
      {label:'마감 임박', value:`${summary.urgent_count}건`, note:'3일 이내 마감', icon:'◷', cls:'alert', jump:'risk', jumpTitle:'리스크 관제로 이동'},
      {label:'분석 예산 총액', value:fmtBillion(summary.budget_total), note:'현재 20개 공고 기준', icon:'●', cls:'gold'},
      {label:'평균 예상 마진', value:fmtPct(summary.avg_margin), note:'가정값 기반 시뮬레이션', icon:'↗', cls:'teal', jump:'simulation', jumpTitle:'수익성 분석으로 이동'}
    ];
    $('#kpiGrid').innerHTML = cards.map(c => {
      const inner = `<div class="kpi-top"><span class="kpi-label">${c.label}</span><span class="kpi-icon">${c.icon}</span></div><div class="kpi-value">${c.value}</div><div class="kpi-note">${c.note}</div>`;
      return c.jump
        ? `<button type="button" class="kpi-card ${c.cls}" data-view-jump="${c.jump}"${c.gradeJump?` data-grade-jump="${c.gradeJump}"`:''} title="${c.jumpTitle}">${inner}</button>`
        : `<article class="kpi-card ${c.cls||''}">${inner}</article>`;
    }).join('');
  }

  function bidReason(bid) {
    if (bid.grade === '적극추천') return `점수 ${bid.score}점 · 예상 마진 ${fmtPct(bid.simulation.estimated_margin_percent)} · 즉시 제외 사유 없음`;
    if (bid.blockers.length) return `즉시 제외 사유 ${bid.blockers.length}건 · 자격 미달 또는 필수조건 확인 필요`;
    if (bid.eligibility.unknown_count) return `미확인 조건 ${bid.eligibility.unknown_count}건 · 담당자 확인 필요`;
    return bid.recommendation_reason || '종합점수 기준 검토';
  }

  function renderTopRecommendations() {
    const top = [...bids].sort((a,b)=>(b.score??-1)-(a.score??-1)).slice(0,5);
    $('#topRecommendations').innerHTML = top.map((b,i)=>`
      <article class="recommend-row g-${gradeClass(b.grade)}" data-open-bid="${b.bid_no}">
        <span class="rank-badge g-${gradeClass(b.grade)}">${i+1}</span>
        <div class="recommend-title"><strong>${esc(b.title)}</strong><small>${esc(b.agency)} · ${esc(b.category)}</small></div>
        <div class="metric-cell">적합도<b>${b.score ?? '-'}점</b></div>
        <div class="metric-cell">예상 마진<b class="${b.simulation.estimated_margin_percent>=15?'good':''}">${fmtPct(b.simulation.estimated_margin_percent)}</b></div>
        <div class="metric-cell">마감<b class="${b.days_left<=3?'danger':b.days_left<=7?'warn':''}">${dday(b.days_left)}</b></div>
        <div class="metric-cell">판정<b class="g-${gradeClass(b.grade)}">${esc(b.grade)}</b></div>
        <button class="row-open" aria-label="상세보기">→</button>
      </article>`).join('');
  }

  function renderDonutAndBars() {
    const rec = summary.grade_counts['적극추천'], rev = summary.grade_counts['검토'], pass = summary.grade_counts['패스'];
    const total = summary.total;
    const a = rec/total*360, b = (rec+rev)/total*360;
    $('#gradeDonut').style.background = `conic-gradient(${GRADE_COLOR.recommend} 0 ${a}deg,${GRADE_COLOR.review} ${a}deg ${b}deg,${GRADE_COLOR.pass} ${b}deg 360deg)`;
    $('#donutTotal').textContent = total;
    $('#gradeLegend').innerHTML = [
      [GRADE_COLOR.recommend,'적극추천',rec],[GRADE_COLOR.review,'검토',rev],[GRADE_COLOR.pass,'패스',pass]
    ].map(([c,n,v])=>`<div class="legend-row"><span class="legend-dot" style="background:${c}"></span><span>${n}</span><b>${v}건</b></div>`).join('');
    const maxBudget = Math.max(...summary.categories.map(c=>c.budget));
    $('#categoryBars').innerHTML = summary.categories.sort((x,y)=>y.budget-x.budget).map(c=>`<div class="bar-row"><span>${esc(c.category)}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(8,c.budget/maxBudget*100)}%"></div></div><b>${fmtBillion(c.budget)}</b></div>`).join('');
  }

  function renderDecisionStrip() {
    const urgent = bids.filter(b=>Number.isFinite(b.days_left)&&b.days_left>=0&&b.days_left<=3).sort((a,b)=>a.days_left-b.days_left);
    const people = bids.reduce((sum,b)=>sum+b.eligibility.unknown_count,0);
    const bestMargin = [...bids].sort((a,b)=>b.simulation.estimated_margin_percent-a.simulation.estimated_margin_percent)[0];
    $('#executiveSummaryText').textContent = `적극추천 ${summary.grade_counts['적극추천']}건은 바로 우선 검토하고, 마감 임박 ${summary.urgent_count}건과 미확인 조건 ${people}개는 담당자 확인이 필요합니다.`;
    const cards = [
      urgent[0]
        ? {label:'가장 임박', value:dday(urgent[0].days_left), title:urgent[0].title, note:'마감 일정 우선 점검', tone:'dc-urgent', bid:urgent[0].bid_no}
        : {label:'가장 임박', value:'없음', title:'', note:'마감 일정 우선 점검', tone:'dc-urgent'},
      {label:'수익성 상위', value:fmtPct(bestMargin.simulation.estimated_margin_percent), title:bestMargin.title, note:'자격/리스크 동시 확인', tone:'dc-profit', bid:bestMargin.bid_no},
      {label:'자동 품질검수', value:`${summary.avg_qa} / 100`, title:'', note:'Judge 평균 · Critical 0', tone:'dc-quality'}
    ];
    $('#decisionCards').innerHTML = cards.map(x=>{
      const inner = `<span class="dc-label">${x.label}</span><strong class="dc-value">${x.value}</strong>${x.title?`<em class="dc-title">${esc(x.title)}</em>`:''}<small class="dc-note">${x.note}</small>`;
      return x.bid ? `<button type="button" class="decision-card ${x.tone}" data-open-bid="${x.bid}">${inner}</button>` : `<div class="decision-card ${x.tone}">${inner}</div>`;
    }).join('');
  }

  function updateFavFilterUI() {
    const chip = $('#favFilterChip');
    if (chip) chip.textContent = `관심 공고 ${state.favorites.size}`;
    $$('#favFilter .filter-chip').forEach(c => c.classList.toggle('active', (c.dataset.favFilter === 'fav') === state.favOnly));
  }

  function renderRecommendationGrid() {
    updateFavFilterUI();
    let items = [...bids];
    items.sort(state.recSort === 'score' ? (a,b)=>(b.score??-1)-(a.score??-1) : (a,b)=>(a.days_left??999)-(b.days_left??999));
    if (state.favOnly) items = items.filter(b => state.favorites.has(b.bid_no));
    const grid = $('#recommendCardsGrid');
    if (!items.length) {
      grid.innerHTML = state.favOnly
        ? '<div class="empty-state">관심으로 저장한 공고가 없습니다.<br/>카드 우측 상단의 별표를 누르면 여기에 모입니다.</div>'
        : '<div class="empty-state">조건에 맞는 공고가 없습니다.</div>';
      return;
    }
    grid.innerHTML = items.map(b=>{
      const fav = state.favorites.has(b.bid_no);
      return `
      <article class="recommend-card">
        <div class="badge-line"><span class="grade-pill ${gradeClass(b.grade)}">${esc(b.grade)}</span><button type="button" class="favorite-btn ${fav?'on':''}" data-favorite="${b.bid_no}" aria-pressed="${fav}" aria-label="관심 공고 ${fav?'해제':'저장'}" title="관심 공고 ${fav?'해제':'저장'}">${fav?'★':'☆'}</button></div>
        <h3>${esc(b.title)}</h3><div class="meta">${esc(b.agency)} · ${esc(b.category)} · <span class="meta-dday ${b.days_left<=3?'hot':''}">${dday(b.days_left)}</span></div>
        <div class="card-stats"><div class="stat-mini"><span>점수</span><b>${b.score ?? '-'}</b></div><div class="stat-mini"><span>예상 마진</span><b class="${b.simulation.estimated_margin_percent>=15?'m-good':b.simulation.estimated_margin_percent>=10?'m-mid':'m-low'}">${fmtPct(b.simulation.estimated_margin_percent)}</b></div><button type="button" class="stat-mini stat-qa" data-qa-jump="${b.bid_no}" title="품질 검증 화면에서 이 공고의 QA 상세 보기"><span class="qa-hint" title="QA = AI 분석 결과를 LLM Judge가 재검수한 품질 점수">QA ⓘ</span><b>${b.qa.overall_score.toFixed(1)}</b></button></div>
        <div class="card-reason ${gradeClass(b.grade)}">${bidReason(b)}</div>
        <div class="card-actions"><button class="primary-btn" data-open-bid="${b.bid_no}">상세 분석</button></div>
      </article>`;
    }).join('');
  }

  function buildCategoryFilters() {
    const cats=['all',...new Set(bids.map(b=>b.category))];
    $('#categoryFilters').innerHTML=cats.map(c=>`<button class="filter-chip ${state.category===c?'active':''}" data-category="${c}">${c==='all'?'전체':esc(c)}</button>`).join('');
  }

  function filteredBids() {
    let out=bids.filter(b=>!state.search||`${b.title} ${b.agency} ${b.category}`.toLowerCase().includes(state.search.toLowerCase()));
    if(state.category!=='all') out=out.filter(b=>b.category===state.category);
    if(state.grade!=='all') out=out.filter(b=>b.grade===state.grade);
    if(state.risk==='high') out=out.filter(b=>b.risk_high>0);
    if(state.risk==='urgent') out=out.filter(b=>Number.isFinite(b.days_left)&&b.days_left>=0&&b.days_left<=3);
    if(state.risk==='blocker') out=out.filter(b=>b.blockers.length>0);
    if(state.risk==='unknown') out=out.filter(b=>b.eligibility.unknown_count>0);
    return out.sort((a,b)=>(b.score??-1)-(a.score??-1));
  }

  function renderSearch(){
    buildCategoryFilters();
    $('#gradeFilter').value=state.grade; $('#riskFilter').value=state.risk;
    const marginCls=v=>v>=15?'m-good':v>=10?'m-mid':'m-low';
    const items=filteredBids();

    /* 공고 탐색 Hero 요약 — 기존 고정 데이터에서만 계산하는 표시용 지표 */
    const analysisDate=new Date(summary.analysis_date+'T00:00:00');
    const sevenDaysAgo=new Date(analysisDate); sevenDaysAgo.setDate(sevenDaysAgo.getDate()-6);
    const recentCount=bids.filter(b=>{
      if(!b.announce_date) return false;
      const d=new Date(b.announce_date+'T00:00:00');
      return d>=sevenDaysAgo && d<=analysisDate;
    }).length;
    const avgBudget=summary.total ? summary.budget_total/summary.total : 0;
    const heroStats=$('#searchHeroStats');
    if(heroStats) heroStats.innerHTML=[
      ['전체 공고',`${summary.total}건`,'현재 데이터 기준'],
      ['최근 7일 신규',`${recentCount}건`,'분석 기준일 포함'],
      ['평균 예정 금액',fmtBillion(avgBudget),'공고 평균 예산']
    ].map(([label,value,note])=>`<div class="search-hero-stat"><span>${label}</span><strong>${value}</strong><small>${note}</small></div>`).join('');

    const maxBudget=Math.max(1,...items.map(b=>b.budget||0));
    const maxMargin=Math.max(1,...items.map(b=>b.simulation?.estimated_margin_percent||0));
    $('#bidTableBody').innerHTML=items.map((b,i)=>{
      const margin=b.simulation.estimated_margin_percent;
      return `<tr data-open-bid="${b.bid_no}">
        <td><span class="search-rank r-${Math.min(i+1,7)}">${i+1}</span></td>
        <td class="bid-name"><strong>${esc(b.title)}</strong><small>${esc(b.category)} · ${b.bid_no}</small></td>
        <td>${esc(b.agency)}</td>
        <td><div class="search-metric"><b>${fmtBillion(b.budget)}</b><span class="search-mini-track"><i style="width:${Math.max(4,(b.budget||0)/maxBudget*100)}%"></i></span></div></td>
        <td><b>${b.score??'-'}</b></td>
        <td><div class="search-metric"><b class="${marginCls(margin)}">${fmtPct(margin)}</b><span class="search-mini-track margin"><i style="width:${Math.max(4,margin/maxMargin*100)}%"></i></span></div></td>
        <td><b class="${b.days_left<=8?'search-dday-hot':''}">${dday(b.days_left)}</b></td>
        <td><span class="grade-pill ${gradeClass(b.grade)}">${esc(b.grade)}</span></td>
        <td><button class="search-row-open" type="button" aria-label="${esc(b.title)} 상세보기">→</button></td>
      </tr>`;
    }).join('') || `<tr><td colspan="9"><div class="empty-state">조건에 맞는 공고가 없습니다.</div></td></tr>`;
    $('#mobileBidList').innerHTML=items.map(b=>`<article class="mobile-bid-card" data-open-bid="${b.bid_no}"><div><span class="grade-pill ${gradeClass(b.grade)}">${esc(b.grade)}</span> <span class="status-pill ${b.days_left<=3?'hot':''}">${dday(b.days_left)}</span></div><h3>${esc(b.title)}</h3><div class="meta">${esc(b.agency)} · ${esc(b.category)} · ${fmtBillion(b.budget)}</div><div class="mobile-stats"><div class="stat-mini"><span>점수</span><b>${b.score??'-'}</b></div><div class="stat-mini"><span>예상 마진</span><b class="${marginCls(b.simulation.estimated_margin_percent)}">${fmtPct(b.simulation.estimated_margin_percent)}</b></div><div class="stat-mini"><span class="qa-hint" title="QA = AI 분석 결과를 LLM Judge가 재검수한 품질 점수">QA ⓘ</span><b>${b.qa.overall_score.toFixed(1)}</b></div></div></article>`).join('') || `<div class="empty-state">조건에 맞는 공고가 없습니다.</div>`;
    syncFilterToggle();
  }

  function syncFilterToggle(){
    const ft=$('#filterToggle'); if(!ft) return;
    const open=ft.classList.contains('open');
    ft.innerHTML=`필터 ${open?'▴':'▾'}`;
    const badges=[];
    if(state.grade!=='all') badges.push(`<button type="button" class="filter-badge" data-clear-filter="grade" title="이 필터 해제">${state.grade==='검토'?'담당자 검토 필요':esc(state.grade)} <span aria-hidden="true">×</span></button>`);
    if(state.risk!=='all'){const m={high:'HIGH 있음',urgent:'마감 3일 이내',blocker:'즉시 제외 사유',unknown:'담당자 확인 필요'};badges.push(`<button type="button" class="filter-badge" data-clear-filter="risk" title="이 필터 해제">${m[state.risk]} <span aria-hidden="true">×</span></button>`);}
    const fb=$('#filterBadges'); if(fb) fb.innerHTML=badges.join('');
  }

  function renderRisk(){
    const urgent=bids.filter(b=>Number.isFinite(b.days_left)&&b.days_left>=0&&b.days_left<=3);
    const unknown=bids.reduce((s,b)=>s+b.eligibility.unknown_count,0);
    const high=bids.filter(b=>b.risk_high>0).length;
    const blocked=bids.filter(b=>b.blockers.length>0).length;
    const manual=bids.filter(b=>b.eligibility.conditions.some(c=>c.manual_confirmation_required)).length;
    $('#riskKpis').innerHTML=[['위험 신호',high,'HIGH 리스크 공고','danger'],['마감 임박',urgent.length,'3일 이내','warn'],['즉시 제외 사유',blocked,'필수 조건 미충족 공고','danger'],['미확인 조건',unknown,'판정 대기 조건 총계','warn'],['사람 확인 필요',manual,'필수 수동 확인 공고','info']].map(([l,v,n,c])=>`<div class="risk-kpi ${c||''}"><span>${l}</span><strong>${v}</strong><small>${n}</small></div>`).join('');
    const items=[...bids].sort((a,b)=>(a.days_left??999)-(b.days_left??999)).filter(b=>b.days_left<=7||b.blockers.length||b.risk_high).slice(0,12);
    $('#riskList').innerHTML=items.map(b=>`<article class="risk-item ${b.risk_high?'sev-high':(Number.isFinite(b.days_left)&&b.days_left<=3?'sev-urgent':'')}" data-open-bid="${b.bid_no}"><div class="risk-dday">${dday(b.days_left)}</div><div><h4>${esc(b.title)}</h4><p>${esc(b.agency)} · <b class="unk">미확인 조건 ${b.eligibility.unknown_count}건</b>${b.blockers.length?` · <b class="blk">즉시 제외 ${b.blockers.length}건</b>`:''}</p></div><div class="risk-tags">${b.risk_high?'<span class="risk-pill high">HIGH</span>':''}${b.risk_medium?'<span class="risk-pill medium">MEDIUM</span>':''}<span class="grade-pill ${gradeClass(b.grade)}">${esc(b.grade)}</span></div></article>`).join('');
    const types={}; bids.forEach(b=>(b.risky_items||[]).forEach(r=>{const k=r.item||r.risk||'기타';types[k]=(types[k]||0)+1;}));
    const arr=Object.entries(types).sort((a,b)=>b[1]-a[1]).slice(0,8), max=Math.max(1,...arr.map(x=>x[1]));
    $('#riskTypeBars').innerHTML=arr.map(([k,v])=>`<div class="bar-row"><span title="${esc(k)}">${esc(truncate(k,9))}</span><div class="bar-track"><div class="bar-fill" style="width:${v/max*100}%;background:linear-gradient(90deg,#e09a48,#b84b49)"></div></div><b>${v}</b></div>`).join('');
  }

  function renderSimulation(){
    const sorted=[...bids].sort((a,b)=>b.simulation.estimated_margin_percent-a.simulation.estimated_margin_percent);
    const chartBids=sorted.slice(0,15);
    const max=Math.max(...chartBids.map(b=>b.simulation.estimated_margin_percent));
    const avg=bids.reduce((s,b)=>s+b.simulation.estimated_margin_percent,0)/bids.length;
    const totalBudget=bids.reduce((s,b)=>s+(b.budget||0),0);
    const topCategory=(()=>{const m={};bids.forEach(b=>{const k=b.category||b.business_category||b.field||'기타';m[k]=(m[k]||[]).concat(b.simulation.estimated_margin_percent)});const rows=Object.entries(m).map(([k,v])=>[k,v.reduce((s,n)=>s+n,0)/v.length]);return rows.sort((x,y)=>y[1]-x[1])[0]||['-',0]})();
    $('#profitKpis').innerHTML=[
      ['분석 대상 공고',`${bids.length}건`,'현재 대시보드 기준','◎'],
      ['평균 예상 마진',fmtPct(avg),'가정값 기반 시뮬레이션','◇'],
      ['분석 예산 총액',fmtBillion(totalBudget),'현재 공고 예산 합계','▥'],
      ['마진 TOP 분야',esc(topCategory[0]),`평균 ${fmtPct(topCategory[1])}`,'♢']
    ].map(x=>`<div class="profit-kpi"><span class="profit-kpi-icon">${x[3]}</span><div><small>${x[0]}</small><strong>${x[1]}</strong><em>${x[2]}</em></div></div>`).join('');
    $('#marginChart').innerHTML=chartBids.map((b,i)=>`<div class="margin-col" data-open-bid="${b.bid_no}" title="${esc(b.title)}"><div class="margin-rank">#${i+1}</div><div class="margin-bar g-${gradeClass(b.grade)}" style="height:${Math.max(8,b.simulation.estimated_margin_percent/max*82)}%"></div><b>${b.simulation.estimated_margin_percent.toFixed(1)}%</b><span title="${esc(b.title)}">${esc(truncate(b.title,8))}</span></div>`).join('');
    $('#marginLegend').innerHTML=[[GRADE_COLOR.recommend,'적극추천'],[GRADE_COLOR.review,'검토'],[GRADE_COLOR.pass,'패스']].map(([c,n])=>`<span class="cl-item"><i class="legend-dot" style="background:${c}"></i>${n}</span>`).join('');
    const sample=sorted[0].simulation.assumptions;
    $('#assumptionBox').innerHTML=sample.map((a,i)=>{
      const m=ASSUMPTION_KO[a.key]||{label:a.key,desc:''};
      return `<div class="assumption-row"><span class="assumption-no">${String(i+1).padStart(2,'0')}</span><div><span class="as-label">${m.label}</span><strong class="as-value">${esc(a.value)}</strong>${m.desc?`<small class="as-desc">${m.desc}</small>`:''}</div></div>`;
    }).join('');
    $('#profitList').innerHTML=sorted.slice(0,8).map((b,i)=>`<article class="profit-item" data-open-bid="${b.bid_no}"><span class="profit-rank">${String(i+1).padStart(2,'0')}</span><div class="profit-info"><div class="profit-head"><h4>${esc(b.title)}</h4><span class="grade-pill ${gradeClass(b.grade)}">${esc(b.grade)}</span></div><p>${esc(b.agency)} · QA ${b.qa.overall_score.toFixed(1)}</p></div><strong>${fmtPct(b.simulation.estimated_margin_percent)}</strong></article>`).join('');
  }

  function renderQuality(){
    $('#avgQaScore').textContent=summary.avg_qa.toFixed(1);
    const avgs={}; Object.keys(QA_AREA_KO).forEach(k=>{avgs[k]=bids.reduce((s,b)=>s+b.qa.areas[k].score,0)/bids.length});
    $('#qaAreaBars').innerHTML=Object.entries(avgs).map(([k,v])=>`<div class="bar-row"><span>${QA_AREA_KO[k]}</span><div class="bar-track"><div class="bar-fill" style="width:${v}%;background:linear-gradient(90deg,#b98b48,#1d7a5e)"></div></div><b>${v.toFixed(1)}</b></div>`).join('');
    $('#qaBidGrid').innerHTML=[...bids].sort((a,b)=>b.qa.overall_score-a.qa.overall_score).map(b=>`<article class="qa-card" data-open-bid="${b.bid_no}" data-bid="${b.bid_no}"><div class="qa-card-top"><span class="grade-pill ${gradeClass(b.grade)}">${esc(b.grade)}</span><div class="qa-score">${b.qa.overall_score.toFixed(1)}</div></div><h4>${esc(b.title)}</h4><p>${b.qa.overall_status} · Critical ${b.qa.critical_review_required?'필요':'0'}</p></article>`).join('');
  }

  /* 자격 조건 — 경영진용 한 줄 요약 + 기술 근거는 펼침으로 분리 */
  function conditionSummary(c){
    if(c.status==='PASS') return '요구 조건이 제공 데이터에서 확인되었습니다.';
    if(c.status==='FAIL') return '필수 요건이 충족되지 않아 확정 차단 사유에 해당합니다.';
    switch(c.type){
      case 'license': return '보유 면허·등록 정보만으로 판단할 수 없어 담당자 확인이 필요합니다.';
      case 'capability': return '회사 역량·보유 여부 데이터가 없어 담당자 확인이 필요합니다.';
      case 'track_record': return '유사 실적 요건 충족 여부를 담당자가 확인해야 합니다.';
      case 'staff': return '투입 인력 요건 충족 여부를 담당자가 확인해야 합니다.';
      case 'mandatory_action': return '계약 전 이행이 필요한 조건이라 담당자 확인이 필요합니다.';
      default: return '회사 데이터만으로 판단할 수 없어 사람 확인이 필요합니다.';
    }
  }

  function openBid(bidNo){
    const b=bids.find(x=>x.bid_no===bidNo); if(!b) return;
    const condHtml=b.eligibility.conditions.map(c=>{
      const st=c.status.toLowerCase();
      const evObj=(c.evidence && typeof c.evidence==='object') ? '\n' + JSON.stringify(c.evidence,null,1) : '';
      const evText=[c.reason||'', evObj].filter(Boolean).join('\n').trim();
      return `<div class="condition-item st-${st}">
        <div class="cond-head"><span class="cond-badge ${st}">${c.status}</span><div class="cond-main"><strong class="cond-title">${esc(c.text)}</strong><p class="cond-summary">${conditionSummary(c)}</p></div></div>
        ${evText?`<button type="button" class="evidence-toggle" data-evidence-toggle aria-expanded="false">근거 보기</button><div class="evidence-box" hidden>${esc(evText)}</div>`:''}
      </div>`;
    }).join('');
    const qaHtml=Object.entries(b.qa.areas).map(([k,v])=>`<div class="qa-area-card"><span>${QA_AREA_KO[k]||k.replaceAll('_',' ')}</span><b>${v.score}</b></div>`).join('');
    $('#drawerContent').innerHTML=`
      <div class="drawer-title"><div class="eyebrow">${esc(b.category)} · ${b.bid_no}</div><h2 id="drawerTitle">${esc(b.title)}</h2><p>${esc(b.agency)} · 공고 ${b.announce_date} · 마감 ${b.bid_deadline}</p></div>
      <div class="drawer-score-row"><div class="drawer-metric"><span>추천등급</span><strong>${esc(b.grade)}</strong></div><div class="drawer-metric"><span>점수</span><strong>${b.score??'-'} / 100</strong></div><div class="drawer-metric"><span>예상 마진</span><strong>${fmtPct(b.simulation.estimated_margin_percent)}</strong></div><div class="drawer-metric"><span>QA</span><strong>${b.qa.overall_score.toFixed(1)}</strong></div></div>
      <div class="detail-section"><h3>경영진 요약</h3><div class="brief-line"><span>예산</span><strong>${fmtBillion(b.budget)}</strong></div><div class="brief-line"><span>마감</span><strong>${dday(b.days_left)} · ${b.bid_deadline}</strong></div><div class="brief-line"><span>예상 투입</span><strong>${b.simulation.estimated_staff}명 / ${b.duration_months}개월</strong></div><div class="brief-line"><span>판단 근거</span><strong>${bidReason(b)}</strong></div></div>
      <div class="detail-section"><h3>자격 판정 · 통과 ${b.eligibility.pass_count} / 차단 ${b.eligibility.fail_count} / 미확인 ${b.eligibility.unknown_count}</h3><div class="condition-list">${condHtml}</div></div>
      <div class="detail-section"><h3>수익성 시뮬레이션</h3><div class="drawer-score-row"><div class="drawer-metric"><span>총원가</span><strong>${fmtBillion(b.simulation.estimated_total_cost)}</strong></div><div class="drawer-metric"><span>예상이익</span><strong>${fmtBillion(b.simulation.estimated_profit)}</strong></div><div class="drawer-metric"><span>일정 리스크</span><strong title="${esc(b.simulation.schedule_risk)}">${esc(LEVEL_KO[b.simulation.schedule_risk]||b.simulation.schedule_risk)}</strong></div><div class="drawer-metric"><span>신뢰도</span><strong title="${esc(b.simulation.simulation_confidence)}">${esc(LEVEL_KO[b.simulation.simulation_confidence]||b.simulation.simulation_confidence)}</strong></div></div><p class="note-line">${esc(b.simulation.margin_note)}</p></div>
      <div class="detail-section"><h3>자동 품질검수</h3><div class="qa-area-grid">${qaHtml}</div><p class="note-line">${esc(b.qa.summary)}</p></div>`;
    $('#detailOverlay').hidden=false; document.body.style.overflow='hidden';
  }

  function closeOverlay(id){ const el=$('#'+id); if(el) el.hidden=true; if(!$$('.overlay:not([hidden])').length) document.body.style.overflow=''; }

  function renderNotifications(){
    const urgent=bids.filter(b=>Number.isFinite(b.days_left)&&b.days_left>=0&&b.days_left<=3).sort((a,b)=>a.days_left-b.days_left);
    const manual=bids.filter(b=>b.eligibility&&b.eligibility.unknown_count>0).sort((a,b)=>(b.eligibility.unknown_count||0)-(a.eligibility.unknown_count||0));
    const highRisk=bids.filter(b=>b.risk_high>0).sort((a,b)=>(b.risk_high||0)-(a.risk_high||0));
    const items=[
      ...urgent.slice(0,3).map(b=>({kind:'urgent',icon:'!',title:`${dday(b.days_left)} 마감 임박`,body:b.title,bid:b.bid_no})),
      ...manual.slice(0,2).map(b=>({kind:'check',icon:'?',title:`필수 확인 · 미확인 ${b.eligibility.unknown_count}건`,body:b.title,bid:b.bid_no})),
      ...highRisk.slice(0,2).map(b=>({kind:'risk',icon:'▲',title:`HIGH 리스크 ${b.risk_high}건`,body:b.title,bid:b.bid_no}))
    ];
    $('#notificationContent').innerHTML=items.length?items.map(x=>`<button class="notification-item ${x.kind}" data-open-bid="${esc(x.bid)}"><span class="notification-icon">${x.icon}</span><span><strong>${esc(x.title)}</strong><small>${esc(x.body)}</small></span><b>›</b></button>`).join(''):'<div class="notification-empty">현재 우선 확인할 알림이 없습니다.</div>';
  }

  function renderBrief(){
    const top=[...bids].sort((a,b)=>(b.score??-1)-(a.score??-1)).slice(0,3);
    const urgent=bids.filter(b=>Number.isFinite(b.days_left)&&b.days_left>=0&&b.days_left<=3).sort((a,b)=>a.days_left-b.days_left);
    $('#briefContent').innerHTML=`
      <section class="brief-sec"><div class="brief-sec-head"><em>01</em><h3>우선 검토</h3></div>
        <ol class="brief-rank">${top.map((b,i)=>`<li><span class="brief-rank-no">${i+1}</span><div><strong>${esc(b.title)}</strong><small>${esc(b.grade)} · ${b.score}점</small></div></li>`).join('')}</ol>
      </section>
      <section class="brief-sec"><div class="brief-sec-head"><em>02</em><h3>마감 리스크</h3></div>
        ${urgent.length?`<ul class="brief-dday-list">${urgent.map(b=>`<li><b class="dday ${b.days_left<=1?'hot':''}">${dday(b.days_left)}</b><span>${esc(b.title)}</span></li>`).join('')}</ul>`:'<p class="brief-plain">3일 이내 마감 공고 없음</p>'}
      </section>
      <section class="brief-sec"><div class="brief-sec-head"><em>03</em><h3>수익성</h3></div>
        <div class="brief-big-row"><div class="brief-big"><strong>${fmtPct(summary.avg_margin)}</strong><span>평균 예상 마진</span></div><small>※ 교육용 가정값 기반 · 실제 회계값이 아닙니다</small></div>
      </section>
      <section class="brief-sec"><div class="brief-sec-head"><em>04</em><h3>품질검수</h3></div>
        <div class="brief-big-row"><div class="brief-big"><strong>${summary.avg_qa} / 100</strong><span>Judge 평균</span></div></div>
        <ul class="brief-check-list"><li>Critical Review 0건</li><li>코드 자동검증 340 / 340 PASS</li></ul>
      </section>
      <section class="brief-sec"><div class="brief-sec-head"><em>05</em><h3>의사결정 원칙</h3></div>
        <ul class="brief-rule-list"><li>확정 FAIL은 차단합니다</li><li>필수 미확인 조건은 적극추천 상한을 '검토'로 제한합니다</li><li>최종 판단은 사람이 수행합니다</li></ul>
      </section>`;
  }

  function renderExtensions(){
    $('#extensionGrid').innerHTML=DATA.extension_ready.map((x,i)=>`<article class="extension-card"><span>0${i+1} · 추가 데이터 연동 시</span><h3>${esc(x.name)}</h3><p>${esc(x.value)}</p><small>필요 데이터: ${esc(x.needs)}</small></article>`).join('');
  }

  function toggleFavorite(bidNo){
    if(state.favorites.has(bidNo)) state.favorites.delete(bidNo); else state.favorites.add(bidNo);
    localStorage.setItem('bidFavorites',JSON.stringify([...state.favorites]));
    renderRecommendationGrid();
  }

  function initEvents(){
    document.addEventListener('click',e=>{
      const evBtn=e.target.closest('[data-evidence-toggle]');
      if(evBtn){const box=evBtn.nextElementSibling; if(box){box.hidden=!box.hidden; evBtn.setAttribute('aria-expanded',String(!box.hidden)); evBtn.textContent=box.hidden?'근거 보기':'근거 숨기기';} return;}
      const cf=e.target.closest('[data-clear-filter]');
      if(cf){
        if(cf.dataset.clearFilter==='grade'){state.grade='all';const sel=$('#gradeFilter');if(sel)sel.value='all';}
        else{state.risk='all';const sel=$('#riskFilter');if(sel)sel.value='all';}
        renderSearch();
        return;
      }
      const nav=e.target.closest('[data-view]'); if(nav){setView(nav.dataset.view); return;}
      const qj=e.target.closest('[data-qa-jump]');
      if(qj){
        setView('quality');
        setTimeout(()=>{
          const card=document.querySelector(`.qa-card[data-bid="${CSS.escape(qj.dataset.qaJump)}"]`);
          if(card){ card.scrollIntoView({behavior:'smooth',block:'center'}); card.classList.add('qa-flash'); setTimeout(()=>card.classList.remove('qa-flash'),1800); }
        },120);
        return;
      }
      const jump=e.target.closest('[data-view-jump]'); if(jump){
        const gj=jump.dataset.gradeJump;
        if(gj){ state.grade=gj; const sel=$('#gradeFilter'); if(sel) sel.value=gj; }
        setView(jump.dataset.viewJump); return;
      }
      const opener=e.target.closest('[data-open-bid]'); if(opener){openBid(opener.dataset.openBid); return;}
      const fav=e.target.closest('[data-favorite]'); if(fav){toggleFavorite(fav.dataset.favorite); return;}
      const favFilter=e.target.closest('[data-fav-filter]'); if(favFilter){state.favOnly=favFilter.dataset.favFilter==='fav'; renderRecommendationGrid(); return;}
      const cat=e.target.closest('[data-category]'); if(cat){state.category=cat.dataset.category;renderSearch();return;}
      const closer=e.target.closest('[data-close-overlay]'); if(closer){closeOverlay(closer.dataset.closeOverlay);return;}
      if(e.target.classList.contains('overlay')) closeOverlay(e.target.id);
    });
    $('#notificationBtn').addEventListener('click',()=>{
      renderNotifications();
      $('#notificationOverlay').hidden=false;
      document.body.style.overflow='hidden';
    });
    $('#closeDrawer').addEventListener('click',()=>closeOverlay('detailOverlay'));
    $('#gradeFilter').addEventListener('change',e=>{state.grade=e.target.value;renderSearch();});
    $('#riskFilter').addEventListener('change',e=>{state.risk=e.target.value;renderSearch();});
    $('#filterToggle').addEventListener('click',()=>{
      const adv=$('#filterAdv');
      const open=adv.classList.toggle('open');
      $('#filterToggle').classList.toggle('open',open);
      $('#filterToggle').setAttribute('aria-expanded',String(open));
      $('#filterToggle').innerHTML=open?'필터 ▴':'필터 ▾';
    });
    $('#globalSearch').addEventListener('input',e=>{state.search=e.target.value.trim(); if(state.search) setView('search'); else if(state.view==='search') renderSearch();});
    $('#openBrief').addEventListener('click',()=>{renderBrief();$('#briefOverlay').hidden=false;document.body.style.overflow='hidden';});
    $('#openExtensions').addEventListener('click',()=>{renderExtensions();$('#extensionOverlay').hidden=false;document.body.style.overflow='hidden';});
    $$('.qa-info-open').forEach(btn=>btn.addEventListener('click',e=>{e.stopPropagation();$('#qaInfoOverlay').hidden=false;document.body.style.overflow='hidden';}));
    $('#recommendSort').addEventListener('click',()=>{
      state.recSort=state.recSort==='score'?'deadline':'score';
      $('#recommendSort').innerHTML=state.recSort==='score'?'⇅&nbsp;점수 높은순':'⇅&nbsp;마감 임박순';
      renderRecommendationGrid();
    });
    $('#showDeterministic').addEventListener('click',()=>{
      const el=$('#deterministicList'); el.hidden=!el.hidden; $('#showDeterministic').textContent=el.hidden?'17개 검증항목 보기':'상세 닫기';
    });
    window.addEventListener('keydown',e=>{ if(e.key==='Escape') $$('.overlay:not([hidden])').forEach(x=>closeOverlay(x.id)); if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('#globalSearch').focus();} });
  }

  function setupPWA(){
    if('serviceWorker' in navigator) navigator.serviceWorker.register('service-worker.js').catch(()=>{});
  }

  function renderStaticCounts(){
    $('#navRecommendCount').textContent=summary.grade_counts['적극추천'];
    const navRisk=$('#navRiskCount');
    navRisk.textContent=bids.filter(b=>b.risk_high>0).length;
    navRisk.title='HIGH 리스크 공고 수 — 리스크 관제 "위험 신호" 카드와 같은 기준';
    $('#deterministicList').innerHTML=DET_ITEMS.map((x,i)=>`<div class="det-item"><b>${String(i+1).padStart(2,'0')}</b><span>${x}</span></div>`).join('');
    // 랜딩/스타트 스크린 실데이터 연동
    const g=summary.grade_counts, mx=Math.max(g['적극추천'],g['검토'],g['패스']);
    const kpiRec=$('#ldKpiRecommend');
    if(kpiRec){
      kpiRec.textContent=g['적극추천'];
      $('#ldKpiReview').textContent=g['검토'];
      $('#ldKpiUrgent').textContent=summary.urgent_count;
      $('#ldKpiMargin').textContent=fmtPct(summary.avg_margin);
      $('#ldStripRecommend').textContent=g['적극추천']+'건';
      $('#ldStripReview').textContent=g['검토']+'건';
      $('#ldStripUrgent').textContent=summary.urgent_count+'건';
      $('#ldStripMargin').textContent=fmtPct(summary.avg_margin);
      $('#ldMiniBars').innerHTML=[['적극추천',g['적극추천'],'recommend'],['검토',g['검토'],'review'],['패스',g['패스'],'pass']]
        .map(([n,v,c])=>`<div class="ld-mini-bar"><span>${n}</span><div class="ld-mini-track"><i class="${c}" style="width:${Math.round(v/mx*100)}%"></i></div><b>${v}</b></div>`).join('');
    }
  }

  function init(){
    renderKPIs();renderTopRecommendations();renderDonutAndBars();renderDecisionStrip();renderRecommendationGrid();renderSearch();renderRisk();renderSimulation();renderQuality();renderStaticCounts();initEvents();setupPWA();
    const hash=location.hash.replace('#',''); if(['recommend','search','risk','simulation','quality'].includes(hash)) setView(hash);
  }
  window.addEventListener('hashchange',()=>{
    const h=location.hash.replace('#','');
    const next=['recommend','search','risk','simulation','quality'].includes(h)?h:'dashboard';
    if(next!==state.view) setView(next,{silent:true});
  });
  init();
})();
