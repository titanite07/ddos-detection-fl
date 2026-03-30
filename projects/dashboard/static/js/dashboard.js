/* ============================================================
   dashboard.js — Real Pipeline Dashboard Logic
   FL-DDoS Monitoring Console  |  Professional B&W Theme
   ============================================================ */

'use strict';

// ── Global State ─────────────────────────────────────────────
const STATE = {
  fl: {}, nodes: {},
  security: { events: [], quarantined_nodes: [] },
  blockchain: { recent_transactions: [] },
  models: {}, history: [], log: [], agents: [],
  status: 'idle', config: {},
  currentPage: 'wizard',
  configured: false,
};

// ── Chart instances ───────────────────────────────────────────
let charts = {};

// ── Chart defaults ────────────────────────────────────────────
function baseOpts(extra) {
  return Object.assign({
    responsive: true, maintainAspectRatio: false, animation: false,
    plugins: { legend: { labels: { color: '#111', font: { size: 12 } } } },
    scales: {
      x: { ticks: { color: '#888', font: { size: 11 } }, grid: { color: '#DDD' } },
      y: { ticks: { color: '#888', font: { size: 11 } }, grid: { color: '#DDD' } }
    }
  }, extra || {});
}

// ══════════════════════════════════════════════
// 1. SPA NAVIGATION
// ══════════════════════════════════════════════
function navigateTo(pageId) {
  STATE.currentPage = pageId;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const page = document.getElementById('page-' + pageId);
  if (page) page.classList.add('active');
  const nav = document.querySelector(`.nav-item[data-page="${pageId}"]`);
  if (nav) nav.classList.add('active');
  renderCurrentPage();
}

function renderCurrentPage() {
  switch (STATE.currentPage) {
    case 'overview':   renderOverview();   break;
    case 'fl':         renderFL();         break;
    case 'nodes':      renderNodes();      break;
    case 'agents':     renderAgents();     break;
    case 'security':   renderSecurity();   break;
    case 'models':     renderModels();     break;
    case 'blockchain': renderBlockchain(); break;
  }
}

// ══════════════════════════════════════════════
// 2. INIT
// ══════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-item').forEach(item =>
    item.addEventListener('click', () => navigateTo(item.dataset.page))
  );
  initCharts();
  connectSocket();
  loadWizardOptions();
  // Update config summary on numeric field or checkbox changes
  ['inp-nodes','inp-rounds','inp-epochs','inp-timesteps'].forEach(id =>
    document.getElementById(id)?.addEventListener('input', updateConfigSummary)
  );
  ['chk-iid','chk-fs'].forEach(id =>
    document.getElementById(id)?.addEventListener('change', updateConfigSummary)
  );
});

// ══════════════════════════════════════════════
// 3. WIZARD
// ══════════════════════════════════════════════
async function loadWizardOptions() {
  try {
    const resp = await fetch('/api/wizard_options');
    const data = await resp.json();

    // ── Dataset dropdown ──────────────────────────────────────────────────
    const dSel = document.getElementById('sel-dataset');
    if (dSel) {
      dSel.innerHTML = data.datasets.map(d =>
        `<option value="${d.id}">${d.label}</option>`
      ).join('');
    }

    // ── Model radio cards (dynamically built) ────────────────────────────
    const mGroup = document.getElementById('radio-model');
    if (mGroup) {
      mGroup.innerHTML = data.models.map((m, i) => `
        <label class="radio-card">
          <input type="radio" name="model" value="${m.id}" ${i === 0 ? 'checked' : ''}/>
          <div class="radio-content">
            <div class="radio-title">${m.label}</div>
            <div class="radio-hint">${m.desc}</div>
          </div>
        </label>`).join('');
      // Re-attach summary update
      mGroup.querySelectorAll('input').forEach(r => r.addEventListener('change', updateConfigSummary));
    }

    // ── Wire data mode radio changes ─────────────────────────────────────
    document.querySelectorAll('input[name="data_mode"]').forEach(r =>
      r.addEventListener('change', () => {
        const mode = r.value;
        const hint = document.getElementById('dataset-hint');
        const group = document.getElementById('dataset-group');
        if (mode === 'live') {
          if (hint) hint.textContent = 'Live mode: dataset used only for evaluation baseline.';
          if (group) group.style.opacity = '0.5';
        } else if (mode === 'hybrid') {
          if (hint) hint.textContent = 'Hybrid: static portion (25%) pulled from selected dataset.';
          if (group) group.style.opacity = '1';
        } else {
          if (hint) hint.textContent = 'Full dataset used for static FL training.';
          if (group) group.style.opacity = '1';
        }
        updateConfigSummary();
      })
    );

    // ── Populate defaults ─────────────────────────────────────────────────
    const def = data.defaults;
    if (dSel) dSel.value = def.dataset || 'cicddos2019_100k';
    document.getElementById('inp-nodes').value    = def.num_nodes;
    document.getElementById('inp-rounds').value   = def.num_rounds;
    document.getElementById('inp-epochs').value   = def.epochs_per_round;
    document.getElementById('inp-timesteps').value = def.timesteps;
    document.getElementById('chk-iid').checked    = def.iid;
    document.getElementById('chk-fs').checked     = def.feature_selection;

    updateConfigSummary();
  } catch (e) {
    console.error('Failed to load wizard options:', e);
  }
}

