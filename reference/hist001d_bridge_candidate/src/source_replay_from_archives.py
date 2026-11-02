#!/usr/bin/env python3
"""Portable exact frozen-March component replay using original 46+3 nested source.
This only reexecutes the HISTORICAL numerics and requires numpy/pandas/scipy.
"""
from __future__ import annotations
import hashlib,io,os,runpy,shutil,sys,tempfile,zipfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NODALKIT='804fd8e26b208c9837638ceee90998843e29b484aa3e5ca794dd5d81b3988973'
ORIGINAL='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
SOURCELOCK='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
TRACE='ad549d2e6aaf290a5cfeb31496928f0136191d8a05e92a1bbde6924c36610eab'

sha=lambda b: hashlib.sha256(b).hexdigest()

def main():
    with zipfile.ZipFile(ROOT/'inputs/proxy_narrow.zip') as n:
        kit=n.read('input/source_nodal.zip')
    if sha(kit)!=NODALKIT:raise RuntimeError('source kit digest drift')
    with zipfile.ZipFile(io.BytesIO(kit)) as k:
        lock=json.loads(k.read('evidence/source_lock_46plus3.json'))
        raw=k.read('source/dma_swells_benchmark_pack_v2_frozen_exact.zip')
        if sha(raw)!=ORIGINAL or lock['original_46plus3_composite_sha256']!=SOURCELOCK:
            raise RuntimeError('original source identity drift')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            if z.testzip() is not None:raise RuntimeError('original source ZIP CRC failure')
            allnames=z.namelist()
            if any(not s.startswith('swells_pack_v2/') or '..' in s.split('/') for s in allnames):raise RuntimeError('path policy')
            for path,hash_ in lock['source_filenames_sha256'].items():
                if sha(z.read('swells_pack_v2/'+path))!=hash_:raise RuntimeError('original source altered')
            if len(lock['source_filenames_sha256'])!=46:raise RuntimeError('source count')
            for name,pin in lock['archived_negative_controls_sha256'].items():
                if sha(k.read('negative_controls/'+name))!=pin:raise RuntimeError('source negative changed')
            with tempfile.TemporaryDirectory(prefix='hist001d_march_immutable_') as td:
                context=Path(td);z.extractall(context)
                with zipfile.ZipFile(ROOT/'inputs/march_180_grid.zip') as m:
                    destination=context/'sampled_binary64';destination.mkdir()
                    for name in m.namelist():
                        if name.startswith('sampled_binary64/') and name.endswith('.bin'):
                            (destination/Path(name).name).write_bytes(m.read(name))
                envkey='HIST001_ORIGINAL_SOURCE_CONTEXT'
                old=os.environ.get(envkey)
                os.environ[envkey]=str(context)
                try:
                    runpy.run_path(str(ROOT/'src/original_component_trace.py'),run_name='__main__')
                finally:
                    if old is None:os.environ.pop(envkey,None)
                    else:os.environ[envkey]=old
    if sha((ROOT/'results/original_180_component_trace.json').read_bytes())!=TRACE:
        raise RuntimeError('recomputed source component trace not byte-identical')
    print('SOURCE_COMPONENTS_REPLAY_PASS_AND_SOURCE_PINNED',TRACE)
if __name__=='__main__':main()
