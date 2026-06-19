/* ═══════════════════════════════════════════════
   MEDAI — app.js
═══════════════════════════════════════════════ */

// ── State ─────────────────────────────────────
let selectedSymptoms = new Set();
let csvData          = null;

// ── DOM refs ──────────────────────────────────
const $ = id => document.getElementById(id);

// ── Init ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initSymptomChecker();
  initCSVUpload();
  initGroupExplorer();
  $('symptomCount').textContent = ALL_SYMPTOMS.length.toLocaleString();
});

/* ══════════════════════════════════════════════
   NAV / TAB SWITCHING
══════════════════════════════════════════════ */
function initNav() {
  const navItems   = document.querySelectorAll('.nav-item');
  const breadcrumb = $('breadcrumb');
  const labels     = { symptom: 'Symptom Checker', csv: 'CSV Prediction', explorer: 'Group Explorer' };

  navItems.forEach(btn => {
    btn.addEventListener('click', () => {
      navItems.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const tab = btn.dataset.tab;
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      const panel = $(`tab-${tab}`);
      panel.classList.add('active');
      // Re-trigger animation
      panel.style.animation = 'none';
      panel.offsetHeight;
      panel.style.animation = '';

      breadcrumb.textContent = labels[tab];
      closeSidebar();
    });
  });

  // Mobile menu
  $('menuBtn').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
}

/* ══════════════════════════════════════════════
   TAB 1 — SYMPTOM CHECKER
══════════════════════════════════════════════ */
function initSymptomChecker() {
  const searchInput = $('symptomSearch');
  const list        = $('symptomList');

  renderSymptomList('');

  searchInput.addEventListener('input', () => {
    renderSymptomList(searchInput.value.toLowerCase().trim());
  });

  $('btnPredict').addEventListener('click', runSymptomCheck);
}

function renderSymptomList(query) {
  const list     = $('symptomList');
  const filtered = query
    ? ALL_SYMPTOMS.filter(s => s.includes(query)).slice(0, 80)
    : ALL_SYMPTOMS.slice(0, 80);

  list.innerHTML = filtered.map(sym => `
    <span class="sym-chip ${selectedSymptoms.has(sym) ? 'selected' : ''}"
          data-sym="${sym}">${sym.replace(/_/g,' ')}</span>
  `).join('');

  list.querySelectorAll('.sym-chip').forEach(chip => {
    chip.addEventListener('click', () => toggleSymptom(chip.dataset.sym));
  });
}

function toggleSymptom(sym) {
  if (selectedSymptoms.has(sym)) {
    selectedSymptoms.delete(sym);
  } else {
    selectedSymptoms.add(sym);
  }
  renderSymptomList($('symptomSearch').value.toLowerCase().trim());
  renderSelectedTags();
}

function renderSelectedTags() {
  const container = $('selectedTags');
  if (selectedSymptoms.size === 0) {
    container.innerHTML = '<span class="tag-empty">No symptoms selected yet</span>';
    return;
  }
  container.innerHTML = [...selectedSymptoms].map(sym => `
    <span class="sel-tag">
      ${sym.replace(/_/g,' ')}
      <span class="sel-tag-remove" data-sym="${sym}">✕</span>
    </span>
  `).join('');

  container.querySelectorAll('.sel-tag-remove').forEach(btn => {
    btn.addEventListener('click', () => toggleSymptom(btn.dataset.sym));
  });
}

async function runSymptomCheck() {
  if (selectedSymptoms.size === 0) {
    shakeElement($('btnPredict'));
    return;
  }

  const resultsArea = $('resultsArea');
  resultsArea.innerHTML = loadingHTML();

  try {
    const res  = await fetch('/api/symptom-check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms: [...selectedSymptoms] })
    });
    const data = await res.json();
    renderSymptomResults(data);
  } catch (e) {
    resultsArea.innerHTML = errorHTML('Failed to connect to the server.');
  }
}

function renderSymptomResults(data) {
  const max = data.results[0]?.percentage || 1;

  const cardsHTML = data.results.map((r, i) => `
    <div class="disease-card" style="animation-delay:${i * 0.07}s">
      <div class="disease-rank">#${i+1}</div>
      <div class="disease-name">${r.disease}</div>
      <div class="disease-pct-wrap">
        <div class="disease-pct">${r.percentage}%</div>
        <div class="disease-bar-bg">
          <div class="disease-bar" style="width:${(r.percentage/max*100).toFixed(1)}%"></div>
        </div>
      </div>
    </div>
  `).join('');

  $('resultsArea').innerHTML = `
    <div class="cluster-banner">
      <div class="cluster-banner-icon">${data.cluster_icon}</div>
      <div class="cluster-banner-text">
        <div class="cluster-label">Predicted Disease Group</div>
        <div class="cluster-name">${data.cluster_name}</div>
      </div>
    </div>
    <div class="disease-results">
      <div class="disease-results-title">Possible Conditions · Ranked by Match</div>
      ${cardsHTML}
    </div>
  `;
}

/* ══════════════════════════════════════════════
   TAB 2 — CSV PREDICTION
══════════════════════════════════════════════ */
function initCSVUpload() {
  const zone   = $('uploadZone');
  const input  = $('csvFile');

  zone.addEventListener('click', () => input.click());
  $('browseBtn').addEventListener('click', e => { e.stopPropagation(); input.click(); });

  input.addEventListener('change', () => {
    if (input.files[0]) uploadCSV(input.files[0]);
  });

  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) uploadCSV(file);
  });

  $('downloadBtn').addEventListener('click', downloadResults);
}

