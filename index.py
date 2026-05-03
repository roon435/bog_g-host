from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
import os, uuid, base64, json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SITES_DIR = "/tmp/sites"
FILES_DIR = "/tmp/files"
os.makedirs(SITES_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

class SitePayload(BaseModel):
    html: str
    files: dict = {}

DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>host.it</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#080809;--surface:#111113;--surface2:#1a1a1f;--border:#222228;
  --text:#f0f0f0;--muted:#555;--muted2:#888;
  --green:#00e87a;--green-dim:#001a0e;--green-mid:#00994f;
  --mono:'DM Mono',monospace;--sans:'Syne',sans-serif;
}
body{background:var(--bg);color:var(--text);font-family:var(--sans);height:100vh;display:flex;flex-direction:column;overflow:hidden;}

/* HEADER */
header{display:flex;align-items:center;justify-content:space-between;padding:0 1.5rem;height:54px;border-bottom:1px solid var(--border);background:var(--surface);flex-shrink:0;gap:12px;}
.logo{font-size:20px;font-weight:800;letter-spacing:-1px;white-space:nowrap;}
.logo span{color:var(--green);}

/* LIGHTNING BUTTON from uiverse */
.button{
  display:flex;align-items:center;gap:8px;
  padding:10px 22px;
  font-family:var(--sans);font-size:14px;font-weight:700;
  color:#fff;
  background:linear-gradient(135deg,#00e87a,#00994f);
  border:none;border-radius:8px;cursor:pointer;
  position:relative;overflow:hidden;
  transition:transform 0.15s,box-shadow 0.15s;
  box-shadow:0 0 0 0 rgba(0,232,122,0.4);
  white-space:nowrap;
}
.button::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,0.15),transparent);
  opacity:0;transition:opacity 0.2s;
}
.button:hover{transform:translateY(-1px);box-shadow:0 0 24px rgba(0,232,122,0.35);}
.button:hover::before{opacity:1;}
.button:active{transform:scale(0.97);}
.button:disabled{opacity:0.4;cursor:not-allowed;transform:none;box-shadow:none;}
.button svg{flex-shrink:0;}

/* TABS */
.tabs{display:flex;gap:2px;background:var(--surface2);border-radius:8px;padding:3px;}
.tab{padding:5px 14px;border-radius:6px;font-size:12px;font-weight:700;cursor:pointer;color:var(--muted2);transition:all 0.15s;border:none;background:none;font-family:var(--sans);}
.tab.active{background:var(--border);color:var(--text);}

/* WORKSPACE */
.workspace{display:grid;grid-template-columns:1fr 1fr;flex:1;overflow:hidden;}
.pane{display:flex;flex-direction:column;overflow:hidden;border-right:1px solid var(--border);}
.pane:last-child{border-right:none;}
.pane-header{display:flex;align-items:center;justify-content:space-between;padding:0 1rem;height:36px;border-bottom:1px solid var(--border);background:var(--surface);font-size:11px;color:var(--muted2);text-transform:uppercase;letter-spacing:1px;flex-shrink:0;}
.dot{width:7px;height:7px;border-radius:50%;background:var(--green);display:inline-block;margin-right:6px;box-shadow:0 0 6px var(--green);}

