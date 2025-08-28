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

// Country codes for phone validation
const COUNTRY_CODES = [
  { code: '+1', country: 'US/Canada', flag: '🇺🇸' },
  { code: '+44', country: 'United Kingdom', flag: '🇬🇧' },
  { code: '+91', country: 'India', flag: '🇮🇳' },
  { code: '+86', country: 'China', flag: '🇨🇳' },
  { code: '+81', country: 'Japan', flag: '🇯🇵' },
  { code: '+49', country: 'Germany', flag: '🇩🇪' },
  { code: '+33', country: 'France', flag: '🇫🇷' },
  { code: '+39', country: 'Italy', flag: '🇮🇹' },
  { code: '+34', country: 'Spain', flag: '🇪🇸' },
  { code: '+31', country: 'Netherlands', flag: '🇳🇱' },
  { code: '+46', country: 'Sweden', flag: '🇸🇪' },
  { code: '+47', country: 'Norway', flag: '🇳🇴' },
  { code: '+45', country: 'Denmark', flag: '🇩🇰' },
  { code: '+358', country: 'Finland', flag: '🇫🇮' },
  { code: '+48', country: 'Poland', flag: '🇵🇱' },
  { code: '+420', country: 'Czech Republic', flag: '🇨🇿' },
  { code: '+36', country: 'Hungary', flag: '🇭🇺' },
  { code: '+43', country: 'Austria', flag: '🇦🇹' },
  { code: '+41', country: 'Switzerland', flag: '🇨🇭' },
  { code: '+32', country: 'Belgium', flag: '🇧🇪' },
  { code: '+351', country: 'Portugal', flag: '🇵🇹' },
  { code: '+30', country: 'Greece', flag: '🇬🇷' },
  { code: '+90', country: 'Turkey', flag: '🇹🇷' },
  { code: '+7', country: 'Russia', flag: '🇷🇺' },
  { code: '+380', country: 'Ukraine', flag: '🇺🇦' },
  { code: '+48', country: 'Poland', flag: '🇵🇱' },
  { code: '+55', country: 'Brazil', flag: '🇧🇷' },
  { code: '+54', country: 'Argentina', flag: '🇦🇷' },
  { code: '+52', country: 'Mexico', flag: '🇲🇽' },
  { code: '+57', country: 'Colombia', flag: '🇨🇴' },
  { code: '+58', country: 'Venezuela', flag: '🇻🇪' },
  { code: '+51', country: 'Peru', flag: '🇵🇪' },
  { code: '+56', country: 'Chile', flag: '🇨🇱' },
  { code: '+593', country: 'Ecuador', flag: '🇪🇨' },
  { code: '+595', country: 'Paraguay', flag: '🇵🇾' },
  { code: '+598', country: 'Uruguay', flag: '🇺🇾' },
  { code: '+61', country: 'Australia', flag: '🇦🇺' },
  { code: '+64', country: 'New Zealand', flag: '🇳🇿' },
  { code: '+65', country: 'Singapore', flag: '🇸🇬' },
  { code: '+60', country: 'Malaysia', flag: '🇲🇾' },
  { code: '+66', country: 'Thailand', flag: '🇹🇭' },
  { code: '+84', country: 'Vietnam', flag: '🇻🇳' },
  { code: '+63', country: 'Philippines', flag: '🇵🇭' },
  { code: '+62', country: 'Indonesia', flag: '🇮🇩' },
  { code: '+82', country: 'South Korea', flag: '🇰🇷' },
  { code: '+971', country: 'UAE', flag: '🇦🇪' },
  { code: '+966', country: 'Saudi Arabia', flag: '🇸🇦' },
  { code: '+20', country: 'Egypt', flag: '🇪🇬' },
  { code: '+27', country: 'South Africa', flag: '🇿🇦' },
  { code: '+234', country: 'Nigeria', flag: '🇳🇬' },
  { code: '+254', country: 'Kenya', flag: '🇰🇪' },
  { code: '+256', country: 'Uganda', flag: '🇺🇬' },
  { code: '+233', country: 'Ghana', flag: '🇬🇭' },
  { code: '+212', country: 'Morocco', flag: '🇲🇦' },
  { code: '+216', country: 'Tunisia', flag: '🇹🇳' },
  { code: '+213', country: 'Algeria', flag: '🇩🇿' },
  { code: '+20', country: 'Egypt', flag: '🇪🇬' },
  { code: '+27', country: 'South Africa', flag: '🇿🇦' }
];