async function uploadCSV(file) {
  const zone = $('uploadZone');
  zone.innerHTML = `
    <div class="upload-inner">
      <div class="loading"><div class="spinner"></div> Analyzing ${file.name}…</div>
    </div>`;

  const fd = new FormData();
  fd.append('file', file);

  try {
    const res  = await fetch('/api/csv-predict', { method: 'POST', body: fd });
    const data = await res.json();
    csvData = data;
    renderCSVResults(data);
  } catch (e) {
    zone.innerHTML = defaultUploadInner();
    alert('Upload failed. Please try again.');
  }
}

function renderCSVResults(data) {
  $('uploadZone').classList.add('hidden');
  const csvResults = $('csvResults');
  csvResults.classList.remove('hidden');

  // Stats
  $('csvStats').innerHTML = `
    <div class="stat-card accent-green">
      <div class="stat-card-label">Patients Analysed</div>
      <div class="stat-card-value">${data.stats.total_patients}</div>
      <div class="stat-card-sub">Total records processed</div>
    </div>
    <div class="stat-card accent-blue">
      <div class="stat-card-label">Symptoms Matched</div>
      <div class="stat-card-value">${data.stats.total_matched}</div>
      <div class="stat-card-sub">Across all patients</div>
    </div>
    <div class="stat-card accent-pink">
      <div class="stat-card-label">Disease Groups</div>
      <div class="stat-card-value">${data.stats.unique_groups}</div>
      <div class="stat-card-sub">Unique categories found</div>
    </div>
  `;

  // Table
  $('resultsBody').innerHTML = data.rows.map(r => `
    <tr>
      <td class="td-patient">${r.patient}</td>
      <td class="td-matched">${r.matched_symptoms}</td>
      <td><span class="td-category">${r.disease_category}</span></td>
      <td style="font-size:.8rem; color:var(--text-2)">${r.possible_diseases}</td>
    </tr>
  `).join('');
}

function downloadResults() {
  if (!csvData) return;
  const headers = ['Patient','Matched Symptoms','Disease Category','Possible Diseases'];
  const rows    = csvData.rows.map(r =>
    [r.patient, r.matched_symptoms, r.disease_category, `"${r.possible_diseases}"`].join(',')
  );
  const csv  = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = 'medai_predictions.csv'; a.click();
  URL.revokeObjectURL(url);
}

function defaultUploadInner() {
  return `
    <div class="upload-inner">
      <div class="upload-icon">⬆</div>
      <p class="upload-title">Drop your CSV here</p>
      <p class="upload-hint">or <span class="link" id="browseBtn">browse files</span></p>
      <p class="upload-format">Columns: patient, Symptom_1, Symptom_2…</p>
    </div>`;
}

/* ══════════════════════════════════════════════
   TAB 3 — GROUP EXPLORER
══════════════════════════════════════════════ */
function initGroupExplorer() {
  document.querySelectorAll('.group-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.group-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      loadGroupData(parseInt(card.dataset.cluster));
    });
  });
}

async function loadGroupData(clusterNum) {
  const results = $('explorerResults');
  results.classList.remove('hidden');
  $('explorerIcon').textContent = '';
  $('explorerName').textContent = 'Loading…';
  $('symptomsChart').innerHTML  = loadingHTML('small');
  $('diseaseList').innerHTML    = '';

  try {
    const res  = await fetch('/api/group-explorer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cluster_num: clusterNum })
    });
    const data = await res.json();

    $('explorerIcon').textContent = CLUSTER_ICONS[clusterNum] || '🏥';
    $('explorerName').textContent = CLUSTER_NAMES[clusterNum] || 'Unknown Group';

    // Symptom bar chart
    const symptoms = Object.entries(data.top_symptoms);
    const maxSym   = symptoms[0]?.[1] || 1;
    $('symptomsChart').innerHTML = symptoms.map(([sym, val]) => `
      <div class="bar-row">
        <div class="bar-label" title="${sym}">${sym.replace(/_/g,' ')}</div>
        <div class="bar-track">
          <div class="bar-fill" style="width:${(val/maxSym*100).toFixed(1)}%"></div>
        </div>
        <div class="bar-val">${(val*100).toFixed(0)}%</div>
      </div>
    `).join('');

    // Disease list
    const diseases = Object.entries(data.top_diseases);
    $('diseaseList').innerHTML = diseases.map(([dis, cnt], i) => `
      <div class="dis-item" style="animation-delay:${i * 0.05}s">
        <div class="dis-dot"></div>
        <span>${dis}</span>
      </div>
    `).join('');

    results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (e) {
    $('explorerName').textContent = 'Failed to load data.';
  }
}

/* ══════════════════════════════════════════════
   HELPERS
══════════════════════════════════════════════ */
function loadingHTML(size = 'normal') {
  const pad = size === 'small' ? '32px' : '80px';
  return `<div class="loading" style="padding:${pad}"><div class="spinner"></div> Analyzing…</div>`;
}

function errorHTML(msg) {
  return `<div class="loading" style="color:var(--accent-3)">⚠ ${msg}</div>`;
}

function shakeElement(el) {
  el.style.animation = 'none';
  el.offsetHeight;
  el.style.animation = 'shake .4s ease';
  setTimeout(() => { el.style.animation = ''; }, 400);
}

// Shake keyframes (injected)
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
@keyframes shake {
  0%,100% { transform: translateX(0); }
  20%      { transform: translateX(-6px); }
  40%      { transform: translateX(6px); }
  60%      { transform: translateX(-4px); }
  80%      { transform: translateX(4px); }
}`;
document.head.appendChild(shakeStyle);
