const API = '/api';

// ── State ──────────────────────────────────────────────────────────────
let categories = [];
let templates = [];
let currentTab = 'dashboard';

// ── Utils ──────────────────────────────────────────────────────────────
function today() {
  return new Date().toISOString().split('T')[0];
}

function isOverdue(task) {
  if (!task.due_date || task.status === '완료') return false;
  return task.due_date < today();
}

function priorityLabel(p) {
  return `P${p}`;
}

async function api(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ── Tab navigation ──────────────────────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    switchTab(tab);
  });
});

function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.nav-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tab);
  });
  document.querySelectorAll('.tab-content').forEach(s => {
    s.classList.toggle('active', s.id === `tab-${tab}`);
  });
  if (tab === 'dashboard') loadDashboard();
  else if (tab === 'tasks') loadAllTasks();
  else if (tab === 'completed') loadCompletedTasks();
  else if (tab === 'categories') loadCategories();
  else if (tab === 'template-manage') loadTemplateManage();
}

// ── Categories ──────────────────────────────────────────────────────────
async function fetchCategories() {
  categories = await api('GET', '/categories');
  return categories;
}

function populateCategorySelects() {
  ['f-category', 'tf-category', 'filter-category'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const first = id === 'filter-category'
      ? '<option value="">전체 종류</option>'
      : '<option value="">선택 안 함</option>';
    el.innerHTML = first + categories.map(c =>
      `<option value="${c.id}">${c.name}</option>`
    ).join('');
  });
}

async function loadCategories() {
  await fetchCategories();
  populateCategorySelects();
  const list = document.getElementById('category-list');
  if (!categories.length) {
    list.innerHTML = '<li><span style="color:var(--text-muted)">업무 종류가 없습니다.</span></li>';
    return;
  }
  list.innerHTML = categories.map(c => `
    <li>
      <span>${c.name}</span>
      <button class="icon-btn" onclick="editCategory(${c.id}, '${c.name.replace(/'/g, "\\'")}')">수정</button>
      <button class="icon-btn danger" onclick="deleteCategory(${c.id})">삭제</button>
    </li>
  `).join('');
}

let editingCatId = null;
document.getElementById('btn-new-cat').addEventListener('click', () => {
  editingCatId = null;
  document.getElementById('cat-input').value = '';
  document.getElementById('cat-form').classList.remove('hidden');
});
document.getElementById('cat-cancel').addEventListener('click', () => {
  document.getElementById('cat-form').classList.add('hidden');
});
document.getElementById('cat-save').addEventListener('click', async () => {
  const name = document.getElementById('cat-input').value.trim();
  if (!name) return alert('이름을 입력하세요.');
  try {
    if (editingCatId) {
      await api('PUT', `/categories/${editingCatId}`, { name });
    } else {
      await api('POST', '/categories', { name });
    }
    document.getElementById('cat-form').classList.add('hidden');
    editingCatId = null;
    loadCategories();
  } catch (e) { alert(e.message); }
});

window.editCategory = (id, name) => {
  editingCatId = id;
  document.getElementById('cat-input').value = name;
  document.getElementById('cat-form').classList.remove('hidden');
};
window.deleteCategory = async (id) => {
  if (!confirm('삭제하시겠습니까?')) return;
  await api('DELETE', `/categories/${id}`);
  loadCategories();
};

// ── Templates ───────────────────────────────────────────────────────────
async function fetchTemplates() {
  templates = await api('GET', '/templates');
  return templates;
}

async function loadTemplateManage() {
  await fetchCategories();
  await fetchTemplates();
  populateCategorySelects();
  const list = document.getElementById('template-list');
  if (!templates.length) {
    list.innerHTML = '<li><span style="color:var(--text-muted)">템플릿이 없습니다.</span></li>';
    return;
  }
  list.innerHTML = templates.map(t => `
    <li>
      <span>${t.title}</span>
      <span class="item-meta">${t.category?.name ?? ''} | P${t.default_priority}</span>
      <button class="icon-btn" onclick="openTmplModal(${t.id})">수정</button>
      <button class="icon-btn danger" onclick="deleteTmpl(${t.id})">삭제</button>
    </li>
  `).join('');
}

function renderTemplateButtons() {
  const grid = document.getElementById('template-buttons');
  if (!templates.length) {
    grid.innerHTML = '<p class="empty-note">템플릿이 없습니다. "템플릿 관리" 탭에서 추가하세요.</p>';
    return;
  }
  grid.innerHTML = templates.map(t => `
    <button class="tmpl-btn" onclick="applyTemplate(${t.id})">${t.title}</button>
  `).join('');
}

window.applyTemplate = async (id) => {
  try {
    await api('POST', `/templates/${id}/apply`);
    await loadDashboard();
  } catch (e) { alert(e.message); }
};

