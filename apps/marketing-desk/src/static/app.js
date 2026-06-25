/* global state */
var currentTab = 'dashboard';
var calYear = new Date().getFullYear();
var calMonth = new Date().getMonth();
var calEvents = {};
var calSelectedDate = null;
var dashLimit = parseInt(localStorage.getItem('dashLimit') || '5', 10);

/* ── API helpers ──────────────────────────────────────────────────── */
async function apiCall(method, path, body) {
  var opts = { method: method, headers: { 'Content-Type': 'application/json' } };
  if (body !== undefined) {
    opts.body = JSON.stringify(body);
  }
  var r = await fetch(path, opts);
  if (!r.ok) {
    var msg = await r.text();
    throw new Error(msg);
  }
  if (r.status === 204) return null;
  return r.json();
}
function apiGet(path) { return apiCall('GET', path, undefined); }
function apiPost(path, body) { return apiCall('POST', path, body); }
function apiPut(path, body) { return apiCall('PUT', path, body); }
function apiDelete(path) { return apiCall('DELETE', path, undefined); }
function apiPatch(path) { return apiCall('PATCH', path, undefined); }

/* ── Tab management ───────────────────────────────────────────────── */
function showTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.section').forEach(function(el) {
    el.classList.remove('active');
  });
  var sec = document.getElementById('section-' + tab);
  if (sec) sec.classList.add('active');
  document.querySelectorAll('.tab-btn').forEach(function(btn) {
    btn.classList.toggle('active', btn.dataset.tab === tab);
  });
  loadTab(tab);
}

function loadTab(tab) {
  if (tab === 'dashboard') { loadDashboard(); }
  else if (tab === 'calendar') { loadCalendar(); }
  else if (tab === 'daily') { loadDaily(); }
  else if (tab === 'month-start') { loadMonthStart(); }
  else if (tab === 'month-end') { loadMonthEnd(); }
  else if (tab === 'weekly') { loadWeekly(); }
  else if (tab === 'always') { loadAlways(); }
}

/* ── Progress helpers ─────────────────────────────────────────────── */
function renderProg(containerId, checked, total) {
  var pct = total > 0 ? Math.round((checked / total) * 100) : 0;
  var el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = '<div class="prog-label"><span>' + checked + ' / ' + total + '</span><span>' + pct + '%</span></div>'
    + '<div class="prog-bar"><div class="prog-fill" style="width:' + pct + '%"></div></div>';
}

/* ── DASHBOARD ────────────────────────────────────────────────────── */
function onLimitChange(val) {
  dashLimit = parseInt(val, 10);
  localStorage.setItem('dashLimit', String(dashLimit));
  loadDashboard();
}

function loadDashboard() {
  var sel = document.getElementById('limit-select');
  if (sel) sel.value = String(dashLimit);
  var url = '/dashboard?limit=' + dashLimit;
  apiGet(url).then(function(d) {
    renderDashHero(d);
    renderDashProgress(d);
    renderDashItems(d.items);
  }).catch(function(e) {
    console.error(e);
  });
}

function renderDashHero(d) {
  var periodMap = {
    month_start: '월초 집중 (1~5일)',
    month_end: '월말 집중 (25일~)',
    normal: '평상시'
  };
  var label = periodMap[d.current_period] || d.current_period;
  var el = document.getElementById('dash-hero');
  if (!el) return;
  el.innerHTML = '<div class="dash-hero">'
    + '<div class="dash-hero-date">' + d.today + '</div>'
    + '<div class="dash-hero-period">오늘 할 일 <span class="period-badge">' + label + '</span></div>'
    + '</div>';
}

