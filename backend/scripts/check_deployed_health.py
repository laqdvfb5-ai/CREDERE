import sys,json,time,subprocess,re
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
import paramiko
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
root=Path("C:/Users/laqdv/OneDrive/Desktop/credere")
lines=[s.strip() for s in (root/"presentation/vps.txt").read_text(encoding="utf-8-sig").splitlines() if s.strip()]
host=next(s for s in lines if re.fullmatch(r"\d+\.\d+\.\d+\.\d+",s))
user=lines[-3];password=lines[-1]
report={"checked_at":datetime.now(timezone.utc).isoformat(),"results":[]}
def emit(k,v):
 r={"check":k,"data":v};report["results"].append(r);print(json.dumps(r,ensure_ascii=True),flush=True)
def cmd(args,timeout=20):
 try:
  p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
  return {"exit":p.returncode,"output":p.stdout.strip()[:4000],"stderr":p.stderr.strip()[:100]}
 except Exception as e:return {"error":type(e).__name__}
def public():
 emit("dns_default",cmd(["nslookup","proxyllm.store"],12))
 emit("dns_1_1_1_1",cmd(["nslookup","proxyllm.store","1.1.1.1"],12))
 paths=["/","/api/apps","/cai-dat","/api/providers","/static/vendor/tabler-1.6.0/tabler.min.css"]
 def one(path):
  results=[]
  for i in range(2 if path in ["/api/apps",paths[-1]] else 1):
   a=["curl.exe","--noproxy","*","-sS","-L","--resolve","proxyllm.store:443:"+host,"-o","NUL","--connect-timeout","8","--max-time","20","-w","%{json}","https://proxyllm.store"+path]
   p=subprocess.run(a,capture_output=True,text=True,timeout=23)
   try:
    j=json.loads(p.stdout);r={k:j.get(k) for k in ["http_code","time_connect","time_appconnect","time_starttransfer","time_total","size_download","speed_download","ssl_verify_result"]}
    r.update(exit=p.returncode,dns_override=True)
   except ValueError:r={"exit":p.returncode}
   results.append(r)
  return {"path":path,"samples":results}
 with ThreadPoolExecutor(max_workers=3) as ex:
  for f in as_completed([ex.submit(one,p) for p in paths]):emit("public_web",f.result())
