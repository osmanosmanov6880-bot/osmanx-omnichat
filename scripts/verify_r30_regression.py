#!/usr/bin/env python3
"""Run every backend test module in a fresh isolated Python process.

Full-suite pytest may hang at interpreter teardown in some environments. This
runner makes teardown failures visible: a module counts only on exit code 0,
not merely because it printed 'passed'. Plugins are opt-out so global host
telemetry/coverage plugins cannot contaminate CI or local verification.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=sorted((ROOT/'backend/tests').glob('test_*.py'))


def main():
    env={**os.environ,'PYTHONPATH':str(ROOT/'backend')+os.pathsep+str(ROOT),
         'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1'}
    total=0
    problems=[]
    for path in FILES:
        cmd=[sys.executable,'-c',
            'import pytest,sys;sys.exit(pytest.main(["-q",sys.argv[1],"--disable-warnings"]))',
            str(path)]
        try:
            proc=subprocess.run(cmd,cwd=ROOT,env=env,text=True,
                                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                timeout=75)
        except subprocess.TimeoutExpired as exc:
            problems.append(f'{path.name}: exceeded 75 seconds')
            print('FAIL',path.name,'TIMEOUT',flush=True)
            continue
        match=re.search(r'(?<!\d)(\d+) passed\b',proc.stdout)
        if proc.returncode!=0 or not match:
            problems.append(f'{path.name}: code {proc.returncode}: {proc.stdout[-1500:]}')
            print('FAIL',path.name,'CODE',proc.returncode,proc.stdout[-700:],flush=True)
            continue
        count=int(match.group(1))
        total+=count
        print('PASS',path.name,count,'tests',flush=True)
    if problems:
        print('REGRESSION_INCOMPLETE',len(problems),'issues',flush=True)
        for issue in problems:print(issue,flush=True)
        return 1
    print(f'R30_ISOLATED_MODULE_REGRESSION=PASS {total} TESTS {len(FILES)} MODULES',flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
