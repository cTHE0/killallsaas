// ─── STATE ────────────────────────────────────────────────────────────────────
const state = {
  cat: 'all',
  sort: 'popular',
  query: '',
  filter: null,
  tools: [],
};

// ─── API ──────────────────────────────────────────────────────────────────────
async function fetchTools() {
  const params = new URLSearchParams({
    cat: state.cat,
    q: state.query,
    sort: state.sort,
    tag: state.filter || '',
  });
  const res = await fetch(`/api/tools?${params}`);
  const data = await res.json();
  return data;
}

async function fetchStats() {
  const res = await fetch('/api/stats');
  return res.json();
}

// ─── RENDER ───────────────────────────────────────────────────────────────────
async function renderCards() {
  const grid = document.getElementById('tools-grid');
  const empty = document.getElementById('empty-state');
  const { tools, total } = await fetchTools();

  state.tools = tools;
  document.getElementById('showing-count').textContent = total;
  grid.querySelectorAll('.tool-card').forEach(c => c.remove());

  if (!total) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';

  tools.forEach(t => {
    const el = document.createElement('div');
    el.className = 'tool-card';
    el.dataset.id = t.id;
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
          ${t.tags.includes('online')   ? '<span class="ctag">online</span>' : ''}
          ${t.tags.includes('selfhost') ? '<span class="ctag">self-host</span>' : ''}
          ${t.is_new                    ? '<span class="ctag new-tag">new</span>' : ''}
        </div>
        <button class="card-launch" data-url="${t.online_url}">Launch →</button>
      </div>`;

    el.querySelector('.card-launch').addEventListener('click', e => {
      e.stopPropagation();
      if (t.hosted_url) openIframe(t);
      else window.open(t.online_url, '_blank', 'noopener');
    });
    el.addEventListener('click', () => openModal(t));
    grid.appendChild(el);
  });
}

// ─── MODAL ────────────────────────────────────────────────────────────────────
function openModal(t) {
  document.getElementById('m-icon').textContent = t.icon;
  document.getElementById('m-name').textContent = t.name;
  document.getElementById('m-sub').textContent  = `Kills ${t.kills} · Generated in ${t.gen_time} · Saves ${t.saving}`;
  const launchBtn = document.getElementById('m-launch');
  if (t.hosted_url) {
    launchBtn.href = '#';
    launchBtn.onclick = (e) => { e.preventDefault(); closeModal(); openIframe(t); };
    launchBtn.textContent = 'Launch on killallsaas →';
  } else {
    launchBtn.href = t.online_url;
    launchBtn.onclick = null;
    launchBtn.textContent = 'Launch free →';
  }
  document.getElementById('m-github').href  = t.github_url;

  document.getElementById('m-stats').innerHTML = `
    <div class="stat"><div class="stat-val green">${t.users}</div><div class="stat-label">Active users</div></div>
    <div class="stat"><div class="stat-val">${t.stars}</div><div class="stat-label">GitHub stars</div></div>
    <div class="stat"><div class="stat-val red">${t.saving}</div><div class="stat-label">Monthly saving</div></div>
    <div class="stat"><div class="stat-val">${t.gen_time}</div><div class="stat-label">AI gen time</div></div>`;

  document.getElementById('m-desc').textContent = t.desc;

  document.getElementById('m-features').innerHTML =
    t.features.map(f => `<div class="feature-item">${f}</div>`).join('');

  document.getElementById('m-deploy').innerHTML =
    t.deploy.split('\n').map(line =>
      line.startsWith('#')
        ? `<span class="deploy-comment">${line}</span>`
        : `<span>${line}</span>`
    ).join('\n');

  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.style.overflow = '';
}

function maybeClose(e) {
  if (e.target === document.getElementById('modal')) closeModal();
}

// ─── IFRAME MODAL ─────────────────────────────────────────────────────────────
function openIframe(t) {
  document.getElementById('iframe-icon').textContent    = t.icon;
  document.getElementById('iframe-name').textContent    = t.name;
  document.getElementById('iframe-github').href         = t.github_url || '#';
  document.getElementById('iframe-external').href       = t.hosted_url;
  document.getElementById('iframe-embed').src           = t.hosted_url;
  document.getElementById('iframe-modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeIframe() {
  document.getElementById('iframe-modal').classList.remove('open');
  document.getElementById('iframe-embed').src = ''; // stop loading
  document.body.style.overflow = '';
}

// ─── SUBMIT MODAL ─────────────────────────────────────────────────────────────
function openSubmitModal() {
  document.getElementById('submit-modal').classList.add('open');
  document.body.style.overflow = 'hidden';
  document.getElementById('submit-msg').textContent = '';
  document.getElementById('submit-name').value = '';
  document.getElementById('submit-email').value = '';
}

function closeSubmitModal() {
  document.getElementById('submit-modal').classList.remove('open');
  document.body.style.overflow = '';
}

function maybeCloseSubmit(e) {
  if (e.target === document.getElementById('submit-modal')) closeSubmitModal();
}

async function submitKill() {
  const name       = document.getElementById('submit-name').value.trim();
  const github_url = document.getElementById('submit-github').value.trim();
  const online_url = document.getElementById('submit-online').value.trim();
  const description= document.getElementById('submit-desc').value.trim();
  const email      = document.getElementById('submit-email').value.trim();
  const msg        = document.getElementById('submit-msg');

  msg.className = 'submit-msg';
  msg.textContent = '';

  if (!name) {
    msg.textContent = 'Please enter the SaaS name to replace.';
    msg.className = 'submit-msg err';
    return;
  }
  if (!github_url) {
    msg.textContent = 'Please enter the GitHub repository URL.';
    msg.className = 'submit-msg err';
    return;
  }

  msg.textContent = 'Submitting…';
  msg.className = 'submit-msg';

  const res  = await fetch('/api/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, github_url, online_url, description, email }),
  });
  const data = await res.json();

  if (data.ok) {
    msg.innerHTML = `🔪 <strong>"${name}"</strong> submitted! We'll review it and publish it on the marketplace.${email ? " We'll notify you at " + email + " when it's live." : ''}`;
    msg.className = 'submit-msg ok';
    // reset form
    ['submit-name','submit-github','submit-online','submit-desc','submit-email']
      .forEach(id => { document.getElementById(id).value = ''; });
  } else {
    msg.textContent = data.error || 'Something went wrong. Please try again.';
    msg.className = 'submit-msg err';
  }
}

// ─── FILTERS & SORT ───────────────────────────────────────────────────────────
document.querySelectorAll('.cat-btn[data-cat]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.cat-btn[data-cat]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.cat = btn.dataset.cat;
    renderCards();
  });
});

