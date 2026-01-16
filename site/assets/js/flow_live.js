const FLOW_LIVE = (()=>{
  let tokens=[]; let lanes=[]; let host=null; let panel=null; let rafId=null; let lastTs=Date.now();
  function cls(st){ return st==='moving'?'ok':(st==='processing'?'ok':(st==='waiting'?'degraded':(st==='blocked'?'degraded':(st==='down'?'offline':'degraded')))); }
  async function fetchAll(){ try{ const L=await AUTH.get('/api/v1/lines'); const O=await AUTH.get('/api/v1/orders'); return {lines:(L.lines||[]), orders:(O.orders||[]), ts: O.last_sync||L.last_sync}; }catch(e){ return {lines:[], orders:[], ts: null}; } }
  function mapLaneName(lid){ const map={1:'Metal & Şase',2:'Boya Hattı',3:'Montaj',4:'Final Test',5:'Paketleme & Sevkiyat'}; return map[lid]||'Montaj'; }
  function build(domHost, sidePanel){ host=domHost; panel=sidePanel; host.innerHTML=''; lanes=['Metal & Şase','Boya Hattı','Montaj','Final Test','Paketleme & Sevkiyat'].map(name=>{ const lane=document.createElement('div'); lane.className='lane'; lane.setAttribute('data-line',name); lane.style.border='1px solid #e0e0e0'; lane.style.borderRadius='8px'; lane.style.padding='8px'; lane.style.minHeight='140px'; lane.innerHTML=`<div style='font-weight:600;margin-bottom:6px'>${name}</div><div class='lane-track' style='position:relative;height:90px;background:#fafbfc;border:1px solid #e0e0e0;border-radius:6px'></div>`; host.appendChild(lane); return lane; }); }
  function setTokens(orders){ tokens = orders.slice(0,12).map((o,i)=>{ const laneName=mapLaneName(o.line_id); const lane=lanes.find(l=> l.getAttribute('data-line')===laneName); const track=lane.querySelector('.lane-track'); const el=document.createElement('div'); el.className='token'; el.style.position='absolute'; el.style.top='30px'; el.style.left='0px'; el.style.width='24px'; el.style.height='24px'; el.style.borderRadius='50%'; el.style.background=tokenColor(o.state); el.style.border='1px solid #333'; track.appendChild(el); el.onclick=()=>showTip(o,el); return {el, laneName, order:o, x:0, targetX: targetPos(o.state)}; }); renderPanel(orders); }
  function tokenColor(state){ if(state==='moving'||state==='processing') return '#16a34a'; if(state==='waiting') return '#f59e0b'; if(state==='blocked') return '#f97316'; if(state==='down') return '#dc2626'; return '#64748b'; }
  function targetPos(state){ if(state==='moving') return 80; if(state==='processing') return 50; if(state==='waiting') return 20; if(state==='blocked') return 35; if(state==='down') return 10; return 15; }
  function showTip(o, el){ const tip=document.createElement('div'); tip.className='token-tip'; tip.style.position='absolute'; tip.style.left=(parseInt(el.style.left||'0')+30)+'px'; tip.style.top='0px'; tip.style.background='#ffffff'; tip.style.border='1px solid #e0e0e0'; tip.style.borderRadius='6px'; tip.style.padding='8px'; tip.style.fontSize='.85rem'; tip.innerHTML = `<div><strong>${o.order_id}</strong></div><div>${mapLaneName(o.line_id)} • Station ${o.station_id}</div><div>Elapsed ${o.elapsed_min}m</div><div>Energy ${o.energy_kwh} kWh</div><div>CO₂ ${o.co2e_kg} kg</div><div>Scrap ${o.scrap_units} • Rework ${o.rework_units}</div><div>ETA ${o.eta_ts}</div>`; el.parentElement.appendChild(tip); setTimeout(()=> tip.remove(), 2500); }
  function renderPanel(orders){ if(!panel) return; panel.innerHTML=''; orders.slice(0,8).forEach(o=>{ const row=document.createElement('div'); row.className='order-row'; row.style.border='1px solid #e0e0e0'; row.style.borderRadius='6px'; row.style.padding='6px'; row.style.marginBottom='6px'; row.innerHTML = `<div style='display:flex;justify-content:space-between'><div>${o.order_id}</div><span class='pill ${cls(o.state)}'>${o.state}</span></div><div style='font-size:.85rem;color:#444'>Energy ${o.energy_kwh} kWh • CO₂ ${o.co2e_kg} kg • Risk ${o.risk}${o.reason_code? ' • '+o.reason_code:''}</div>`; panel.appendChild(row); }); }
  function lerp(a,b,t){ return a+(b-a)*t; }
  function step(){ tokens.forEach(t=>{ t.x = lerp(t.x, t.targetX, 0.05); t.el.style.left = (t.x)+'%'; }); rafId=requestAnimationFrame(step); }
  async function start(domHost, sidePanel){ build(domHost, sidePanel); const data=await fetchAll(); setTokens(data.orders); step(); setInterval(async()=>{ const data=await fetchAll(); setTokens(data.orders); }, 3000); }
  return { start };
})();

