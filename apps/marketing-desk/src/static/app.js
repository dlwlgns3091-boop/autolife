
// State
var currentTab='dashboard';
var monthlyGroup='early';
var editCtx=null;
var dashLimit=parseInt(localStorage.getItem('dashLimit')||'5');
var COUNTS=[1,3,5,0];

function gel(id){return document.getElementById(id);}
function api(path,opts){return fetch(path,Object.assign({headers:{'Content-Type':'application/json'}},opts||{})).then(function(r){if(!r.ok)throw r;return r.status===204?null:r.json();});}
function apiD(path,opts){return fetch(path,opts||{});}
function fmt(d){if(!d)return null;var dt=new Date(d+'T00:00:00');return dt.toLocaleDateString('ko-KR',{month:'numeric',day:'numeric'});}
function isUrgent(dl){if(!dl)return false;var t=new Date(dl+'T00:00:00');var now=new Date();now.setHours(0,0,0,0);return t<=now;}
function statusLabel(s){return s==='done'?'완료':s==='in_progress'?'진행중':'대기';}
function pStar(p){var s='';for(var i=0;i<p;i++)s+='★';for(var j=p;j<5;j++)s+='☆';return s;}
function pLabel(g){return g==='early'?'월초':g==='mid'?'월중':'월말';}
function escH(s){return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}

function switchTab(tab){
  currentTab=tab;
  document.querySelectorAll('.section').forEach(function(s){s.classList.remove('active');});
  document.querySelectorAll('.bottom-nav button').forEach(function(b){b.classList.remove('active');});
  gel('sec-'+tab).classList.add('active');
  document.querySelector('[data-sec="'+tab+'"]').classList.add('active');
  if(tab==='dashboard')loadDashboard();
  else if(tab==='step0')loadStep0();
  else if(tab==='weekly')loadWeekly();
  else if(tab==='monthly')loadMonthly();
  else if(tab==='immediate')loadImmediate();
}

function openModal(id){gel(id).classList.add('open');}
function closeModal(id){gel(id).classList.remove('open');}
function showForm(id){gel(id).classList.add('visible');}
function hideForm(id){gel(id).classList.remove('visible');}

// === DASHBOARD ===
function loadDashboard(){
  api('/dashboard?limit='+dashLimit).then(function(data){
    renderSummary(data);
    renderDashItems(data);
    renderCountBtns();
  }).catch(function(e){console.error(e);});
}

function renderCountBtns(){
  var el=gel('count-btns');
  el.innerHTML='';
  var labels=['1','3','5','전체'];
  COUNTS.forEach(function(v,i){
    var b=document.createElement('button');
    b.className='count-btn'+(v===dashLimit?' active':'');
    b.textContent=labels[i];
    (function(val){b.onclick=function(){dashLimit=val;localStorage.setItem('dashLimit',val);loadDashboard();};})(v);
    el.appendChild(b);
  });
}

function renderSummary(data){
  var el=gel('dash-summary');
  var sections=[
    ['step0','STEP 0',data.step0],
    ['weekly','매주 루틴',data.weekly],
    ['monthly','매월 루틴',data.monthly],
    ['immediate','즉시처리',data.immediate]
  ];
  el.innerHTML=sections.map(function(s){
    return '<div class="sum-card" onclick="switchTab(\''+s[0]+'\')" style="cursor:pointer">'
      +'<div class="sum-num">'+s[2].checked+'/'+s[2].total+'</div>'
      +'<div class="sum-label">'+s[1]+'</div></div>';
  }).join('');
}

function renderDashItems(data){
  var el=gel('dash-items');
  if(!data.items.length){
    el.innerHTML='<div class="dash-empty">✅ 지금 당장 할 일이 없어요!</div>';
    return;
  }
  var typeTabMap={step0:'step0',weekly:'weekly',monthly:'monthly','immediate':'immediate'};
  var typeLabelMap={step0:'STEP0',weekly:'매주',monthly:'매월','immediate':'즉시처리'};
  el.innerHTML=data.items.map(function(item){
    var tl=typeLabelMap[item.type]||'';
    if(item.type==='monthly'&&item.group)tl+=('('+pLabel(item.group)+')');
    var meta=tl+(item.deadline?' · '+fmt(item.deadline):'')+(item.priority?' · P'+item.priority:'');
    var tab=typeTabMap[item.type]||'dashboard';
    return '<div class="dash-item">'
      +'<div class="dash-item-circle" onclick="dashCheck(event,\''+item.type+'\','+item.id+')"></div>'
      +'<div class="dash-item-info" onclick="switchTab(\''+tab+'\')">'
      +'<div class="dash-item-title'+(item.is_urgent?' urgent':'')+'">'+escH(item.title)+'</div>'
      +'<div class="dash-item-type">'+meta+'</div></div></div>';
  }).join('');
}