function getFormModel() {
  const sel = document.querySelector('input[name="model"]:checked');
  return sel ? sel.value : 'cnn_bilstm';
}
function getFormDataMode() {
  const sel = document.querySelector('input[name="data_mode"]:checked');
  return sel ? sel.value : 'static';
}
function getModelLabel() {
  const modelMap = { cnn_bilstm: 'CNN-BiLSTM', transformer: 'Transformer', hybrid: 'Hybrid Ensemble' };
  return modelMap[getFormModel()] || 'CNN-BiLSTM';
}
function getModeLabel() {
  const modeMap = { static: 'Static (Pre-processed)', live: 'Live Traffic (Scapy)', hybrid: 'Hybrid (75% Live / 25% Static)' };
  return modeMap[getFormDataMode()] || 'Static';
}

function updateConfigSummary() {
  const ds  = document.getElementById('sel-dataset')?.options[document.getElementById('sel-dataset').selectedIndex]?.text || '—';
  const nn  = document.getElementById('inp-nodes')?.value || '—';
  const nr  = document.getElementById('inp-rounds')?.value || '—';
  const ep  = document.getElementById('inp-epochs')?.value || '—';
  const ts  = document.getElementById('inp-timesteps')?.value || '—';
  const iid = document.getElementById('chk-iid')?.checked;
  const fs  = document.getElementById('chk-fs')?.checked;

  const el = document.getElementById('config-summary');
  if (el) el.textContent =
    `Data Mode         : ${getModeLabel()}\n` +
    `Dataset           : ${ds}\n` +
    `Model             : ${getModelLabel()}\n` +
    `Nodes             : ${nn}\n` +
    `FL Rounds         : ${nr}\n` +
    `Epochs / Round    : ${ep}\n` +
    `CNN Timesteps     : ${ts}\n` +
    `Data Distribution : ${iid ? 'IID (balanced)' : 'Non-IID (imbalanced)'}\n` +
    `Feature Selection : ${fs ? 'Enabled' : 'Disabled'}`;
}

