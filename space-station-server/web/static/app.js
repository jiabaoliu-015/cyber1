const el = id => document.getElementById(id);

el('login-form').addEventListener('submit', async event => {
  event.preventDefault();
  const status = el('login-status');
  status.className = 'form-status';
  status.textContent = 'Signing in…';
  el('login-button').disabled = true;
  try {
    const response = await fetch('/api/login', { method: 'POST', body: new URLSearchParams({
      username: el('login-username').value.trim(), password: el('login-password').value
    }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to sign in.');
    el('login-password').value = '';
    status.textContent = '';
    location.assign('/messages');
  } catch (error) {
    status.textContent = error instanceof TypeError ? 'Unable to connect. Please try again.' : error.message;
    status.classList.add('error');
  } finally { el('login-button').disabled = false; }
});
