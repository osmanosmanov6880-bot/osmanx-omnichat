"""Run each existing CI test group in a clean pytest interpreter.

R21-R27 combined pytest teardown can hang; independent processes are
mandatory until a separate root cause is fixed. This script never counts a
printed 'passed' as success unless the OS process itself exits with code zero.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend'/'tests'
GROUPS={
    'core': 'bot_channels claim command_center connection_confidence_v10 customer_onboarding_v06 delivery_safety extended international_ops live_readiness_v08 mvp preflight_v08 quickstart_v09',
    'history_team_recovery': 'r20_message_history r21_collaboration r22_outbox_control r23_crash_recovery',
    'reconstructed': 'recovered_v16_v18',
    'worker_security': 'v11_security v12_resilience v13_scaling v14_worker_health',
    'receipts_r24': 'r24_provider_receipts',
    'pause_r25': 'r25_emergency_pause',
    'pause_r26': 'r26_global_incident_pause',
    'sender_r27': 'r27_sender_slots',
    'backup_website_templates': 'v15_backup website whatsapp_approved_templates',
    'delivery_truth_r28': 'r28_delivery_truth',
}

def main():
    env=dict(os.environ,PYTHONPATH='backend:.')
    total=0
    for name,items in GROUPS.items():
        files=[str(BASE/f'test_{s}.py') for s in items.split()]
        cmd=[sys.executable,'-m','pytest','-q',*files]
        print('START',name,flush=True)
        try:
            result=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=80)
        except subprocess.TimeoutExpired as exc:
            print('TIMEOUT',name,exc,flush=True)
            return 1
        summary=result.stdout.strip().splitlines()[-1] if result.stdout.strip() else 'no-stdout'
        print('DONE',name,'exit='+str(result.returncode),summary,flush=True)
        if result.returncode!=0:
            print(result.stdout[-6000:],result.stderr[-4000:],flush=True)
            return result.returncode
        import re
        match=re.search(r'(\d+) passed',summary)
        if not match:
            print('FAIL NO VERIFIED PASS COUNT',name,flush=True)
            return 2
        total+=int(match.group(1))
    print('ALL_R28_GROUPS_OK',total,'EXIT_CODE_ZERO_PER_GROUP',flush=True)
    return 0
if __name__=='__main__':sys.exit(main())
