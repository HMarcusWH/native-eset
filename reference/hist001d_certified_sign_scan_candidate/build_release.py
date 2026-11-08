"""Build reproducible source-only distribution; no protected parent archives."""
from __future__ import annotations
import hashlib, json, os, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'HIST001D_CERTIFIED_BINARY64_SIGN_SCANNER_SOURCE_ONLY_v0_1_2026_11_07.zip'
INVENTORY=ROOT/'MANIFEST_SHA256.json'

def main():
    files=sorted(p for p in ROOT.iterdir() if p.is_file() and p.name!='MANIFEST_SHA256.json')
    if not files or any('SOURCE_BOUND' in p.name for p in files):
        raise SystemExit('REJECT_UNSAFE_INVENTORY')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    manifest={'schema':'HIST001D_SOURCE_ONLY_RELEASE_SHA256_MANIFEST_V1',
              'scope':'SOURCE_ONLY_NONPROMOTING_NO_PROTECTED_ARRAYS',
              'file_count':len(hashes),'files':hashes}
    INVENTORY.write_text(json.dumps(manifest,sort_keys=True,indent=2,ensure_ascii=True)+'\n',encoding='ascii')
    entries=sorted([*files,INVENTORY],key=lambda p:p.name)
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in entries:
            zi=zipfile.ZipInfo('hist001d_certified_sign_scan_v0_1/'+p.name)
            zi.date_time=(2026,11,7,0,0,0)
            zi.compress_type=zipfile.ZIP_DEFLATED
            zi.external_attr=0o100644<<16
            z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print(json.dumps({'archive':str(OUT),'size':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
                      'members':len(entries),'manifest_files':len(hashes)},indent=2))
if __name__=='__main__':main()