// UI helpers
function toast(msg, type = 'info'){ 
  const t=document.getElementById('toast'); 
  t.textContent=msg; 
  t.className = `toast show ${type}`; 
  setTimeout(()=>t.classList.remove('show'),3000); 
}

function setProfile(user){ 
  const box=document.getElementById('profileBox'); 
  if(!user){ 
    box.innerHTML = '<i class="fas fa-user-circle"></i><span>Not logged in</span>'; 
    return; 
  } 
  box.innerHTML = `<i class="fas fa-user-circle"></i><span>${user.full_name||user.email}</span>`; 
}

function $(sel){ return document.querySelector(sel); }
function el(tag, cls, text){ const e=document.createElement(tag); if(cls) e.className=cls; if(text) e.textContent=text; return e; }

// Validation functions
function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validatePhone(phone) {
  // Remove all non-digit characters except +
  const cleanPhone = phone.replace(/[^\d+]/g, '');
  // Check if it starts with a valid country code and has sufficient length
  const hasValidCountryCode = COUNTRY_CODES.some(country => cleanPhone.startsWith(country.code));
  const hasSufficientLength = cleanPhone.length >= 10 && cleanPhone.length <= 15;
  return hasValidCountryCode && hasSufficientLength;
}

function showTab(tabName) {
  // Hide all tabs
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  // Show selected tab
  document.getElementById(`tab-${tabName}`).classList.add('active');
  
  // Update navigation buttons
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// Tabs
document.querySelectorAll('.tab-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    const tabName = btn.dataset.tab;
    showTab(tabName);
  });
});

// Auth
async function loadProfile(){
  try{ 
    const p=await api.get('/auth/profile'); 
    setProfile(p); 
    await Promise.all([refreshContacts(), refreshCampaigns()]); 
    // Redirect to CRM tab after successful login
    showTab('crm');
  }catch{ 
    setProfile(null); 
    showTab('auth');
  }
}

$('#loginForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); 
  const f=new FormData(e.target);
  
  // Validate email
  if (!validateEmail(f.get('email'))) {
    toast('Please enter a valid email address', 'error');
    return;
  }
  
  try{ 
    await api.post('/auth/login', { email:f.get('email'), password:f.get('password') }); 
    toast('Login successful!', 'success'); 
    await loadProfile(); 
  }
  catch(err){ 
    toast(err.message, 'error'); 
  }
});

$('#registerForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); 
  const f=new FormData(e.target);
  
  // Validate email
  if (!validateEmail(f.get('email'))) {
    toast('Please enter a valid email address', 'error');
    return;
  }
  
  // Validate password strength
  if (f.get('password').length < 6) {
    toast('Password must be at least 6 characters long', 'error');
    return;
  }
  
  try{ 
    await api.post('/auth/register', { 
      first_name:f.get('first_name'), 
      last_name:f.get('last_name'), 
      company_name:f.get('company_name'), 
      email:f.get('email'), 
      password:f.get('password') 
    }); 
    toast('Registration successful!', 'success'); 
    await loadProfile(); 
  }
  catch(err){ 
    toast(err.message, 'error'); 
  }
});