async function submitConfig(evt) {
  evt.preventDefault();
  const alertEl = document.getElementById('wizard-alert');

  const config = {
    dataset:          document.getElementById('sel-dataset').value,
    data_mode:        getFormDataMode(),
    model:            getFormModel(),
    num_nodes:        parseInt(document.getElementById('inp-nodes').value),
    num_rounds:       parseInt(document.getElementById('inp-rounds').value),
    epochs_per_round: parseInt(document.getElementById('inp-epochs').value),
    timesteps:        parseInt(document.getElementById('inp-timesteps').value),
    iid:              document.getElementById('chk-iid').checked,
    feature_selection:document.getElementById('chk-fs').checked,
    live_ratio:       0.75,
  };

  try {
    const resp = await fetch('/api/configure', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    const result = await resp.json();

    STATE.config = result.config;
    STATE.configured = true;
    STATE.status = 'configured';

    alertEl.className = 'wizard-alert';
    alertEl.textContent = `✓ Configured: ${getModelLabel()} on ${getModeLabel()} data. Click "Start Training" to begin.`;
    alertEl.style.display = 'block';

    document.getElementById('btn-start').disabled = false;
    setStatusPill('configured');
    setEnvBadge('CONFIGURED');
  } catch (e) {
    alertEl.className = 'wizard-alert error';
    alertEl.textContent = `✗ Failed to save configuration: ${e.message}`;
    alertEl.style.display = 'block';
  }
}

async function startTraining() {
  if (STATE.fl.is_training) return;

  const alertEl = document.getElementById('wizard-alert');
  alertEl.className = 'wizard-alert';
  alertEl.textContent = '⏳ Starting real FL pipeline… This may take a moment to load data and build the model.';
  alertEl.style.display = 'block';

  document.getElementById('btn-start').disabled = true;
  document.getElementById('btn-stop').style.display = 'block';

  setEnvBadge('RUNNING');
  setStatusPill('running');

  await fetch('/api/start_training');
  navigateTo('overview');
}

// ══════════════════════════════════════════════
// 4. CHART INITIALISATION
// ══════════════════════════════════════════════
function initCharts() {
  const c1 = document.getElementById('chart-acc-loss');
  if (c1) charts.accLoss = new Chart(c1, {
    type: 'line',
    data: { labels: [], datasets: [
      { label: 'Accuracy', data: [], borderColor: '#111', backgroundColor: 'rgba(0,0,0,0.04)',
        tension: 0.3, pointRadius: 3, borderWidth: 2 },
      { label: 'Loss', data: [], borderColor: '#888', backgroundColor: 'rgba(0,0,0,0.03)',
        tension: 0.3, pointRadius: 3, borderDash: [4, 3], borderWidth: 2, yAxisID: 'y1' }
    ]},
    options: baseOpts({ scales: {
      x:  { ticks: { color: '#888', font: { size: 11 } }, grid: { color: '#DDD' } },
      y:  { ticks: { color: '#888' }, grid: { color: '#DDD' },
            title: { display: true, text: 'Accuracy', color: '#111' } },
      y1: { ticks: { color: '#888' }, grid: { drawOnChartArea: false },
            position: 'right', title: { display: true, text: 'Loss', color: '#555' } }
    }})
  });

  const c2 = document.getElementById('chart-fl-acc');
  if (c2) charts.flAcc = new Chart(c2, {
    type: 'line',
    data: { labels: [], datasets: [
      { label: 'Global Accuracy', data: [], borderColor: '#111', backgroundColor: 'rgba(0,0,0,0.04)',
        tension: 0.3, pointRadius: 2, borderWidth: 2 }
    ]},
    options: baseOpts()
  });

  const c3 = document.getElementById('chart-fl-loss');
  if (c3) charts.flLoss = new Chart(c3, {
    type: 'line',
    data: { labels: [], datasets: [
      { label: 'Loss', data: [], borderColor: '#555', backgroundColor: 'rgba(0,0,0,0.03)',
        tension: 0.3, pointRadius: 2, borderWidth: 2, borderDash: [5, 3] }
    ]},
    options: baseOpts()
  });

  const c4 = document.getElementById('chart-nodes-acc');
  if (c4) charts.nodeAcc = new Chart(c4, {
    type: 'bar',
    data: { labels: [], datasets: [
      { label: 'Local Accuracy', data: [],
        backgroundColor: 'rgba(0,0,0,0.15)', borderColor: '#111', borderWidth: 1 }
    ]},
    options: baseOpts({ scales: {
      x: { ticks: { color: '#888' }, grid: { color: '#DDD' } },
      y: { ticks: { color: '#888' }, grid: { color: '#DDD' }, max: 1 }
    }})
  });

  const c5 = document.getElementById('chart-models');
  if (c5) charts.models = new Chart(c5, {
    type: 'line',
    data: { labels: [], datasets: [
      { label: 'CNN-BiLSTM (Global)', data: [], borderColor: '#111', pointStyle: 'circle',
        pointRadius: 3, tension: 0.3, borderWidth: 2 }
    ]},
    options: baseOpts()
  });
}

// ══════════════════════════════════════════════
// 5. SOCKETIO
// ══════════════════════════════════════════════
function connectSocket() {
  const socket = io({ reconnectionDelay: 1000 });

  socket.on('connect',    () => setConnStatus(true));
  socket.on('disconnect', () => setConnStatus(false));

  socket.on('full_state', data => {
    Object.keys(data).forEach(k => { if (data[k] !== undefined) STATE[k] = data[k]; });
    setStatusPill(STATE.status);
    if (STATE.status === 'running') setEnvBadge('RUNNING');
    else if (STATE.status === 'complete') setEnvBadge('COMPLETE');
    else if (STATE.status === 'configured') setEnvBadge('CONFIGURED');
    renderCurrentPage();
    renderOverviewKPIs();
  });

  socket.on('fl_update', data => {
    if (data.fl)         Object.assign(STATE.fl, data.fl);
    if (data.security)   { STATE.security.posture = data.security.posture; STATE.security.threat_level = data.security.threat_level; STATE.security.quarantined_nodes = data.security.quarantined_nodes || []; }
    if (data.blockchain) Object.assign(STATE.blockchain, { total_blocks: data.blockchain.total_blocks, ledger_health: data.blockchain.ledger_health, latest_hash: data.blockchain.latest_hash });
    if (data.models)     Object.assign(STATE.models, data.models);
    if (data.history)    STATE.history = data.history;
    renderOverviewKPIs();
    updateAllCharts();
    renderCurrentPage();
  });

  socket.on('node_update', node => {
    STATE.nodes[node.node_id] = node;
    if (STATE.currentPage === 'nodes') renderNodes();
    updateNodeChart();
  });

  socket.on('security_alert', ev => {
    if (!STATE.security.events) STATE.security.events = [];
    STATE.security.events.unshift(ev);
    if (STATE.currentPage === 'security') renderSecurity();
    renderOverviewEvents();
  });

  socket.on('blockchain_commit', tx => {
    if (!STATE.blockchain.recent_transactions) STATE.blockchain.recent_transactions = [];
    STATE.blockchain.recent_transactions.unshift(tx);
    if (STATE.currentPage === 'blockchain') renderBlockchain();
  });

  socket.on('pipeline_log', entry => {
    if (!STATE.log) STATE.log = [];
    STATE.log.unshift(entry);
    STATE.log = STATE.log.slice(0, 100);
    renderOverviewLog();
  });

  socket.on('agent_update', data => {
    if (!STATE.agents) STATE.agents = [];
    STATE.agents.unshift(data);
    STATE.agents = STATE.agents.slice(0, 30);
    if (STATE.currentPage === 'agents') renderAgents();
  });

  socket.on('training_complete', data => {
    STATE.status = 'complete';
    STATE.fl.is_training = false;
    setStatusPill('complete');
    setEnvBadge('COMPLETE');
    document.getElementById('btn-stop').style.display = 'none';
    document.getElementById('btn-start').disabled = false;
    showToast(`✓ Training complete — Final accuracy: ${(data.final_accuracy * 100).toFixed(2)}% | Best Model: ${data.best_model}`);
  });

  socket.on('pipeline_error', data => {
    STATE.status = 'error';
    setStatusPill('error');
    setEnvBadge('ERROR');
    document.getElementById('btn-stop').style.display = 'none';
    document.getElementById('btn-start').disabled = false;
    showToast(`✗ Pipeline error: ${data.error}`);
    console.error('Pipeline error:', data.error);
  });

  // Stop button
  document.getElementById('btn-stop').addEventListener('click', async () => {
    await fetch('/api/stop_training');
    STATE.fl.is_training = false;
    STATE.status = 'idle';
    setStatusPill('idle');
    setEnvBadge('STOPPED');
    document.getElementById('btn-stop').style.display = 'none';
    document.getElementById('btn-start').disabled = false;
  });
}

// ══════════════════════════════════════════════
// 6. HELPERS
// ══════════════════════════════════════════════
function setConnStatus(ok) {
  const dot  = document.getElementById('conn-dot');
  const text = document.getElementById('conn-text');
  if (dot)  dot.className = 'conn-dot' + (ok ? ' connected' : '');
  if (text) text.textContent = ok ? 'Connected' : 'Disconnected';
}
function setEnvBadge(label) {
  const el = document.getElementById('env-badge');
  if (el) el.textContent = label;
}
function setStatusPill(status) {
  const el = document.getElementById('status-pill');
  if (!el) return;
  el.className = 'status-pill ' + status;
  el.textContent = status.toUpperCase();
}
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val ?? '—';
}
function showToast(msg) {
  const t = document.getElementById('toast-banner');
  if (!t) return;
  t.textContent = msg; t.style.display = 'block';
  setTimeout(() => { t.style.display = 'none'; }, 9000);
}
function pct(v)  { return v != null && v !== 0 ? (v * 100).toFixed(2) + '%' : '—'; }
function fmt4(v) { return v != null ? parseFloat(v).toFixed(4) : '—'; }

