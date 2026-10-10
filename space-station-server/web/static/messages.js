const el = id => document.getElementById(id);
function accountLabel(username) {
  if (username === 'captain') return 'Jin Hong · Captain';
  if (username === 'crew') return 'Crew Access';
  return username;
}
const formatTime = new Intl.DateTimeFormat('en', {dateStyle:'medium', timeStyle:'short'});
let before = null;
let reading = null;
let leaving = false;
let memoRevision = 0;
let memoDirty = false;
let memoOwner = null;

function leave() {
  leaving = true;
  el('message-list').replaceChildren();
  el('memo-content').value = '';
  location.replace('/login');
}
function card(message) {
  const article = document.createElement('article');
  article.className = 'message-card';
  const header = document.createElement('header');
  const name = document.createElement('h3');
  const author = message.author_label || accountLabel(message.username);
  name.textContent = author;
  const time = document.createElement('time');
  time.dateTime = message.created_at;
  time.textContent = formatTime.format(new Date(message.created_at));
  header.append(name, time);
  if (message.can_delete) {
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'delete-message';
    remove.textContent = 'Delete';
    remove.setAttribute('aria-label', `Delete message by ${author}`);
    remove.addEventListener('click', async () => {
      if (!window.confirm('Delete this message?')) return;
      remove.disabled = true;
      try {
        const response = await fetch('/api/messages/delete', {method:'POST', body:new URLSearchParams({id:message.id})});
        if (response.status === 401) { leave(); return; }
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Unable to delete.');
        await load();
      } catch (error) { el('send-status').textContent = error.message; }
      finally { remove.disabled = false; }
    });
    header.append(remove);
  }
  const body = document.createElement('p');
  body.className = 'message-body';
  body.textContent = message.message;
  article.append(header, body);
  return article;
}
async function load(older = false) {
  if (reading) await reading;
  if (leaving) return;
  const task = (async () => {
    el('older').disabled = true;
    el('retry').hidden = true;
    el('message-list').setAttribute('aria-busy', 'true');
    el('list-status').textContent = 'Loading messages…';
    try {
      const response = await fetch('/api/messages' + (older && before ? `?before=${before}` : ''));
      if (response.status === 401) { leave(); return; }
      if (!response.ok) throw new Error();
      const data = await response.json();
      if (leaving) return;
      const scroll = el('message-scroll');
      const oldHeight = scroll.scrollHeight;
      const oldTop = scroll.scrollTop;
      const cards = data.messages.slice().reverse().map(card);
      if (older) el('message-list').prepend(...cards);
      else el('message-list').replaceChildren(...cards);
      before = data.next_before;
      el('older').hidden = !before;
      el('no-messages').hidden = data.total !== 0;
      el('list-status').textContent = '';
      scroll.scrollTop = older ? oldTop + scroll.scrollHeight - oldHeight : scroll.scrollHeight;
    } catch (_) {
      el('list-status').textContent = 'Unable to load messages.';
      el('retry').hidden = false;
    } finally {
      el('older').disabled = false;
      el('message-list').setAttribute('aria-busy', 'false');
    }
  })();
  reading = task;
  await task;
  if (reading === task) reading = null;
}
el('older').addEventListener('click', () => load(true));
el('retry').addEventListener('click', () => load());
el('send-form').addEventListener('submit', async event => {
  event.preventDefault();
  const input = el('new-message');
  const status = el('send-status');
  const message = input.value.trim();
  status.className = 'form-status';
  if (!message) { status.textContent = 'Enter a message.'; return; }
  el('send').disabled = true;
  input.disabled = true;
  status.textContent = 'Sending…';
  try {
    const response = await fetch('/api/messages/private', {method:'POST', body:new URLSearchParams({message})});
    if (response.status === 401) { leave(); return; }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to send.');
    input.value = '';
    status.textContent = 'Sent.';
    await load();
  } catch (error) {
    status.classList.add('error');
    status.textContent = error instanceof TypeError ? 'Connection interrupted. Check the board before retrying.' : error.message;
  } finally {
    el('send').disabled = false;
    input.disabled = false;
    input.focus();
  }
});
el('sign-out').addEventListener('click', async () => {
  if (memoDirty && !window.confirm('Your memo has unsaved changes. Sign out anyway?')) return;
  el('sign-out').disabled = true;
  try {
    const response = await fetch('/api/logout', {method:'POST', body:new URLSearchParams()});
    if (!response.ok) throw new Error();
    leave();
  } catch (_) {
    el('send-status').textContent = 'Unable to sign out. Please try again.';
  } finally { el('sign-out').disabled = false; }
});
window.addEventListener('pageshow', () => load());
window.addEventListener('focus', async () => {
  try {
    const response = await fetch('/api/me');
    if (response.status === 401) { leave(); return; }
    if (response.ok) {
      const user = await response.json();
      if (memoOwner && memoOwner !== user.username) { leave(); return; }
    }
  } catch (_) { /* The board displays connection errors. */ }
  load();
});

