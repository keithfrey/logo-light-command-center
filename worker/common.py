import os, time
import psycopg
import redis

DB=os.environ["DATABASE_URL"]
R=redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

def init_db():
    with psycopg.connect(DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS agent_runs (
          id BIGSERIAL PRIMARY KEY, agent TEXT NOT NULL, task TEXT NOT NULL,
          status TEXT NOT NULL, result TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          completed_at TIMESTAMPTZ)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS system_events (
          id BIGSERIAL PRIMARY KEY, event_type TEXT NOT NULL, message TEXT NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
        conn.commit()

def event(kind,msg):
    with psycopg.connect(DB) as conn:
        conn.execute("INSERT INTO system_events(event_type,message) VALUES (%s,%s)",(kind,msg))
        conn.commit()

def start_run(agent,task):
    with psycopg.connect(DB) as conn:
        row=conn.execute("INSERT INTO agent_runs(agent,task,status) VALUES (%s,%s,'Running') RETURNING id",(agent,task)).fetchone()
        conn.commit()
        return row[0]

def finish_run(run_id,result,status="Complete"):
    with psycopg.connect(DB) as conn:
        conn.execute("UPDATE agent_runs SET status=%s,result=%s,completed_at=NOW() WHERE id=%s",(status,result,run_id))
        conn.commit()