// PATCH START flow_live-enhance (assets/js/flow_live.js)
(function(){
  if(!window.FLOW_LIVE) return;
  // augment FLOW_LIVE with smoother token reuse + updating tooltip
  const API = {
    async lines(){ try{ const r=await AUTH.get('/api/v1/lines'); return (r.lines||[]); }catch(e){ return []; } },
    async orders(){ try{ const r=await AUTH.get('/api/v1/orders'); return (r.orders||[]); }catch(e){ return []; } }
  };
  const laneName = (lid)=>({1:'Metal & Şase',2:'Boya Hattı',3:'Montaj',4:'Final Test',5:'Paketleme & Sevkiyat'})[lid]||'Montaj';
  const tokenColor = (s)=> s==='down'?'#dc2626' : s==='blocked'?'#f97316' : s==='waiting'?'#f59e0b' : '#16a34a';
  const targetPos = (s)=> s==='moving'?80 : s==='processing'?50 : s==='waiting'?20 : s==='blocked'?35 : s==='down'?10 : 15;

  let tokensById = {}; // {order_id: {el, x, targetX, laneName, order}}
  let lanesCache = []; // DOM lanes
  let tipEl = null;
  let selectedOrderId = null;
  let rafId = null;
  let started = false;

  function build(host){
    host.innerHTML='';
    lanesCache = ['Metal & Şase','Boya Hattı','Montaj','Final Test','Paketleme & Sevkiyat'].map(name=>{
      const lane=document.createElement('div');
      lane.className='lane';
      lane.setAttribute('data-line',name);
      lane.style.border='1px solid #e0e0e0';
      lane.style.borderRadius='8px';
      lane.style.padding='8px';
      lane.style.minHeight='140px';
      lane.innerHTML=`<div style='font-weight:600;margin-bottom:6px'>${name}</div><div class='lane-track' style='position:relative;height:90px;background:#fafbfc;border:1px solid #e0e0e0;border-radius:6px'></div>`;
      host.appendChild(lane);
      return lane;
    });
  }
  function showTip(o, tokenEl){
    // remove previous
    if(tipEl && tipEl.parentElement) tipEl.remove();
    selectedOrderId = o.order_id;
    tipEl = document.createElement('div');
    tipEl.className='token-tip';
    tipEl.style.position='absolute';
    tipEl.style.left=(parseFloat(tokenEl.style.left||'0')+30)+'%';
    tipEl.style.top='0px';
    tipEl.style.background='#ffffff';
    tipEl.style.border='1px solid #e0e0e0';
    tipEl.style.borderRadius='6px';
    tipEl.style.padding='8px';
    tipEl.style.fontSize='.85rem';
    tipEl.style.boxShadow='0 4px 12px rgba(0,0,0,.08)';
    tipEl.innerHTML = tipHtml(o);
    tokenEl.parentElement.appendChild(tipEl);
  
    
    if(window.__ZERO_CLAMP_TIP) setTimeout(function(){ window.__ZERO_CLAMP_TIP(tokenEl, tipEl); }, 0);
}
  function tipHtml(o){
    const ln = laneName(o.line_id);
    const stName = 'Station '+(o.station_id||'-');
    return `<div><strong>${o.order_id}</strong></div>
            <div>${ln} • ${stName}</div>
            <div>State: ${o.state} • Risk: ${o.risk}${o.reason_code? ' • '+o.reason_code:''}</div>
            <div>Elapsed ${Math.round(o.elapsed_min||0)}m</div>
            <div>Energy ${o.energy_kwh||0} kWh • CO₂ ${o.co2e_kg||0} kg</div>
            <div>Scrap ${o.scrap_units||0} • Rework ${o.rework_units||0}</div>
            <div>ETA ${o.eta_ts||'-'}</div>`;
  }
  function updateTipIfSelected(orders){
    if(!selectedOrderId || !tipEl) return;
    const o = orders.find(x=> x.order_id===selectedOrderId);
    if(!o){ tipEl.remove(); tipEl=null; selectedOrderId=null; return; }
    tipEl.innerHTML = tipHtml(o);
    const t = tokensById[selectedOrderId];
    if(t && t.el){
      tipEl.style.left=(parseFloat(t.el.style.left||'0')+30)+'%';
    }
  }
  function ensureToken(order){
    const id = order.order_id;
    const laneN = laneName(order.line_id);
    let t = tokensById[id];
    if(!t){
      const lane = lanesCache.find(l=> l.getAttribute('data-line')===laneN);
      if(!lane) return;
      const track = lane.querySelector('.lane-track');
      const el = document.createElement('div');
      el.className='token';
      el.style.position='absolute';
      el.style.top='30px';
      el.style.left='0%';
      el.style.width='28px';
      el.style.height='28px';
      el.style.borderRadius='50%';
      el.style.border='1px solid #333';
      el.style.background='#fff';
      el.style.display='flex';
      el.style.alignItems='center';
      el.style.justifyContent='center';
      el.style.fontSize='18px';
      el.textContent='🧺';
      el.style.color=tokenColor(order.state);
      el.onclick=()=>showTip(order, el);
      track.appendChild(el);
      t = tokensById[id] = { el, x:0, targetX: targetPos(order.state), laneName: laneN, order };
    }else{
      t.order = order;
      t.targetX = targetPos(order.state);
      t.el.style.color = tokenColor(order.state);
    }
  }
  function setTokens(orders){
    // add/update
    orders.slice(0,12).forEach(o=> ensureToken(o));
    // remove missing
    Object.keys(tokensById).forEach(id=>{
      if(!orders.find(o=> o.order_id===id)){
        const t = tokensById[id];
        if(t && t.el && t.el.parentElement) t.el.parentElement.removeChild(t.el);
        delete tokensById[id];
      }
    });
    updateTipIfSelected(orders);
  }
  function lerp(a,b,t){ return a+(b-a)*t; }
  function step(){
    Object.values(tokensById).forEach(t=>{
      t.x = lerp(t.x, t.targetX, 0.06);
      t.el.style.left = t.x+'%';
    });
    rafId = requestAnimationFrame(step);
  }
  function makeSimOrders(lines){
    const blockedBoya = !!(lines||[]).find(l=> (l.line_name||l.name)==='Boya Hattı' && (l.status||'')==='Down');
    const now = Date.now();
    const mk = (id,lid,sid,state,energy,co2,risk,rc,note)=>({
      order_id:id,line_id:lid,station_id:sid,state,
      start_ts:new Date(now-40*60000).toISOString(),
      updated_ts:new Date(now).toISOString(),
      elapsed_min:40,energy_kwh:energy,co2e_kg:co2,
      scrap_units:0,rework_units:0,eta_ts:new Date(now+60*60000).toISOString(),
      risk,reason_code:rc,payload:{note}
    });
    const arr = [
      mk('SIM-0001',3,3,'moving',4.0,1.8,'ok','', 'Montaj akışta'),
      mk('SIM-0002',3,3,'processing',4.5,2.0,'ok','RC12','Montaj istasyonda'),
      mk('SIM-0003',1,1,'moving',3.1,1.3,'ok','', 'Metal akışta'),
      mk('SIM-0004',5,1,'waiting',2.2,1.0,'at_risk','RC10','Paketleme bekliyor')
    ];
    if(blockedBoya){
      arr.push(mk('SIM-0005',2,2,'down',2.8,1.2,'late','RC11','Boya arıza'));
      arr.push(mk('SIM-0006',2,2,'blocked',2.0,0.9,'at_risk','RC11','Boya bekliyor'));
    }else{
      arr.push(mk('SIM-0005',2,2,'moving',2.3,1.0,'ok','', 'Boya akışta'));
    }
    return arr;
  }
  async function pollOnce(simBadge){
    const [lines, orders] = await Promise.all([API.lines(), API.orders()]);
    const useSim = !orders.length;
    const dataOrders = useSim ? makeSimOrders(lines) : orders;
    setTokens(dataOrders);
    if(simBadge){ simBadge.style.display = useSim ? 'inline-block' : 'none'; }
  }
  // expose enhanced start that keeps single raf/interval
  const origStart = window.FLOW_LIVE.start;
  window.FLOW_LIVE.start = async function(domHost, sidePanel){
    if(started) return;
    started = true;
    build(domHost);
    const simBadge = document.getElementById('simBadge');
    await pollOnce(simBadge);
    if(!rafId) step();
    setInterval(()=>{ pollOnce(simBadge); }, 3000);
  };
})();
// PATCH END flow_live-enhance


