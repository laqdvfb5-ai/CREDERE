"""Export both the timed talk and its hidden appendix into the shared PDF."""
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
profile=(Path.home()/'.credere'/'lo-presentation-profile').as_uri()
out=HERE/'render'/'15p'
out.mkdir(parents=True,exist_ok=True)
options='pdf:impress_pdf_Export:'+json.dumps({'ExportHiddenSlides':{'type':'boolean','value':'true'}},separators=(',',':'))
args=['C:/Program Files/LibreOffice/program/soffice.exe',f'-env:UserInstallation={profile}',
      '--headless','--convert-to',options,'--outdir',str(out),str(HERE/'Credere_15_phut_day_du.pptx')]
startup=subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow=0
result=subprocess.run(args,startupinfo=startup,capture_output=True,timeout=60)
if result.returncode:
    print(result.stderr.decode('utf-8','replace'))
sys.exit(result.returncode)
