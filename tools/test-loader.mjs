// Tests automatiques du loader : il doit s'afficher, puis disparaître, dans tous les cas.
// Usage : node tools/test-loader.mjs   (Node 22+ et Google Chrome installés)
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, extname, resolve } from 'node:path';

const ROOT = resolve(new URL('..', import.meta.url).pathname);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 8799, DPORT = 9333;
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.json': 'application/json' };

// Serveur statique qui renvoie 404.html pour une adresse inconnue (comme GitHub Pages / Netlify)
const server = createServer(async (req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (p.endsWith('/')) p += 'index.html';
  const file = join(ROOT, p);
  try {
    if (!file.startsWith(ROOT)) throw new Error('out');
    const st = await stat(file); if (!st.isFile()) throw new Error('dir');
    res.writeHead(200, { 'content-type': TYPES[extname(file)] || 'application/octet-stream' });
    res.end(await readFile(file));
  } catch {
    res.writeHead(404, { 'content-type': TYPES['.html'] });
    res.end(await readFile(join(ROOT, '404.html')));
  }
}).listen(PORT);

const profile = mkdtempSync(join(tmpdir(), 'teddy-chrome-'));
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${DPORT}`, `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check', '--window-size=1280,900', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function devtools() {
  for (let i = 0; i < 60; i++) {
    try { return await (await fetch(`http://127.0.0.1:${DPORT}/json/version`)).json(); } catch { await sleep(200); }
  }
  throw new Error('Chrome ne répond pas');
}

class Page {
  static async open() {
    const t = await (await fetch(`http://127.0.0.1:${DPORT}/json/new?about:blank`, { method: 'PUT' })).json();
    const p = new Page(); p.id = t.id; p.ws = new WebSocket(t.webSocketDebuggerUrl);
    p.n = 0; p.wait = new Map(); p.events = [];
    await new Promise((r) => p.ws.addEventListener('open', r, { once: true }));
    p.ws.addEventListener('message', (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && p.wait.has(m.id)) { p.wait.get(m.id)(m); p.wait.delete(m.id); } else if (m.method) p.events.push(m);
    });
    await p.send('Page.enable'); await p.send('Runtime.enable'); await p.send('Network.enable');
    return p;
  }
  send(method, params = {}) { const id = ++this.n; this.ws.send(JSON.stringify({ id, method, params })); return new Promise((r) => this.wait.set(id, r)); }
  async eval(expr) { const r = await this.send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }); return r.result?.result?.value; }
  async close() { this.ws.close(); await fetch(`http://127.0.0.1:${DPORT}/json/close/${this.id}`); }
}

// État du loader : 'visible', 'absent' (jamais affiché) ou 'caché'
const LOADER_STATE = `(() => {
  const l = document.getElementById('loader');
  if (!l) return 'pas-de-loader';
  const cs = getComputedStyle(l);
  if (cs.display === 'none') return document.documentElement.classList.contains('js') && !l.classList.contains('is-gone') ? 'absent' : 'cache';
  if (cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.05) return 'cache';
  return 'visible';
})()`;

async function waitState(page, want, maxMs, step = 40) {
  const t0 = Date.now();
  while (Date.now() - t0 < maxMs) {
    const s = await page.eval(LOADER_STATE).catch(() => null);
    if (want.includes(s)) return { ok: true, ms: Date.now() - t0, state: s };
    await sleep(step);
  }
  return { ok: false, ms: maxMs, state: await page.eval(LOADER_STATE).catch(() => 'erreur') };
}

async function goto(page, url) { await page.send('Page.navigate', { url }); }

const results = [];
function check(name, cond, detail = '') { results.push({ name, ok: !!cond, detail }); console.log(`${cond ? '  OK ' : '  ÉCHEC'}  ${name}${detail ? '  (' + detail + ')' : ''}`); }

