(function(){
  function gen(n, start, vol, drift, min, max){
    const a=[]; let v=start;
    for(let i=0;i<n;i++){
      v = v + (Math.random()-0.5)*vol + drift;
      v = Math.max(min, Math.min(max, v));
      a.push(Number(v.toFixed(1)));
    }
    return a;
  }
  function labels(n){
    const out=[];
    for(let i=n-1;i>=0;i--) out.push(i===0 ? "now" : ("-"+i+"h"));
    return out.reverse();
  }

  function render(){
    const c1=document.getElementById("chartPower");
    const c2=document.getElementById("chartTemp");
    if(!c1 || !c2) return;

    if(!window.Chart){
      console.warn("Trendler: Chart.js missing");
      return;
    }

    const n=12;
    const xs=labels(n);

    // Mock ama “gerçekçi” aralıklar
    const power = gen(n, 28, 3.2, 0.2, 18, 42);   // kWh/h
    const temp  = gen(n, 39, 1.8, 0.05, 30, 55);  // °C

    try{ if(c1.__ch) c1.__ch.destroy(); }catch(e){}
    try{ if(c2.__ch) c2.__ch.destroy(); }catch(e){}

    c1.__ch = new Chart(c1.getContext("2d"), {
      type: "line",
      data: { labels: xs, datasets: [{ label:"Power (kWh/h)", data: power, tension:0.35, borderWidth:2, pointRadius:2 }] },
      options: { responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:true } }, scales:{ y:{ beginAtZero:false } } }
    });

    c2.__ch = new Chart(c2.getContext("2d"), {
      type: "line",
      data: { labels: xs, datasets: [{ label:"Temp (°C)", data: temp, tension:0.35, borderWidth:2, pointRadius:2 }] },
      options: { responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:true } }, scales:{ y:{ beginAtZero:false } } }
    });
  }

  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", render);
  else render();

  window.__renderTrendsCharts = render;
})();
