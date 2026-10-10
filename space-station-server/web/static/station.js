function mountStationApp(root, route, embedded = false) {
const $ = id => root.querySelector('#' + id);
const linkFor = url => embedded ? '#' + url.replace(/^\//, '') : url;
const navigate = url => { if (embedded) location.hash = linkFor(url); else location.assign(url); };
function accountLabel(username) {
  if (username === 'captain') return 'Jin Hong · Captain';
  if (username === 'crew') return 'Crew Access';
  return username;
}
const path = route.pathname;
const status = message => { $('status').textContent = message; };
async function api(url, values) {
  const response = await fetch(url, values ? {method:'POST',body:new URLSearchParams(values)} : undefined);
  if (response.status === 401) { location.replace('/login'); throw Error('Sign in required.'); }
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Request failed.');
  return data;
}
function row(title, subtitle, href) {
  const item = document.createElement(href ? 'a' : 'div');
  item.className = 'station-result';
  if (href) item.href = linkFor(href);
  const strong = document.createElement('strong'); strong.textContent = title;
  const span = document.createElement('span'); span.textContent = subtitle;
  item.append(strong,span); return item;
}
if (path === '/roster') {
  async function search() {
    try {
      status('');
      const data = await api('/api/roster?q='+encodeURIComponent($('roster-query').value));
      $('results').replaceChildren(...data.results.map(r => row(r.crew_name, r.shift_start+' · '+r.station)));
      if (!data.results.length) status('No matching assignments.');
    } catch (error) { status(error.message); }
  }
  $('roster-form').addEventListener('submit', e => { e.preventDefault(); search(); });
  search();
} else if (path === '/tickets') {
  async function loadTickets() {
    try {
      const data = await api('/api/tickets');
      $('results').replaceChildren(...data.tickets.map(t => row('#'+t.id+' · '+t.subject, accountLabel(t.owner)+' · '+t.created_at, '/tickets/'+t.id)));
      if (!data.tickets.length) status('No tickets yet.');
    } catch (error) { status(error.message); }
  }
  $('ticket-form').addEventListener('submit', async e => {
    e.preventDefault();
    try {
      const data = await api('/api/tickets', {subject:$('ticket-subject').value,description:$('ticket-description').value});
      navigate('/tickets/'+data.id);
    } catch (error) { status(error.message); }
  });
  api('/api/me').then(user => {
    if (user.role === 'captain') $('ops-panel').hidden = false;
  }).catch(() => {});
  $('ops-open').addEventListener('click', async () => {
    try {
      const grant = await api('/api/ops/grants', {});
      navigate('/manifests?access='+encodeURIComponent(grant.access));
    } catch (error) { status(error.message); }
  });
  loadTickets();
} else if (path.startsWith('/tickets/')) {
  const id = path.split('/').pop();
  async function loadTicket() {
    try {
      const data = await api('/api/tickets/'+id);
      $('ticket-title').textContent = '#'+id+' · '+data.ticket.subject;
      $('ticket-owner').textContent = 'Opened by '+accountLabel(data.ticket.owner)+' · '+data.ticket.created_at;
      $('ticket-description').innerHTML = data.ticket.description;
      $('results').replaceChildren(...data.comments.map(c => row(accountLabel(c.author), c.content)));
      if (!data.comments.length) status('No updates yet.'); else status('');
    } catch (error) { status(error.message); }
  }
  $('comment-form').addEventListener('submit', async e => {
    e.preventDefault();
    try { await api('/api/tickets/comment',{ticket_id:id,content:$('comment').value}); $('comment').value=''; await loadTicket(); }
    catch (error) { status(error.message); }
  });
  loadTicket();
} else if (path === '/manifests') {
  const access = new URLSearchParams(route.search).get('access') || '';
  async function load() {
    try {
      const data = await api('/api/manifests?access='+encodeURIComponent(access));
      $('results').replaceChildren(...data.manifests.map(m => {
        const item = row('#'+m.id+' · '+m.title,'Open record', '#'+m.id);
        item.addEventListener('click', e => { e.preventDefault(); openManifest(m.id); });
        return item;
      }));
      const selected = Number(embedded ? route.searchParams.get('record') : route.hash.slice(1));
      if (selected) openManifest(selected);
    } catch (error) { status(error.message); }
  }
  async function openManifest(id) {
    try {
      const item = await api('/api/manifests/'+id+'?access='+encodeURIComponent(access));
      $('manifest-title').textContent = item.title;
      $('manifest-data').textContent = item.data;
      $('manifest-detail').hidden = false;
      if (!embedded) location.hash = id;
      status('');
    } catch (error) { status(error.message); }
  }
  load();
}

}
if (!document.body.classList.contains('messages-page')) {
  mountStationApp(document, new URL(location.href));
}
