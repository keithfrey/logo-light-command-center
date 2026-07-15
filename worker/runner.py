import os, json, time, requests
from bs4 import BeautifulSoup
from common import init_db, event, start_run, finish_run, R

URL=os.environ.get("LOGO_LIGHT_URL","https://logolightstore.com/")
init_db()
event("SYSTEM","Agent worker started")

def watchtower():
    rid=start_run("Watchtower","Check Logo Light homepage availability")
    started=time.time()
    try:
        r=requests.get(URL,timeout=25,headers={"User-Agent":"LogoLight-Watchtower/0.1"})
        ms=int((time.time()-started)*1000)
        soup=BeautifulSoup(r.text,"html.parser")
        title=soup.title.get_text(" ",strip=True) if soup.title else "No title"
        result=f"HTTP {r.status_code}; {ms} ms; title: {title[:100]}"
        finish_run(rid,result,"Complete" if r.ok else "Alert")
        event("WATCHTOWER",result)
    except Exception as e:
        finish_run(rid,str(e),"Failed")
        event("ALERT",f"Homepage check failed: {e}")

while True:
    item=R.blpop("agent_jobs",timeout=10)
    if item:
        _,payload=item
        job=json.loads(payload)
        if job.get("type")=="watchtower_homepage":
            watchtower()
    time.sleep(1)
