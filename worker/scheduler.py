import json, time
from datetime import datetime, timezone
from common import init_db, event, R

init_db()
event("SYSTEM","Scheduler started")
last_hour=None

while True:
    now=datetime.now(timezone.utc)
    hour_key=now.strftime("%Y-%m-%dT%H")
    if hour_key!=last_hour:
        R.rpush("agent_jobs",json.dumps({"type":"watchtower_homepage","scheduled_at":now.isoformat()}))
        event("SCHEDULE","Queued hourly Watchtower homepage check")
        last_hour=hour_key
    time.sleep(20)