// ══════════════════════════════════════════════
// 7. CHART UPDATES
// ══════════════════════════════════════════════
function updateAllCharts() {
  const h = (STATE.history || []).slice(-60);
  if (!h.length) return;
  const labels = h.map(r => `R${r.round}`);
  const acc    = h.map(r => r.accuracy);
  const loss   = h.map(r => r.loss);

  if (charts.accLoss) {
    charts.accLoss.data.labels = labels;
    charts.accLoss.data.datasets[0].data = acc;
    charts.accLoss.data.datasets[1].data = loss;
    charts.accLoss.update();
  }
  if (charts.flAcc) {
    charts.flAcc.data.labels = labels;
    charts.flAcc.data.datasets[0].data = acc;
    charts.flAcc.update();
  }
  if (charts.flLoss) {
    charts.flLoss.data.labels = labels;
    charts.flLoss.data.datasets[0].data = loss;
    charts.flLoss.update();
  }
  if (charts.models) {
    charts.models.data.labels = labels;
    charts.models.data.datasets[0].data = acc;
    charts.models.update();
  }
}

function updateNodeChart() {
  if (!charts.nodeAcc) return;
  const nodes = Object.values(STATE.nodes || {});
  charts.nodeAcc.data.labels = nodes.map(n => n.node_id);
  charts.nodeAcc.data.datasets[0].data = nodes.map(n => n.local_accuracy ?? 0);
  charts.nodeAcc.update();
}