function dashCheck(e,type,id){
  e.stopPropagation();
  var p;
  if(type==='step0')p=apiD('/step0/'+id+'/check?checked=true',{method:'PATCH'});
  else if(type==='weekly')p=apiD('/weekly/'+id+'/check?checked=true',{method:'PATCH'});
  else if(type==='monthly')p=apiD('/monthly/'+id+'/check?checked=true',{method:'PATCH'});
  else p=apiD('/immediate/'+id+'/status?status=done',{method:'PATCH'});
  p.then(function(){loadDashboard();});
}

// === STEP 0 ===
function loadStep0(){
  api('/step0').then(function(items){
    var checked=items.filter(function(i){return i.is_checked;}).length;
    var pct=items.length?Math.round(checked/items.length*100):0;
    gel('step0-prog-label').textContent='진행률 '+checked+'/'+items.length+' ('+pct+'%)';
    gel('step0-bar').style.width=pct+'%';
    gel('step0-list').innerHTML=items.length
      ?items.map(function(i){return renderCheck(i,'step0');}).join('')
      :'<p style="color:var(--muted);font-size:13px;padding:8px 0">항목이 없습니다.</p>';
  });
}

function renderCheck(i,type){
  return '<div class="check-item">'
    +'<div class="check-circle'+(i.is_checked?' checked':'')+'" onclick="toggleCheck(\''+type+'\','+i.id+','+(i.is_checked?'false':'true')+')"></div>'
    +'<div class="check-body"><div class="check-title'+(i.is_checked?' done-text':'')+'">'+escH(i.title)+'</div>'
    +(i.memo?'<div class="check-memo">'+escH(i.memo)+'</div>':'')
    +'</div><div class="check-actions">'
    +'<button class="icon-btn" onclick="openEdit(\''+type+'\','+i.id+')">✏️</button>'
    +'<button class="icon-btn del" onclick="delCheck(\''+type+'\','+i.id+')">🗑️</button>'
    +'</div></div>';
}

function toggleCheck(type,id,checked){
  var ep=type==='step0'?'/step0/':type==='weekly'?'/weekly/':'/monthly/';
  apiD(ep+id+'/check?checked='+checked,{method:'PATCH'}).then(function(){
    if(type==='step0')loadStep0();else if(type==='weekly')loadWeekly();else loadMonthly();
  });
}

function saveStep0(){
  var title=gel('step0-title').value.trim();
  if(!title){alert('제목을 입력하세요');return;}
  api('/step0',{method:'POST',body:JSON.stringify({title:title,memo:gel('step0-memo').value.trim()||null})}).then(function(){
    gel('step0-title').value='';gel('step0-memo').value='';hideForm('step0-form');loadStep0();
  });
}

function delCheck(type,id){
  if(!confirm('삭제할까요?'))return;
  var ep=type==='step0'?'/step0/':type==='weekly'?'/weekly/':'/monthly/';
  apiD(ep+id,{method:'DELETE'}).then(function(){
    if(type==='step0')loadStep0();else if(type==='weekly')loadWeekly();else loadMonthly();
  });
}

// === WEEKLY ===
function loadWeekly(){
  api('/weekly').then(function(items){
    var checked=items.filter(function(i){return i.is_checked;}).length;
    var pct=items.length?Math.round(checked/items.length*100):0;
    gel('weekly-prog-label').textContent='진행률 '+checked+'/'+items.length+' ('+pct+'%)';
    gel('weekly-bar').style.width=pct+'%';
    gel('weekly-list').innerHTML=items.length
      ?items.map(function(i){return renderCheck(i,'weekly');}).join('')
      :'<p style="color:var(--muted);font-size:13px;padding:8px 0">항목이 없습니다.</p>';
  });
}

function saveWeekly(){
  var title=gel('weekly-title').value.trim();
  if(!title){alert('제목을 입력하세요');return;}
  api('/weekly',{method:'POST',body:JSON.stringify({title:title,memo:gel('weekly-memo').value.trim()||null})}).then(function(){
    gel('weekly-title').value='';gel('weekly-memo').value='';hideForm('weekly-form');loadWeekly();
  });
}

function resetWeek(){
  if(!confirm('이번 주 체크를 모두 초기화할까요?'))return;
  apiD('/weekly/reset',{method:'POST'}).then(function(){loadWeekly();});
}