// Template modal
const tmplModal = document.getElementById('tmpl-modal');
const overlay = document.getElementById('overlay');

document.getElementById('btn-new-tmpl').addEventListener('click', () => openTmplModal(null));
document.getElementById('tmpl-modal-cancel').addEventListener('click', closeTmplModal);
overlay.addEventListener('click', () => { closeTaskModal(); closeTmplModal(); });

window.openTmplModal = (id) => {
  const t = id ? templates.find(x => x.id === id) : null;
  document.getElementById('tmpl-id').value = id ?? '';
  document.getElementById('tmpl-modal-title').textContent = id ? '템플릿 수정' : '템플릿 추가';
  document.getElementById('tf-title').value = t?.title ?? '';
  document.getElementById('tf-category').value = t?.category_id ?? '';
  document.getElementById('tf-priority').value = t?.default_priority ?? 3;
  tmplModal.classList.remove('hidden');
  overlay.classList.remove('hidden');
};

function closeTmplModal() {
  tmplModal.classList.add('hidden');
  overlay.classList.add('hidden');
}

document.getElementById('tmpl-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('tmpl-id').value;
  const body = {
    title: document.getElementById('tf-title').value.trim(),
    category_id: document.getElementById('tf-category').value || null,
    default_priority: parseInt(document.getElementById('tf-priority').value),
  };
  if (body.category_id) body.category_id = parseInt(body.category_id);
  try {
    if (id) {
      await api('PUT', `/templates/${id}`, body);
    } else {
      await api('POST', '/templates', body);
    }
    closeTmplModal();
    if (currentTab === 'template-manage') loadTemplateManage();
    else loadDashboard();
  } catch (e) { alert(e.message); }
});

window.deleteTmpl = async (id) => {
  if (!confirm('삭제하시겠습니까?')) return;
  await api('DELETE', `/templates/${id}`);
  loadTemplateManage();
};

// ── Task Modal ───────────────────────────────────────────────────────────
const taskModal = document.getElementById('task-modal');

function openTaskModal(task = null) {
  document.getElementById('task-id').value = task?.id ?? '';
  document.getElementById('modal-title').textContent = task ? '업무 수정' : '업무 추가';
  document.getElementById('f-title').value = task?.title ?? '';
  document.getElementById('f-category').value = task?.category_id ?? '';
  document.getElementById('f-clinic').value = task?.clinic ?? '';
  document.getElementById('f-priority').value = task?.priority ?? 3;
  document.getElementById('f-due-date').value = task?.due_date ?? '';
  document.getElementById('f-status').value = task?.status ?? '대기';
  document.getElementById('f-memo').value = task?.memo ?? '';
  taskModal.classList.remove('hidden');
  overlay.classList.remove('hidden');
}

function closeTaskModal() {
  taskModal.classList.add('hidden');
  overlay.classList.add('hidden');
}

document.getElementById('modal-cancel').addEventListener('click', closeTaskModal);

document.getElementById('task-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('task-id').value;
  const catVal = document.getElementById('f-category').value;
  const body = {
    title: document.getElementById('f-title').value.trim(),
    category_id: catVal ? parseInt(catVal) : null,
    clinic: document.getElementById('f-clinic').value.trim() || null,
    priority: parseInt(document.getElementById('f-priority').value),
    due_date: document.getElementById('f-due-date').value || null,
    status: document.getElementById('f-status').value,
    memo: document.getElementById('f-memo').value.trim() || null,
  };
  try {
    if (id) {
      await api('PATCH', `/tasks/${id}`, body);
    } else {
      await api('POST', '/tasks', body);
    }
    closeTaskModal();
    refreshCurrentTab();
  } catch (e) { alert(e.message); }
});

function refreshCurrentTab() {
  if (currentTab === 'dashboard') loadDashboard();
  else if (currentTab === 'tasks') loadAllTasks();
  else if (currentTab === 'completed') loadCompletedTasks();
}