// ══════════════════════════════════════════════
// 8. OVERVIEW
// ══════════════════════════════════════════════
function renderOverview() {
  renderOverviewKPIs();
  updateAllCharts();
  renderOverviewLog();
  renderOverviewEvents();
}

function renderOverviewKPIs() {
  const fl  = STATE.fl  || {};
  const sec = STATE.security || {};
  const mod = STATE.models || {};

  setText('kpi-round',    `${fl.current_round ?? 0} / ${fl.total_rounds ?? (STATE.config?.num_rounds ?? 0)}`);
  setText('kpi-accuracy', pct(fl.accuracy));
  setText('kpi-loss',     fmt4(fl.loss));
  setText('kpi-nodes',    fl.active_nodes ?? Object.keys(STATE.nodes || {}).length);
  setText('kpi-posture',  sec.posture ?? 'MONITOR');
  setText('kpi-model',    mod.best_model ?? '—');

  const pEl = document.getElementById('kpi-posture');
  if (pEl) {
    pEl.className = 'kpi-value';
    if (sec.posture === 'ALERT') pEl.classList.add('warning');
    else if (sec.posture === 'ACTIVE_BLOCK') pEl.classList.add('critical');
  }
}

function renderOverviewLog() {
  const tb = document.getElementById('overview-log-body');
  if (!tb) return;
  const entries = (STATE.log || []).slice(0, 8);
  tb.innerHTML = entries.map(e => `
    <tr>
      <td class="text-mono">${e.time}</td>
      <td><span class="pill ${(e.level||'').toLowerCase()}">${e.level||'INFO'}</span></td>
      <td>${e.msg}</td>
    </tr>`).join('') || '<tr><td colspan="3" class="text-muted text-sm" style="padding:12px;">No log entries yet.</td></tr>';
}

function renderOverviewEvents() {
  const tb = document.getElementById('overview-events-body');
  if (!tb) return;
  const evs = (STATE.security.events || []).slice(0, 5);
  tb.innerHTML = evs.map(ev => `
    <tr>
      <td class="text-mono">${ev.timestamp || ''}</td>
      <td><span class="pill ${(ev.level||'').toLowerCase()}">${ev.level}</span></td>
      <td>${ev.message || ''}</td>
    </tr>`).join('') || '<tr><td colspan="3" class="text-muted text-sm" style="padding:12px;">No events yet.</td></tr>';
}