function renderDashProgress(d) {
  var el = document.getElementById('dash-prog-grid');
  if (!el) return;
  var monthData = d.current_period === 'month_start' ? d.month_start : d.month_end;
  var monthLabel = d.current_period === 'month_start' ? '월초' : d.current_period === 'month_end' ? '월말' : '월간';
  var sections = [
    { label: '매일', data: d.daily },
    { label: monthLabel, data: monthData },
    { label: '주간', data: d.weekly },
    { label: '상시', data: d.always }
  ];
  el.innerHTML = sections.map(function(s) {
    var pct = s.data.total > 0 ? Math.round((s.data.checked / s.data.total) * 100) : 0;
    return '<div class="prog-mini">'
      + '<div class="prog-mini-label">' + s.label + '</div>'
      + '<div class="prog-mini-nums"><span>' + s.data.checked + '/' + s.data.total + '</span><span>' + pct + '%</span></div>'
      + '<div class="prog-bar"><div class="prog-fill" style="width:' + pct + '%"></div></div>'
      + '</div>';
  }).join('');
}

function renderDashItems(items) {
  var el = document.getElementById('dash-items');
  if (!el) return;
  if (!items || items.length === 0) {
    el.innerHTML = '<div class="dash-empty">오늘 할 일이 없습니다!</div>';
    return;
  }
  var typeLabels = {
    daily: '매일', month_start: '월초', month_end: '월말',
    weekly: '주간', always: '상시'
  };
  el.innerHTML = items.map(function(it) {
    var typeLabel = typeLabels[it.type] || it.type;
    var urgentClass = it.is_urgent ? ' urgent' : '';
    var deadlineStr = it.deadline ? ' · 마감: ' + it.deadline : '';
    var prioStr = it.priority ? ' · P' + it.priority : '';
    var metaStr = (it.status || it.deadline)
      ? '<div style="font-size:11px;color:var(--text-dim);margin-top:3px">' + (it.status || '') + deadlineStr + prioStr + '</div>'
      : '';
    return '<div class="dash-item' + urgentClass + '">'
      + '<span class="dash-item-type type-' + it.type + '">' + typeLabel + '</span>'
      + '<div><div class="dash-item-title">' + esc(it.title) + '</div>' + metaStr + '</div>'
      + '</div>';
  }).join('');
}

/* ── CALENDAR ─────────────────────────────────────────────────────── */
function calPrev() {
  calMonth -= 1;
  if (calMonth < 0) { calMonth = 11; calYear -= 1; }
  loadCalendar();
}

function calNext() {
  calMonth += 1;
  if (calMonth > 11) { calMonth = 0; calYear += 1; }
  loadCalendar();
}

function loadCalendar() {
  var monthNames = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'];
  var label = document.getElementById('cal-month-label');
  if (label) label.textContent = calYear + '년 ' + monthNames[calMonth];
  apiGet('/calendar?year=' + calYear + '&month=' + (calMonth + 1)).then(function(events) {
    calEvents = {};
    events.forEach(function(ev) {
      var d = ev.event_date;
      if (!calEvents[d]) calEvents[d] = [];
      calEvents[d].push(ev);
    });
    renderCalGrid();
  }).catch(function(e) { console.error(e); });
}