document.querySelectorAll('.cat-btn[data-filter]').forEach(btn => {
  btn.addEventListener('click', () => {
    const same = state.filter === btn.dataset.filter;
    document.querySelectorAll('.cat-btn[data-filter]').forEach(b => b.classList.remove('active'));
    state.filter = same ? null : btn.dataset.filter;
    if (!same) btn.classList.add('active');
    renderCards();
  });
});

document.querySelectorAll('.pill').forEach(p => {
  p.addEventListener('click', () => {
    document.querySelectorAll('.pill').forEach(x => x.classList.remove('active'));
    p.classList.add('active');
    state.sort = p.dataset.sort;
    renderCards();
  });
});

let searchTimer;
document.getElementById('search').addEventListener('input', e => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.query = e.target.value;
    renderCards();
  }, 200);
});

// ─── KEYBOARD ─────────────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeModal(); closeSubmitModal(); closeIframe(); }
  if (e.key === '/' && document.activeElement !== document.getElementById('search')) {
    e.preventDefault();
    document.getElementById('search').focus();
  }
});

// ─── TICKER LOOP ──────────────────────────────────────────────────────────────
const ticker = document.getElementById('ticker-inner');
ticker.innerHTML += ticker.innerHTML;

// ─── STATS ────────────────────────────────────────────────────────────────────
async function loadStats() {
  const stats = await fetchStats();
  const el = document.getElementById('stat-savings');
  if (el) el.textContent = '$' + Math.round(stats.total_savings_yearly / 12).toLocaleString() + '/mo';
}

// ─── INIT ─────────────────────────────────────────────────────────────────────
renderCards();
loadStats();
