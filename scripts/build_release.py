"""Package reproducible source zip without developer secrets, caches or local DBs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from hashlib import sha256
import os
import sys

project=Path(__file__).resolve().parents[1]
output=Path(sys.argv[1] if len(sys.argv)>1 else project.parent/'OSMANX_OMNICHAT_R36_INTEGRATED_R35_SOURCE.zip')
skip_dirs={'.git','.pytest_cache','.mypy_cache','.venv','node_modules','__pycache__','dist','backups'}
skip_suffixes={'.pyc','.pyo','.db','.sqlite','.sqlite3','.log','.tmp','.dump','.backup','.sql','.gz'}
skip_files={'.env','.env.local','.DS_Store','RELEASE_MANIFEST_SHA256.txt'}
files=[]
for p in project.rglob('*'):
    if not p.is_file() or any(part in skip_dirs for part in p.relative_to(project).parts):
        continue
    if p.name in skip_files or p.suffix.lower() in skip_suffixes or p.name.startswith('.env.') and p.name!='.env.example':
        continue
    files.append(p)
files.sort(key=lambda p: str(p.relative_to(project)))
manifest=['OSMANX OMNICHAT R36 integrated on R35 source: tenant fair recovery + outbound dispatch safety - SHA256 manifest','']
for p in files:
    manifest.append(sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(project).as_posix())
manifest_text='\n'.join(manifest)+'\n'
output.parent.mkdir(parents=True,exist_ok=True)
with ZipFile(output,'w',ZIP_DEFLATED,compresslevel=8) as archive:
    for p in files:
        archive.write(p,'osmanx-omnichat/'+p.relative_to(project).as_posix())
    archive.writestr('osmanx-omnichat/RELEASE_MANIFEST_SHA256.txt',manifest_text)
with ZipFile(output) as verify:
    bad=verify.testzip()
    if bad:raise RuntimeError('Archive corrupted: '+bad)
    names=verify.namelist()
    assert not any('/.env' in path and not path.endswith('/.env.example') for path in names)
    assert 'osmanx-omnichat/README.md' in names
    assert 'osmanx-omnichat/backend/app/website.py' in names
    assert 'osmanx-omnichat/frontend/public/embed.css' in names
print('RELEASE',output)
print('FILES',len(files)+1)
print('BYTES',output.stat().st_size)
print('SHA256',sha256(output.read_bytes()).hexdigest())