// ── Task rendering ───────────────────────────────────────────────────────
function renderTaskCard(task, showStatus = true) {
  const overdue = isOverdue(task);
  const done = task.status === '완료';
  const priorityColors = {5:'#dc2626',4:'#ea580c',3:'#ca8a04',2:'#16a34a',1:'#6b7280'};
  const pColor = priorityColors[task.priority] || '#6b7280';

  const meta = [];
  if (task.category) meta.push(`<span class="tag">${task.category.name}</span>`);
  if (task.clinic) meta.push(`<span class="tag">🏥 ${task.clinic}</span>`);
  if (task.due_date) {
    const cls = overdue ? ' overdue' : '';
    meta.push(`<span class="tag${cls}">📅 ${task.due_date}${overdue ? ' 기한초과' : ''}</span>`);
  }
  if (showStatus) meta.push(`<span class="tag status-${task.status}">${task.status}</span>`);
  if (task.memo) meta.push(`<span class="tag">📝 ${task.memo.substring(0, 30)}${task.memo.length > 30 ? '…' : ''}</span>`);

  return `
    <div class="task-card${overdue ? ' overdue' : ''}${done ? ' completed' : ''}" data-id="${task.id}">
      <input type="checkbox" class="task-check" ${done ? 'checked' : ''}
        onchange="toggleComplete(${task.id}, this.checked)" />
      <div class="task-body">
        <div class="task-title">${task.title}</div>
        <div class="task-meta">${meta.join('')}</div>
      </div>
      <div class="task-actions">
        <select class="priority-select" onchange="changePriority(${task.id}, this.value)"
          title="우선순위 변경" style="border-left: 3px solid ${pColor}">
          ${[5,4,3,2,1].map(p => `<option value="${p}" ${task.priority===p?'selected':''}>${priorityLabel(p)}</option>`).join('')}
        </select>
        <button class="icon-btn" onclick="openEditTask(${task.id})">수정</button>
        <button class="icon-btn danger" onclick="deleteTask(${task.id})">삭제</button>
      </div>
    </div>
  `;
}

// ── Dashboard ────────────────────────────────────────────────────────────
async function loadDashboard() {
  const [summary] = await Promise.all([
    api('GET', '/tasks/summary'),
    fetchCategories(),
    fetchTemplates(),
  ]);
  document.getElementById('sum-today').textContent = summary.today_count;
  document.getElementById('sum-overdue').textContent = summary.overdue_count;
  document.getElementById('sum-inprogress').textContent = summary.in_progress_count;
  populateCategorySelects();
  renderTemplateButtons();
  await applyFilters();
}

async function applyFilters() {
  const period = document.getElementById('filter-period').value;
  const categoryId = document.getElementById('filter-category').value;
  const clinic = document.getElementById('filter-clinic').value.trim();

  let qs = 'status=incomplete';
  if (period) qs += `&period=${period}`;
  if (categoryId) qs += `&category_id=${categoryId}`;
  if (clinic) qs += `&clinic=${encodeURIComponent(clinic)}`;

  const tasks = await api('GET', `/tasks?${qs}`);
  const list = document.getElementById('task-list');
  if (!tasks.length) {
    list.innerHTML = '<p class="empty-note" style="padding:.5rem">미완료 업무가 없습니다.</p>';
    return;
  }
  list.innerHTML = tasks.map(t => renderTaskCard(t)).join('');
}

['filter-period', 'filter-category'].forEach(id => {
  document.getElementById(id).addEventListener('change', applyFilters);
});
document.getElementById('filter-clinic').addEventListener('input', debounce(applyFilters, 400));

document.getElementById('btn-new-task-dash').addEventListener('click', () => {
  populateCategorySelects();
  openTaskModal();
});

// ── All tasks tab ─────────────────────────────────────────────────────────
async function loadAllTasks() {
  await fetchCategories();
  populateCategorySelects();
  const tasks = await api('GET', '/tasks?status=incomplete');
  const list = document.getElementById('all-task-list');
  if (!tasks.length) {
    list.innerHTML = '<p class="empty-note" style="padding:.5rem">업무가 없습니다.</p>';
    return;
  }
  list.innerHTML = tasks.map(t => renderTaskCard(t)).join('');
}
document.getElementById('btn-new-task').addEventListener('click', () => {
  populateCategorySelects();
  openTaskModal();
});

// ── Completed tasks tab ───────────────────────────────────────────────────
async function loadCompletedTasks() {
  const tasks = await api('GET', '/tasks?status=완료');
  const list = document.getElementById('completed-task-list');
  if (!tasks.length) {
    list.innerHTML = '<p class="empty-note" style="padding:.5rem">완료된 업무가 없습니다.</p>';
    return;
  }
  list.innerHTML = tasks.map(t => renderTaskCard(t, false)).join('');
}

// ── Quick actions ─────────────────────────────────────────────────────────
window.toggleComplete = async (id, checked) => {
  await api('PATCH', `/tasks/${id}`, { status: checked ? '완료' : '대기' });
  refreshCurrentTab();
};

window.changePriority = async (id, value) => {
  await api('PATCH', `/tasks/${id}`, { priority: parseInt(value) });
  refreshCurrentTab();
};

window.openEditTask = async (id) => {
  await fetchCategories();
  populateCategorySelects();
  const task = await api('GET', `/tasks/${id}`);
  openTaskModal(task);
};

window.deleteTask = async (id) => {
  if (!confirm('삭제하시겠습니까?')) return;
  await api('DELETE', `/tasks/${id}`);
  refreshCurrentTab();
};

// ── Helpers ───────────────────────────────────────────────────────────────
function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// ── Init ──────────────────────────────────────────────────────────────────
loadDashboard();