async function loadMemo() {
  el('retry-memo').hidden = true;
  try {
    const response = await fetch('/api/memo');
    if (response.status === 401) { leave(); return; }
    if (!response.ok) throw new Error();
    const data = await response.json();
    if (leaving) return;
    el('memo-content').value = data.content;
    memoRevision = data.revision;
    memoOwner = data.username;
    memoDirty = false;
    el('memo-content').disabled = false;
    el('save-memo').disabled = false;
    el('memo-status').textContent = data.revision ? 'Saved.' : 'Your private notes go here.';
  } catch (_) {
    el('memo-status').textContent = 'Unable to load your memo.';
    el('retry-memo').hidden = false;
  }
}
el('memo-content').addEventListener('input', () => {
  memoDirty = true;
  el('memo-status').textContent = 'Unsaved changes';
});
el('retry-memo').addEventListener('click', loadMemo);
el('memo-form').addEventListener('submit', async event => {
  event.preventDefault();
  const content = el('memo-content').value;
  el('save-memo').disabled = true;
  el('memo-content').disabled = true;
  el('memo-status').textContent = 'Saving…';
  try {
    const response = await fetch('/api/memo', {method:'POST', body:new URLSearchParams({content, revision:memoRevision, expected_user:memoOwner})});
    if (response.status === 401) { leave(); return; }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to save.');
    memoRevision = data.revision;
    memoDirty = false;
    el('memo-status').textContent = 'Saved.';
  } catch (error) { el('memo-status').textContent = error.message; }
  finally { el('save-memo').disabled = false; el('memo-content').disabled = false; }
});
window.addEventListener('beforeunload', event => {
  if (memoDirty && !leaving) { event.preventDefault(); event.returnValue = ''; }
});
(async () => {
  try {
    const response = await fetch('/api/me');
    if (response.status === 401) { leave(); return; }
    if (response.ok) {
      const user = await response.json();
      el('account-name').textContent = accountLabel(user.username);
    }
  } catch (_) { /* Message loading handles connection errors. */ }
})();
loadMemo();

// Switch modules without discarding message or personal-memo drafts.
const stationViews = {
  overview: 'Station Overview',
  roster: 'Scheduled Tasks Module',
  tickets: 'Maintenance tickets',
  ticket: 'Maintenance tickets',
  manifests: 'Ration & O2 manifests',
  members: 'Crew Members',
  messages: 'Messages'
};
let moduleRequest = null;
async function loadStationModule(route) {
  if (moduleRequest) moduleRequest.abort();
  const request = new AbortController();
  moduleRequest = request;
  const panel = el('station-app-panel');
  panel.textContent = 'Loading…';
  try {
    const response = await fetch(route.pathname + route.search, {signal: request.signal});
    if (response.status === 401 || new URL(response.url).pathname === '/login') { leave(); return; }
    if (!response.ok) throw Error('Unable to load this module.');
    const page = new DOMParser().parseFromString(await response.text(), 'text/html');
    if (request.signal.aborted) return;
    const content = page.querySelector('.station-shell');
    if (!content) throw Error('Unable to load this module.');
    const module = document.createElement('div');
    module.className = 'station-shell station-embedded';
    module.append(...content.childNodes);
    const heading = module.querySelector('h1');
    if (heading && heading.id === 'ticket-title') {
      const title = document.createElement('h2');
      title.id = heading.id;
      title.textContent = heading.textContent;
      heading.replaceWith(title);
    } else if (heading) heading.remove();
    if (!route.pathname.startsWith('/tickets/')) module.querySelector('nav')?.remove();
    module.querySelectorAll('a[href]').forEach(link => {
      const href = link.getAttribute('href');
      if (href.startsWith('/')) link.setAttribute('href', '#' + href.slice(1));
    });
    panel.replaceChildren(module);
    mountStationApp(module, route, true);
  } catch (error) {
    if (request.signal.aborted) return;
    panel.textContent = error.message;
    const retry = document.createElement('button');
    retry.className = 'quiet-button';
    retry.textContent = 'Try again';
    retry.addEventListener('click', () => loadStationModule(route));
    panel.append(document.createElement('br'), retry);
  }
}
function showStationView() {
  const requested = location.hash.slice(1);
  const route = new URL('/' + requested, location.origin);
  const name = route.pathname.slice(1);
  const view = /^tickets\/\d+$/.test(name) ? 'ticket' : Object.prototype.hasOwnProperty.call(stationViews, name) ? name : 'messages';
  const isMessages = view === 'messages';
  const isOverview = view === 'overview';
  document.body.classList.toggle('has-overview', isOverview);
  el('overview-motto').hidden = !isOverview;
  el('station-overview').hidden = !isOverview;
  document.querySelector('.conversation-header h1').textContent = stationViews[view];
  document.title = stationViews[view] + ' · Station';
  el('message-scroll').hidden = !isMessages;
  el('send-form').hidden = !isMessages;
  el('module-content').hidden = isMessages;
  el('module-content').setAttribute('aria-label', stationViews[view]);
  el('crew-profiles').hidden = view !== 'members';
  const isApp = ['roster', 'tickets', 'ticket', 'manifests'].includes(view);
  el('station-app-panel').hidden = !isApp;
  if (moduleRequest) moduleRequest.abort();
  if (isApp) loadStationModule(route);
  el('module-content').scrollTop = 0;
  const activeView = ['ticket', 'manifests'].includes(view) ? 'tickets' : view;
  document.querySelectorAll('[data-view]').forEach(link => {
    if (link.dataset.view === activeView) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
}
window.addEventListener('hashchange', showStationView);
showStationView();