function renderCalGrid() {
  var grid = document.getElementById('cal-grid');
  if (!grid) return;
  var dows = ['일','월','화','수','목','금','토'];
  var html = dows.map(function(d) { return '<div class="cal-dow">' + d + '</div>'; }).join('');
  var firstDay = new Date(calYear, calMonth, 1).getDay();
  var daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
  var prevDays = new Date(calYear, calMonth, 0).getDate();
  var today = new Date();
  var todayY = today.getFullYear();
  var todayM = today.getMonth();
  var todayD = today.getDate();

  var cells = [];
  var i;
  for (i = 0; i < firstDay; i++) {
    cells.push({ day: prevDays - firstDay + 1 + i, curMonth: false, date: null });
  }
  for (i = 1; i <= daysInMonth; i++) {
    var dateStr = calYear + '-' + pad2(calMonth + 1) + '-' + pad2(i);
    cells.push({ day: i, curMonth: true, date: dateStr });
  }
  var rem = cells.length % 7 === 0 ? 0 : 7 - (cells.length % 7);
  for (i = 1; i <= rem; i++) {
    cells.push({ day: i, curMonth: false, date: null });
  }

  html += cells.map(function(c) {
    var classes = ['cal-day'];
    if (!c.curMonth) { classes.push('other-month'); }
    if (c.curMonth) {
      if (c.day >= 1 && c.day <= 5) { classes.push('period-ms'); }
      else if (c.day >= 25) { classes.push('period-me'); }
      var dateObj = new Date(calYear, calMonth, c.day);
      if (dateObj.getDay() === 1) { classes.push('period-weekly'); }
      if (calYear === todayY && calMonth === todayM && c.day === todayD) { classes.push('today'); }
    }
    var dots = '';
    if (c.date && calEvents[c.date] && calEvents[c.date].length > 0) {
      var count = Math.min(calEvents[c.date].length, 3);
      for (var x = 0; x < count; x++) {
        dots += '<div class="dot"></div>';
      }
    }
    var clickAttr = c.date ? ' onclick="openCalDay(\'' + c.date + '\')"' : '';
    return '<div class="' + classes.join(' ') + '"' + clickAttr + '>'
      + '<span class="cal-day-num">' + c.day + '</span>'
      + '<div class="dot-wrap">' + dots + '</div>'
      + '</div>';
  }).join('');

  grid.innerHTML = html;
}

function openCalDay(dateStr) {
  calSelectedDate = dateStr;
  var modal = document.getElementById('cal-modal');
  var titleEl = document.getElementById('cal-modal-title');
  if (titleEl) titleEl.textContent = dateStr + ' 일정';
  document.getElementById('cal-ev-title').value = '';
  document.getElementById('cal-ev-memo').value = '';
  renderCalEventList();
  if (modal) modal.classList.remove('hidden');
}

function renderCalEventList() {
  var el = document.getElementById('cal-event-list');
  if (!el) return;
  var events = (calSelectedDate && calEvents[calSelectedDate]) || [];
  if (events.length === 0) {
    el.innerHTML = '<div style="color:var(--text-dim);font-size:13px;margin-bottom:8px">일정 없음</div>';
    return;
  }
  el.innerHTML = events.map(function(ev) {
    return '<div class="cal-event-item">'
      + '<div style="flex:1">'
        + '<div class="cal-event-item-title">' + esc(ev.title) + '</div>'
        + (ev.memo ? '<div class="cal-event-item-memo">' + esc(ev.memo) + '</div>' : '')
      + '</div>'
      + '<button class="icon-btn del" onclick="deleteCalEvent(' + ev.id + ')">&#128465;</button>'
      + '</div>';
  }).join('');
}

function closeCalModal() {
  document.getElementById('cal-modal').classList.add('hidden');
  calSelectedDate = null;
}

function saveCalEvent() {
  var title = document.getElementById('cal-ev-title').value.trim();
  if (!title || !calSelectedDate) return;
  var memoVal = document.getElementById('cal-ev-memo').value.trim();
  var memo = memoVal || null;
  apiPost('/calendar', { event_date: calSelectedDate, title: title, memo: memo }).then(function(ev) {
    if (!calEvents[calSelectedDate]) calEvents[calSelectedDate] = [];
    calEvents[calSelectedDate].push(ev);
    document.getElementById('cal-ev-title').value = '';
    document.getElementById('cal-ev-memo').value = '';
    renderCalEventList();
    renderCalGrid();
  }).catch(function(e) { alert('저장 실패: ' + e.message); });
}

function deleteCalEvent(id) {
  if (!confirm('삭제할까요?')) return;
  apiDelete('/calendar/' + id).then(function() {
    if (calSelectedDate && calEvents[calSelectedDate]) {
      calEvents[calSelectedDate] = calEvents[calSelectedDate].filter(function(ev) { return ev.id !== id; });
    }
    renderCalEventList();
    renderCalGrid();
  }).catch(function(e) { alert('삭제 실패: ' + e.message); });
}