const PAGES = ['index.html', 'carte.html', 'mentions-legales.html', 'confidentialite.html', '404.html', 'cette-page-nexiste-pas'];
const base = `http://127.0.0.1:${PORT}/`;

await devtools();
try {
  // 1. Arrivée sur chaque page : le loader s'affiche puis disparaît
  console.log('\n1. Arrivée sur chaque page');
  for (const p of PAGES) {
    const page = await Page.open();
    await goto(page, base + p);
    const shown = await waitState(page, ['visible'], 1500, 20);
    const gone = await waitState(page, ['cache'], 3500);
    check(`${p} : loader affiché`, shown.ok, `après ${shown.ms} ms`);
    check(`${p} : loader retiré`, gone.ok, gone.ok ? `après ${shown.ms + gone.ms} ms environ` : `état final : ${gone.state}`);
    const title = await page.eval(`(() => { const h = document.querySelector('h1'); if (!h) return 'aucun h1'; const r = h.getBoundingClientRect(); return getComputedStyle(h).opacity > 0.5 && r.height > 0 ? 'visible' : 'invisible'; })()`);
    check(`${p} : titre lisible après le loader`, title === 'visible', title);
    await page.close();
  }

  // 2. Clic sur le logo depuis chaque page
  console.log('\n2. Clic sur le logo (en-tête) depuis chaque page');
  for (const p of PAGES) {
    const page = await Page.open();
    await goto(page, base + p);
    await waitState(page, ['cache'], 4000);
    await page.eval(`window.scrollTo(0, 600)`);
    await page.eval(`document.querySelector('.site-header a[data-logo]').click()`);
    const shown = await waitState(page, ['visible'], 600, 15);
    check(`${p} : loader rejoué au clic`, shown.ok, `après ${shown.ms} ms`);
    await sleep(1200);
    const gone = await waitState(page, ['cache'], 3500);
    const url = await page.eval('location.pathname');
    const y = await page.eval('Math.round(scrollY)');
    check(`${p} : retour à l'accueil`, /\/(index\.html)?$/.test(url), url);
    check(`${p} : loader retiré après le clic`, gone.ok, gone.ok ? '' : `état : ${gone.state}`);
    check(`${p} : en haut de page`, y === 0, `scrollY=${y}`);
    await page.close();
  }

  // 3. Clic sur le logo du pied de page
  console.log('\n3. Clic sur le logo du pied de page');
  {
    const page = await Page.open();
    await goto(page, base + 'carte.html'); await waitState(page, ['cache'], 4000);
    await page.eval(`document.querySelector('.site-footer a[data-logo]').click()`);
    const shown = await waitState(page, ['visible'], 600, 15);
    await sleep(1200);
    const gone = await waitState(page, ['cache'], 3500);
    check('pied de page : loader rejoué', shown.ok);
    check('pied de page : loader retiré', gone.ok, gone.state);
    await page.close();
  }

  // 4. Double clic rapide sur le logo
  console.log('\n4. Clics répétés sur le logo');
  {
    const page = await Page.open();
    await goto(page, base + 'index.html'); await waitState(page, ['cache'], 4000);
    await page.eval(`(() => { const a = document.querySelector('.site-header a[data-logo]'); a.click(); a.click(); setTimeout(() => a.click(), 120); })()`);
    await sleep(800);
    const gone = await waitState(page, ['cache'], 3500);
    check('accueil : triple clic, loader retiré', gone.ok, gone.state);
    await page.close();
  }

  // 5. Retour arrière du navigateur
  console.log('\n5. Retour arrière et avant du navigateur');
  {
    const page = await Page.open();
    await goto(page, base + 'carte.html'); await waitState(page, ['cache'], 4000);
    await page.eval(`document.querySelector('.site-header a[data-logo]').click()`);
    await sleep(1500); await waitState(page, ['cache'], 3500);
    await page.eval('history.back()');
    await sleep(300);
    const back = await waitState(page, ['cache'], 3500);
    check('retour arrière : loader retiré', back.ok, `état : ${back.state}, ${back.ms} ms`);
    await page.eval('history.forward()');
    await sleep(300);
    const fwd = await waitState(page, ['cache'], 3500);
    check('retour avant : loader retiré', fwd.ok, `état : ${fwd.state}`);
    await page.close();
  }

  // 6. Script principal bloqué (panne réseau, bloqueur de pub)
  console.log('\n6. Script du site bloqué');
  for (const p of ['index.html', 'carte.html']) {
    const page = await Page.open();
    await page.send('Network.setBlockedURLs', { urls: ['*site.js*'] });
    await goto(page, base + p);
    const gone = await waitState(page, ['cache'], 6000);
    check(`${p} sans site.js : le loader finit par disparaître`, gone.ok, gone.ok ? `après ${gone.ms} ms (sécurité CSS)` : gone.state);
    const vis = await page.eval(`[...document.querySelectorAll('.reveal')].filter(e => getComputedStyle(e).opacity < 0.5).length`);
    check(`${p} sans site.js : aucun contenu caché`, vis === 0, `${vis} élément(s) masqué(s)`);
    await page.close();
  }

  // 7. JavaScript désactivé
  console.log('\n7. JavaScript désactivé');
  {
    const page = await Page.open();
    await page.send('Emulation.setScriptExecutionDisabled', { value: true });
    await goto(page, base + 'index.html'); await sleep(1200);
    const r = await page.send('Runtime.evaluate', { expression: '1' });
    const dom = await page.send('DOM.getDocument', {});
    await page.send('Emulation.setScriptExecutionDisabled', { value: false });
    const st = await page.eval(`(() => { const l = document.getElementById('loader'); return getComputedStyle(l).display; })()`);
    check('sans JavaScript : le loader ne s\'affiche jamais', st === 'none', `display=${st}`);
    await page.close();
  }

  // 8. Connexion lente (3G)
  console.log('\n8. Connexion lente');
  for (const p of ['index.html', 'carte.html']) {
    const page = await Page.open();
    await page.send('Network.emulateNetworkConditions', { offline: false, latency: 300, downloadThroughput: 60 * 1024, uploadThroughput: 30 * 1024 });
    await page.send('Network.setCacheDisabled', { cacheDisabled: true });
    const t0 = Date.now();
    await goto(page, base + p);
    const gone = await waitState(page, ['cache'], 9000, 100);
    check(`${p} en 3G : loader retiré`, gone.ok, gone.ok ? `${Date.now() - t0} ms après le début du chargement` : gone.state);
    await page.close();
  }

  // 9. Mouvements réduits
  console.log('\n9. Préférence « réduire les animations »');
  {
    const page = await Page.open();
    await page.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
    await goto(page, base + 'index.html');
    const gone = await waitState(page, ['cache'], 2500);
    check('mouvements réduits : loader retiré vite', gone.ok, `${gone.ms} ms`);
    await page.close();
  }

  // 10. Ctrl/Cmd + clic sur le logo : pas de loader (ouverture dans un nouvel onglet)
  console.log('\n10. Cmd + clic sur le logo');
  {
    const page = await Page.open();
    await goto(page, base + 'carte.html'); await waitState(page, ['cache'], 4000);
    await page.eval(`document.querySelector('.site-header a[data-logo]').dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, metaKey: true, button: 0 }))`);
    await sleep(200);
    const s = await page.eval(LOADER_STATE);
    check('cmd + clic : le loader ne bloque pas la page', s === 'cache', s);
    await page.close();
  }
} finally {
  const ko = results.filter((r) => !r.ok);
  console.log(`\nRÉSULTAT : ${results.length - ko.length}/${results.length} tests réussis`);
  if (ko.length) { console.log('Échecs :'); ko.forEach((r) => console.log(' - ' + r.name + ' ' + r.detail)); }
  chrome.kill(); server.close();
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
  process.exitCode = ko.length ? 1 : 0;
}