// PATCH START tip-clamp
(function(){
  // Bubble/tooltip ekranda taşmasın (iPad Safari safe)
  function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }

  // tokenEl: clicked token, tipEl: created bubble (absolute)
  window.__ZERO_CLAMP_TIP = function(tokenEl, tipEl){
    try{
      if(!(tokenEl && tipEl)) return;

      // tip container = token parent (lane-track) olmalı
      var container = tokenEl.parentElement;
      if(!container) return;

      var cr = container.getBoundingClientRect();
      var tok = tokenEl.getBoundingClientRect();

      // token'a göre başlangıç konumu (px)
      var left = (tok.left - cr.left) + 36;  // token sağında
      var top  = (tok.top  - cr.top)  - 6;   // biraz yukarı

      // ölçüleri güvenli al
      var w = tipEl.offsetWidth  || 240;
      var h = tipEl.offsetHeight || 140;

      // sağdan taşıyorsa sola geçir
      if(left + w > cr.width - 8){
        left = (tok.left - cr.left) - w - 12;
      }

      // alttan taşıyorsa yukarı al
      if(top + h > cr.height - 8){
        top = cr.height - h - 8;
      }

      // üstten taşıyorsa aşağı al
      if(top < 8) top = 8;

      // clamp
      var maxLeft = Math.max(8, cr.width - w - 8);
      var maxTop  = Math.max(8, cr.height - h - 8);
      left = clamp(left, 8, maxLeft);
      top  = clamp(top,  8, maxTop);

      tipEl.style.left = left + "px";
      tipEl.style.top  = top + "px";
    }catch(e){}
  };
})();
// PATCH END tip-clamp