// ══════════════════════════════════════════════
// 9. FL ENGINE
// ══════════════════════════════════════════════
function renderFL() {
  const fl = STATE.fl || {};
  setText('fl-current-round', fl.current_round ?? 0);
  setText('fl-accuracy',      pct(fl.accuracy));
  setText('fl-loss',          fmt4(fl.loss));
  setText('fl-active-nodes',  fl.active_nodes ?? Object.keys(STATE.nodes).length);
  setText('fl-strategy',      fl.aggregation_strategy ?? 'FedAvg');
  setText('fl-convergence',   fl.convergence_status ?? '—');
  updateAllCharts();

  const tb = document.getElementById('fl-history-body');
  if (!tb) return;
  const hist = (STATE.history || []).slice().reverse().slice(0, 30);
  tb.innerHTML = hist.map(r => `
    <tr>
      <td>${r.round}</td>
      <td>${pct(r.accuracy)}</td>
      <td>${fmt4(r.loss)}</td>
      <td>${r.strategy || 'FedAvg'}</td>
      <td class="text-mono text-sm">${(r.timestamp || '').slice(11, 19)}</td>
    </tr>`).join('') || '<tr><td colspan="5" class="text-muted text-sm" style="padding:12px;">No rounds yet.</td></tr>';
}

// ══════════════════════════════════════════════
// 10. NODES
// ══════════════════════════════════════════════
function renderNodes() {
  const nodes = Object.values(STATE.nodes || {});
  const tb = document.getElementById('nodes-table-body');
  if (tb) {
    tb.innerHTML = nodes.map(n => {
      const trust = n.trust_score ?? 0;
      const st    = (n.status || 'ACTIVE').toLowerCase();
      return `<tr>
        <td><strong>${n.node_id}</strong></td>
        <td>${n.role ?? 'Worker'}</td>
        <td><span class="pill ${st}">${n.status}</span></td>
        <td>
          ${(trust * 100).toFixed(1)}%
          <div class="progress-wrap"><div class="progress-fill" style="width:${(trust*100).toFixed(1)}%"></div></div>
        </td>
        <td>${pct(n.local_accuracy)}</td>
        <td>${(n.data_size ?? 0).toLocaleString()}</td>
        <td>${n.rounds_participated ?? 0}</td>
        <td>${((n.last_gradient_alignment ?? 0) * 100).toFixed(1)}%</td>
      </tr>`;
    }).join('') || '<tr><td colspan="8" class="text-muted text-sm" style="padding:12px;">Start training to populate node data.</td></tr>';
  }
  updateNodeChart();
}

// ══════════════════════════════════════════════
// 10.5 AI AGENTS
// ══════════════════════════════════════════════
function renderAgents() {
  const current = STATE.agents?.[0] || {};
  
  if (current.security) {
    setText('agent-threat', current.security.threat_level || 'MOCK');
    setText('agent-strategy', current.aggregation_strategy || 'FedAvg');
    
    const pEl = document.getElementById('agent-threat');
    if (pEl) {
      if (current.security.threat_level === 'HIGH' || current.security.threat_level === 'CRITICAL') pEl.style.color = '#C62828';
      else if (current.security.threat_level === 'MEDIUM' || current.security.threat_level === 'ALERT') pEl.style.color = '#F57F17';
      else pEl.style.color = '#111';
    }
  }

  const tb = document.getElementById('agents-table-body');
  if (!tb) return;
  const hist = (STATE.agents || []);
  tb.innerHTML = hist.map(r => `
    <tr>
      <td><strong>R${r.round || '?'}</strong></td>
      <td>${r.security?.threat_level || 'MOCK'}</td>
      <td><strong>${r.aggregation_strategy || 'FedAvg'}</strong></td>
      <td class="text-sm">${r.explanation || '...'}</td>
    </tr>`).join('') || '<tr><td colspan="4" class="text-muted text-sm" style="padding:12px;">Waiting for multi-agent coordination…</td></tr>';
}