/* ── CHECKLIST helpers ────────────────────────────────────────────── */
function renderCheckItem(item, type) {
  var checkedClass = item.is_checked ? ' checked' : '';
  var textClass = item.is_checked ? ' done' : '';
  var nextChecked = !item.is_checked;
  var safeTitle = escAttr(item.title);
  return '<div class="check-item">'
    + '<button class="check-circle' + checkedClass + '" onclick="toggleCheck(\'' + type + '\',' + item.id + ',' + nextChecked + ')"></button>'
    + '<div class="check-body"><div class="check-title' + textClass + '">' + esc(item.title) + '</div></div>'
    + '<div class="check-actions">'
      + '<button class="icon-btn" onclick="openEditModal(\'' + type + '\',' + item.id + ',\'' + safeTitle + '\')">&#9999;&#65039;</button>'
      + '<button class="icon-btn del" onclick="deleteCheckItem(\'' + type + '\',' + item.id + ')">&#128465;</button>'
    + '</div>'
    + '</div>';
}

function toggleCheck(type, id, checked) {
  var pathMap = {
    daily: '/daily/' + id + '/check?checked=' + checked,
    'month-start-task': '/month-start/tasks/' + id + '/check?checked=' + checked,
    'month-end': '/month-end/' + id + '/check?checked=' + checked,
    weekly: '/weekly-tasks/' + id + '/check?checked=' + checked
  };
  var path = pathMap[type];
  if (!path) return;
  apiPatch(path).then(function() { loadTab(currentTab); })
    .catch(function(e) { alert('변경 실패: ' + e.message); });
}

function deleteCheckItem(type, id) {
  if (!confirm('삭제할까요?')) return;
  var pathMap = {
    daily: '/daily/' + id,
    'month-start-task': '/month-start/tasks/' + id,
    'month-end': '/month-end/' + id,
    weekly: '/weekly-tasks/' + id
  };
  var path = pathMap[type];
  if (!path) return;
  apiDelete(path).then(function() { loadTab(currentTab); })
    .catch(function(e) { alert('삭제 실패: ' + e.message); });
}

function openEditModal(type, id, title) {
  document.getElementById('edit-type').value = type;
  document.getElementById('edit-id').value = String(id);
  document.getElementById('edit-title-input').value = title;
  document.getElementById('edit-modal').classList.remove('hidden');
}

function closeEditModal() {
  document.getElementById('edit-modal').classList.add('hidden');
}

function saveEditItem() {
  var type = document.getElementById('edit-type').value;
  var id = parseInt(document.getElementById('edit-id').value, 10);
  var title = document.getElementById('edit-title-input').value.trim();
  if (!title) return;
  var pathMap = {
    daily: '/daily/' + id,
    'month-start-task': '/month-start/tasks/' + id,
    'month-end': '/month-end/' + id,
    weekly: '/weekly-tasks/' + id
  };
  var path = pathMap[type];
  if (!path) return;
  apiPut(path, { title: title }).then(function() {
    closeEditModal();
    loadTab(currentTab);
  }).catch(function(e) { alert('수정 실패: ' + e.message); });
}

/* ── DAILY ────────────────────────────────────────────────────────── */
function loadDaily() {
  apiGet('/daily').then(function(items) {
    var checked = items.filter(function(i) { return i.is_checked; }).length;
    renderProg('daily-prog', checked, items.length);
    var el = document.getElementById('daily-list');
    if (el) el.innerHTML = items.map(function(i) { return renderCheckItem(i, 'daily'); }).join('');
  }).catch(function(e) { console.error(e); });
}

function addDailyItem() {
  var inp = document.getElementById('daily-input');
  var title = inp.value.trim();
  if (!title) return;
  apiPost('/daily', { title: title }).then(function() {
    inp.value = '';
    loadDaily();
  }).catch(function(e) { alert('추가 실패: ' + e.message); });
}

