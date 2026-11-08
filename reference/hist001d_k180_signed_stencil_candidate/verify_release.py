#!/usr/bin/env python3
"""HIST001D PR59 release acceptance uses an *external* whole-ZIP SHA-256.

Historical v1 --full checked locally rewriteable files, and a forged local
independent verifier could echo the saved receipt and still PASS. Reject that
unpinned route: only the v1r2 executed-source attestor may authorize a PASS.
"""
from __future__ import annotations
import argparse,json,sys,zipfile
from pathlib import Path
from attested_replay_v1r2 import replay


def verify(archive:Path,expected_sha256:str|None=None,full:bool=True,budget_seconds:int=180)->dict:
    if not expected_sha256:
        raise ValueError('UNRESOLVED: independent whole archive SHA required; use --expected-sha256')
    return replay(archive,expected_sha256,budget_seconds=budget_seconds)


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path)
    p.add_argument('--expected-sha256')
    p.add_argument('--full',action='store_true',help='now always full source-replay; retained for historical CLI compatibility')
    p.add_argument('--budget-seconds',type=int,default=180)
    a=p.parse_args()
    try:
        if a.archive is None:raise ValueError('UNRESOLVED: archive is required')
        result=verify(a.archive,a.expected_sha256,a.full,a.budget_seconds)
    except (ValueError,TypeError,KeyError,zipfile.BadZipFile,OSError,RuntimeError,OverflowError) as exc:
        print(json.dumps({'status':'UNRESOLVED','reason':str(exc)},sort_keys=True));return 2
    print(json.dumps(result,indent=2,sort_keys=True));return 0
if __name__=='__main__':sys.exit(main())
