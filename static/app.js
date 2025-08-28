const api = {
  base: '',
  get headers() { return { 'Content-Type': 'application/json' }; },
  async post(path, body) {
    const res = await fetch(`${this.base}${path}`, { method: 'POST', headers: this.headers, body: JSON.stringify(body), credentials: 'include' });
    return this._handle(res);
  },
  async get(path) {
    const res = await fetch(`${this.base}${path}`, { credentials: 'include' });
    return this._handle(res);
  },
  async _handle(res) {
    let data = null; try { data = await res.json(); } catch (_) {}
    if (!res.ok) throw new Error((data && data.error) || `HTTP ${res.status}`);
    return data;
  }
};

// UI helpers
function toast(msg){ const t=document.getElementById('toast'); t.textContent=msg; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),2000); }
function setProfile(user){ const box=document.getElementById('profileBox'); if(!user){ box.textContent='Not logged in'; return; } box.textContent=`${user.full_name||user.email}`; }
function $(sel){ return document.querySelector(sel); }
function el(tag, cls, text){ const e=document.createElement(tag); if(cls) e.className=cls; if(text) e.textContent=text; return e; }

// Tabs
document.querySelectorAll('.tab-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
  });
});

// Auth
async function loadProfile(){
  try{ const p=await api.get('/auth/profile'); setProfile(p); await Promise.all([refreshContacts(), refreshCampaigns()]); }catch{ setProfile(null); }
}

$('#loginForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); const f=new FormData(e.target);
  try{ await api.post('/auth/login', { email:f.get('email'), password:f.get('password') }); toast('Logged in'); await loadProfile(); }
  catch(err){ toast(err.message); }
});

$('#registerForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); const f=new FormData(e.target);
  try{ await api.post('/api/auth/register', { first_name:f.get('first_name'), last_name:f.get('last_name'), company_name:f.get('company_name'), email:f.get('email'), password:f.get('password') }); toast('Registered and logged in'); await loadProfile(); }
  catch(err){ toast(err.message); }
});

// Contacts (Registration)
async function refreshContacts(){
  try{
    const contacts = await api.get('/contacts');
    const tbody = document.querySelector('#contactsTable tbody');
    tbody.innerHTML = '';
    contacts.forEach(c=>{
      const tr=document.createElement('tr');
      tr.innerHTML = `<td>${(c.first_name||'')+' '+(c.last_name||'')}</td><td>${c.phone_number||''}</td><td>${c.email||''}</td><td>${c.company||''}</td><td>${c.status||''}</td>`;
      tbody.appendChild(tr);
    });
    // also update demo selects
    const sel = document.getElementById('demoContactSelect'); sel.innerHTML='';
    contacts.forEach(c=>{ const o=el('option'); o.value=c.id; o.textContent=`${c.first_name||'Contact'} (${c.phone_number})`; sel.appendChild(o); });
  }catch(err){ /* ignore when not logged in */ }
}

document.getElementById('contactForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); const f=new FormData(e.target);
  try{
    await api.post('/contacts', {
      first_name:f.get('first_name')||undefined,
      last_name:f.get('last_name')||undefined,
      email:f.get('email')||undefined,
      company:f.get('company')||undefined,
      phone_number:f.get('phone_number'),
    });
    toast('Contact added'); e.target.reset(); await refreshContacts();
  }catch(err){ toast(err.message); }
});

// Campaigns
async function refreshCampaigns(){
  try{
    const campaigns = await api.get('/campaigns');
    const tbody = document.querySelector('#campaignsTable tbody');
    tbody.innerHTML='';
    campaigns.forEach(c=>{
      const tr=document.createElement('tr');
      const created = c.created_at || '';
      tr.innerHTML = `<td>${c.name||''}</td><td>${c.description||''}</td><td>${created}</td>`;
      tbody.appendChild(tr);
    });
    const sel = document.getElementById('demoCampaignSelect'); sel.innerHTML='';
    campaigns.forEach(c=>{ const o=el('option'); o.value=c.id; o.textContent=c.name; sel.appendChild(o); });
  }catch(err){ /* ignore */ }
}

document.getElementById('campaignForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); const f=new FormData(e.target);
  try{
    await api.post('/campaigns', { name:f.get('name'), type:f.get('type') });
    toast('Campaign created'); e.target.reset(); await refreshCampaigns();
  }catch(err){ toast(err.message); }
});

// Demo Chat / Calls
const chatWindow = document.getElementById('chatWindow');
function appendMsg(role, text){
  const row=el('div','msg '+role);
  const b=el('div','bubble '+role); b.textContent=text; row.appendChild(b);
  chatWindow.appendChild(row); chatWindow.scrollTop = chatWindow.scrollHeight;
}

document.getElementById('startCallBtn').addEventListener('click', async ()=>{
  const contact_id = document.getElementById('demoContactSelect').value;
  const campaign_id = document.getElementById('demoCampaignSelect').value;
  const phone_number = document.getElementById('demoPhone').value;
  try{
    const res = await api.post('/calls/start', { contact_id, campaign_id, phone_number });
    toast(res.message || 'Call started');
    chatWindow.innerHTML='';
    appendMsg('agent', 'Call started. You can chat below.');
  }catch(err){ toast(err.message); }
});

document.getElementById('endCallBtn').addEventListener('click', async ()=>{
  try{ await api.post('/calls/end', { status: 'completed' }); toast('Call ended'); appendMsg('agent','Call ended.'); }
  catch(err){ toast(err.message); }
});

document.getElementById('sendMsgBtn').addEventListener('click', sendMsg);
document.getElementById('chatInput').addEventListener('keydown', (e)=>{ if(e.key==='Enter') sendMsg(); });
async function sendMsg(){
  const input = document.getElementById('chatInput'); const text=input.value.trim(); if(!text) return;
  appendMsg('user', text); input.value='';
  try{
    const res = await api.post('/calls/process', { text });
    appendMsg('agent', res.response || '');
  }catch(err){ toast(err.message); }
}

// CRM
document.getElementById('refreshConversationsBtn').addEventListener('click', async ()=>{
  try{
    const calls = await api.get('/calls/status');
    // Also show a simple card list of conversations via sample latest status
    const list = document.getElementById('crmList');
    list.innerHTML='';
    if (calls && calls.status && calls.status === 'no_active_call') {
      list.appendChild(el('div','card','No active call. Use Demo Chat to start one.'));
    } else if (calls && calls.transcript_length !== undefined) {
      const card = el('div','card');
      card.appendChild(el('div',null,`Campaign: ${calls.campaign}`));
      card.appendChild(el('div',null,`Stage: ${calls.stage}`));
      card.appendChild(el('div',null,`Duration: ${calls.duration||0}s`));
      list.appendChild(card);
    }
  }catch(err){ toast(err.message); }
});

// Initial load
loadProfile();