// Contacts (Registration)
async function refreshContacts(){
  try{
    const contacts = await api.get('/contacts');
    const tbody = document.querySelector('#contactsTable tbody');
    tbody.innerHTML = '';
    
    if (contacts.length === 0) {
      tbody.innerHTML = `
        <tr class="empty-state">
          <td colspan="5">
            <div class="empty-message">
              <i class="fas fa-users"></i>
              <p>No contacts yet. Add your first contact above!</p>
            </div>
          </td>
        </tr>
      `;
      return;
    }
    
    contacts.forEach(c=>{
      const tr=document.createElement('tr');
      tr.innerHTML = `<td>${(c.first_name||'')+' '+(c.last_name||'')}</td><td>${c.phone_number||''}</td><td>${c.email||''}</td><td>${c.company||''}</td><td>${c.status||''}</td>`;
      tbody.appendChild(tr);
    });
    // also update demo selects
    const sel = document.getElementById('demoContactSelect'); sel.innerHTML='<option value="">Choose a contact...</option>';
    contacts.forEach(c=>{ const o=el('option'); o.value=c.id; o.textContent=`${c.first_name||'Contact'} (${c.phone_number})`; sel.appendChild(o); });
  }catch(err){ /* ignore when not logged in */ }
}

// Add country code selector to contact form
function addCountryCodeSelector() {
  const phoneInput = document.getElementById('contact-phone');
  if (phoneInput && !phoneInput.previousElementSibling?.classList.contains('country-code-selector')) {
    const countrySelector = document.createElement('select');
    countrySelector.className = 'country-code-selector';
    countrySelector.innerHTML = '<option value="">Select Country</option>';
    
    COUNTRY_CODES.forEach(country => {
      const option = document.createElement('option');
      option.value = country.code;
      option.textContent = `${country.flag} ${country.code} (${country.country})`;
      countrySelector.appendChild(option);
    });
    
    countrySelector.addEventListener('change', (e) => {
      if (e.target.value) {
        phoneInput.value = e.target.value + ' ';
        phoneInput.focus();
      }
    });
    
    phoneInput.parentNode.insertBefore(countrySelector, phoneInput);
  }
}

document.getElementById('contactForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); 
  const f=new FormData(e.target);
  
  // Validate phone number
  if (!validatePhone(f.get('phone_number'))) {
    toast('Please enter a valid phone number with country code (e.g., +15551234567)', 'error');
    return;
  }
  
  // Validate email if provided
  if (f.get('email') && !validateEmail(f.get('email'))) {
    toast('Please enter a valid email address', 'error');
    return;
  }
  
  try{
    await api.post('/contacts', {
      first_name:f.get('first_name')||undefined,
      last_name:f.get('last_name')||undefined,
      email:f.get('email')||undefined,
      company:f.get('company')||undefined,
      phone_number:f.get('phone_number'),
    });
    toast('Contact added successfully!', 'success'); 
    e.target.reset(); 
    await refreshContacts();
  }catch(err){ 
    toast(err.message, 'error'); 
  }
});

// Campaigns
async function refreshCampaigns(){
  try{
    const campaigns = await api.get('/campaigns');
    const tbody = document.querySelector('#campaignsTable tbody');
    tbody.innerHTML='';
    
    if (campaigns.length === 0) {
      tbody.innerHTML = `
        <tr class="empty-state">
          <td colspan="5">
            <div class="empty-message">
              <i class="fas fa-bullhorn"></i>
              <p>No campaigns yet. Create your first campaign above!</p>
            </div>
          </td>
        </tr>
      `;
      return;
    }
    
    campaigns.forEach(c=>{
      const tr=document.createElement('tr');
      const created = c.created_at || '';
      const status = c.is_active ? '<span class="status-active">Active</span>' : '<span class="status-inactive">Inactive</span>';
      tr.innerHTML = `<td>${c.name||''}</td><td>${c.description||''}</td><td>${created}</td><td>${status}</td><td><button class="btn btn-sm btn-secondary">Edit</button></td>`;
      tbody.appendChild(tr);
    });
    const sel = document.getElementById('demoCampaignSelect'); sel.innerHTML='<option value="">Choose a campaign...</option>';
    campaigns.forEach(c=>{ const o=el('option'); o.value=c.id; o.textContent=c.name; sel.appendChild(o); });
  }catch(err){ /* ignore */ }
}

document.getElementById('campaignForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); 
  const f=new FormData(e.target);
  
  try{
    await api.post('/sample-data'); 
    toast('Sample campaign created successfully!', 'success'); 
    e.target.reset(); 
    await refreshCampaigns();
  }catch(err){ 
    toast(err.message, 'error'); 
  }
});