function resetDaily() {
  if (!confirm('오늘 체크한 항목을 모두 초기화할까요?')) return;
  apiPost('/daily/reset', {}).then(function() { loadDaily(); })
    .catch(function(e) { alert('초기화 실패: ' + e.message); });
}

/* ── MONTH START ──────────────────────────────────────────────────── */
function loadMonthStart() {
  Promise.all([
    apiGet('/month-start/tasks'),
    apiGet('/month-start/hospitals/cafe'),
    apiGet('/month-start/hospitals/review')
  ]).then(function(results) {
    var tasks = results[0];
    var cafe = results[1];
    var review = results[2];
    var checked = tasks.filter(function(i) { return i.is_checked; }).length;
    renderProg('ms-prog', checked, tasks.length);
    var el = document.getElementById('ms-task-list');
    if (el) el.innerHTML = tasks.map(function(i) { return renderCheckItem(i, 'month-start-task'); }).join('');
    renderHospGrid('ms-cafe-list', 'ms-cafe-prog', cafe, 'cafe');
    renderHospGrid('ms-review-list', 'ms-review-prog', review, 'review');
  }).catch(function(e) { console.error(e); });
}

function addMsTask() {
  var inp = document.getElementById('ms-input');
  var title = inp.value.trim();
  if (!title) return;
  apiPost('/month-start/tasks', { title: title }).then(function() {
    inp.value = '';
    loadMonthStart();
  }).catch(function(e) { alert('추가 실패: ' + e.message); });
}

function resetMonthStart() {
  if (!confirm('월초 체크를 모두 초기화할까요?')) return;
  apiPost('/month-start/reset', {}).then(function() { loadMonthStart(); })
    .catch(function(e) { alert('초기화 실패: ' + e.message); });
}

function renderHospGrid(listId, progId, items, kind) {
  var checkedCount = items.filter(function(i) { return i.is_checked; }).length;
  renderProg(progId, checkedCount, items.length);
  var el = document.getElementById(listId);
  if (!el) return;
  el.innerHTML = items.map(function(item) {
    var cls = item.is_checked ? ' checked' : '';
    return '<div class="hosp-item' + cls + '" onclick="toggleHosp(\'' + kind + '\',' + item.id + ',' + !item.is_checked + ')">'
      + '<div class="hosp-circle"></div>'
      + '<span class="hosp-name">' + esc(item.name) + '</span>'
      + '</div>';
  }).join('');
}

function toggleHosp(kind, id, checked) {
  var path = '/month-start/hospitals/' + kind + '/' + id + '/check?checked=' + checked;
  apiPatch(path).then(function() { loadMonthStart(); })
    .catch(function(e) { alert('변경 실패: ' + e.message); });
}

/* ── MONTH END ────────────────────────────────────────────────────── */
function loadMonthEnd() {
  apiGet('/month-end').then(function(items) {
    var checked = items.filter(function(i) { return i.is_checked; }).length;
    renderProg('me-prog', checked, items.length);
    var el = document.getElementById('me-list');
    if (el) el.innerHTML = items.map(function(i) { return renderCheckItem(i, 'month-end'); }).join('');
  }).catch(function(e) { console.error(e); });
}

function addMeItem() {
  var inp = document.getElementById('me-input');
  var title = inp.value.trim();
  if (!title) return;
  apiPost('/month-end', { title: title }).then(function() {
    inp.value = '';
    loadMonthEnd();
  }).catch(function(e) { alert('추가 실패: ' + e.message); });
}

function resetMonthEnd() {
  if (!confirm('월말 체크를 모두 초기화할까요?')) return;
  apiPost('/month-end/reset', {}).then(function() { loadMonthEnd(); })
    .catch(function(e) { alert('초기화 실패: ' + e.message); });
}

