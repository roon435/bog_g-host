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

@app.get("/", response_class=HTMLResponse)
def editor():
    return open("dashboard/index.html").read()

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
    return open(path).read()

handler = Mangum(app, lifespan="off")
