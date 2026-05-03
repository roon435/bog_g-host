from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
import os, uuid

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SITES_DIR = "/tmp/sites"
os.makedirs(SITES_DIR, exist_ok=True)

class SitePayload(BaseModel):
    html: str

DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>host.it</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@500;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0e0e11; --surface: #18181c; --border: #2a2a30;
    --text: #f0f0f0; --muted: #888; --green: #1D9E75;
    --green-dim: #0f4a37; --green-glow: rgba(29,158,117,0.15);
    --mono: 'DM Mono', monospace; --sans: 'Syne', sans-serif;
  }
  body { background: var(--bg); color: var(--text); font-family: var(--sans); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
  header { display: flex; align-items: center; justify-content: space-between; padding: 0 1.5rem; height: 52px; border-bottom: 1px solid var(--border); background: var(--surface); flex-shrink: 0; }
  .logo { font-size: 18px; font-weight: 700; letter-spacing: -0.5px; }
  .logo span { color: var(--green); }
  .header-right { display: flex; align-items: center; gap: 12px; }
  .pill { font-size: 11px; background: var(--green-dim); color: var(--green); padding: 4px 10px; border-radius: 20px; font-weight: 500; }
  .btn-host { background: var(--green); color: #fff; border: none; padding: 8px 20px; border-radius: 8px; font-family: var(--sans); font-size: 14px; font-weight: 700; cursor: pointer; transition: opacity 0.15s, transform 0.1s; display: flex; align-items: center; gap: 8px; }
  .btn-host:hover { opacity: 0.88; }
  .btn-host:active { transform: scale(0.97); }
  .btn-host:disabled { opacity: 0.4; cursor: not-allowed; }
  .workspace { display: grid; grid-template-columns: 1fr 1fr; flex: 1; overflow: hidden; }
  .pane { display: flex; flex-direction: column; overflow: hidden; border-right: 1px solid var(--border); }
  .pane:last-child { border-right: none; }
  .pane-header { display: flex; align-items: center; justify-content: space-between; padding: 0 1rem; height: 38px; border-bottom: 1px solid var(--border); background: var(--surface); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; flex-shrink: 0; }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); display: inline-block; margin-right: 6px; }
  textarea { flex: 1; background: var(--bg); color: #c9d1d9; border: none; outline: none; resize: none; font-family: var(--mono); font-size: 13px; line-height: 1.7; padding: 1.25rem; tab-size: 2; }
  iframe { flex: 1; border: none; background: #fff; display: none; }
  .preview-empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; color: var(--muted); font-size: 13px; }
  .preview-empty svg { opacity: 0.3; }
  .status-bar { height: 28px; background: var(--surface); border-top: 1px solid var(--border); display: flex; align-items: center; padding: 0 1rem; gap: 1rem; font-size: 11px; color: var(--muted); flex-shrink: 0; font-family: var(--mono); }
  .live-url { color: var(--green); text-decoration: none; font-weight: 500; }
  .live-url:hover { text-decoration: underline; }
  .toast { position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%) translateY(80px); background: var(--surface); border: 1px solid var(--green); color: var(--text); padding: 12px 20px; border-radius: 10px; font-size: 13px; display: flex; align-items: center; gap: 10px; transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1); z-index: 100; box-shadow: 0 0 30px var(--green-glow); }
  .toast.show { transform: translateX(-50%) translateY(0); }
  .toast a { color: var(--green); font-family: var(--mono); font-size: 12px; }
  .spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; display: none; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<header>
  <div class="logo">host<span>.</span>it</div>
  <div class="header-right">
    <div class="pill">Free</div>
    <button class="btn-host" id="btn" onclick="hostSite()">
      <div class="spinner" id="spinner"></div>
      <span id="btn-label">⚡ Host it</span>
    </button>
  </div>
</header>
<div class="workspace">
  <div class="pane">
    <div class="pane-header">
      <span><span class="dot"></span>index.html</span>
      <span id="char-count">0 chars</span>
    </div>
    <textarea id="editor" spellcheck="false" placeholder="<!DOCTYPE html>
<html>
<body>
  <h1>Hello world!</h1>
</body>
</html>"></textarea>
  </div>
  <div class="pane">
    <div class="pane-header">
      <span>Preview</span>
      <span id="preview-url"></span>
    </div>
    <div class="preview-empty" id="preview-empty">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="4" y="10" width="40" height="30" rx="3"/>
        <path d="M4 16h40"/>
        <circle cx="10" cy="13" r="1.5" fill="currentColor"/>
        <circle cx="15" cy="13" r="1.5" fill="currentColor"/>
        <circle cx="20" cy="13" r="1.5" fill="currentColor"/>
      </svg>
      Hit "Host it" to see your site live
    </div>
    <iframe id="preview"></iframe>
  </div>
</div>
<div class="status-bar">
  <span id="status">Ready</span>
  <span id="live-link"></span>
</div>
<div class="toast" id="toast"></div>
<script>
  const editor = document.getElementById('editor');
  const btn = document.getElementById('btn');
  const btnLabel = document.getElementById('btn-label');
  const spinner = document.getElementById('spinner');
  const preview = document.getElementById('preview');
  const previewEmpty = document.getElementById('preview-empty');
  const previewUrl = document.getElementById('preview-url');
  const status = document.getElementById('status');
  const liveLink = document.getElementById('live-link');
  const charCount = document.getElementById('char-count');
  const toast = document.getElementById('toast');

  editor.addEventListener('input', () => {
    charCount.textContent = editor.value.length + ' chars';
  });

  editor.addEventListener('keydown', e => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const s = editor.selectionStart;
      editor.value = editor.value.substring(0, s) + '  ' + editor.value.substring(editor.selectionEnd);
      editor.selectionStart = editor.selectionEnd = s + 2;
    }
  });

  async function hostSite() {
    const html = editor.value.trim();
    if (!html) return showToast('Paste some HTML first!');
    btn.disabled = true;
    spinner.style.display = 'block';
    btnLabel.textContent = 'Hosting...';
    status.textContent = 'Deploying...';
    try {
      const res = await fetch('/host', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ html })
      });
      const data = await res.json();
      const url = window.location.origin + data.url;
      preview.src = url;
      preview.style.display = 'block';
      previewEmpty.style.display = 'none';
      previewUrl.innerHTML = '<a class="live-url" href="' + url + '" target="_blank">' + data.url + '</a>';
      liveLink.innerHTML = 'Live at <a class="live-url" href="' + url + '" target="_blank">' + url + '</a>';
      status.textContent = 'Hosted!';
      showToast('Live at <a href="' + url + '" target="_blank">' + url + '</a>');
    } catch(e) {
      status.textContent = 'Error — try again';
      showToast('Something went wrong');
    } finally {
      btn.disabled = false;
      spinner.style.display = 'none';
      btnLabel.textContent = '⚡ Host it';
    }
  }

  function showToast(msg) {
    toast.innerHTML = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 4000);
  }
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def editor():
    return DASHBOARD

@app.post("/host")
def host_site(payload: SitePayload):
    site_id = uuid.uuid4().hex[:8]
    path = os.path.join(SITES_DIR, f"{site_id}.html")
    with open(path, "w") as f:
        f.write(payload.html)
    return {"url": f"/site/{site_id}"}

@app.get("/site/{site_id}", response_class=HTMLResponse)
def serve_site(site_id: str):
    path = os.path.join(SITES_DIR, f"{site_id}.html")
    if not os.path.exists(path):
        raise HTTPException(404, "Site not found")
    with open(path) as f:
        return f.read()

handler = Mangum(app, lifespan="off")