/* ── WEEKLY ───────────────────────────────────────────────────────── */
function loadWeekly() {
  apiGet('/weekly-tasks').then(function(items) {
    var checked = items.filter(function(i) { return i.is_checked; }).length;
    renderProg('weekly-prog', checked, items.length);
    var el = document.getElementById('weekly-list');
    if (el) el.innerHTML = items.map(function(i) { return renderCheckItem(i, 'weekly'); }).join('');
  }).catch(function(e) { console.error(e); });
}

function addWeeklyItem() {
  var inp = document.getElementById('weekly-input');
  var title = inp.value.trim();
  if (!title) return;
  apiPost('/weekly-tasks', { title: title }).then(function() {
    inp.value = '';
    loadWeekly();
  }).catch(function(e) { alert('추가 실패: ' + e.message); });
}

function resetWeekly() {
  if (!confirm('주간 체크를 모두 초기화할까요?')) return;
  apiPost('/weekly-tasks/reset', {}).then(function() { loadWeekly(); })
    .catch(function(e) { alert('초기화 실패: ' + e.message); });
}

/* ── ALWAYS ON ────────────────────────────────────────────────────── */
function loadAlways() {
  apiGet('/always').then(function(items) {
    var el = document.getElementById('always-list');
    if (!el) return;
    if (items.length === 0) {
      el.innerHTML = '<div class="dash-empty">등록된 할 일이 없습니다.</div>';
      return;
    }
    el.innerHTML = items.map(function(t) { return renderAlwaysItem(t); }).join('');
  }).catch(function(e) { console.error(e); });
}

function renderAlwaysItem(t) {
  var today = new Date();
  var isUrgent = false;
  if (t.deadline) {
    var dl = new Date(t.deadline);
    var diff = (dl - today) / 86400000;
    if (diff <= 3) isUrgent = true;
  }
  if (t.priority >= 4) isUrgent = true;
  var urgentClass = isUrgent ? ' urgent' : '';
  var prioClass = 'badge badge-p' + t.priority;
  var stClass = 'badge badge-' + t.status;
  var stLabels = { pending: '대기', in_progress: '진행중', done: '완료' };
  var stText = stLabels[t.status] || t.status;
  var dlStr = t.deadline
    ? '<span class="badge badge-deadline' + (isUrgent ? ' urgent' : '') + '">&#128197; ' + t.deadline + '</span>'
    : '';
  var memoStr = t.memo ? '<div class="task-memo">' + esc(t.memo) + '</div>' : '';
  var doneClass = t.status === 'done' ? ' done-text' : '';
  return '<div class="task-item' + urgentClass + '">'
    + '<div class="task-header">'
      + '<div class="task-title' + doneClass + '">' + esc(t.title) + '</div>'
      + '<div class="task-actions">'
        + '<button class="icon-btn" onclick="openAlwaysModal(' + t.id + ')">&#9999;&#65039;</button>'
        + '<button class="icon-btn del" onclick="deleteAlwaysTask(' + t.id + ')">&#128465;</button>'
      + '</div>'
    + '</div>'
    + '<div class="task-meta">'
      + '<span class="' + prioClass + '">P' + t.priority + '</span>'
      + '<span class="' + stClass + '">' + stText + '</span>'
      + dlStr
    + '</div>'
    + memoStr
    + '</div>';
}

function openAlwaysModal(id) {
  document.getElementById('always-modal-title').textContent = id ? '할 일 수정' : '할 일 추가';
  document.getElementById('always-edit-id').value = id ? String(id) : '';
  document.getElementById('always-title-input').value = '';
  document.getElementById('always-priority-input').value = '3';
  document.getElementById('always-status-input').value = 'pending';
  document.getElementById('always-deadline-input').value = '';
  document.getElementById('always-memo-input').value = '';
  if (id) {
    apiGet('/always/' + id).then(function(t) {
      document.getElementById('always-title-input').value = t.title;
      document.getElementById('always-priority-input').value = String(t.priority);
      document.getElementById('always-status-input').value = t.status;
      document.getElementById('always-deadline-input').value = t.deadline || '';
      document.getElementById('always-memo-input').value = t.memo || '';
    }).catch(function(e) { console.error(e); });
  }
  document.getElementById('always-modal').classList.remove('hidden');
}