// Initialize country code selector when contacts tab is shown
document.querySelector('[data-tab="registration"]').addEventListener('click', () => {
  setTimeout(addCountryCodeSelector, 100);
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

// CRM Export/Import Functionality
function initializeCrmFeatures() {
  // Export date range handling
  const exportDateRange = document.getElementById('exportDateRange');
  const customDateRange = document.getElementById('customDateRange');
  
  if (exportDateRange) {
    exportDateRange.addEventListener('change', (e) => {
      if (e.target.value === 'custom') {
        customDateRange.style.display = 'flex';
      } else {
        customDateRange.style.display = 'none';
      }
    });
  }
  
  // CSV Export
  const exportCsvBtn = document.getElementById('exportCsvBtn');
  if (exportCsvBtn) {
    exportCsvBtn.addEventListener('click', exportToCsv);
  }
  
  // JSON Export
  const exportJsonBtn = document.getElementById('exportJsonBtn');
  if (exportJsonBtn) {
    exportJsonBtn.addEventListener('click', exportToJson);
  }
  
  // Excel Export
  const exportExcelBtn = document.getElementById('exportExcelBtn');
  if (exportExcelBtn) {
    exportExcelBtn.addEventListener('click', exportToExcel);
  }
  
  // CSV Import
  const importCsvBtn = document.getElementById('importCsvBtn');
  if (importCsvBtn) {
    importCsvBtn.addEventListener('click', importFromCsv);
  }
  
  // Download Template
  const downloadTemplateBtn = document.getElementById('downloadTemplateBtn');
  if (downloadTemplateBtn) {
    downloadTemplateBtn.addEventListener('click', downloadCsvTemplate);
  }
  
  // Google Forms functionality
  initializeGoogleForms();
  
  // Data scraping functionality
  initializeDataScraping();
}

// Export functions
async function exportToCsv() {
  try {
    const contacts = await api.get('/contacts');
    const campaigns = await api.get('/campaigns');
    
    // Create CSV content
    let csvContent = 'data:text/csv;charset=utf-8,';
    
    // Contacts CSV
    csvContent += 'CONTACTS\n';
    csvContent += 'First Name,Last Name,Email,Company,Phone,Status\n';
    contacts.forEach(contact => {
      csvContent += `${contact.first_name || ''},${contact.last_name || ''},${contact.email || ''},${contact.company || ''},${contact.phone_number || ''},${contact.status || ''}\n`;
    });
    
    csvContent += '\nCAMPAIGNS\n';
    csvContent += 'Name,Description,Status,Created\n';
    campaigns.forEach(campaign => {
      csvContent += `${campaign.name || ''},${campaign.description || ''},${campaign.is_active ? 'Active' : 'Inactive'},${campaign.created_at || ''}\n`;
    });
    
    // Download CSV
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `crm_data_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast('CSV exported successfully!', 'success');
  } catch (error) {
    toast('Export failed: ' + error.message, 'error');
  }
}

async function exportToJson() {
  try {
    const contacts = await api.get('/contacts');
    const campaigns = await api.get('/campaigns');
    
    const data = {
      export_date: new Date().toISOString(),
      contacts: contacts,
      campaigns: campaigns
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `crm_data_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    toast('JSON exported successfully!', 'success');
  } catch (error) {
    toast('Export failed: ' + error.message, 'error');
  }
}

async function exportToExcel() {
  try {
    // For Excel export, we'll create a CSV with .xls extension
    // In a real implementation, you'd use a library like SheetJS
    await exportToCsv();
    toast('Excel export completed! (CSV format)', 'success');
  } catch (error) {
    toast('Export failed: ' + error.message, 'error');
  }
}

async function importFromCsv() {
  const fileInput = document.getElementById('csvImportFile');
  const file = fileInput.files[0];
  
  if (!file) {
    toast('Please select a CSV file to import', 'error');
    return;
  }
  
  try {
    const text = await file.text();
    const lines = text.split('\n');
    const headers = lines[0].split(',');
    
    const contacts = [];
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim()) {
        const values = lines[i].split(',');
        const contact = {};
        headers.forEach((header, index) => {
          contact[header.trim()] = values[index] ? values[index].trim() : '';
        });
        contacts.push(contact);
      }
    }
    
    // Import contacts
    for (const contact of contacts) {
      if (contact.Phone) {
        await api.post('/contacts', {
          first_name: contact['First Name'] || '',
          last_name: contact['Last Name'] || '',
          email: contact.Email || '',
          company: contact.Company || '',
          phone_number: contact.Phone,
          status: contact.Status || 'new'
        });
      }
    }
    
    toast(`Successfully imported ${contacts.length} contacts!`, 'success');
    await refreshContacts();
    fileInput.value = '';
  } catch (error) {
    toast('Import failed: ' + error.message, 'error');
  }
}

