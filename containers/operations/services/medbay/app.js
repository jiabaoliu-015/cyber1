const $ = id => document.getElementById(id);
const value = id => $(id).value;
async function request(path, body, extra = {}) {
  const response = await fetch(path, {method: body === undefined ? 'GET' : 'POST',
    headers: {'Content-Type': 'application/json', ...extra},
    credentials: 'same-origin', body: body === undefined ? undefined : JSON.stringify(body)});
  const result = await response.json();
  $('output').textContent = JSON.stringify({status: response.status, ...result}, null, 2);
  return result;
}
function basic() { return {'Authorization': 'Basic ' + btoa(value('config-user') + ':' + value('config-token'))}; }
function bind(id, action) { $(id).addEventListener('click', async () => {
  try { await action(); } catch (err) { $('output').textContent = 'Network error: ' + err.message; }
}); }
bind('login', () => request('/api/login', {username: value('username'), password: value('password')}));
bind('me', () => request('/api/me'));
bind('grants', () => request('/api/access/grants'));
bind('read-grant', () => request('/api/access/grants/' + encodeURIComponent(value('grant-id'))));
bind('recover', () => request('/api/access/recover', {recovery_code: value('recovery-code'), new_password: value('new-password')}));
bind('open-medbay', () => request('/api/medbay'));
bind('reconcile', () => request('/api/medbay/reconcile', {audit_reference: value('audit-reference')}));
bind('submit', () => request('/api/medbay/submit', {fate: value('fate'), timestamp: value('timestamp')}));
bind('config', () => request('/api/failsafe/config', undefined, basic()));
bind('isolate', () => request('/api/failsafe/isolate', {panel: value('panel'), mode: value('mode')}, basic()));