function closeAlwaysModal() {
  document.getElementById('always-modal').classList.add('hidden');
}

function saveAlwaysTask() {
  var editId = document.getElementById('always-edit-id').value;
  var title = document.getElementById('always-title-input').value.trim();
  if (!title) { alert('제목을 입력하세요.'); return; }
  var priority = parseInt(document.getElementById('always-priority-input').value, 10);
  var status = document.getElementById('always-status-input').value;
  var deadlineVal = document.getElementById('always-deadline-input').value;
  var deadline = deadlineVal || null;
  var memoVal = document.getElementById('always-memo-input').value.trim();
  var memo = memoVal || null;
  var body = { title: title, priority: priority, status: status, deadline: deadline, memo: memo };
  var p = editId ? apiPut('/always/' + editId, body) : apiPost('/always', body);
  p.then(function() {
    closeAlwaysModal();
    loadAlways();
    if (currentTab === 'dashboard') loadDashboard();
  }).catch(function(e) { alert('저장 실패: ' + e.message); });
}

function deleteAlwaysTask(id) {
  if (!confirm('삭제할까요?')) return;
  apiDelete('/always/' + id).then(function() {
    loadAlways();
    if (currentTab === 'dashboard') loadDashboard();
  }).catch(function(e) { alert('삭제 실패: ' + e.message); });
}

function openBulkModal() {
  document.getElementById('bulk-text').value = '';
  document.getElementById('bulk-preview').textContent = '';
  document.getElementById('bulk-modal').classList.remove('hidden');
}

function closeBulkModal() {
  document.getElementById('bulk-modal').classList.add('hidden');
}

function confirmBulk() {
  var text = document.getElementById('bulk-text').value.trim();
  if (!text) return;
  apiPost('/always/bulk', { text: text }).then(function(items) {
    closeBulkModal();
    loadAlways();
    alert(items.length + '개 항목이 등록되었습니다.');
  }).catch(function(e) { alert('등록 실패: ' + e.message); });
}

function copyForAI() {
  apiGet('/always').then(function(items) {
    if (items.length === 0) { alert('등록된 할 일이 없습니다.'); return; }
    var stLabels = { pending: '대기', in_progress: '진행중', done: '완료' };
    var lines = ['[상시 할 일 목록]'];
    items.forEach(function(t) {
      var dl = t.deadline ? ' | 마감: ' + t.deadline : '';
      var memo = t.memo ? ' | ' + t.memo : '';
      var st = stLabels[t.status] || t.status;
      lines.push('- ' + t.title + ' (P' + t.priority + ', ' + st + dl + memo + ')');
    });
    var text = lines.join('\n');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function() {
        alert('클립보드에 복사되었습니다.');
      }).catch(function() {
        fallbackCopy(text);
      });
    } else {
      fallbackCopy(text);
    }
  }).catch(function(e) { alert('불러오기 실패: ' + e.message); });
}

function fallbackCopy(text) {
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.top = '0';
  ta.style.left = '0';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  try {
    document.execCommand('copy');
    alert('클립보드에 복사되었습니다.');
  } catch (err) {
    alert('복사 실패. 직접 복사하세요:\n' + text);
  }
  document.body.removeChild(ta);
}

/* ── UTILS ────────────────────────────────────────────────────────── */
function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escAttr(str) {
  if (!str) return '';
  return String(str)
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
    .replace(/\n/g, ' ');
}

function pad2(n) {
  return n < 10 ? '0' + n : String(n);
}

/* ── INIT ─────────────────────────────────────────────────────────── */
(function init() {
  var sel = document.getElementById('limit-select');
  if (sel) sel.value = String(dashLimit);
  loadDashboard();
}());