// === MONTHLY ===
function switchGroup(g){
  monthlyGroup=g;
  document.querySelectorAll('.group-tab').forEach(function(b){b.classList.toggle('active',b.dataset.group===g);});
  loadMonthly();
}

function loadMonthly(){
  api('/monthly').then(function(all){
    var items=all.filter(function(i){return i.group===monthlyGroup;});
    var checked=items.filter(function(i){return i.is_checked;}).length;
    var pct=items.length?Math.round(checked/items.length*100):0;
    gel('monthly-prog-label').textContent=pLabel(monthlyGroup)+' 진행률 '+checked+'/'+items.length+' ('+pct+'%)';
    gel('monthly-bar').style.width=pct+'%';
    gel('monthly-list').innerHTML=items.length
      ?items.map(function(i){return renderCheck(i,'monthly');}).join('')
      :'<p style="color:var(--muted);font-size:13px;padding:8px 0">항목이 없습니다.</p>';
  });
}

function saveMonthly(){
  var title=gel('monthly-title').value.trim();
  if(!title){alert('제목을 입력하세요');return;}
  api('/monthly',{method:'POST',body:JSON.stringify({title:title,memo:gel('monthly-memo').value.trim()||null,group:monthlyGroup})}).then(function(){
    gel('monthly-title').value='';gel('monthly-memo').value='';hideForm('monthly-form');loadMonthly();
  });
}

function resetMonth(){
  if(!confirm('이번 달 체크를 모두 초기화할까요?'))return;
  apiD('/monthly/reset',{method:'POST'}).then(function(){loadMonthly();});
}

// === IMMEDIATE ===
function loadImmediate(){
  api('/immediate').then(function(tasks){
    if(!tasks.length){gel('immediate-list').innerHTML='<div class="card" style="text-align:center;color:var(--muted)">할일이 없습니다 🎉</div>';return;}
    gel('immediate-list').innerHTML='<div class="card">'+tasks.map(function(t){return renderTask(t);}).join('')+'</div>';
  });
}

function renderTask(t){
  var urg=isUrgent(t.deadline);
  var dlLabel=t.deadline?fmt(t.deadline):null;
  var stCls=t.status==='done'?'badge-st':t.status==='in_progress'?'badge-st ip':'badge-st pending';
  return '<div class="task-item">'
    +'<div class="task-body"><div class="task-title'+(urg?' urgent':'')+'">'+escH(t.title)+'</div>'
    +'<div class="task-meta"><span class="badge badge-p">'+pStar(t.priority)+'</span>'
    +(dlLabel?'<span class="badge badge-dl'+(urg?'':' ok')+'">📅 '+dlLabel+'</span>':'')
    +'<span class="badge '+stCls+'">'+statusLabel(t.status)+'</span>'
    +(t.memo?'<span style="font-size:11px;color:var(--muted)">'+escH(t.memo)+'</span>':'')
    +'</div></div>'
    +'<div class="task-actions"><button class="icon-btn" onclick="openEdit(\'immediate\','+t.id+')">✏️</button>'
    +'<button class="icon-btn del" onclick="delTask('+t.id+')">🗑️</button></div></div>';
}

function submitAddTask(){
  var title=gel('add-task-title').value.trim();
  if(!title){alert('제목을 입력하세요');return;}
  var body={title:title,priority:parseInt(gel('add-task-priority').value),status:gel('add-task-status').value,
    memo:gel('add-task-memo').value.trim()||null,deadline:gel('add-task-deadline').value||null};
  api('/immediate',{method:'POST',body:JSON.stringify(body)}).then(function(){
    closeModal('add-task-modal');
    ['add-task-title','add-task-deadline','add-task-memo'].forEach(function(id){gel(id).value='';});
    loadImmediate();
  });
}

function delTask(id){
  if(!confirm('삭제할까요?'))return;
  apiD('/immediate/'+id,{method:'DELETE'}).then(function(){loadImmediate();});
}

function copyAI(){
  api('/immediate').then(function(tasks){
    if(!tasks.length){alert('할일이 없습니다');return;}
    var lines=tasks.map(function(t){
      return '- [P'+t.priority+'] '+t.title
        +(t.deadline?' (마감:'+t.deadline+')')
        +(t.status!=='pending'?' ['+statusLabel(t.status)+']':'')
        +(t.memo?' // '+t.memo:'');
    });
    var text='마케팅 데스크 즉시처리 현황:\n\n'+lines.join('\n')+'\n\n우선순위/마감을 고려해 오늘 집중할 3가지를 추천해주세요.';
    navigator.clipboard.writeText(text).then(function(){alert('📋 AI용 텍스트가 복사되었습니다!');});
  });
}

