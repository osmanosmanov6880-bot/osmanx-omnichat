"""Independent test processes; a printed 'passed' is not enough without exit 0."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
modules=sorted((ROOT/'backend/tests').glob('test_*.py'))
env=os.environ.copy()
env['PYTHONPATH']=str(ROOT/'backend')+os.pathsep+str(ROOT)
env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
results=[]
for module in modules:
    try:
        res=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(module)],
            cwd=ROOT,env=env,capture_output=True,text=True,timeout=90)
    except subprocess.TimeoutExpired:
        print('REGRESSION_TIMEOUT',module.name,flush=True)
        sys.exit(2)
    output=res.stdout+'\n'+res.stderr
    match=re.search(r'(\d+) passed(?:, \d+ warnings?)? in [\d.]+s',output)
    if res.returncode!=0 or not match:
        print('REGRESSION_FAILED',module.name,res.returncode,output[-2500:],flush=True)
        sys.exit(1)
    count=int(match.group(1))
    results.append({'module':module.name,'passed':count,'exit_code':res.returncode})
    print('PASS',module.name,count,'TOTAL',sum(x['passed'] for x in results),flush=True)
record={'release':'R35','modules':len(results),'passed':sum(x['passed'] for x in results),
        'failures':0,'runs':results,'executed_at_utc':datetime.now(timezone.utc).isoformat()}
(ROOT/'docs/qa_r35_module_results.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('R35_ALL_MODULES_PASS',record['modules'],record['passed'],flush=True)
