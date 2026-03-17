// ─────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────
const state = {
  cat: 'all',
  sort: 'popular',
  query: '',
  filter: null,
};

// ─────────────────────────────────────────────────────────────
// API
// ─────────────────────────────────────────────────────────────
async function fetchTools() {
  const params = new URLSearchParams({
    cat: state.cat,
    sort: state.sort,
    q: state.query,
    tag: state.filter || '',
  });
  const res = await fetch(`/api/tools?${params}`);
  return res.json();
}

async function fetchStats() {
  const res = await fetch('/api/stats');
  return res.json();
}

async function submitKillRequest(saas_name, email) {
  const res = await fetch('/api/kill-request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ saas_name, email }),
  });
  return res.json();
}

async function fetchKillQueue() {
  const res = await fetch('/api/kill-requests');
  return res.json();
}

async function voteKillRequest(id) {
  const res = await fetch(`/api/kill-request/${id}/vote`, { method: 'POST' });
  return res.json();
}

// ─────────────────────────────────────────────────────────────
// RENDER CARDS
// ─────────────────────────────────────────────────────────────
async function renderCards() {
  const grid = document.getElementById('tools-grid');
  const empty = document.getElementById('empty-state');
  const skeleton = document.getElementById('skeleton');

  if (skeleton) skeleton.style.display = 'contents';
  empty.style.display = 'none';
  grid.querySelectorAll('.tool-card').forEach(c => c.remove());

  const data = await fetchTools();
  if (skeleton) skeleton.style.display = 'none';

  document.getElementById('showing-count').textContent = data.total;

  if (!data.tools || data.tools.length === 0) {
    empty.style.display = 'block';
    return;
  }

  data.tools.forEach((t, i) => {
    const el = document.createElement('div');
    el.className = 'tool-card';
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    el.innerHTML = `
      <div class="saving-badge">saves ${t.saving}</div>
      <div class="card-top">
        <div class="card-icon">${t.icon}</div>
        <div class="card-meta">
          <div class="card-name">${t.name}</div>
          <div class="card-kills"><span>kills</span> ${t.kills}</div>
        </div>
      </div>
      <div class="card-desc">${t.desc}</div>
      <div class="card-footer">
        <div class="card-tags">
          ${t.tags.includes('online') ? '<span class="ctag">online</span>' : ''}
          ${t.tags.includes('selfhost') ? '<span class="ctag">self-host</span>' : ''}
          ${t.is_new ? '<span class="ctag ctag-new">new</span>' : ''}
        </div>
        <button class="card-launch" data-url="${t.online_url}">Launch →</button>
      </div>`;
    el.querySelector('.card-launch').addEventListener('click', e => {
      e.stopPropagation();
      window.open(t.online_url, '_blank', 'noopener');
    });
    el.addEventListener('click', () => openModal(t));
    grid.appendChild(el);

    // Staggered fade-in
    requestAnimationFrame(() => {
      setTimeout(() => {
        el.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      }, i * 25);
    });
  });
}

// ─────────────────────────────────────────────────────────────
// STATS
// ─────────────────────────────────────────────────────────────
async function loadStats() {
  const stats = await fetchStats();

  // Animate kill counter
  const el = document.getElementById('kill-count');
  let n = 0;
  const target = stats.total_kills;
  const step = () => {
    n = Math.min(n + Math.ceil(target / 60), target);
    el.textContent = n.toLocaleString();
    if (n < target) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);

  // Category counts
  const cats = stats.categories;
  Object.entries(cats).forEach(([cat, count]) => {
    const el = document.getElementById(`cnt-${cat}`);
    if (el) el.textContent = count;
  });
  const allEl = document.getElementById('cnt-all');
  if (allEl) allEl.textContent = stats.total_tools;

  // Total savings
  const savEl = document.getElementById('total-savings');
  if (savEl) {
    const yearly = stats.total_savings_yearly;
    savEl.textContent = yearly >= 1000
      ? `$${(yearly / 1000).toFixed(0)}k/yr`
      : `$${yearly}/yr`;
  }
}

// ─────────────────────────────────────────────────────────────
// MODAL: Tool detail
// ─────────────────────────────────────────────────────────────
function openModal(t) {
  document.getElementById('m-icon').textContent = t.icon;
  document.getElementById('m-name').textContent = t.name;
  document.getElementById('m-sub').textContent =
    `Kills ${t.kills} · Generated in ${t.gen_time} · Saves ${t.saving}`;
  document.getElementById('m-launch').href = t.online_url;
  document.getElementById('m-github').href = t.github_url;

  document.getElementById('m-stats').innerHTML = `
    <div class="stat"><div class="stat-val green">${t.users}</div><div class="stat-label">Active users</div></div>
    <div class="stat"><div class="stat-val">${t.stars}</div><div class="stat-label">GitHub stars</div></div>
    <div class="stat"><div class="stat-val red">${t.saving}</div><div class="stat-label">Monthly saving</div></div>
    <div class="stat"><div class="stat-val">${t.gen_time}</div><div class="stat-label">AI gen time</div></div>`;

  document.getElementById('m-desc').textContent = t.desc;

  document.getElementById('m-features').innerHTML =
    t.features.map(f => `<div class="feature-item">${f}</div>`).join('');

  const lines = t.deploy.split('\n');
  document.getElementById('m-deploy').innerHTML = lines.map(l =>
    l.startsWith('#')
      ? `<span class="deploy-comment">${l}</span>`
      : `<span>${l}</span>`
  ).join('\n');

  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.style.overflow = '';
}