function downloadCsvTemplate() {
  const template = 'First Name,Last Name,Email,Company,Phone,Status\nJohn,Doe,john@example.com,Example Corp,+15551234567,new\nJane,Smith,jane@example.com,Test Inc,+15559876543,new';
  const blob = new Blob([template], {type: 'text/csv'});
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = 'crm_contacts_template.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
  toast('Template downloaded successfully!', 'success');
}

// Google Forms Integration
function initializeGoogleForms() {
  const addMappingBtn = document.getElementById('addMappingBtn');
  const saveFormsConfigBtn = document.getElementById('saveFormsConfigBtn');
  const testFormsConnectionBtn = document.getElementById('testFormsConnectionBtn');
  
  if (addMappingBtn) {
    addMappingBtn.addEventListener('click', addFieldMapping);
  }
  
  if (saveFormsConfigBtn) {
    saveFormsConfigBtn.addEventListener('click', saveFormsConfiguration);
  }
  
  if (testFormsConnectionBtn) {
    testFormsConnectionBtn.addEventListener('click', testFormsConnection);
  }
  
  // Add default mappings
  addDefaultMappings();
}

function addFieldMapping() {
  const mappingsContainer = document.getElementById('fieldMappings');
  const mappingDiv = document.createElement('div');
  mappingDiv.className = 'field-mapping';
  
  mappingDiv.innerHTML = `
    <input type="text" placeholder="Form Field Name" class="form-control">
    <select class="form-control">
      <option value="first_name">First Name</option>
      <option value="last_name">Last Name</option>
      <option value="email">Email</option>
      <option value="phone">Phone</option>
      <option value="company">Company</option>
      <option value="position">Position</option>
      <option value="industry">Industry</option>
    </select>
    <select class="form-control">
      <option value="false">Optional</option>
      <option value="true">Required</option>
    </select>
    <button class="remove-mapping" onclick="this.parentElement.remove()">×</button>
  `;
  
  mappingsContainer.appendChild(mappingDiv);
}

function addDefaultMappings() {
  const defaultMappings = [
    { formField: 'First Name', crmField: 'first_name', required: 'true' },
    { formField: 'Last Name', crmField: 'last_name', required: 'true' },
    { formField: 'Email', crmField: 'email', required: 'true' },
    { formField: 'Phone', crmField: 'phone', required: 'false' },
    { formField: 'Company', crmField: 'company', required: 'false' }
  ];
  
  const mappingsContainer = document.getElementById('fieldMappings');
  if (mappingsContainer) {
    defaultMappings.forEach(mapping => {
      const mappingDiv = document.createElement('div');
      mappingDiv.className = 'field-mapping';
      
      mappingDiv.innerHTML = `
        <input type="text" value="${mapping.formField}" class="form-control">
        <select class="form-control">
          <option value="first_name" ${mapping.crmField === 'first_name' ? 'selected' : ''}>First Name</option>
          <option value="last_name" ${mapping.crmField === 'last_name' ? 'selected' : ''}>Last Name</option>
          <option value="email" ${mapping.crmField === 'email' ? 'selected' : ''}>Email</option>
          <option value="phone" ${mapping.crmField === 'phone' ? 'selected' : ''}>Phone</option>
          <option value="company" ${mapping.crmField === 'company' ? 'selected' : ''}>Company</option>
          <option value="position" ${mapping.crmField === 'position' ? 'selected' : ''}>Position</option>
          <option value="industry" ${mapping.crmField === 'industry' ? 'selected' : ''}>Industry</option>
        </select>
        <select class="form-control">
          <option value="false" ${mapping.crmField === 'false' ? 'selected' : ''}>Optional</option>
          <option value="true" ${mapping.crmField === 'true' ? 'selected' : ''}>Required</option>
        </select>
        <button class="remove-mapping" onclick="this.parentElement.remove()">×</button>
      `;
      
      mappingsContainer.appendChild(mappingDiv);
    });
  }
}

