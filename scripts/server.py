#!/usr/bin/env python3
from __future__ import annotations
import os, glob, subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(APP_ROOT, "out")
LOG_DIR = os.path.join(OUT_DIR, "logs")
app = FastAPI(title="Agent Mode Dashboard", version="0.2.0")
@app.get("/reports")
def list_reports():
    reports = []
    for pat in ("reports/*.md", "reports/*.csv", "docs/*.md"):
        for p in glob.glob(os.path.join(OUT_DIR, pat)):
            reports.append(os.path.relpath(p, OUT_DIR))
    return {"reports": sorted(reports)}
@app.get("/reports/{path:path}")
def get_report(path: str):
    abspath = os.path.join(OUT_DIR, path)
    if not os.path.exists(abspath):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(abspath)
@app.get("/logs")
def list_logs():
    files = sorted(glob.glob(os.path.join(LOG_DIR, "*.log")))
    return {"logs": [os.path.basename(f) for f in files]}
@app.get("/logs/{name}")
def get_log(name: str):
    p = os.path.join(LOG_DIR, name)
    if not os.path.exists(p):
        raise HTTPException(status_code=404, detail="Log not found")
    with open(p, 'r', encoding='utf-8') as f:
        return PlainTextResponse(f.read())
@app.post("/run/{agent}")
def run_agent(agent: str):
    cmd = ["python", "-m", "scripts.agent_runner", "--agent", agent, "--verbose"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {"rc": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Runner timed out")
