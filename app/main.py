import os
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import FileResponse
import psycopg

DB = os.environ["DATABASE_URL"]
STATIC = Path(__file__).parent / "static"
app = FastAPI(title="Logo Light Command Center")

def init_db():
    with psycopg.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_runs (
          id BIGSERIAL PRIMARY KEY,
          agent TEXT NOT NULL,
          task TEXT NOT NULL,
          status TEXT NOT NULL,
          result TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          completed_at TIMESTAMPTZ
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS system_events (
          id BIGSERIAL PRIMARY KEY,
          event_type TEXT NOT NULL,
          message TEXT NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""")
        conn.commit()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")

@app.get("/api/status")
def status():
    with psycopg.connect(DB) as conn:
        runs = conn.execute("""
          SELECT id, agent, task, status, result, created_at, completed_at
          FROM agent_runs ORDER BY id DESC LIMIT 20
        """).fetchall()
        events = conn.execute("""
          SELECT id, event_type, message, created_at
          FROM system_events ORDER BY id DESC LIMIT 20
        """).fetchall()
    return {
      "updated_at": datetime.now(timezone.utc).isoformat(),
      "agents": [
        {"name":"Conductor","status":"Running","current_task":"Orchestrating task queue"},
        {"name":"Watchtower","status":"Running","current_task":"Website availability checks"},
        {"name":"Pulse","status":"Queued","current_task":"LinkedIn optimization package"},
        {"name":"Studio","status":"Waiting","current_task":"Visionary Vic source review"},
        {"name":"Atlas","status":"Queued","current_task":"Homepage evidence audit"},
        {"name":"Sentinel","status":"Running","current_task":"Approval and safety gate"}
      ],
      "runs":[
        {"id":r[0],"agent":r[1],"task":r[2],"status":r[3],"result":r[4],
         "created_at":r[5].isoformat() if r[5] else None,
         "completed_at":r[6].isoformat() if r[6] else None}
        for r in runs
      ],
      "events":[
        {"id":e[0],"type":e[1],"message":e[2],
         "created_at":e[3].isoformat() if e[3] else None}
        for e in events
      ]
    }

@app.get("/api/health")
def health():
    return {"status":"ok"}
