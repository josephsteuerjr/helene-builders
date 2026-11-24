"""Assemble the native acceptance fixture from the released platform package."""
from pathlib import Path
import json, shutil, zipfile, hashlib, sys, os, platform
D=Path(__file__).resolve().parent
target=sys.argv[1]
names={'windows':'','mac-arm':'-macos-arm64','mac-intel':'-macos-x86_64','debian':'-linux-x86_64','fedora':'-fedora-x86_64','server-arm':'-server-linux-arm64'}
name='Helene-3.0.0'+names[target]+'.zip'
receipt, = [r for r in (D/'artifact').glob('*.json') if not r.stem.endswith('-native')]
row=json.loads(receipt.read_bytes())
assert row['asset']==name and row['source_commit']=='043372658d5663a373e5730b6db3f77e3835188b'
digest=row['sha256']
archive=receipt.parent/name
with archive.open('rb') as f:
    checksum=hashlib.sha256()
    for chunk in iter(lambda:f.read(1<<20),b''): checksum.update(chunk)
assert checksum.hexdigest()==digest
root=D/'desktop'
with zipfile.ZipFile(archive) as z:
    for row in z.infolist():
        n=row.filename.removeprefix('Helene/')
        if n.startswith(('verification/','verification-tools/')) or row.is_dir(): continue
        out=root/n
        assert out.resolve().is_relative_to(root)
        out.parent.mkdir(parents=True,exist_ok=True)
        with z.open(row) as src,out.open('wb') as dst:shutil.copyfileobj(src,dst)
        if os.name!='nt':out.chmod((row.external_attr>>16)&0o777 or 0o644)
(D/'evidence'/'archive.json').write_text(json.dumps({"asset":name,"sha256":digest,"commit":row["source_commit"]}))
print(target,name,digest,platform.machine(),flush=True)