REMOTE=r'''
import os,json,time,subprocess,socket,shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from collections import Counter
import httpx
def emit(k,v):print(json.dumps({"check":k,"data":v},ensure_ascii=True),flush=True)
def command(a):
 try:
  p=subprocess.run(a,capture_output=True,text=True,timeout=18)
  return {"exit":p.returncode,"output":p.stdout.strip()[:3500]}
 except Exception as e:return {"error":type(e).__name__}
mem={k:int(v.split()[0]) for k,v in (l.split(":",1) for l in Path("/proc/meminfo").read_text().splitlines())}
disk=shutil.disk_usage("/")
emit("vps_resources",{"cpus":os.cpu_count(),"load":os.getloadavg(),"ram_total_mib":round(mem["MemTotal"]/1024),"ram_available_mib":round(mem["MemAvailable"]/1024),"swap_total_mib":round(mem["SwapTotal"]/1024),"swap_free_mib":round(mem["SwapFree"]/1024),"disk_total_gib":round(disk.total/2**30,2),"disk_free_gib":round(disk.free/2**30,2)})
for service in ["credere","nginx"]:
 emit("service_"+service,command(["systemctl","show",service,"--property=ActiveState,SubState,NRestarts,MemoryCurrent,TasksCurrent,MainPID"]))
emit("listeners",command(["ss","-ltn"]))
emit("cpu_sample",command(["vmstat","1","3"]))
with httpx.Client(timeout=10,trust_env=False) as c:
 for path in ["/api/apps","/api/providers"]:
  results=[]
  for i in range(3 if path=="/api/apps" else 1):
   t=time.perf_counter();r=c.get("http://127.0.0.1:8000"+path)
   results.append({"status":r.status_code,"seconds":round(time.perf_counter()-t,4),"bytes":len(r.content)})
  emit("loopback_app",{"path":path,"samples":results})
def curl(url):
 p=subprocess.run(["curl","--noproxy","*","-sS","-L","-o","/dev/null","--connect-timeout","8","--max-time","15","-w","%{json}",url],capture_output=True,text=True,timeout=18)
 try:
  j=json.loads(p.stdout)
  return {k:j.get(k) for k in ["http_code","time_namelookup","time_connect","time_appconnect","time_starttransfer","time_total","size_download","speed_download","ssl_verify_result"]}|{"exit":p.returncode}
 except ValueError:return {"exit":p.returncode}
emit("vps_https",curl("https://proxyllm.store/api/apps"))
emit("vps_egress_5mb",curl("https://speed.cloudflare.com/__down?bytes=5000000"))
emit("tls_certificate",command(["openssl","x509","-in","/etc/letsencrypt/live/proxyllm.store/fullchain.pem","-noout","-dates","-issuer"]))
try:
 p=Path("/var/log/nginx/access.log")
 with p.open("rb") as f:
  f.seek(max(0,p.stat().st_size-400000));logs=f.read().decode("utf-8","replace").splitlines()
 counts=Counter()
 for l in logs[-1000:]:
  fields=l.split('"')
  if len(fields)>2 and fields[2].strip():counts[fields[2].split()[0]]+=1
 emit("recent_nginx_status",dict(counts))
except Exception as e:emit("recent_nginx_status",{"error":type(e).__name__})
os.environ["CREDERE_HOME"]="/opt/credere/.credere"
os.environ["CREDERE_DATA"]="/opt/credere/credere-data"
from app.config import load_env,ModelConfig
from app.llm import load_providers
env=load_env();providers,strategy=load_providers(env)
emit("providers",{"usable":[p.name for p in providers],"strategy":strategy})
def probe(p,model=None):
 t=time.perf_counter();row={"provider":p.name,"model":model,"kind":"generation_16_tokens" if model else "models_listing"}
 try:
  with httpx.Client(timeout=httpx.Timeout(40,connect=8),trust_env=False) as c:
   h={"Authorization":"Bearer "+env[p.key_env]}
   if model:r=c.post(p.url(),headers=h,json={"model":p.model_id(model),"messages":[{"role":"user","content":"Reply with exactly OK."}],"max_tokens":16})
   else:r=c.get(p.url().removesuffix("/chat/completions")+"/models",headers=h)
  row.update(status=r.status_code,seconds=round(time.perf_counter()-t,3))
  if r.status_code==200:
   b=r.json()
   if model:row.update(content_present=bool(b.get("choices",[{}])[0].get("message",{}).get("content")),returned_model=b.get("model"),usage=b.get("usage"))
   else:row["model_count"]=len(b.get("data",[]))
  else:
   b=r.text.lower()
   row["category"]="balance_or_quota" if any(w in b for w in ["balance","credit","quota"]) else "auth" if r.status_code in (401,403) else "rate_limit" if r.status_code==429 else "upstream_error"
 except Exception as e:row.update(error=type(e).__name__,seconds=round(time.perf_counter()-t,3))
 return row
with ThreadPoolExecutor(max_workers=3) as pool:
 fs=[pool.submit(probe,p) for p in providers]
 for model in dict.fromkeys([ModelConfig().master,ModelConfig().worker]):
  p=next((p for p in providers if p.model_id(model)),None)
  if p:fs.append(pool.submit(probe,p,model))
 for f in as_completed(fs):emit("upstream_check",f.result())
'''
def remote():
 ssh=paramiko.SSHClient();ssh.load_host_keys(str(Path.home()/".ssh/known_hosts"));ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
 t=time.perf_counter()
 try:
  ssh.connect(host,username=user,password=password,look_for_keys=False,allow_agent=False,timeout=10,auth_timeout=12,banner_timeout=12)
  emit("ssh",{"connected":True,"seconds":round(time.perf_counter()-t,3)})
  stdin,stdout,stderr=ssh.exec_command("/opt/credere/venv/bin/python -u -",timeout=55)
  stdin.write(REMOTE);stdin.flush();stdin.channel.shutdown_write()
  for l in stdout:
   try:r=json.loads(l);emit(r["check"],r["data"])
   except (ValueError,KeyError):emit("unparsed_remote_line",True)
  emit("remote_done",{"exit":stdout.channel.recv_exit_status(),"stderr_present":bool(stderr.read())})
 except Exception as e:emit("ssh_error",{"type":type(e).__name__,"seconds":round(time.perf_counter()-t,3)})
 finally:ssh.close()
with ThreadPoolExecutor(max_workers=2) as ex:
 for f in as_completed([ex.submit(public),ex.submit(remote)]):
  try:f.result()
  except Exception as e:emit("diagnostic_error",type(e).__name__)
out=Path.home()/".credere"/"health-checks"/datetime.now().strftime("%Y%m%d-%H%M%S")
out.mkdir(parents=True,exist_ok=True)
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("REPORT "+str(out/"report.json"),flush=True)

