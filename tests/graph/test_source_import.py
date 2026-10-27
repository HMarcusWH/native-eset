import json
from pathlib import Path
import pytest
from native_eset.sources.acquire import prepare_verified_snapshot
from native_eset.graph.snapshot import GraphIntegrityError,GraphSnapshot,canonical_graph_digest


def test_atomic_offline_acquisition(tmp_path:Path):
    src=tmp_path/'original';src.mkdir()
    entry={'id':'x','type':'TheoryFamily','name':'X'}
    blob=(json.dumps(entry)+'\n').encode()
    (src/'theories.jsonl').write_bytes(blob)
    import hashlib
    lock={'schema':'NATIVE_ESET_THEORY_STATE_GRAPH_LOCK_V1',
          'files':[{'name':'theories.jsonl','sha256':hashlib.sha256(blob).hexdigest()}],
          'file_count':1,'record_count':1,'relation_count':0,'verdict_count':0,
          'graph_sha256':canonical_graph_digest([entry]),'release_version':'TEST'}
    lp=tmp_path/'lock.json';lp.write_text(json.dumps(lock))
    dest=tmp_path/'verified'
    assert prepare_verified_snapshot(src,lp,dest)['status']=='PASS_BYTE_CHECK_ONLY'
    assert GraphSnapshot.load(dest,lp).graph_sha256==lock['graph_sha256']
    with pytest.raises(FileExistsError):prepare_verified_snapshot(src,lp,dest)
    (src/'theories.jsonl').write_text('CORRUPTED\n')
    with pytest.raises(GraphIntegrityError):prepare_verified_snapshot(src,lp,tmp_path/'failed')
    assert not (tmp_path/'failed').exists()