// ══════════════════════════════════════════════
// 11. SECURITY
// ══════════════════════════════════════════════
function renderSecurity() {
  const sec = STATE.security || {};
  const posture = sec.posture || 'MONITOR';
  const threat  = sec.threat_level ?? 0;

  setText('sec-posture-label', posture);
  const pEl = document.getElementById('sec-posture-label');
  if (pEl) {
    pEl.className = 'posture-label';
    if (posture === 'ALERT') pEl.classList.add('alert');
    else if (posture === 'ACTIVE_BLOCK') pEl.classList.add('active_block');
  }
  setText('sec-threat-val', threat);
  const bar = document.getElementById('sec-threat-bar');
  if (bar) bar.style.width = Math.min(100, threat) + '%';

  const qTb = document.getElementById('sec-quarantine-body');
  if (qTb) {
    const q = sec.quarantined_nodes || [];
    qTb.innerHTML = q.length
      ? q.map(nid => `<tr><td><strong>${nid}</strong></td><td>Byzantine gradient / anomaly</td><td>Excluded from aggregation</td></tr>`).join('')
      : '<tr><td colspan="3" class="text-muted text-sm" style="padding:12px;">No quarantined nodes.</td></tr>';
  }

  const eTb = document.getElementById('sec-events-body');
  if (eTb) {
    const evs = (sec.events || []).slice(0, 50);
    eTb.innerHTML = evs.map(ev => `
      <tr>
        <td class="text-mono text-sm">${ev.timestamp || ''}</td>
        <td><span class="pill ${(ev.level||'').toLowerCase()}">${ev.level}</span></td>
        <td>${ev.message || ''}</td>
        <td class="text-muted text-sm">${ev.node_id || ''}</td>
      </tr>`).join('') || '<tr><td colspan="4" class="text-muted text-sm" style="padding:12px;">No events.</td></tr>';
  }
}

// ══════════════════════════════════════════════
// 12. MODELS
// ══════════════════════════════════════════════
function renderModels() {
  const m    = STATE.models || {};
  const best = (m.best_model || '').toLowerCase();
  
  const labelsMap = {
    cnn_bilstm: 'CNN-BiLSTM',
    transformer: 'Transformer',
    hybrid: 'Hybrid Ensemble'
  };

  // Get dynamic architectures tracked in state (exclude the 'best_model' tracking key)
  const trackedKeys = Object.keys(m).filter(k => k !== 'best_model');
  const rows = trackedKeys.map(k => [k, labelsMap[k] || k.toUpperCase()]);
  
  const tb = document.getElementById('models-table-body');
  if (tb) {
    tb.innerHTML = rows.map(([key, label]) => {
      const d = m[key] || {};
      const isBest = best.includes(key.replace('_', '')) || best === label.toLowerCase() || rows.length === 1; 
      
      return `<tr>
        <td><strong>${label}</strong></td>
        <td>${pct(d.accuracy)}</td>
        <td>${pct(d.f1)}</td>
        <td>${pct(d.precision)}</td>
        <td>${pct(d.recall)}</td>
        <td><span class="pill ${isBest && d.accuracy ? 'best' : 'normal'}">${isBest && d.accuracy ? 'BEST' : 'TRAINING'}</span></td>
      </tr>`;
    }).join('') || '<tr><td colspan="6" class="text-muted text-sm" style="padding:12px;">Start training to populate model data.</td></tr>';
  }
  updateAllCharts();
}

// ══════════════════════════════════════════════
// 13. BLOCKCHAIN
// ══════════════════════════════════════════════
function renderBlockchain() {
  const bc = STATE.blockchain || {};
  setText('bc-total',  bc.total_blocks ?? '0');
  setText('bc-health', bc.ledger_health ?? 'SYNCED');
  setText('bc-hash',   bc.latest_hash ? bc.latest_hash.slice(0, 20) + '…' : '—');

  const tb = document.getElementById('bc-table-body');
  if (!tb) return;
  const txs = (bc.recent_transactions || []).slice(0, 20);
  tb.innerHTML = txs.map(tx => `
    <tr>
      <td>${tx.block ?? '—'}</td>
      <td><span class="pill normal">${tx.type}</span></td>
      <td class="text-mono">${(tx.hash || '').slice(0, 20)}…</td>
      <td>${tx.preview || ''}</td>
      <td class="text-mono text-sm">${tx.timestamp || ''}</td>
    </tr>`).join('') || '<tr><td colspan="5" class="text-muted text-sm" style="padding:12px;">No transactions yet.</td></tr>';
}