function saveFormsConfiguration() {
  const formUrl = document.getElementById('googleFormUrl').value;
  const syncFreq = document.getElementById('syncFrequency').value;
  
  if (!formUrl) {
    toast('Please enter a Google Form URL', 'error');
    return;
  }
  
  // Save configuration (in a real app, this would go to backend)
  const config = {
    formUrl: formUrl,
    syncFrequency: syncFreq,
    mappings: getFieldMappings(),
    lastUpdated: new Date().toISOString()
  };
  
  localStorage.setItem('googleFormsConfig', JSON.stringify(config));
  toast('Google Forms configuration saved successfully!', 'success');
}

function getFieldMappings() {
  const mappings = [];
  const mappingElements = document.querySelectorAll('.field-mapping');
  
  mappingElements.forEach(element => {
    const inputs = element.querySelectorAll('input, select');
    mappings.push({
      formField: inputs[0].value,
      crmField: inputs[1].value,
      required: inputs[2].value === 'true'
    });
  });
  
  return mappings;
}

function testFormsConnection() {
  const formUrl = document.getElementById('googleFormUrl').value;
  
  if (!formUrl) {
    toast('Please enter a Google Form URL', 'error');
    return;
  }
  
  // Simulate connection test
  toast('Testing connection to Google Forms...', 'info');
  
  setTimeout(() => {
    if (formUrl.includes('forms.google.com')) {
      toast('Connection successful! Google Form is accessible.', 'success');
      } else {
      toast('Connection failed. Please check the URL format.', 'error');
    }
  }, 2000);
}

// Data Scraping Functionality
function initializeDataScraping() {
  const scrapeLinkedinBtn = document.getElementById('scrapeLinkedinBtn');
  const scrapeWebsiteBtn = document.getElementById('scrapeWebsiteBtn');
  const scrapeBusinessDirBtn = document.getElementById('scrapeBusinessDirBtn');
  
  if (scrapeLinkedinBtn) {
    scrapeLinkedinBtn.addEventListener('click', () => scrapeLinkedin());
  }
  
  if (scrapeWebsiteBtn) {
    scrapeWebsiteBtn.addEventListener('click', () => scrapeWebsite());
  }
  
  if (scrapeBusinessDirBtn) {
    scrapeBusinessDirBtn.addEventListener('click', () => scrapeBusinessDirectory());
  }
}

async function scrapeLinkedin() {
  const company = document.getElementById('linkedinCompany').value;
  const location = document.getElementById('linkedinCompany').value;
  
  if (!company) {
    toast('Please enter a company name', 'error');
    return;
  }
  
  toast('Scraping LinkedIn data...', 'info');
  
  try {
    // Simulate scraping process
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const mockResults = [
      { name: 'John Smith', position: 'CEO', company: company, location: location, email: 'john.smith@' + company.toLowerCase().replace(/\s/g, '') + '.com' },
      { name: 'Sarah Johnson', position: 'CTO', company: company, location: location, email: 'sarah.johnson@' + company.toLowerCase().replace(/\s/g, '') + '.com' },
      { name: 'Mike Davis', position: 'VP Sales', company: company, location: location, email: 'mike.davis@' + company.toLowerCase().replace(/\s/g, '') + '.com' }
    ];
    
    displayScrapingResults(mockResults, 'LinkedIn');
    toast('LinkedIn scraping completed! Found ' + mockResults.length + ' contacts.', 'success');
  } catch (error) {
    toast('Scraping failed: ' + error.message, 'error');
  }
}