// ─────────────────────────────────────────────────────────────
// MODAL: Kill request
// ─────────────────────────────────────────────────────────────
async function openKillRequest() {
  document.getElementById('req-saas').value = '';
  document.getElementById('req-email').value = '';
  document.getElementById('req-error').style.display = 'none';
  document.getElementById('req-success').style.display = 'none';

  // Load existing queue
  await renderQueue();

  document.getElementById('modal-request').classList.add('open');
  document.body.style.overflow = 'hidden';
  document.getElementById('req-saas').focus();
}

function closeKillRequest() {
  document.getElementById('modal-request').classList.remove('open');
  document.body.style.overflow = '';
}

async function renderQueue() {
  const data = await fetchKillQueue();
  const list = document.getElementById('queue-list');
  if (!data.requests || data.requests.length === 0) {
    list.innerHTML = '<div style="font-size:0.72rem;color:var(--muted);padding:0.5rem 0;">No requests yet. Be first.</div>';
    return;
  }
  list.innerHTML = data.requests.slice(0, 8).map(r => `
    <div class="queue-item">
      <span>${r.saas_name}</span>
      <button class="queue-votes" data-id="${r.id}">▲ ${r.votes}</button>
    </div>`).join('');

  list.querySelectorAll('.queue-votes').forEach(btn => {
    btn.addEventListener('click', async () => {
      await voteKillRequest(btn.dataset.id);
      await renderQueue();
    });
  });
}

async function handleKillSubmit() {
  const saas = document.getElementById('req-saas').value.trim();
  const email = document.getElementById('req-email').value.trim();
  const errEl = document.getElementById('req-error');
  const okEl = document.getElementById('req-success');

  errEl.style.display = 'none';
  okEl.style.display = 'none';

  if (!saas) {
    errEl.textContent = 'Please enter the name of the SaaS to kill.';
    errEl.style.display = 'block';
    return;
  }

  const data = await submitKillRequest(saas, email);
  if (data.error) {
    errEl.textContent = data.error;
    errEl.style.display = 'block';
  } else {
    okEl.textContent = `🔪 "${saas}" added to kill queue — position #${data.queue_position}`;
    okEl.style.display = 'block';
    document.getElementById('req-saas').value = '';
    document.getElementById('req-email').value = '';
    await renderQueue();
  }
}

// ─────────────────────────────────────────────────────────────
// EVENT LISTENERS
// ─────────────────────────────────────────────────────────────

// Category buttons
document.querySelectorAll('.cat-btn[data-cat]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.cat-btn[data-cat]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.cat = btn.dataset.cat;
    renderCards();
  });
});

// Filter buttons
document.querySelectorAll('.cat-btn[data-filter]').forEach(btn => {
  btn.addEventListener('click', () => {
    const same = state.filter === btn.dataset.filter;
    document.querySelectorAll('.cat-btn[data-filter]').forEach(b => b.classList.remove('active'));
    state.filter = same ? null : btn.dataset.filter;
    if (!same) btn.classList.add('active');
    renderCards();
  });
});

// Sort pills
document.querySelectorAll('.pill').forEach(p => {
  p.addEventListener('click', () => {
    document.querySelectorAll('.pill').forEach(x => x.classList.remove('active'));
    p.classList.add('active');
    state.sort = p.dataset.sort;
    renderCards();
  });
});

// Search (debounced)
let searchTimeout;
document.getElementById('search').addEventListener('input', e => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    state.query = e.target.value.trim();
    renderCards();
  }, 220);
});

// Tool detail modal
document.getElementById('btn-modal-close').addEventListener('click', closeModal);
document.getElementById('modal').addEventListener('click', e => {
  if (e.target === document.getElementById('modal')) closeModal();
});

// Kill request modal
document.getElementById('btn-kill-request').addEventListener('click', openKillRequest);
document.getElementById('btn-request-from-empty').addEventListener('click', openKillRequest);
document.getElementById('btn-request-close').addEventListener('click', closeKillRequest);
document.getElementById('btn-submit-request').addEventListener('click', handleKillSubmit);
document.getElementById('modal-request').addEventListener('click', e => {
  if (e.target === document.getElementById('modal-request')) closeKillRequest();
});
document.getElementById('req-saas').addEventListener('keydown', e => {
  if (e.key === 'Enter') handleKillSubmit();
});

// Escape key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeModal(); closeKillRequest(); }
});

// ─────────────────────────────────────────────────────────────
// TICKER — duplicate for seamless loop
// ─────────────────────────────────────────────────────────────
const ticker = document.getElementById('ticker-inner');
if (ticker) ticker.innerHTML += ticker.innerHTML;

// ─────────────────────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────────────────────
loadStats();
renderCards();