/* EDITOR PANEL */
.editor-wrap{display:flex;flex-direction:column;flex:1;overflow:hidden;}
textarea{flex:1;background:var(--bg);color:#c9d1d9;border:none;outline:none;resize:none;font-family:var(--mono);font-size:13px;line-height:1.75;padding:1.25rem;tab-size:2;}

/* FILE UPLOAD PANEL */
.upload-panel{background:var(--bg);border-top:1px solid var(--border);flex-shrink:0;max-height:180px;overflow-y:auto;}
.upload-toggle{display:flex;align-items:center;gap:8px;padding:8px 1rem;cursor:pointer;font-size:12px;color:var(--muted2);border:none;background:none;font-family:var(--sans);font-weight:700;width:100%;text-align:left;border-top:1px solid var(--border);}
.upload-toggle:hover{color:var(--text);}
.upload-toggle .arrow{transition:transform 0.2s;display:inline-block;}
.upload-toggle.open .arrow{transform:rotate(90deg);}
.upload-body{display:none;padding:0 1rem 1rem;}
.upload-body.open{display:block;}
.drop-zone{border:1.5px dashed var(--border);border-radius:8px;padding:1rem;text-align:center;cursor:pointer;transition:border-color 0.2s;font-size:12px;color:var(--muted2);}
.drop-zone:hover,.drop-zone.drag{border-color:var(--green);color:var(--green);}
.drop-zone span{color:var(--green);font-weight:700;cursor:pointer;}
#file-input{display:none;}
.file-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;}
.chip{background:var(--surface2);border:1px solid var(--border);border-radius:20px;padding:3px 10px;font-size:11px;color:var(--muted2);display:flex;align-items:center;gap:6px;font-family:var(--mono);}
.chip-img{width:18px;height:18px;border-radius:3px;object-fit:cover;}
.chip-del{cursor:pointer;color:var(--muted);font-size:14px;line-height:1;}
.chip-del:hover{color:#ff4444;}

/* PREVIEW */
iframe{flex:1;border:none;background:#fff;display:none;}
.preview-empty{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;color:var(--muted);font-size:13px;}
.preview-empty svg{opacity:0.2;}

/* STATUS BAR */
.status-bar{height:26px;background:var(--surface);border-top:1px solid var(--border);display:flex;align-items:center;padding:0 1rem;gap:1rem;font-size:11px;color:var(--muted2);flex-shrink:0;font-family:var(--mono);}
.live-url{color:var(--green);text-decoration:none;font-weight:500;}
.live-url:hover{text-decoration:underline;}

/* TOAST */
.toast{position:fixed;bottom:2rem;left:50%;transform:translateX(-50%) translateY(100px);background:var(--surface);border:1px solid var(--green);color:var(--text);padding:12px 20px;border-radius:10px;font-size:13px;display:flex;align-items:center;gap:10px;transition:transform 0.35s cubic-bezier(0.34,1.56,0.64,1);z-index:100;box-shadow:0 0 40px rgba(0,232,122,0.2);white-space:nowrap;}
.toast.show{transform:translateX(-50%) translateY(0);}
.toast a{color:var(--green);font-family:var(--mono);font-size:12px;}

/* SPINNER */
.spinner{width:14px;height:14px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 0.6s linear infinite;display:none;}
@keyframes spin{to{transform:rotate(360deg);}}

/* SCROLLBAR */
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
</style>
</head>
<body>

<header>
  <div class="logo">host<span>.</span>it</div>
  <button class="button" id="btn" onclick="hostSite()">
    <div class="spinner" id="spinner"></div>
    <svg viewBox="0 0 16 16" fill="currentColor" height="16" width="16" xmlns="http://www.w3.org/2000/svg">
      <path d="M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09z"/>
    </svg>
    <span id="btn-label">Host it</span>
  </button>
</header>

<div class="workspace">
  <div class="pane">
    <div class="pane-header">
      <span><span class="dot"></span>index.html</span>
      <span id="char-count">0 chars</span>
    </div>
    <div class="editor-wrap">
      <textarea id="editor" spellcheck="false" placeholder="<!DOCTYPE html>
<html>
<body>
  <h1>Hello world!</h1>
</body>
</html>"></textarea>
    </div>

    <button class="upload-toggle" id="upload-toggle" onclick="toggleUpload()">
      <span class="arrow">▶</span>
      Add images / files (optional)
      <span id="file-badge" style="color:var(--green);display:none;"></span>
    </button>
    <div class="upload-body" id="upload-body">
      <div class="drop-zone" id="drop-zone">
        Drop images here or <span onclick="document.getElementById('file-input').click()">browse</span>
        <input type="file" id="file-input" accept="image/*" multiple>
      </div>
      <div class="file-chips" id="file-chips"></div>
    </div>
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
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileChips = document.getElementById('file-chips');
const fileBadge = document.getElementById('file-badge');

let uploadedFiles = {};

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

function toggleUpload() {
  const toggle = document.getElementById('upload-toggle');
  const body = document.getElementById('upload-body');
  toggle.classList.toggle('open');
  body.classList.toggle('open');
}

dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag'));
dropZone.addEventListener('drop', e => { e.preventDefault(); dropZone.classList.remove('drag'); handleFiles(e.dataTransfer.files); });
fileInput.addEventListener('change', e => handleFiles(e.target.files));

function handleFiles(files) {
  Array.from(files).forEach(f => {
    if (!f.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = ev => {
      const b64 = ev.target.result;
      uploadedFiles[f.name] = b64;
      renderChips();
    };
    reader.readAsDataURL(f);
  });
}

function renderChips() {
  const names = Object.keys(uploadedFiles);
  fileBadge.textContent = names.length ? names.length + ' file' + (names.length > 1 ? 's' : '') : '';
  fileBadge.style.display = names.length ? 'inline' : 'none';
  fileChips.innerHTML = names.map(n => `
    <div class="chip">
      <img class="chip-img" src="${uploadedFiles[n]}" alt="${n}">
      ${n}
      <span class="chip-del" onclick="removeFile('${n}')">×</span>
    </div>
  `).join('');
}

function removeFile(name) {
  delete uploadedFiles[name];
  renderChips();
}

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
      body: JSON.stringify({ html, files: uploadedFiles })
    });
    const data = await res.json();
    const url = window.location.origin + '/site/' + data.id;
    preview.src = url;
    preview.style.display = 'block';
    previewEmpty.style.display = 'none';
    previewUrl.innerHTML = '<a class="live-url" href="' + url + '" target="_blank">/' + data.id + '</a>';
    liveLink.innerHTML = 'Live: <a class="live-url" href="' + url + '" target="_blank">' + url + '</a>';
    status.textContent = 'Hosted!';
    showToast('Live at <a href="' + url + '" target="_blank">' + url + '</a>');
  } catch(e) {
    status.textContent = 'Error — try again';
    showToast('Something went wrong');
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    btnLabel.textContent = 'Host it';
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
def dashboard():
    return DASHBOARD

@app.post("/host")
async def host_site(payload: SitePayload):
    site_id = uuid.uuid4().hex[:8]
    site_dir = os.path.join(SITES_DIR, site_id)
    os.makedirs(site_dir, exist_ok=True)

    # save uploaded files (base64 images)
    for filename, b64data in payload.files.items():
        try:
            header, data = b64data.split(",", 1)
            file_bytes = base64.b64decode(data)
            safe_name = os.path.basename(filename)
            with open(os.path.join(site_dir, safe_name), "wb") as f:
                f.write(file_bytes)
        except Exception:
            continue

    # inject base64 images directly into html so they work without static serving
    html = payload.html
    for filename, b64data in payload.files.items():
        html = html.replace(f'src="{filename}"', f'src="{b64data}"')
        html = html.replace(f"src='{filename}'", f"src='{b64data}'")

    with open(os.path.join(site_dir, "index.html"), "w") as f:
        f.write(html)

    return {"id": site_id}

@app.get("/site/{site_id}", response_class=HTMLResponse)
def serve_site(site_id: str):
    path = os.path.join(SITES_DIR, site_id, "index.html")
    if not os.path.exists(path):
        raise HTTPException(404, "Site not found")
    with open(path) as f:
        return f.read()

handler = Mangum(app, lifespan="off")
