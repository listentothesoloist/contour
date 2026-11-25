/* North Berry · accountant workspace. Invoice reconciliation against case datasets. */
(function () {
  'use strict';
  const INITIAL_DATA = window.CASE04_DATA || {items:[], orders:[], approvals:[], rules:[], jury_presets:[], summary:{}};
  let DATA = INITIAL_DATA;
  const $ = id => document.getElementById(id);
  const escapeHtml = str => String(str ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  const formatAmount = val => '$' + Number(val || 0).toLocaleString('en-US',{maximumFractionDigits:2});
  const number = val => Number(val || 0).toLocaleString('en-US',{maximumFractionDigits:2});
  const icon = name => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
  const cleanSupplier = str => String(str || '').replace(/[«»"]/g,'');
  const STATUS = {
    READY_TO_PAY:{label:'Ready for registry',color:'emerald'},
    CRITICAL_REQUISITES:{label:'Bank details',color:'rose'},
    DUPLICATE_OR_REPLACED:{label:'Duplicate / version',color:'amber'},
    PRICE_OR_QTY_UNAPPROVED:{label:'Price / quantity',color:'orange'},
    MATH_ERROR:{label:'Arithmetic error',color:'purple'},
    NOT_ACCEPTED_YET:{label:'No receipt',color:'blue'},
    INFO_LETTER:{label:'Info email',color:'slate'},
    NEEDS_REVIEW:{label:'Needs review',color:'slate'}
  };
  const needsAttention = x => !['READY_TO_PAY','INFO_LETTER'].includes(x.status_code);
  let readyItems = [];
  let blockedItems = [];
  let treasurerChecks = {};
  let customXlsxBase64 = null;
  let currentSourceName = 'case04.xlsx';
  let xlsxReview = null;
  const hasXlsxProposal = item => xlsxReview && Object.hasOwn(xlsxReview.proposals, item.id);
  const badge = item => {const s = (item.status_code==='NOT_ACCEPTED_YET' && (item.available_accepted_qty??item.order?.accepted_qty)>0 ? {label:'Partial receipt',color:'blue'} : null) || STATUS[item.status_code] || {label:item.status_label || 'Needs review',color:'slate'};return `<span class="status-badge badge-${s.color}" title="${escapeHtml(item.status_label)}">${escapeHtml(s.label)}</span>`;};
  let selectedEmailId = null;
  let statusFilter = 'ALL', reasonFilter = 'ALL', ruleFilter = 'ALL', searchQuery = '', newestFirst = true;
  let currentTab = 'tab-queue';
  let currentJuryResult = null;
  const compactWorkspace = matchMedia('(max-width: 860px)');
  const pageMeta = {
    'tab-queue':['Supplier Invoices','Snapshot as of Nov 16, 2026, 12:00 UTC'],
    'tab-registry':['Payment Registry','Verify bank statements and export confirmed invoices for payment processing.'],
    'tab-jury':['Check Email','Reconcile an invoice against purchase orders and warehouse receipts'],
    'tab-reference':['Reference Data','Purchase orders, receipts, and approvals backing every decision.'],
    'tab-analytics':['Analytics','Queue breakdown, discrepancy drivers, and pilot impact estimate.']
  };
  function navigate(id, updateHash = true) {
    if (!pageMeta[id]) id='tab-queue';
    currentTab=id;
    document.querySelectorAll('.nav-tab').forEach(b=>{const active=b.dataset.tab===id;b.classList.toggle('active',active);if(active)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
    document.querySelectorAll('.tab-panel').forEach(p=>{p.classList.toggle('active',p.id===id);p.hidden=p.id!==id;});
    $('pageTitle').textContent=pageMeta[id][0];$('pageDescription').textContent=pageMeta[id][1];
    document.title=pageMeta[id][0]+' — North Berry';
    const gotoBtn=document.querySelector('.page-heading [data-goto]');
    if(gotoBtn) gotoBtn.hidden=id==='tab-jury';
    if(updateHash) history.replaceState(null,'','#'+id.replace('tab-',''));
  }
  document.querySelectorAll('.nav-tab').forEach(button => {
    button.title = button.textContent.trim();
    button.addEventListener('click', () => navigate(button.dataset.tab));
  });
  document.querySelectorAll('[data-goto]').forEach(b => b.addEventListener('click', () => {
    navigate(b.dataset.goto);
    if (b.dataset.goto === 'tab-jury') showJuryPane('editor');
    $('main').focus({preventScroll: true});
  }));
  document.querySelector('.skip-link').addEventListener('click', event => {
    event.preventDefault();
    $('main').focus({preventScroll: true});
  });
  window.addEventListener('hashchange',()=>navigate('tab-'+location.hash.slice(1),false));
  function toast(text) {$('appToast').textContent=text;$('appToast').hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('appToast').hidden=true,4000);}

  $('btnToggleSidebar').addEventListener('click', event => {
    const button = event.currentTarget;
    const collapsed = $('appFrame').classList.toggle('sidebar-collapsed');
    const label = collapsed ? 'Expand sidebar' : 'Collapse sidebar';
    button.setAttribute('aria-expanded', String(!collapsed));
    button.setAttribute('aria-label', label);
    button.title = label;
  });

  function showQueueList() {
    $('queueSplit').dataset.pane = 'list';
    const selected = $('queueTableBody').querySelector('[aria-current="true"]');
    (selected || $('queueSearchInput')).focus({preventScroll: true});
  }

  document.querySelectorAll('[data-segments]').forEach(control => {
    const buttons = [...control.querySelectorAll('[data-show-pane]')];
    buttons.forEach(button => button.addEventListener('click', () => {
      buttons.forEach(segment => {
        const active = segment === button;
        segment.classList.toggle('active', active);
        segment.setAttribute('aria-pressed', String(active));
        $(segment.dataset.showPane).hidden = !active;
      });
    }));
  });

  // Queue filters and sorting.
  function filteredItems() {
    return DATA.items.filter(x=>{
      if(statusFilter==='ATTENTION'&&!needsAttention(x)) return false;
      if(!['ALL','ATTENTION'].includes(statusFilter)&&x.status_code!==statusFilter)return false;
      if(reasonFilter!=='ALL'&&x.status_code!==reasonFilter)return false;
      if(ruleFilter!=='ALL'&&!(x.triggered_rules||[]).includes(ruleFilter))return false;
      const hay=[x.id,x.sender,x.text,x.order_id,x.raw_invoice_no,x.status_label,x.primary_reason,x.order?.buyer,x.order?.material].join(' ').toLocaleLowerCase('en');
      return hay.includes(searchQuery.trim().toLocaleLowerCase('en'));
    }).sort((a,b)=>newestFirst?b.received_at.localeCompare(a.received_at):a.received_at.localeCompare(b.received_at));
  }
  function setStatusFilter(status) {
    statusFilter=status;reasonFilter='ALL';ruleFilter='ALL';$('reasonFilterSelect').value='ALL';
    document.querySelectorAll('#statusFilterPills .pill').forEach(b=>{const active=b.dataset.status===status;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
    renderQueue();
  }
  function renderQueue() {
    const filtered=filteredItems();
    if(!filtered.some(x=>x.id===selectedEmailId))selectedEmailId=filtered[0]?.id || null;
    $('queueCount').textContent=filtered.length;
    $('queueResultsLabel').textContent=`Showing ${filtered.length} of ${DATA.items.length} documents${ruleFilter!=='ALL'?' · '+ruleFilter:''}`;
    $('queueEmptyState').hidden=filtered.length>0;
    $('queueTableBody').innerHTML=filtered.map(item=>{
      const name=cleanSupplier(item.supplier_name),initials=name.split(/[\s-]+/).slice(0,2).map(w=>w[0]||'').join('').toUpperCase();
      const tone=[...name].reduce((s,c)=>s+c.charCodeAt(0),0)%5;
      const selected=item.id===selectedEmailId;
      const notes = [item.material_mapping, item.unit_mapping].filter(Boolean).map(mapping =>
        `<span>${escapeHtml(mapping.source)} → ${escapeHtml(mapping.target)}</span>`
      );
      if (hasXlsxProposal(item)) notes.push('<span>Confirm fields</span>');
      const matches = notes.length ? `<div class="queue-ai-note">${notes.join('')}</div>` : '';
      return `<tr data-email-id="${escapeHtml(item.id)}" class="${selected?'selected-row':''}"><td><div class="supplier-cell"><span class="supplier-avatar tone-${tone}" aria-hidden="true">${escapeHtml(initials)}</span><div class="supplier-info"><button class="supplier-name" aria-label="Open ${escapeHtml(item.id)}, ${escapeHtml(name)}" ${selected?'aria-current="true"':''}>${escapeHtml(name)}</button><div class="document-meta">${escapeHtml(item.id)} <span>·</span> ${item.raw_invoice_no&&item.raw_invoice_no!=='—'?'No. '+escapeHtml(item.raw_invoice_no):'Email'} <span>·</span> ${escapeHtml(item.order_id)}</div>${matches}</div></div></td><td>${badge(item)}</td><td class="number-cell"><div class="amount">${item.stated_amount?formatAmount(item.stated_amount):'—'}</div><div class="received-date">${escapeHtml(item.received_at)}</div></td><td>${icon('chevron')}</td></tr>`;
    }).join('');
    $('queueTableBody').querySelectorAll('[data-email-id]').forEach(row=>row.addEventListener('click',()=>{
      selectedEmailId=row.dataset.emailId;renderQueue();
      if (compactWorkspace.matches) {
        $('queueSplit').dataset.pane = 'detail';
        $('inspectorPanel').focus({preventScroll: true});
      } else {
        $('queueTableBody').querySelector('[aria-current="true"]')?.focus({preventScroll: true});
      }
    }));
    renderInspector();
  }
  document.querySelectorAll('#statusFilterPills .pill').forEach(b=>b.addEventListener('click',()=>setStatusFilter(b.dataset.status)));
  document.querySelectorAll('[data-quick-filter]').forEach(b=>b.addEventListener('click',()=>{searchQuery='';$('queueSearchInput').value='';setStatusFilter(b.dataset.quickFilter);}));
  $('queueSearchInput').addEventListener('input',e=>{searchQuery=e.target.value;renderQueue();});
  $('reasonFilterSelect').addEventListener('change',e=>{reasonFilter=e.target.value;renderQueue();});
  $('btnSortQueue').addEventListener('click',()=>{newestFirst=!newestFirst;$('btnSortQueue').title=newestFirst?'Newest first':'Oldest first';$('btnSortQueue').setAttribute('aria-label','Sort by date: '+$('btnSortQueue').title.toLowerCase());renderQueue();toast('Sorted: '+$('btnSortQueue').title.toLowerCase());});
  $('btnResetFilters').addEventListener('click',()=>{searchQuery='';$('queueSearchInput').value='';setStatusFilter('ALL');});
  document.addEventListener('keydown', event => {
    if (event.key !== '/' || currentTab !== 'tab-queue' || event.metaKey || event.ctrlKey || event.altKey ||
        /INPUT|TEXTAREA|SELECT/.test(event.target.tagName) || event.target.isContentEditable || $('messageModal').open) return;
    event.preventDefault();
    $('queueSplit').dataset.pane = 'list';
    $('queueSearchInput').focus();
  });

  // Inspector card: decision -> evidence -> next step.
  function buildCard(item, jury=false) {
    if(!item)return `<div class="inspector-empty">${icon(jury?'spark':'file')}<h3>${jury?'Result will appear here':'Select a document'}</h3><p>${jury?'Enter an email and run reconciliation to see the matched purchase order and any discrepancies.':'Documents matching the current filters appear in the queue on the left.'}</p></div>`;
    const ord=item.order, app=item.approval, ready=item.status_code==='READY_TO_PAY',info=item.status_code==='INFO_LETTER',review=item.status_code==='NEEDS_REVIEW';
    const checks=item.rule_checks||[],passed=checks.filter(c=>c.status==='ok').length;
    const calculated=item.raw_qty!=null&&item.raw_price!=null?item.raw_qty*item.raw_price:null;
    const title=ready?'Reconciliation passed':info?'Order information':review?'Manual review required':'Discrepancy detected';
    let comparison='';
    if(item.status_code==='MATH_ERROR'&&calculated!==null) comparison=`<div class="comparison"><div><span>Stated</span><strong>${formatAmount(item.stated_amount)}</strong></div><div><span>Calculated</span><strong>${formatAmount(calculated)}</strong></div><div class="difference"><span>Variance</span><strong>${item.stated_amount-calculated>0?'+':''}${formatAmount(item.stated_amount-calculated)}</strong></div></div>`;
    const checkHtml=checks.map(c=>`<li class="rule-check-item status-${escapeHtml(c.status)}">${icon(c.status==='ok'?'check':'alert')}<div><strong>${escapeHtml(c.rule)}</strong>${escapeHtml(c.detail)}</div></li>`).join('');
    const mappingHtml = [
      ['Material mapping', item.material_mapping],
      ['Unit mapping', item.unit_mapping]
    ].filter(([, mapping]) => mapping).map(([label, mapping]) =>
      `<div class="material-line material-mapping"><strong>${label}</strong><p>"${escapeHtml(mapping.source)}" → "${escapeHtml(mapping.target)}"</p><small>${mapping.method === 'ai' ? 'AI and order verification' : 'Order verification'} ${escapeHtml(item.order_id)}</small></div>`
    ).join('');
    const backButton = jury ? '' : '<button type="button" class="mobile-back">‹ Back to list</button>';
    const nextStep = `<div class="next-step"><div class="next-step-label">Next step</div><p>${escapeHtml(item.next_step)}</p>${(item.actions||[]).length?`<button type="button" class="btn btn-primary btn-open-draft">${icon('mail')}${ready?'Request statement check':'Open draft request'}</button>`:''}</div>`;
    return `<div class="inspector-top">${backButton}<span>${jury?'Check result':'Document analysis'}</span><span class="document-id">${escapeHtml(item.id)}</span></div>
    <div class="inspector-main">
      <div class="inspector-title-row"><h2>${info?'Order email':'Invoice No. '+escapeHtml(item.raw_invoice_no||'—')}</h2>${badge(item)}</div>
      <div class="inspector-subtitle"><strong>${escapeHtml(cleanSupplier(item.supplier_name))}</strong> · ${escapeHtml(item.received_at)}</div>
      ${info?'':`<div class="invoice-total"><span>Invoice total, excl. tax</span><strong>${formatAmount(item.stated_amount)}</strong></div>`}
      <div class="decision-box ${ready?'decision-ok':info||review?'decision-info':''}"><div class="decision-title">${icon(ready?'check':info||review?'info':'alert')}${title}</div><p>${escapeHtml(item.primary_reason)}</p></div>
      ${comparison}${mappingHtml}${nextStep}
      <details class="detail-disclosure"><summary><span>${icon('grid')}Invoice, order, and receipt ${ord?`<span class="disclosure-count">${escapeHtml(ord.order_id)}</span>`:''}</span>${icon('chevron')}</summary>
        ${ord?`<dl class="detail-kv"><dt>Order</dt><dd>${escapeHtml(ord.order_id)} dated ${escapeHtml(ord.order_date)}</dd><dt>Invoiced</dt><dd>${item.converted_qty!=null?number(item.converted_qty)+' '+escapeHtml(item.converted_unit)+' × '+formatAmount(item.converted_unit_price):'No line items'}</dd><dt>Ordered / accepted</dt><dd>${number(ord.ordered_qty)} / ${number(ord.accepted_qty)} ${escapeHtml(ord.unit)}</dd><dt>Order price</dt><dd>${formatAmount(ord.order_price)}</dd><dt>Buyer</dt><dd>${escapeHtml(ord.buyer)}</dd></dl><div class="material-line">${escapeHtml(ord.material)}</div>`:'<p>Purchase order not found in the workbook.</p>'}${item.conversion_formula?`<div class="formula-box">Packaging conversion · ${escapeHtml(item.conversion_formula)}</div>`:''}
      </details>
      <details class="detail-disclosure"><summary><span>${icon('mail')}Source email</span>${icon('chevron')}</summary><div class="email-sender">From: ${escapeHtml(item.sender)}</div><blockquote class="email-quote">${escapeHtml(item.text)}</blockquote></details>
      <details class="detail-disclosure"><summary><span>${icon('check')}Verification log <span class="disclosure-count">${passed} of ${checks.length}</span></span>${icon('chevron')}</summary><ul class="rule-check-list">${checkHtml}</ul><div class="approval-note">${app?`<strong>${escapeHtml(app.approval_id)} · ${escapeHtml(app.status)}</strong><br>${escapeHtml(app.summary||app.change_summary)}${app.signed_by?'<br>Signed by: '+escapeHtml(app.signed_by):''}`:'No addenda for this order. Original purchase order terms apply.'}</div></details>
    </div>`;
  }
  function renderInspector() {
    const item = DATA.items.find(x => x.id === selectedEmailId);
    const panel = $('inspectorPanel');
    const preservePosition = panel.dataset.emailId === item?.id;
    const position = preservePosition ? panel.scrollTop : 0;
    panel.dataset.emailId = item?.id ?? '';
    panel.innerHTML = buildCard(item);
    panel.querySelector('.mobile-back')?.addEventListener('click', showQueueList);
    panel.scrollTop = position;
    bindDraft(panel, item);
    if (!item || !hasXlsxProposal(item)) return;
    const proposal = xlsxReview.proposals[item.id];
    panel.querySelector('.decision-box').insertAdjacentHTML('afterend', `
      <section class="ai-proposal" aria-labelledby="xlsxProposalTitle">
        <h3 id="xlsxProposalTitle">Confirm extracted email fields</h3>
        <p>Compare the proposed values against the source email and confirm them to re-run reconciliation.</p>
        <dl>${aiFieldsMarkup(proposal.fields)}</dl>
        <button type="button" class="btn btn-primary" id="btnConfirmXlsxFields" ${xlsxReview.pending ? 'disabled' : ''}>Confirm and reconcile</button>
      </section>`);
    $('btnConfirmXlsxFields').addEventListener('click', () => runXlsxReview(item.id));
  }
  function bindDraft(container,item){container.querySelectorAll('.btn-open-draft').forEach(b=>b.addEventListener('click',()=>openActionModal(item.actions[0])));}
  function openActionModal(action){if(!action)return;$('modalRecipientRole').textContent=`${action.recipient_role} · ${action.rule_ref}`;$('modalRecipientName').textContent=action.recipient_name;$('modalSubject').textContent=action.subject;$('modalBodyText').textContent=action.body;$('copyConfirmToast').textContent='';$('messageModal').showModal();}
  $('messageModal').addEventListener('click',e=>{if(e.target!==$('messageModal'))return;const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();});
  $('btnCopyMessage').addEventListener('click',async()=>{const text=`Subject: ${$('modalSubject').textContent}\n\n${$('modalBodyText').textContent}`;try{await navigator.clipboard.writeText(text);$('copyConfirmToast').textContent='Subject and body copied';}catch{const range=document.createRange();range.selectNodeContents($('modalBodyText'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);$('copyConfirmToast').textContent='Automatic copy failed. Text selected — press Cmd+C or Ctrl+C.';}});

  // Payment registry. Treasurer confirmations are never auto-checked.
  function renderRegistry(){
    $('registryTotalLabel').textContent=formatAmount(readyItems.reduce((s,x)=>s+x.payable_amount,0));
    $('registryIntroText').textContent=`${readyItems.length} invoices passed order and receipt checks. Confirm they have not been paid before exporting.`;
    $('blockedCount').textContent=blockedItems.length;
    $('registryTableBody').innerHTML=readyItems.map(x=>`<tr><th scope="row">${escapeHtml(x.id)}<span class="table-sub">Invoice No. ${escapeHtml(x.raw_invoice_no)}</span></th><td><strong>${escapeHtml(cleanSupplier(x.supplier_name))}</strong><span class="table-sub">${escapeHtml(x.order?.material)}</span></td><td>${escapeHtml(x.order_id)}<span class="table-sub">${escapeHtml(x.approval?.approval_id||'Order terms')}</span></td><td>${number(x.order?.accepted_qty)} ${escapeHtml(x.order?.unit)}<span class="table-sub">${escapeHtml(x.order?.last_acceptance_date)}</span></td><td class="number-cell">${formatAmount(x.payable_amount)}</td><td><label class="check-label"><input type="checkbox" data-check-id="${escapeHtml(x.id)}" ${treasurerChecks[x.id]?'checked':''}><span>Not previously paid<span class="table-sub">${escapeHtml(x.id)} · verified against statement</span></span></label></td></tr>`).join('');
    $('registryTableBody').querySelectorAll('[data-check-id]').forEach(el=>el.addEventListener('change',()=>{treasurerChecks[el.dataset.checkId]=el.checked;updateTreasurerTotals();}));
    $('blockedTableBody').innerHTML=blockedItems.map(x=>`<tr><th scope="row">${escapeHtml(x.id)}<span class="table-sub">No. ${escapeHtml(x.raw_invoice_no)} · ${escapeHtml(x.order_id)}</span></th><td>${escapeHtml(cleanSupplier(x.supplier_name))}</td><td>${badge(x)}<span class="table-sub">${escapeHtml(x.primary_reason)}</span></td><td class="number-cell">${formatAmount(x.prevented_risk)}</td><td>${x.actions?.length?`<button class="btn btn-sm" data-draft-id="${escapeHtml(x.id)}">${icon('mail')}Draft</button>`:'Archive'}</td></tr>`).join('');
    $('blockedTableBody').querySelectorAll('[data-draft-id]').forEach(b=>b.addEventListener('click',()=>openActionModal(DATA.items.find(x=>x.id===b.dataset.draftId).actions[0])));updateTreasurerTotals();
  }
  function updateTreasurerTotals(){const checked=readyItems.filter(x=>treasurerChecks[x.id]);$('treasurerVerifiedTotal').textContent=`${formatAmount(checked.reduce((s,x)=>s+x.payable_amount,0))} · ${checked.length} of ${readyItems.length}`;$('btnExportRegistry').disabled=!checked.length||Boolean(xlsxReview?.pending);}

  // Single email check and demo presets.
  const aiDemo = {
    sender: 'PackLine Supply, invoice@packline.example',
    received_at: '16.11 14:25',
    text: 'Invoice 215 under order PO-13: berry pouch 500 g. Shipped 4000 peice. Each — 4 dollars. Amount due — 16,000 dollars.'
  };
  const presetTitles=['Corrected invoice','No order ID + box packaging','Hidden duplicate','Unauthorized bank switch','Roll arithmetic error'];
  $('juryPresetSelect').innerHTML += (DATA.jury_presets||[]).map((p,i)=>`<option value="${i}">${i+1}. ${escapeHtml(presetTitles[i]||p.title)}</option>`).join('');
  $('juryPresetSelect').add(new Option('AI: "adhesion" instead of "adhesive"', 'ai-material'));
  $('juryPresetSelect').add(new Option('AI: typo in unit of measure', 'ai-demo'));
  const juryInputs = ['juryPresetSelect', 'jurySenderInput', 'juryDateInput', 'juryTextInput'];
  const online = location.protocol !== 'file:';
  let aiProposal = null;
  let juryBusy = false;

  function showJuryPane(pane) {
    $('jurySplit').dataset.pane = pane;
    for (const [id, active] of [['btnJuryEditor', pane === 'editor'], ['btnJuryResult', pane === 'result']]) {
      $(id).classList.toggle('active', active);
      $(id).setAttribute('aria-pressed', String(active));
    }
  }
  $('btnJuryEditor').addEventListener('click', () => showJuryPane('editor'));
  $('btnJuryResult').addEventListener('click', () => showJuryPane('result'));

  function aiFieldsMarkup(fields) {
    return Object.values(fields).map(({label, value, source}) => {
      const suggestion = source === value ? escapeHtml(value) : `"${escapeHtml(source)}" → ${escapeHtml(value)}`;
      return `<div><dt>${escapeHtml(label)}</dt><dd><strong>${suggestion}</strong></dd></div>`;
    }).join('');
  }

  function renderAiProposal() {
    $('aiProposal').hidden = !aiProposal;
    $('btnAiConfirm').disabled = juryBusy || !aiProposal;
    if (aiProposal) $('aiFields').innerHTML = aiFieldsMarkup(aiProposal.fields);
  }

  function renderJuryResult() {
    $('juryResultContainer').innerHTML = buildCard(currentJuryResult, true);
    $('juryResultContainer').scrollTop = 0;
    bindDraft($('juryResultContainer'), currentJuryResult);
    renderAiProposal();
  }

  $('juryPresetSelect').addEventListener('change', e => {
    if (e.target.value === '') return;
    const first = DATA.jury_presets[0];
    const presets = {'ai-demo': aiDemo, 'ai-material': {...first, text: first.text.replace('adhesive tape', 'adhesion tape')}};
    const preset = presets[e.target.value] || DATA.jury_presets[Number(e.target.value)];
    $('jurySenderInput').value = preset.sender;
    $('juryDateInput').value = preset.received_at;
    $('juryTextInput').value = preset.text;
    aiProposal = null;
    currentJuryResult = null;
    renderJuryResult();
    $('juryEngineStatus').textContent = 'Sample loaded. Click "Run reconciliation".';
  });

  juryInputs.slice(1).forEach(id => $(id).addEventListener('input', () => {
    $('juryPresetSelect').value = '';
    aiProposal = null;
    currentJuryResult = null;
    renderJuryResult();
    $('juryEngineStatus').textContent = 'Text modified. Re-run reconciliation.';
  }));

  function juryValues() {
    return {
      sender: $('jurySenderInput').value.trim(),
      text: $('juryTextInput').value.trim(),
      received_at: $('juryDateInput').value.trim()
    };
  }

  function setJuryBusy(busy) {
    juryBusy = busy;
    juryInputs.forEach(id => { $(id).disabled = busy; });
    $('btnAnalyze').disabled = busy || Boolean(xlsxReview?.pending);
    $('btnAiConfirm').disabled = busy || !aiProposal || Boolean(xlsxReview?.pending);
    if (busy) $('juryResultContainer').setAttribute('aria-busy', 'true');
    else $('juryResultContainer').removeAttribute('aria-busy');
  }

  async function runJuryCheck(token = null) {
    if (juryBusy || xlsxReview?.pending || !$('juryCustomForm').reportValidity()) return;
    const {sender, text, received_at} = juryValues();
    if (!sender || !text || !received_at) {
      $('juryEngineStatus').textContent = 'Fill in sender, timestamp, and email text.';
      return;
    }
    const sourceFile = customXlsxBase64;
    const sourceReview = xlsxReview;
    const sourceData = DATA;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60_000);
    setJuryBusy(true);
    $('juryEngineStatus').textContent = 'Matching email against orders and checking rules…';
    try {
      if (!online) {
        const preset = (DATA.jury_presets || []).find(p => p.sender === sender && p.text === text && p.received_at === received_at);
        currentJuryResult = preset ? preset.result : analyzeCustomOnClient(sender, text, received_at);
        $('juryEngineStatus').textContent = preset ? 'Verified sample result' : 'Start the Python server to reconcile new emails.';
      } else {
        const body = {sender, text, received_at, use_ai: true};
        if (sourceReview) body.review_id = sourceReview.id;
        else if (sourceFile) body.xlsx_base64 = sourceFile;
        if (token) Object.assign(body, {ai_token: token, ai_confirmed: true});
        const response = await fetch('/api/analyze-custom', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(body), signal: controller.signal
        });
        const payload = await response.json();
        if (!response.ok || !payload.ok) throw new Error(payload.error || 'HTTP ' + response.status);
        if (sourceData !== DATA || sourceReview?.pending) {
          $('juryEngineStatus').textContent = 'Data source changed. Re-run reconciliation.';
          return;
        }
        currentJuryResult = payload.item;
        aiProposal = payload.proposal;
        const message = payload.ai_message || (aiProposal
          ? 'Confirm only the fields recovered by AI from the email.'
          : 'Reconciliation against case rules completed.');
        $('juryEngineStatus').textContent = sourceFile ? `${message} Source: ${currentSourceName}.` : message;
      }
      renderJuryResult();
      if (compactWorkspace.matches && currentJuryResult && !aiProposal) {
        showJuryPane('result');
        $('juryResultContainer').focus({preventScroll: true});
      }
    } catch (error) {
      $('juryEngineStatus').textContent = error.name === 'AbortError'
        ? 'Reconciliation timed out. Please retry.'
        : 'Reconciliation failed. ' + error.message;
    } finally {
      clearTimeout(timeout);
      setJuryBusy(false);
    }
  }

  $('juryCustomForm').addEventListener('submit', e => { e.preventDefault(); runJuryCheck(); });
  $('btnAiConfirm').addEventListener('click', () => {
    if (aiProposal?.token) runJuryCheck(aiProposal.token);
  });

  // Custom Excel (.xlsx) upload
  function renderXlsxReviewStatus() {
    const review = xlsxReview;
    $('xlsxReview').hidden = !review;
    $('btnRetryXlsxReview').hidden = !review?.error || Boolean(review?.pending);
    $('btnExportAudit').disabled = Boolean(review?.pending);
    $('btnAnalyze').disabled = juryBusy || Boolean(review?.pending);
    $('btnAiConfirm').disabled = juryBusy || !aiProposal || Boolean(review?.pending);
    if (!review) {
      $('xlsxReviewStatus').textContent = '';
      return;
    }
    const mapped = DATA.items.filter(item =>
      item.material_mapping?.method === 'ai' || item.unit_mapping?.method === 'ai'
    ).length;
    const pendingFields = Object.keys(review.proposals).length;
    $('xlsxReviewStatus').textContent = review.pending
      ? 'AI is reviewing disputed Excel rows…'
      : review.error
        ? `AI review completed partially. ${review.error}`
        : `AI review complete · mappings in ${mapped} rows · fields awaiting confirmation in ${pendingFields} rows`;
  }

  async function runXlsxReview(invoiceId = null) {
    const review = xlsxReview;
    if (!review || review.pending) return;
    review.controller = new AbortController();
    review.pending = true;
    review.error = null;
    renderXlsxReviewStatus();
    updateTreasurerTotals();
    const confirm = $('btnConfirmXlsxFields');
    if (confirm) confirm.disabled = true;
    try {
      const body = {review_id: review.id};
      if (invoiceId !== null) Object.assign(body, {invoice_id: invoiceId, ai_confirmed: true});
      const response = await fetch('/api/xlsx-review', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body),
        signal: review.controller.signal
      });
      const payload = await response.json();
      if (xlsxReview !== review) return;
      if (!response.ok || !payload.ok) throw new Error(payload.error || 'HTTP ' + response.status);
      review.proposals = payload.proposals;
      review.error = payload.ai_message;
      review.pending = false;
      if (currentJuryResult || aiProposal) {
        currentJuryResult = null;
        aiProposal = null;
        $('juryEngineStatus').textContent = 'Workbook reconciliation updated. Re-run the email check.';
      }
      applyDataset(payload.data, currentSourceName, true, customXlsxBase64, true, invoiceId);
      if (invoiceId !== null && selectedEmailId === invoiceId) {
        const title = $('inspectorPanel').querySelector('h2');
        title.tabIndex = -1;
        title.focus({preventScroll: true});
      }
    } catch (error) {
      if (xlsxReview !== review) return;
      review.error = error.message;
      if (invoiceId !== null) toast(error.message);
    } finally {
      if (xlsxReview === review) {
        review.pending = false;
        review.controller = null;
        renderXlsxReviewStatus();
        updateTreasurerTotals();
        if ($('btnConfirmXlsxFields')) $('btnConfirmXlsxFields').disabled = false;
      }
    }
  }

  $('btnRetryXlsxReview').addEventListener('click', () => runXlsxReview());

  function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    const chunkSize = 8192;
    for (let i = 0; i < bytes.length; i += chunkSize) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
    }
    return btoa(binary);
  }

  $('btnUploadXlsx').addEventListener('click', () => {
    if (location.protocol === 'file:') {
      toast('To upload a custom .xlsx, start the server: python3 app.py and open http://127.0.0.1:8040');
      return;
    }
    $('xlsxFileInput').click();
  });

  $('xlsxFileInput').addEventListener('change', async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    $('btnUploadXlsx').disabled = true;
    $('btnResetXlsx').disabled = true;
    $('uploadXlsxLabel').textContent = 'Uploading…';
    try {
      const buffer = await file.arrayBuffer();
      const b64 = arrayBufferToBase64(buffer);
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 20000);
      try {
        const response = await fetch('/api/upload-xlsx', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename: file.name, data_base64: b64, use_ai: true }),
          signal: controller.signal
        });
        const payload = await response.json();
        if (!response.ok || !payload.ok || !payload.data) {
          throw new Error(payload.error || 'HTTP ' + response.status);
        }
        xlsxReview?.controller?.abort();
        xlsxReview = {id: payload.review_id, pending: false, error: null, proposals: {}};
        applyDataset(payload.data, payload.filename || file.name, true, b64);
        toast(`Loaded ${payload.filename || file.name} (${payload.data.items.length} documents)`);
        runXlsxReview();
      } finally {
        clearTimeout(timeout);
      }
    } catch (error) {
      $('uploadXlsxLabel').textContent = customXlsxBase64 ? currentSourceName : 'Choose Excel (.xlsx)';
      toast('Excel upload error: ' + (error.message || 'check .xlsx format'));
    } finally {
      $('btnUploadXlsx').disabled = false;
      $('btnResetXlsx').disabled = false;
      $('xlsxFileInput').value = '';
    }
  });

  $('btnResetXlsx').addEventListener('click', () => {
    xlsxReview?.controller?.abort();
    xlsxReview = null;
    applyDataset(INITIAL_DATA, 'case04.xlsx', false, null);
    toast('Restored default workbook case04.xlsx');
  });

  // Reference data and rule explanations.
  function renderReference(){
    $('refRulesCount').textContent=DATA.rules.length;
    $('refOrdersCount').textContent=DATA.orders.length;
    $('refApprovalsCount').textContent=DATA.approvals.length;
    $('rulesCardsGrid').innerHTML=DATA.rules.map(r=>{const count=DATA.items.filter(x=>x.triggered_rules.includes(r.rule_id)).length;return `<article class="rule-card"><span class="rule-card-code">${escapeHtml(r.rule_id)}</span><h3>${escapeHtml(r.topic)}</h3><p>${escapeHtml(r.text)}</p><button data-rule="${escapeHtml(r.rule_id)}">Documents with this rule: ${count} →</button></article>`;}).join('');
    $('rulesCardsGrid').querySelectorAll('[data-rule]').forEach(b=>b.addEventListener('click',()=>{searchQuery='';$('queueSearchInput').value='';setStatusFilter('ALL');ruleFilter=b.dataset.rule;renderQueue();navigate('tab-queue');showQueueList();toast('Filtered by rule '+ruleFilter);}));
    $('ordersTableBody').innerHTML=DATA.orders.map(o=>`<tr><th scope="row">${escapeHtml(o.order_id)}<span class="table-sub">${escapeHtml(o.order_date)}</span></th><td>${escapeHtml(o.supplier)}<span class="table-sub">${escapeHtml(o.buyer)}</span></td><td>${escapeHtml(o.material)}</td><td>${number(o.ordered_qty)} ${escapeHtml(o.unit)}</td><td>${number(o.accepted_qty)} ${escapeHtml(o.unit)}<span class="table-sub">${escapeHtml(o.last_acceptance_date||'Not accepted')}</span></td><td>${formatAmount(o.order_price)}</td><td>${escapeHtml(o.approval_id||'—')}</td></tr>`).join('');
    $('approvalsTableBody').innerHTML=DATA.approvals.map(a=>`<tr><th scope="row">${escapeHtml(a.approval_id)}<span class="table-sub">${escapeHtml(a.date)}</span></th><td>${escapeHtml(a.order_id)}</td><td>${escapeHtml(a.change_summary)}</td><td><span class="status-badge badge-${a.status==='Signed'?'emerald':'amber'}">${escapeHtml(a.status)}</span></td><td>${escapeHtml(a.signed_by||'—')}</td></tr>`).join('');
  }
  function renderAnalytics(){
    const infoCount=DATA.items.filter(x=>x.status_code==='INFO_LETTER').length;
    $('analyticsSummaryText').textContent=`${readyItems.length} of ${DATA.items.length} documents are ready for the draft registry. ${blockedItems.length} require follow-up actions, and ${infoCount} are informational emails.`;
    const colors={emerald:'#8ba9df',amber:'#ac8bd3',orange:'#c99dcf',slate:'#a0a6c3',rose:'#cf8eb4',blue:'#82b7d7',purple:'#9a8ddd'};
    const groups=Object.keys(STATUS).map(code=>({code,...STATUS[code],count:DATA.items.filter(x=>x.status_code===code).length})).filter(g=>g.count);
    $('distributionBar').innerHTML=groups.map(g=>`<span style="width:${100*g.count/(DATA.items.length||1)}%;background:${colors[g.color]}" title="${escapeHtml(g.label)}: ${g.count}"></span>`).join('');
    $('analyticsBarsContainer').innerHTML=groups.map(g=>`<div class="bar-row"><span><i style="background:${colors[g.color]}"></i>${escapeHtml(g.label)}</span><strong>${g.count}<small>${Math.round(100*g.count/(DATA.items.length||1))}%</small></strong></div>`).join('');
    const categories={duplicate:'Duplicates & superseded versions',unaccepted_goods:'Without confirmed receipt',requisites:'Bank details switch',unapproved_change:'Unapproved price or quantity',math_error:'Arithmetic errors'};
    $('riskBreakdown').innerHTML=Object.entries(categories).map(([key,label])=>`<div class="risk-card"><span>${label}</span><strong>${formatAmount(DATA.summary.risk_breakdown_rub?.[key])}</strong></div>`).join('');
    updateRoi();
  }
  function updateRoi(){const n=Number($('roiInvoicesRange').value),minutes=Number($('roiMinutesRange').value),rate=Number($('roiRateRange').value);$('roiInvoicesVal').textContent=number(n);$('roiMinutesVal').textContent=number(minutes);$('roiRateVal').textContent=formatAmount(rate);const hours=n*Math.max(0,minutes-1.5)/60;$('roiSavedHours').textContent=number(Math.round(hours*10)/10)+' hrs / month';$('roiSavedPayroll').textContent=formatAmount(Math.round(hours*12*rate))+' / year';}
  ['roiInvoicesRange','roiMinutesRange','roiRateRange'].forEach(id=>$(id).addEventListener('input',updateRoi));

  // CSV is built from current selection, including only explicit treasurer checkmarks.
  function downloadCsvBlob(filename,rows){const safe=cell=>{let value=String(cell??'');if(/^[=+@\t\r]/.test(value)||(/^\-/.test(value)&&!/^\-\d+(?:[.,]\d+)?$/.test(value)))value="'"+value;return '"'+value.replace(/"/g,'""')+'"';};const csv='\uFEFF'+rows.map(row=>row.map(safe).join(';')).join('\r\n');const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);toast('CSV file prepared for download');}
  $('btnExportRegistry').addEventListener('click',()=>{const checked=readyItems.filter(x=>treasurerChecks[x.id]);if(!checked.length)return;downloadCsvBlob('payment_registry_north_berry.csv',[
    ['Email','Date','ERP Order','Supplier','Invoice No.','Material','Accepted','Payable Amount (USD)','Buyer','Treasurer Check (R-9)'],
    ...checked.map(x=>[x.id,x.received_at,x.order_id,x.supplier_name,x.raw_invoice_no,x.order?.material,`${x.order?.accepted_qty} ${x.order?.unit}`,x.payable_amount,x.order?.buyer,'Confirmed against bank statement by user'])
  ]);});
  $('btnExportAudit').addEventListener('click',()=>downloadCsvBlob('audit_emails_north_berry.csv',[
    ['Email ID','Received','Sender','Order','Invoice No.','Status','Stated Amount (USD)','Payable (USD)','Flagged Risk (USD)','Rules','Reason','Next Step'],
    ...DATA.items.map(x=>[x.id,x.received_at,x.sender,x.order_id,x.raw_invoice_no,x.status_label,x.stated_amount,x.payable_amount,x.prevented_risk,x.triggered_rules.join(', '),x.primary_reason,x.next_step])
  ]));
  function renderDailyChart(){
    const days = [...new Set(DATA.items.map(item=>item.received_at.split(' ')[0]))].sort();
    const groups = days.map(date=>({date,all:DATA.items.filter(x=>x.received_at.startsWith(date)).length,attention:DATA.items.filter(x=>x.received_at.startsWith(date)&&needsAttention(x)).length}));
    const max = Math.max(1,...groups.map(x=>x.all));
    $('dailyChart').innerHTML=groups.map(g=>`<div class="chart-column" title="${escapeHtml(g.date)}: emails — ${g.all}, needs attention — ${g.attention}"><span class="chart-bars"><i class="incoming-bar" style="height:${g.all/max*100}%"><span>${g.all}</span></i><i class="attention-bar" style="height:${g.attention/max*100}%;${g.attention?'':'visibility:hidden'}"></i></span><span class="chart-day">${escapeHtml(g.date)}</span></div>`).join('');
    $('dailyChart').setAttribute('aria-label',groups.map(g=>`${g.date}: emails — ${g.all}, needs attention — ${g.attention}`).join('; '));
    const peak=groups.reduce((a,b)=>b.all>a.all?b:a,groups[0]);
    $('peakDayLabel').textContent=peak?`Peak: ${peak.date} · ${peak.all} emails`:'';
  }
  function applyDataset(newData, sourceName = 'case04.xlsx', isCustom = false, xlsxBase64 = null, refresh = false, confirmedId = null){
    const previousReady = new Map(readyItems.map(item => [item.id, item]));
    DATA = {
      ...newData,
      jury_presets: newData.jury_presets || INITIAL_DATA.jury_presets || []
    };
    currentSourceName = sourceName;
    if (!refresh && (isCustom || customXlsxBase64 !== xlsxBase64)) {
      currentJuryResult = null;
      aiProposal = null;
      showJuryPane('editor');
      $('queueSplit').dataset.pane = 'list';
    }
    customXlsxBase64 = xlsxBase64;
    readyItems = DATA.items.filter(x=>x.status_code==='READY_TO_PAY');
    blockedItems = DATA.items.filter(needsAttention);
    treasurerChecks = Object.fromEntries(readyItems.map(item => [
      item.id,
      Boolean(refresh && treasurerChecks[item.id] && JSON.stringify(previousReady.get(item.id)) === JSON.stringify(item))
    ]));
    if (!refresh) selectedEmailId = [...DATA.items].sort((a,b)=>b.received_at.localeCompare(a.received_at))[0]?.id || null;
    pageMeta['tab-queue'][1] = isCustom ? `Uploaded file: ${sourceName}` : 'Snapshot as of Nov 16, 2026, 12:00 UTC';
    if (currentTab === 'tab-queue') $('pageDescription').textContent = pageMeta['tab-queue'][1];
    $('uploadXlsxLabel').textContent = isCustom ? sourceName : 'Choose Excel (.xlsx)';
    $('navSourceName').textContent = sourceName;
    $('navSourceName').title = sourceName;
    $('btnResetXlsx').hidden = !isCustom;
    $('sourceNoteText').innerHTML = `${icon('file')}Source: ${escapeHtml(sourceName)} · ${isCustom ? 'custom Excel workbook' : 'sample export, no live ERP connection'}`;

    $('kpiTotalEmails').innerHTML=number(DATA.items.length)+' <small>emails</small>';
    $('kpiPayableRub').innerHTML=formatAmount(readyItems.reduce((s,x)=>s+x.payable_amount,0));
    $('kpiPreventedRub').innerHTML=formatAmount(blockedItems.reduce((s,x)=>s+x.prevented_risk,0));
    $('ordersCount').textContent=DATA.orders.length;$('approvalsCount').textContent=DATA.approvals.length+' approvals';
    $('readyCount').textContent=readyItems.length;$('attentionCount').textContent=blockedItems.length;
    const infoCount=DATA.items.filter(x=>x.status_code==='INFO_LETTER').length;
    $('filterAllCount').textContent=DATA.items.length;$('filterAttentionCount').textContent=blockedItems.length;$('filterReadyCount').textContent=readyItems.length;$('filterInfoCount').textContent=infoCount;

    renderDailyChart();
    if (!refresh) setStatusFilter(!isCustom && blockedItems.length ? 'ATTENTION' : 'ALL');
    else if (confirmedId && confirmedId === selectedEmailId && !filteredItems().some(item => item.id === confirmedId)) setStatusFilter('ALL');
    else renderQueue();
    renderXlsxReviewStatus();
    renderRegistry();
    renderJuryResult();
    renderReference();
    renderAnalytics();
  }
  function initialize(){
    applyDataset(INITIAL_DATA, 'case04.xlsx', false, null);
    navigate('tab-'+(location.hash.slice(1)||'queue'),false);
  }

  // Offline file mode has no Python engine. Only exact presets have precomputed results.
  function analyzeCustomOnClient(sender, text, receivedAt) {
    return {
      id:'LOCAL', sender, text, received_at:receivedAt, supplier_name:sender,
      raw_invoice_no:'—', order_id:'—', order:null, approval:null,
      stated_amount:0, payable_amount:0, prevented_risk:0, match_confidence:0,
      status_code:'NEEDS_REVIEW', status_label:'Server reconciliation required',
      status_color:'slate', triggered_rules:[], actions:[], rule_checks:[],
      primary_reason:'Reconciling a custom email requires the Python server engine. Offline mode supports only built-in presets.',
      next_step:'Run python3 app.py in the project directory and open http://127.0.0.1:8040/#jury.'
    };
  }

  initialize();
})();
