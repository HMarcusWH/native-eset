import hashlib
import json
from pathlib import Path
import pytest
from native_eset.graph.snapshot import GraphSnapshot, GraphIntegrityError, canonical_graph_digest
from native_eset.graph.query import GraphQuery
from native_eset.graph.projections import closure_comparison,select_projection


def fixture(tmp_path:Path):
    root=tmp_path/"graph";root.mkdir(parents=True)
    source={
      "theories.jsonl":[
        {"id":"n:a","type":"TheoryFamily","name":"A"},
        {"id":"n:b","type":"TheoryModule","name":"B","status":"OPEN"},
        {"id":"n:c","type":"TheoryModule","name":"C","status":"CLOSED"},
      ],
      "relations.jsonl":[
        {"id":"r:ab","type":"Relation","name":"AB","subject":"n:a","predicate":"REQUIRES","object":"n:b"},
        {"id":"r:bc","type":"Relation","name":"BC","subject":"n:b","predicate":"REQUIRES","object":"n:c"},
        {"id":"r:ca","type":"Relation","name":"CA","subject":"n:c","predicate":"REQUIRES","object":"n:a"},
        {"id":"r:block","type":"Relation","name":"BB","subject":"n:b","predicate":"BLOCKS","object":"n:a"},
      ],
    }
    files=[]
    for name,rows in source.items():
        p=root/name
        p.write_text("".join(json.dumps(o,sort_keys=True)+"\n" for o in rows))
        files.append({"name":name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
    lock={"schema":"NATIVE_ESET_THEORY_STATE_GRAPH_LOCK_V1","file_count":2,
          "files":files,"record_count":7,"relation_count":4,"verdict_count":0,
          "graph_sha256":canonical_graph_digest([x for xs in source.values() for x in xs]),
          "release_version":"TEST_ONLY"}
    lp=tmp_path/"lock.json";lp.write_text(json.dumps(lock))
    return root,lp,lock


def test_load_query_cycle_and_direction(tmp_path):
    root,lock,_=fixture(tmp_path)
    s=GraphSnapshot.load(root,lock)
    q=GraphQuery(s)
    assert len(s.nodes)==3 and len(s.relations)==4
    assert len(q.reachable('n:a',['REQUIRES'],direction='out')['depths'])==2
    result=q.shortest_path('n:a','n:c',['REQUIRES'])
    assert result['edge_count']==2 and result['edges'][0]['subject']=='n:a'
    assert q.shortest_path('n:c','n:a',['REQUIRES'],direction='in')['edge_count']==2
    assert q.blockers('n:a')['blockers'][0]['blocker_declared_state']=='OPEN'
    assert q.impact('n:c')['depths']['n:a']==2
    assert 'BLOCKS' not in select_projection('SCIENTIFIC_DEPENDENCY')
    assert closure_comparison({'a','b'},{'a'})['relation']=='RIGHT_STRICT_SUBSET'
    assert q.diff(s)['modified']==[]


def test_integrity_detects_tamper_duplicate_and_missing_end(tmp_path):
    root,lock,_=fixture(tmp_path)
    p=root/'theories.jsonl'
    p.write_text(p.read_text()+'\n')
    with pytest.raises(GraphIntegrityError,match='source hash'):
        GraphSnapshot.load(root,lock)

    root2,lock2,_=fixture(tmp_path/'case2')
    lp=Path(lock2)
    with (root2/'theories.jsonl').open('a') as f:
        f.write('{"id":"n:a","type":"TheoryFamily","name":"A AGAIN"}\n')
    update_lock(root2,lp)
    with pytest.raises(GraphIntegrityError,match='duplicate graph id'):
        GraphSnapshot.load(root2,lp)

    root3,lock3,_=fixture(tmp_path/'case3')
    rel=root3/'relations.jsonl'
    raw=rel.read_text().replace('"object": "n:b"','"object": "ghost"',1)
    rel.write_text(raw)
    update_lock(root3,lock3)
    with pytest.raises(GraphIntegrityError,match='missing relation endpoint'):
        GraphSnapshot.load(root3,lock3)


def update_lock(root,lock_file):
    obj=json.loads(Path(lock_file).read_text())
    records=[]
    for item in obj['files']:
        p=root/item['name']
        item['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        records.extend(json.loads(x) for x in p.read_text().splitlines() if x.strip())
    obj['graph_sha256']=canonical_graph_digest(records)
    obj['record_count']=len(records)
    Path(lock_file).write_text(json.dumps(obj))


def test_invalid_predicate_needs_vocabulary(tmp_path):
    root,lp,_=fixture(tmp_path)
    (root/'relations.jsonl').write_text((root/'relations.jsonl').read_text().replace('"REQUIRES"','"MAKES_TRUE"'))
    update_lock(root,lp)
    vocab=tmp_path/'vocab.json'
    vocab.write_text(json.dumps({'object_types':['TheoryFamily','TheoryModule','Relation'],
                                'relation_types':['REQUIRES','BLOCKS']}))
    with pytest.raises(GraphIntegrityError,match='unknown relation predicate'):
        GraphSnapshot.load(root,lp,vocabulary_file=vocab)
