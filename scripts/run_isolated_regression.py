"""R34 isolated QA: one pytest process per module, bounded timeouts."""
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
MODULES=sorted((ROOT/'backend/tests').glob('test_*.py'))
ENV=os.environ.copy()
ENV['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
ENV['PYTHONPATH']=str(ROOT/'backend')+os.pathsep+str(ROOT)
TIMEOUT=int(os.getenv('QA_MODULE_TIMEOUT','90'))

def check(path):
    started=time.monotonic()
    try:
        p=subprocess.run([sys.executable,'-m','pytest','-q',str(path)],cwd=ROOT,
             env=ENV,capture_output=True,text=True,timeout=TIMEOUT)
        body=p.stdout+'\n'+p.stderr
        passed=re.search(r'(\d+) passed',body)
        count=int(passed.group(1)) if passed else 0
        return {'module':path.name,'passed':count,'exit_code':p.returncode,
                'duration_seconds':round(time.monotonic()-started,2),'tail':body[-1400:]}
    except subprocess.TimeoutExpired:
        return {'module':path.name,'passed':0,'exit_code':124,
                'duration_seconds':round(time.monotonic()-started,2),'tail':'TIMEOUT'}


def main():
    print('MODULES',len(MODULES),flush=True)
    data=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(check,mod):mod for mod in MODULES}
        for f in concurrent.futures.as_completed(futures):
            result=f.result();data.append(result)
            print('PASS' if result['exit_code']==0 else 'FAIL',
                result['module'],result['passed'],'tests',
                result['duration_seconds'],'s',flush=True)
    data.sort(key=lambda item:item['module'])
    report={'modules':len(data),'passed':sum(x['passed'] for x in data),
            'all_exit_zero':all(x['exit_code']==0 for x in data),'results':data}
    report_path=Path(os.getenv('QA_REPORT_PATH',str(ROOT/'docs/qa_r34_module_results.json')))
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('SUMMARY',report['passed'],'passed across',report['modules'],'modules',
          'all_exit_zero',report['all_exit_zero'],flush=True)
    if not report['all_exit_zero']:
        for item in data:
            if item['exit_code']!=0:print('FAILED',item['module'],item['tail'],flush=True)
        sys.exit(1)

if __name__=='__main__':main()
