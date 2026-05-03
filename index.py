from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from mangum import Mangum
import shutil, os, uuid

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED = {"image/jpeg", "image/png", "image/gif", "image/webp"}

@app.get("/", response_class=HTMLResponse)
def root():
    return """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>host.it</title></head>
<body>
  <h1>Upload working!</h1>
  <input type="file" id="f" accept="image/*">
  <button onclick="upload()">Upload</button>
  <div id="out"></div>
  <script>
    async function upload() {
      const file = document.getElementById('f').files[0];
      const form = new FormData();
      form.append('file', file);
      const res = await fetch('/upload', { method: 'POST', body: form });
      const data = await res.json();
      document.getElementById('out').textContent = JSON.stringify(data);
    }
  </script>
</body>
</html>"""

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, "Only images allowed")
    ext = file.filename.rsplit(".", 1)[-1]
    name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, name)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": name, "message": "uploaded successfully"}

@app.get("/files")
def list_files():
    if not os.path.exists(UPLOAD_DIR):
        return []
    files = []
    for fn in os.listdir(UPLOAD_DIR):
        fp = os.path.join(UPLOAD_DIR, fn)
        files.append({"filename": fn, "size": os.path.getsize(fp)})
    return files

handler = Mangum(app, lifespan="off")
