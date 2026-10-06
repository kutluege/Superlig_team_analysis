"""Etkileşimli pano şablonu. `/*__DATA__*/null` yerine JSON veri gömülür.

Sayfa gövdesi doctype/html/head etiketleri olmadan yazılır (Artifact
yayınında bunları sarmalayıcı ekler); depodaki `reports/pano.html` için
viz.dashboard() aynı içeriği tam bir HTML belgesine sarar.
"""

TEMPLATE = r"""<title>Süper Lig Sıralama Panosu</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
/* Düzen: tek sütun, puan tablosu dilinde satırlar; üstte filtre şeridi, altta veri kalitesi. */
:root {
  --bg: #f6f7f4;
  --panel: #ffffff;
  --ink: #15181b;
  --ink-2: #4f5551;
  --muted: #858b86;
  --grid: #e3e6e1;
  --zebra: #f1f3ef;
  --bar: #2a78d6;
  --bar-soft: #cde2fb;
  --focus: #1c5cab;
  --chip-on: #15181b;
  --chip-on-ink: #ffffff;
  --logo-chip: transparent;
  --warn-bg: #fff4dc;
  --warn-ink: #6b4a00;
  --display: "Barlow Condensed", "Arial Narrow", "Roboto Condensed", sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #121513; --panel: #1a1d1b; --ink: #f2f4f1; --ink-2: #c3c8c2; --muted: #8e958f;
    --grid: #2c312d; --zebra: #1f2320; --bar: #3987e5; --bar-soft: #184f95; --focus: #86b6ef;
    --chip-on: #f2f4f1; --chip-on-ink: #121513; --logo-chip: #e9ece7;
    --warn-bg: #3a2f12; --warn-ink: #f3d68a; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #121513; --panel: #1a1d1b; --ink: #f2f4f1; --ink-2: #c3c8c2; --muted: #8e958f;
  --grid: #2c312d; --zebra: #1f2320; --bar: #3987e5; --bar-soft: #184f95; --focus: #86b6ef;
  --chip-on: #f2f4f1; --chip-on-ink: #121513; --logo-chip: #e9ece7;
  --warn-bg: #3a2f12; --warn-ink: #f3d68a; color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 15px; line-height: 1.5; }
.wrap { max-width: 1080px; margin: 0 auto; padding-inline: 20px; padding-block: 28px 56px; display: grid; gap: 40px; }
h1, h2 { font-family: var(--display); font-weight: 700; letter-spacing: .01em; text-wrap: balance; margin: 0; line-height: 1.05; }
h1 { font-size: clamp(2.2rem, 5vw, 3.4rem); text-transform: uppercase; }
h2 { font-size: 1.7rem; text-transform: uppercase; }
p { margin: 0; }
.nw { white-space: nowrap; }
.lede { color: var(--ink-2); max-width: 68ch; margin-top: 10px; }
.meta { display: flex; flex-wrap: wrap; gap: 8px 22px; margin-top: 16px; font-size: .9rem; color: var(--ink-2); font-variant-numeric: tabular-nums; }
.meta b { font-family: var(--display); font-size: 1.35rem; color: var(--ink); font-weight: 600; margin-right: 4px; }
section { display: grid; gap: 14px; min-width: 0; }
.sec-head { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 6px 16px; }
.sec-note { color: var(--muted); font-size: .85rem; }
.controls { display: grid; gap: 10px; background: var(--panel); border: 1px solid var(--grid); border-radius: 10px; padding: 12px 14px; }
.ctl-row { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.ctl-label { font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); width: 64px; flex: none; }
.chip { font: inherit; font-size: .85rem; border: 1px solid var(--grid); background: transparent; color: var(--ink-2); padding: 4px 10px; border-radius: 999px; cursor: pointer; font-variant-numeric: tabular-nums; }
.chip:hover { border-color: var(--muted); color: var(--ink); }
.chip[aria-pressed="true"] { background: var(--chip-on); color: var(--chip-on-ink); border-color: var(--chip-on); }
.chip:focus-visible, .cell:focus-visible, .row:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
.board { background: var(--panel); border: 1px solid var(--grid); border-radius: 10px; padding: 8px 0; }
.board-cap { display: flex; justify-content: space-between; gap: 12px; padding: 6px 16px 10px; color: var(--muted); font-size: .8rem; border-bottom: 1px solid var(--grid); }
.row { display: grid; grid-template-columns: 30px 30px minmax(110px, 210px) 1fr; align-items: center; gap: 10px; padding: 4px 16px; min-height: 36px; }
.row:nth-child(even) { background: var(--zebra); }
.rk { font-family: var(--display); font-weight: 600; font-size: 1.1rem; text-align: right; color: var(--ink-2); font-variant-numeric: tabular-nums; }
.logo { width: 28px; height: 28px; border-radius: 50%; background: var(--logo-chip); display: grid; place-items: center; }
.logo img { width: 24px; height: 24px; object-fit: contain; display: block; }
.nm { font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.nm small { color: var(--muted); font-weight: 400; margin-left: 6px; font-size: .78rem; }
.track { display: flex; align-items: center; gap: 8px; min-width: 0; }
.bar { height: 18px; background: var(--bar); border-radius: 0 4px 4px 0; min-width: 2px; flex: none; transition: width .35s ease; }
.bar.neg { background: var(--bar-soft); }
.val { font-variant-numeric: tabular-nums; font-weight: 600; font-size: .9rem; white-space: nowrap; }
.empty { padding: 28px 16px; display: grid; gap: 8px; color: var(--ink-2); max-width: 70ch; }
.empty strong { color: var(--ink); font-family: var(--display); font-size: 1.3rem; font-weight: 600; text-transform: uppercase; }
.tip { position: fixed; z-index: 10; pointer-events: none; background: var(--panel); color: var(--ink); border: 1px solid var(--grid); border-radius: 8px; padding: 10px 12px; font-size: .82rem; box-shadow: 0 6px 24px rgba(0,0,0,.14); min-width: 180px; font-variant-numeric: tabular-nums; }
.tip h4 { margin: 0 0 6px; font-family: var(--display); font-size: 1.05rem; font-weight: 600; }
.tip dl { display: grid; grid-template-columns: auto auto; gap: 2px 14px; margin: 0; }
.tip dt { color: var(--muted); } .tip dd { margin: 0; text-align: right; }
.scroll { overflow-x: auto; background: var(--panel); border: 1px solid var(--grid); border-radius: 10px; }
.heat { border-collapse: separate; border-spacing: 3px; padding: 8px; font-variant-numeric: tabular-nums; }
.heat th { font-weight: 500; font-size: .78rem; color: var(--muted); padding: 2px 4px; white-space: nowrap; }
.heat th.team { text-align: left; color: var(--ink); font-size: .85rem; font-weight: 500; position: sticky; left: 0; background: var(--panel); z-index: 1; }
.heat th.team span { display: inline-flex; align-items: center; gap: 8px; }
.heat th.team .logo { width: 24px; height: 24px; } .heat th.team .logo img { width: 20px; height: 20px; }
.cell { width: 58px; height: 30px; text-align: center; border-radius: 4px; font-size: .85rem; cursor: default; }
.cell.na { border: 1px dashed var(--grid); }
.legend { display: flex; align-items: center; gap: 8px; font-size: .8rem; color: var(--muted); flex-wrap: wrap; }
.ramp { display: flex; } .ramp i { width: 22px; height: 12px; display: block; }
.ramp i:first-child { border-radius: 3px 0 0 3px; } .ramp i:last-child { border-radius: 0 3px 3px 0; }
.na-key { width: 22px; height: 12px; border: 1px dashed var(--muted); border-radius: 3px; display: inline-block; }
.podium { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
.season { background: var(--panel); border: 1px solid var(--grid); border-radius: 10px; padding: 12px; display: grid; gap: 8px; }
.season h3 { margin: 0; font-family: var(--display); font-size: 1.15rem; font-weight: 600; }
.champ { display: flex; align-items: center; gap: 10px; }
.champ .logo { width: 44px; height: 44px; } .champ .logo img { width: 40px; height: 40px; }
.champ b { display: block; line-height: 1.2; } .champ span { color: var(--muted); font-size: .8rem; }
.runners { display: grid; gap: 4px; font-size: .82rem; color: var(--ink-2); border-top: 1px solid var(--grid); padding-top: 8px; }
.runners div { display: flex; align-items: center; gap: 6px; font-variant-numeric: tabular-nums; }
.runners .logo { width: 20px; height: 20px; } .runners .logo img { width: 17px; height: 17px; }
.runners em { margin-left: auto; font-style: normal; color: var(--muted); }
.quality { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.card { background: var(--panel); border: 1px solid var(--grid); border-radius: 10px; padding: 14px 16px; display: grid; gap: 8px; align-content: start; min-width: 0; }
.card h3 { margin: 0; font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
.notice { background: var(--warn-bg); color: var(--warn-ink); border-radius: 8px; padding: 10px 12px; font-size: .88rem; }
table.mini { border-collapse: collapse; width: 100%; font-size: .82rem; font-variant-numeric: tabular-nums; }
table.mini th, table.mini td { padding: 5px 6px; border-bottom: 1px solid var(--grid); text-align: left; white-space: nowrap; }
table.mini th { color: var(--muted); font-weight: 500; }
.foot { color: var(--muted); font-size: .8rem; max-width: 80ch; }
@media (max-width: 560px) {
  .row { grid-template-columns: 24px 28px minmax(84px, 120px) 1fr; gap: 6px; padding: 4px 10px; }
  .ctl-label { width: 100%; }
  .nm small { display: none; }
}
@media (prefers-reduced-motion: reduce) { .bar { transition: none; } }
</style>

<div class="wrap">
  <header>
    <h1>Süper Lig <span class="nw">2016-17</span> → <span class="nw">2025-26</span></h1>
    <p class="lede">On sezonun maç sonuçlarından hesaplanan sıralamalar. Bir sezon ve bir ölçüt seçin; satırların üzerine gelince takımın o sezonki tüm değerleri görünür.</p>
    <div class="meta" id="meta"></div>
  </header>

  <section aria-labelledby="h-rank">
    <div class="sec-head"><h2 id="h-rank">Sıralama</h2><span class="sec-note" id="rank-note"></span></div>
    <div class="controls">
      <div class="ctl-row" role="group" aria-label="Sezon"><span class="ctl-label">Sezon</span><div class="ctl-row" id="seasons"></div></div>
      <div class="ctl-row" role="group" aria-label="Ölçüt"><span class="ctl-label">Ölçüt</span><div class="ctl-row" id="metrics"></div></div>
    </div>
    <div class="board" id="board"></div>
  </section>

  <section aria-labelledby="h-heat">
    <div class="sec-head"><h2 id="h-heat">Sezon sonu sıraları</h2>
      <div class="legend"><span>1.</span><span class="ramp" id="ramp"></span><span>son sıra</span><span class="na-key"></span><span>ligde değil (NaN)</span></div>
    </div>
    <div class="scroll"><table class="heat" id="heat"></table></div>
  </section>

  <section aria-labelledby="h-pod">
    <div class="sec-head"><h2 id="h-pod">Şampiyonlar ve podyum</h2></div>
    <div class="podium" id="podium"></div>
  </section>

  <section aria-labelledby="h-q">
    <div class="sec-head"><h2 id="h-q">Veri kalitesi</h2></div>
    <div class="quality" id="quality"></div>
    <p class="foot">Kaynaklar: maç sonuçları football-data.co.uk; Sofascore, openfootball/europe ve Transfermarkt (c0ze/super-lig) ile çapraz kontrol. Seyirci ve stadyum kapasitesi Wikipedia sezon sayfaları ve Sofascore. Puanlar maç skorlarından hesaplanmıştır; TFF puan silme cezaları dahil değildir. Amblemler: luukhopman/football-logos; 2021 öncesi düşen yedi kulüp için kulüp renklerinde kısa kodlu yer tutucu rozet kullanılmıştır.</p>
  </section>
</div>
<div class="tip" id="tip" hidden></div>

<script>
const D = /*__DATA__*/null;
const ALL = "Tümü";
const nf = new Intl.NumberFormat("tr-TR");
const METRICS = [
  {k: "puan", l: "Puan", agg: "sum"},
  {k: "galibiyet", l: "Galibiyet", agg: "sum"},
  {k: "atilan_gol", l: "Atılan gol", agg: "sum"},
  {k: "averaj", l: "Averaj", agg: "sum", signed: true},
  {k: "mbp", l: "Maç başı puan", agg: "ratio", dec: 2},
  {k: "ic_saha_puan", l: "İç saha puanı", agg: "sum"},
  {k: "dis_saha_puan", l: "Dış saha puanı", agg: "sum"},
  {k: "yenilen_gol", l: "En az yenilen gol", agg: "sum", asc: true},
  {k: "ort_seyirci", l: "Ort. seyirci", agg: "mean", att: true},
  {k: "kapasite", l: "Stadyum kapasitesi", agg: "last", att: true},
  {k: "doluluk", l: "Doluluk", agg: "mean", att: true, pct: true},
];
const state = {season: D.seasons[D.seasons.length - 1], metric: "puan"};
try { const s = JSON.parse(localStorage.getItem("slpano") || "{}"); if (s.season) state.season = s.season; if (s.metric) state.metric = s.metric; } catch (e) {}

const logo = t => `<span class="logo"><img src="${D.logos[t]}" alt="" width="24" height="24"></span>`;
const fmt = (m, v) => v == null || Number.isNaN(v) ? "–" : m.pct ? (v * 100).toFixed(0) + "%" :
  m.dec ? v.toFixed(m.dec).replace(".", ",") : (m.signed && v > 0 ? "+" : "") + nf.format(Math.round(v));

function rowsFor(season) {
  if (season !== ALL) return D.rows.filter(r => r.sezon === season).map(r => ({...r, mbp: r.puan / r.oynanan, n: 1}));
  const by = {};
  for (const r of D.rows) (by[r.takim] ||= []).push(r);
  return Object.entries(by).map(([t, rs]) => {
    const o = {takim: t, n: rs.length, sezonlar: rs.map(r => r.sezon)};
    for (const k of ["oynanan", "galibiyet", "beraberlik", "maglubiyet", "atilan_gol", "yenilen_gol", "averaj", "puan", "ic_saha_puan", "dis_saha_puan"])
      o[k] = rs.reduce((a, r) => a + (r[k] || 0), 0);
    o.mbp = o.puan / o.oynanan;
    const mean = k => { const v = rs.map(r => r[k]).filter(x => x != null); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null; };
    o.ort_seyirci = mean("ort_seyirci"); o.doluluk = mean("doluluk");
    const caps = rs.map(r => r.kapasite).filter(x => x != null); o.kapasite = caps.length ? caps[caps.length - 1] : null;
    o.sira = mean("sira");
    return o;
  });
}

function chips() {
  const sh = [ALL, ...D.seasons].map(s => `<button class="chip" id="s-${s}" data-s="${s}" aria-pressed="${s === state.season}">${s === ALL ? "10 sezon toplam" : s}</button>`).join("");
  document.getElementById("seasons").innerHTML = sh;
  document.getElementById("metrics").innerHTML = METRICS.map(m => `<button class="chip" id="m-${m.k}" data-m="${m.k}" aria-pressed="${m.k === state.metric}">${m.l}</button>`).join("");
}

function render() {
  const m = METRICS.find(x => x.k === state.metric);
  let rows = rowsFor(state.season);
  const board = document.getElementById("board");
  const note = document.getElementById("rank-note");
  const has = rows.filter(r => r[m.k] != null && !Number.isNaN(r[m.k]));
  if (!has.length) {
    board.innerHTML = `<div class="empty"><strong>${m.l} verisi yok</strong><p>${D.summary.att_reason || "Bu ölçüt için kaynaklarda veri bulunamadı."}</p><p>Veri uydurulmadı: değerler attendance.csv içinde NaN olarak duruyor. Kaynaklara erişim açıldığında veri hattı yeniden çalıştırılınca bu sıralama kendiliğinden dolar.</p></div>`;
    note.textContent = "";
    return;
  }
  if (state.season === ALL && m.k === "mbp") rows = rows.filter(r => r.n >= 3);
  rows = has.filter(r => rows.includes(r));
  rows.sort((a, b) => m.asc ? a[m.k] - b[m.k] : b[m.k] - a[m.k] || (a.sira ?? 99) - (b.sira ?? 99));
  const maxAbs = Math.max(...rows.map(r => Math.abs(r[m.k]))) || 1;
  note.textContent = state.season === ALL
    ? (m.k === "mbp" ? "En az 3 sezon ligde kalan takımlar" : `${rows.length} takım · parantez içinde ligde geçirilen sezon`)
    : `${rows.length} takım · ${state.season}`;
  const cap = `<div class="board-cap"><span>Takım</span><span>${m.l}${m.asc ? " (az olan üstte)" : ""}</span></div>`;
  board.innerHTML = cap + rows.map((r, i) => {
    // çubuk uzunluğu sıfırdan ölçülür; negatif averaj açık tonla çizilir
    const pct = Math.max(0.5, Math.abs(r[m.k]) / maxAbs * 82);
    const neg = r[m.k] < 0 ? " neg" : "";
    return `<div class="row" tabindex="0" data-i="${i}">
      <span class="rk">${i + 1}</span>${logo(r.takim)}
      <span class="nm">${r.takim}${state.season === ALL ? `<small>(${r.n})</small>` : ""}</span>
      <span class="track"><span class="bar${neg}" style="width:${pct}%"></span><span class="val">${fmt(m, r[m.k])}</span></span></div>`;
  }).join("");
  board.querySelectorAll(".row").forEach(el => {
    const r = rows[+el.dataset.i];
    const show = e => tip(e, el, r);
    el.addEventListener("mousemove", show); el.addEventListener("focus", show);
    el.addEventListener("mouseleave", hide); el.addEventListener("blur", hide);
  });
}

const tipEl = document.getElementById("tip");
function tip(e, el, r) {
  const all = state.season === ALL;
  const pairs = [
    [all ? "Sezon sayısı" : "Lig sırası", all ? r.n : r.sira], ["Oynanan", r.oynanan],
    ["G / B / M", `${r.galibiyet} / ${r.beraberlik} / ${r.maglubiyet}`], ["Atılan – yenilen", `${r.atilan_gol} – ${r.yenilen_gol}`],
    ["Puan", r.puan], ["Maç başı puan", r.mbp.toFixed(2).replace(".", ",")],
    ["İç / dış saha puanı", `${r.ic_saha_puan} / ${r.dis_saha_puan}`],
    ["Ort. seyirci", r.ort_seyirci == null ? "veri yok" : nf.format(Math.round(r.ort_seyirci))],
  ];
  tipEl.innerHTML = `<h4>${r.takim} · ${all ? "10 sezon" : state.season}</h4><dl>${pairs.map(([a, b]) => `<dt>${a}</dt><dd>${b}</dd>`).join("")}</dl>`;
  tipEl.hidden = false;
  const box = el.getBoundingClientRect();
  const x = e.clientX ?? box.left + 120, y = e.clientY ?? box.top;
  const tw = tipEl.offsetWidth, th = tipEl.offsetHeight;
  tipEl.style.left = Math.min(window.innerWidth - tw - 8, x + 14) + "px";
  tipEl.style.top = Math.max(8, Math.min(window.innerHeight - th - 8, y + 14)) + "px";
}
function hide() { tipEl.hidden = true; }

const RAMP = ["#0d366b", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4", "#cde2fb"];
function rankColor(rank, n) {
  const f = (rank - 1) / Math.max(1, n - 1);
  return RAMP[Math.min(RAMP.length - 1, Math.floor(f * RAMP.length))];
}
function heat() {
  const nPer = {}; D.rows.forEach(r => nPer[r.sezon] = (nPer[r.sezon] || 0) + 1);
  const by = {};
  D.rows.forEach(r => (by[r.takim] ||= {})[r.sezon] = r);
  const teams = Object.keys(by).sort((a, b) => {
    const na = Object.keys(by[a]).length, nb = Object.keys(by[b]).length;
    if (na !== nb) return nb - na;
    const avg = t => Object.values(by[t]).reduce((s, r) => s + r.sira, 0) / Object.keys(by[t]).length;
    return avg(a) - avg(b);
  });
  let h = `<thead><tr><th></th>${D.seasons.map(s => `<th>${s}</th>`).join("")}</tr></thead><tbody>`;
  for (const t of teams) {
    h += `<tr><th class="team" scope="row"><span>${logo(t)}${t}</span></th>`;
    for (const s of D.seasons) {
      const r = by[t][s];
      if (!r) { h += `<td class="cell na" title="${t} ${s}: Süper Lig'de değil"></td>`; continue; }
      const c = rankColor(r.sira, nPer[s]);
      const dark = RAMP.indexOf(c) < 4;
      h += `<td class="cell" tabindex="0" style="background:${c};color:${dark ? "#fff" : "#0b0b0b"};font-weight:${r.sira === 1 ? 700 : 400}" title="${t} · ${s}: ${r.sira}. sıra, ${r.puan} puan">${r.sira}</td>`;
    }
    h += "</tr>";
  }
  document.getElementById("heat").innerHTML = h + "</tbody>";
  document.getElementById("ramp").innerHTML = RAMP.map(c => `<i style="background:${c}"></i>`).join("");
}

function podium() {
  document.getElementById("podium").innerHTML = D.seasons.map(s => {
    const top = D.rows.filter(r => r.sezon === s).sort((a, b) => a.sira - b.sira).slice(0, 3);
    const [c, ...rest] = top;
    return `<div class="season"><h3>${s}</h3>
      <div class="champ">${logo(c.takim)}<div><b>${c.takim}</b><span>${c.puan} puan</span></div></div>
      <div class="runners">${rest.map(r => `<div><span>${r.sira}.</span>${logo(r.takim)}<span>${r.takim}</span><em>${r.puan}</em></div>`).join("")}</div></div>`;
  }).join("");
}

function quality() {
  const sc = D.conflicts.filter(c => c.alan === "skor");
  const tc = D.conflicts.filter(c => c.alan === "tarih");
  const nT = new Set(D.rows.map(r => r.takim)).size;
  document.getElementById("meta").innerHTML =
    `<span><b>${D.seasons.length}</b>sezon</span><span><b>${nf.format(D.n_matches)}</b>maç</span><span><b>${nT}</b>takım</span><span><b>${sc.length}</b>skor çelişkisi</span>`;
  const conflictRows = sc.map(c => `<tr><td>${c.sezon}</td><td>${c.ev} – ${c.deplasman}</td><td>${c["football-data"] || "–"}</td><td>${c.sofascore || "–"}</td><td>${c.openfootball || "–"}</td><td>${c.transfermarkt || "–"}</td><td><b>${c.secilen}</b></td></tr>`).join("");
  document.getElementById("quality").innerHTML = `
    <div class="card"><h3>Seyirci ve kapasite</h3>
      <div class="notice">Seyircisi olmayan takım-sezon: ${D.summary.att_missing} (2020-21 seyircisiz sezon). Kapasitesi eksik takım-sezon: ${D.summary.cap_missing}.</div>
      <p>Seyirci: european-football-statistics sezon ortalamaları, yoksa Transfermarkt/ESPN maç bazlı ortalamalar (seyirci araştırma ajanı). 2020-21 COVID-19 nedeniyle seyircisiz. 2025-26 kısmi sezon. Kapasite o sezon oynanan stada göre.</p></div>
    <div class="card"><h3>Maç skorları</h3>
      <p>${nf.format(D.n_matches)} maçın tamamı en az iki kaynakla karşılaştırıldı. ${sc.length} maçta kaynaklar farklı skor veriyor; çoğunluğun skoru kullanıldı ve hepsi celiskiler.csv dosyasında duruyor. ${tc.length ? tc.length + " maçta yalnızca tarih farkı var." : ""}</p>
      <p>Eksik maç skoru olan takım-sezon sayısı: ${D.summary.match_missing}.</p></div>
    <div class="card" style="grid-column: 1 / -1"><h3>Skor çelişkileri</h3>
      <div style="overflow-x:auto"><table class="mini"><thead><tr><th>Sezon</th><th>Maç</th><th>football-data</th><th>Sofascore</th><th>openfootball</th><th>Transfermarkt</th><th>Kullanılan</th></tr></thead><tbody>${conflictRows}</tbody></table></div></div>`;
}

document.addEventListener("click", e => {
  const b = e.target.closest(".chip"); if (!b) return;
  if (b.dataset.s) state.season = b.dataset.s;
  if (b.dataset.m) state.metric = b.dataset.m;
  try { localStorage.setItem("slpano", JSON.stringify(state)); } catch (err) {}
  chips(); render();
});
chips(); render(); heat(); podium(); quality();
</script>
"""