function askAI(){
  api('/immediate').then(function(tasks){
    var lines=tasks.map(function(t){
      return '- [P'+t.priority+'] '+t.title
        +(t.deadline?' (마감:'+t.deadline+')')
        +(t.status!=='pending'?' ['+statusLabel(t.status)+']':'')
        +(t.memo?' // '+t.memo:'');
    });
    var text='마케팅 데스크 즉시처리 현황:\n\n'+lines.join('\n')+'\n\n우선순위/마감을 고려해 오늘 집중할 3가지를 추천해주세요.';
    navigator.clipboard.writeText(text).then(function(){alert('✅ 클립보드에 복사되었어요!\n\nClaude/ChatGPT에 붙여넣으면 AI 조언을 받을 수 있습니다.');});
  });
}

function previewBulk(){
  var text=gel('bulk-text').value;
  if(!text.trim()){alert('내용을 입력하세요');return;}
  api('/immediate/bulk/preview',{method:'POST',body:JSON.stringify({text:text})}).then(function(data){
    if(!data.preview||!data.preview.length){
      gel('bulk-preview-area').innerHTML='<p style="color:var(--danger);font-size:12px;margin-top:8px">파싱된 항목이 없습니다.</p>';
      gel('bulk-confirm-btn').style.display='none';return;
    }
    gel('bulk-preview-area').innerHTML='<div class="bulk-preview">'+data.preview.map(function(r){
      return '<div class="bulk-row">P'+r.priority+' | '+escH(r.title)+(r.deadline?' | '+r.deadline:'')+(r.memo?' | '+escH(r.memo):'')+'</div>';
    }).join('')+'</div>';
    gel('bulk-confirm-btn').style.display='inline-block';
  });
}

function confirmBulk(){
  var text=gel('bulk-text').value;
  api('/immediate/bulk',{method:'POST',body:JSON.stringify({text:text})}).then(function(){
    closeModal('bulk-modal');
    gel('bulk-text').value='';gel('bulk-preview-area').innerHTML='';gel('bulk-confirm-btn').style.display='none';
    loadImmediate();
  });
}

// === EDIT MODAL ===
function openEdit(type,id){
  editCtx={type:type,id:id};
  var isTask=(type==='immediate');
  var isMon=(type==='monthly');
  gel('edit-modal-title').textContent=isTask?'할일 수정':'항목 수정';
  gel('edit-group-row').style.display=isMon?'block':'none';
  gel('edit-deadline-row').style.display=isTask?'block':'none';
  gel('edit-priority-row').style.display=isTask?'block':'none';
  gel('edit-status-row').style.display=isTask?'block':'none';
  var ep=type==='step0'?'/step0/':type==='weekly'?'/weekly/':type==='monthly'?'/monthly/':'/immediate/';
  api(ep+id).then(function(item){
    gel('edit-title').value=item.title||'';
    gel('edit-memo').value=item.memo||'';
    if(isMon)gel('edit-group').value=item.group||monthlyGroup;
    if(isTask){gel('edit-deadline').value=item.deadline||'';gel('edit-priority').value=item.priority||3;gel('edit-status').value=item.status||'pending';}
    openModal('edit-modal');
  });
}

function submitEdit(){
  if(!editCtx)return;
  var type=editCtx.type;var id=editCtx.id;
  var title=gel('edit-title').value.trim();
  if(!title){alert('제목을 입력하세요');return;}
  var body={title:title,memo:gel('edit-memo').value.trim()||null};
  if(type==='monthly')body.group=gel('edit-group').value;
  if(type==='immediate'){body.deadline=gel('edit-deadline').value||null;body.priority=parseInt(gel('edit-priority').value);body.status=gel('edit-status').value;}
  var ep=type==='step0'?'/step0/':type==='weekly'?'/weekly/':type==='monthly'?'/monthly/':'/immediate/';
  api(ep+id,{method:'PUT',body:JSON.stringify(body)}).then(function(){
    closeModal('edit-modal');
    if(type==='step0')loadStep0();else if(type==='weekly')loadWeekly();else if(type==='monthly')loadMonthly();else loadImmediate();
  });
}

// GET individual items for edit (need these endpoints)
// We use the list endpoints and filter — or add individual GET routes
// For now, relying on the edit modal's data being passed inline via onclick

// Init
(function(){
  loadDashboard();
  var d=new Date();
  var day=d.getDate();
  monthlyGroup=day<=10?'early':day<=20?'mid':'late';
  document.querySelectorAll('.group-tab').forEach(function(t){t.classList.toggle('active',t.dataset.group===monthlyGroup);});
})();