// PATCH START flow_live-enhance-v2
(function(){
  if(!window.FLOW_LIVE) return;
  if(!window.AUTH || typeof window.AUTH.get !== 'function'){
    try{ console.warn('[Zero@Factory] AUTH.get missing; skip flow_live enhance'); }catch(e){}
    return;
  }

  const API = {
    async lines(){ try{ const r=await AUTH.get('/api/v1/lines'); return (r.lines||[]); }catch(e){ return []; } },
    async orders(){ try{ const r=await AUTH.get('/api/v1/orders'); return (r.orders||[]); }catch(e){ return []; } }
  };

  const laneName = (lid)=>({1:'Metal & Şase',2:'Boya Hattı',3:'Montaj',4:'Final Test',5:'Paketleme & Sevkiyat'})[lid]||'Montaj';
  const tokenColor = (st)=> st==='down' ? '#dc2626' : st==='blocked' ? '#f97316' : st==='waiting' ? '#f59e0b' : '#16a34a';
  const targetPos = (st)=> st==='moving' ? 80 : st==='processing' ? 50 : st==='waiting' ? 20 : st==='blocked' ? 35 : st==='down' ? 10 : 15;

  let tokensById = {};     // {order_id: {el, x, targetX, laneName, order}}
  let lanesCache = [];     // DOM lanes
  let tipEl = null;
  let selectedOrderId = null;
  let rafId = null;
  let started = false;

  function clampTip(tokenEl, tipEl){
    try{
      // fixed-position bubble: clamp within viewport
      tipEl.style.position = 'fixed';
      tipEl.style.maxWidth = '280px';
      tipEl.style.zIndex = '9999';

      // compute desired position near token
      const rect = tokenEl.getBoundingClientRect();
      const vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
      const vh = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

      // set temp to measure
      tipEl.style.left = '0px';
      tipEl.style.top  = '0px';

      const tr = tipEl.getBoundingClientRect();
      const w = tr.width  || 260;
      const h = tr.height || 140;

      let left = rect.left + rect.width + 10;
      let top  = rect.top  - 8;

      // flip left if overflow
      if(left + w > vw - 10) left = rect.left - w - 10;
      if(left < 10) left = 10;

      // clamp top
      if(top + h > vh - 10) top = vh - h - 10;
      if(top < 10) top = 10;

      tipEl.style.left = left + 'px';
      tipEl.style.top  = top  + 'px';
    }catch(e){}
  }

  function build(host){
    host.innerHTML = '';
    lanesCache = ['Metal & Şase','Boya Hattı','Montaj','Final Test','Paketleme & Sevkiyat'].map(name=>{
      const lane = document.createElement('div');
      lane.className = 'lane';
      lane.setAttribute('data-line', name);
      lane.style.border = '1px solid #e0e0e0';
      lane.style.borderRadius = '8px';
      lane.style.padding = '8px';
      lane.style.minHeight = '140px';
      lane.innerHTML = `
        <div style="font-weight:600;margin-bottom:6px">${name}</div>
        <div class="lane-track" style="position:relative;height:90px;background:#fafbfc;border:1px solid #e0e0e0;border-radius:6px;overflow:hidden"></div>
      `;
      host.appendChild(lane);
      return lane;
    });
  }

  function tipHtml(o){
    const ln = laneName(o.line_id);
    const stName = 'Station ' + (o.station_id || '-');
    const eta = o.eta_ts ? new Date(o.eta_ts).toLocaleTimeString('tr-TR') : '-';
    const up  = o.updated_ts ? new Date(o.updated_ts).toLocaleTimeString('tr-TR') : '-';
    return `
      <div style="font-weight:700;margin-bottom:6px">${o.order_id}</div>
      <div style="color:#444;margin-bottom:6px">${ln} • ${stName}</div>
      <div style="margin-bottom:6px">State: <strong>${o.state}</strong> • Risk: <strong>${o.risk||'-'}</strong>${o.reason_code? ' • '+o.reason_code:''}</div>
      <div style="margin-bottom:6px">Elapsed: ${Math.round(o.elapsed_min||0)}m • Updated: ${up}</div>
      <div style="margin-bottom:6px">Energy: <strong>${(o.energy_kwh||0)}</strong> kWh • CO₂: <strong>${(o.co2e_kg||0)}</strong> kg</div>
      <div style="margin-bottom:6px">Scrap: ${o.scrap_units||0} • Rework: ${o.rework_units||0}</div>
      <div>ETA: ${eta}</div>
    `;
  }

  function showTip(o, tokenEl){
    try{
      if(tipEl && tipEl.parentElement) tipEl.remove();
    }catch(e){}
    selectedOrderId = o.order_id;

    tipEl = document.createElement('div');
    tipEl.className = 'token-tip';
    tipEl.style.background = '#ffffff';
    tipEl.style.border = '1px solid #e0e0e0';
    tipEl.style.borderRadius = '10px';
    tipEl.style.padding = '10px 12px';
    tipEl.style.fontSize = '.85rem';
    tipEl.style.boxShadow = '0 10px 25px rgba(0,0,0,.10)';
    tipEl.style.pointerEvents = 'auto';
    tipEl.innerHTML = tipHtml(o);

    document.body.appendChild(tipEl);
    clampTip(tokenEl, tipEl);

    // close on outside click
    setTimeout(()=>{
      const onDoc = (ev)=>{
        try{
          if(!tipEl) return;
          if(ev && ev.target && (tipEl.contains(ev.target) || tokenEl.contains(ev.target))) return;
          tipEl.remove(); tipEl=null; selectedOrderId=null;
          document.removeEventListener('pointerdown', onDoc, true);
        }catch(e){}
      };
      document.addEventListener('pointerdown', onDoc, true);
    }, 0);
  }

  function updateTipIfSelected(orders){
    if(!selectedOrderId || !tipEl) return;
    const o = orders.find(x=> x.order_id === selectedOrderId);
    if(!o){ try{ tipEl.remove(); }catch(e){} tipEl=null; selectedOrderId=null; return; }
    tipEl.innerHTML = tipHtml(o);
    const t = tokensById[selectedOrderId];
    if(t && t.el) clampTip(t.el, tipEl);
  }

  function ensureToken(order){
    const id = order.order_id;
    const laneN = laneName(order.line_id);
    let t = tokensById[id];

    if(!t){
      const lane = lanesCache.find(l => l.getAttribute('data-line') === laneN);
      if(!lane) return;
      const track = lane.querySelector('.lane-track');
      const el = document.createElement('div');
      el.className = 'token';
      el.style.position = 'absolute';
      el.style.top = '30px';
      el.style.left = '0%';
      el.style.width = '28px';
      el.style.height = '28px';
      el.style.borderRadius = '50%';
      el.style.border = '1px solid rgba(0,0,0,.35)';
      el.style.background = '#fff';
      el.style.display = 'flex';
      el.style.alignItems = 'center';
      el.style.justifyContent = 'center';
      el.style.fontSize = '18px';
      el.textContent = '🧺';
      el.style.color = tokenColor(order.state);
      el.style.cursor = 'pointer';
      el.onclick = ()=> showTip(order, el);
      track.appendChild(el);

      t = tokensById[id] = { el, x:0, targetX: targetPos(order.state), laneName: laneN, order };
    }else{
      t.order = order;
      t.targetX = targetPos(order.state);
      t.el.style.color = tokenColor(order.state);
    }
  }

  function setTokens(orders){
    orders.slice(0, 14).forEach(o=> ensureToken(o));

    Object.keys(tokensById).forEach(id=>{
      if(!orders.find(o=> o.order_id === id)){
        const t = tokensById[id]
        try{ if(t && t.el && t.el.parentElement) t.el.parentElement.removeChild(t.el); }catch(e){}
        delete tokensById[id];
      }
    });

    updateTipIfSelected(orders);
  }

  function lerp(a,b,t){ return a + (b-a)*t; }

  function step(){
    Object.values(tokensById).forEach(t=>{
      t.x = lerp(t.x, t.targetX, 0.06);
      t.el.style.left = t.x + '%';
    });
    rafId = requestAnimationFrame(step);
  }

  function makeSimOrders(lines){
    const boyaDown = !!(lines||[]).find(l => (l.line_name||l.name)==='Boya Hattı' && (l.status||'')==='Down');
    const now = Date.now();
    const mk = (id,lid,sid,state,energy,co2,risk,rc,note)=>({
      order_id:id,line_id:lid,station_id:sid,state,
      start_ts:new Date(now-40*60000).toISOString(),
      updated_ts:new Date(now).toISOString(),
      elapsed_min:40,energy_kwh:energy,co2e_kg:co2,
      scrap_units:0,rework_units:0,eta_ts:new Date(now+60*60000).toISOString(),
      risk,reason_code:rc,payload:{note}
    });
    const arr = [
      mk('SIM-0001',1,1,'moving',3.1,1.3,'ok','', 'Metal akışta'),
      mk('SIM-0002',3,3,'processing',4.5,2.0,'ok','RC12','Montaj istasyonda'),
      mk('SIM-0003',3,3,'moving',4.0,1.8,'ok','', 'Montaj akışta'),
      mk('SIM-0004',5,1,'waiting',2.2,1.0,'at_risk','RC10','Paketleme bekliyor')
    ];
    if(boyaDown){
      arr.push(mk('SIM-0005',2,2,'down',2.8,1.2,'late','RC11','Boya arıza'));
      arr.push(mk('SIM-0006',2,2,'blocked',2.0,0.9,'at_risk','RC11','Boya bekliyor'));
    }else{
      arr.push(mk('SIM-0005',2,2,'moving',2.3,1.0,'ok','', 'Boya akışta'));
    }
    return arr;
  }

  async function pollOnce(simBadge){
    const [lines, orders] = await Promise.all([API.lines(), API.orders()]);
    const useSim = !orders.length;
    const dataOrders = useSim ? makeSimOrders(lines) : orders;
    setTokens(dataOrders);
    if(simBadge) simBadge.style.display = useSim ? 'inline-block' : 'none';
  }

  const origStart = window.FLOW_LIVE.start;
  window.FLOW_LIVE.start = async function(domHost, sidePanel){
    if(started) return;
    started = true;

    build(domHost);

    // Optional: keep original sidePanel behavior if needed
    // (we don't break it; dashboard already fills Active Orders separately)

    const simBadge = document.getElementById('simBadge');
    await pollOnce(simBadge);

    if(!rafId) step();
    setInterval(()=>{ pollOnce(simBadge); }, 3000);
  };

  try{ console.log('[Zero@Factory] flow_live-enhance-v2 active'); }catch(e){}
})();
// PATCH END flow_live-enhance-v2