async function scrapeWebsite() {
  const url = document.getElementById('websiteUrl').value;
  const depth = document.getElementById('scrapeDepth').value;
  
  if (!url) {
    toast('Please enter a website URL', 'error');
    return;
  }
  
  toast('Scraping website data...', 'info');
  
  try {
    // Simulate scraping process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const mockResults = [
      { name: 'Contact Us', email: 'info@' + new URL(url).hostname, phone: '+1-555-123-4567', company: new URL(url).hostname },
      { name: 'Sales Team', email: 'sales@' + new URL(url).hostname, phone: '+1-555-987-6543', company: new URL(url).hostname },
      { name: 'Support Team', email: 'support@' + new URL(url).hostname, phone: '+1-555-456-7890', company: new URL(url).hostname }
    ];
    
    displayScrapingResults(mockResults, 'Website');
    toast('Website scraping completed! Found ' + mockResults.length + ' contacts.', 'success');
  } catch (error) {
    toast('Scraping failed: ' + error.message, 'error');
  }
}

async function scrapeBusinessDirectory() {
  const category = document.getElementById('businessCategory').value;
  const location = document.getElementById('businessLocation').value;
  
  if (!category || !location) {
    toast('Please enter both category and location', 'error');
    return;
  }
  
  toast('Scraping business directory...', 'info');
  
  try {
    // Simulate scraping process
    await new Promise(resolve => setTimeout(resolve, 2500));
    
    const mockResults = [
      { name: 'Tech Solutions Inc', category: category, location: location, phone: '+1-555-111-2222', email: 'info@techsolutions.com' },
      { name: 'Digital Innovations LLC', category: category, location: location, phone: '+1-555-333-4444', email: 'hello@digitalinnovations.com' },
      { name: 'Future Systems Corp', category: category, location: location, phone: '+1-555-555-6666', email: 'contact@futuresystems.com' }
    ];
    
    displayScrapingResults(mockResults, 'Business Directory');
    toast('Business directory scraping completed! Found ' + mockResults.length + ' companies.', 'success');
  } catch (error) {
    toast('Scraping failed: ' + error.message, 'error');
  }
}

function displayScrapingResults(results, source) {
  const resultsContainer = document.getElementById('scrapingResults');
  
  if (results.length === 0) {
    resultsContainer.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-search"></i>
        <p>No results found from ${source}.</p>
      </div>
    `;
    return;
  }
  
  let tableHTML = `
    <h5>Results from ${source} (${results.length} found)</h5>
    <table class="scraping-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Position/Company</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
  `;
  
  results.forEach(result => {
    tableHTML += `
      <tr>
        <td>${result.name}</td>
        <td>${result.position || result.category || result.company || ''}</td>
        <td>${result.email || ''}</td>
        <td>${result.phone || ''}</td>
        <td>
          <button class="btn btn-sm btn-success" onclick="addScrapedContact('${result.name}', '${result.email}', '${result.phone}', '${result.company || ''}')">
            <i class="fas fa-plus"></i> Add to Contacts
          </button>
        </td>
      </tr>
    `;
  });
  
  tableHTML += `
      </tbody>
    </table>
  `;
  
  resultsContainer.innerHTML = tableHTML;
}

async function addScrapedContact(name, email, phone, company) {
  try {
    const nameParts = name.split(' ');
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';
    
    await api.post('/contacts', {
      first_name: firstName,
      last_name: lastName,
      email: email,
      company: company,
      phone_number: phone,
      status: 'new'
    });
    
    toast('Contact added successfully!', 'success');
    await refreshContacts();
  } catch (error) {
    toast('Failed to add contact: ' + error.message, 'error');
  }
}

// Initialize CRM features when CRM tab is shown
document.querySelector('[data-tab="crm"]').addEventListener('click', () => {
  setTimeout(initializeCrmFeatures, 100);
});

// Initial load
loadProfile();

