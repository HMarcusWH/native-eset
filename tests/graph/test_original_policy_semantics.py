"""Exercise original source resolver policy on synthetic records, without promotion."""
import json
import random
import subprocess
import sys
import pytest
from native_eset.graph.resolver_adapter import RESOLVER_SCRIPT, RESOLVER_POLICY


def fixture(verdicts, relations=()):
    return {'branches':[{'id':'b','type':'TheoryBranch','name':'B'}],
            'authorities':[{'id':'old','type':'Authority','name':'Old','authority_scope':['FORMAL_STATUS']},
                           {'id':'new','type':'Authority','name':'New','authority_scope':['FORMAL_STATUS']}],
            'verdicts':verdicts, 'relations':list(relations)}


def verdict(id='v', value='OPEN', scope='S', authority='old'):
    return {'id':id,'type':'Verdict','name':id,'subject':'b','axis':'formal_state','scope':scope,
            'resolution_facet':'GENERAL','value':value,'authority_refs':[authority] if authority else []}


def execute(tmp_path, files):
    graph, out = tmp_path/'graph', tmp_path/'out'
    graph.mkdir(parents=True)
    for name, rows in files.items():
        (graph/f'{name}.jsonl').write_bytes((''.join(json.dumps(x)+'\n' for x in rows)).encode())
    subprocess.run([sys.executable,'-X','utf8',str(RESOLVER_SCRIPT),'--graph-dir',str(graph),
                    '--policy',str(RESOLVER_POLICY),'--out-dir',str(out)],check=True,capture_output=True)
    audit=json.loads((out/'resolver_audit_v0_2.json').read_text(encoding='utf-8'))
    parts=[json.loads(x) for x in (out/'resolved_verdict_state_v0_2.jsonl').read_text(encoding='utf-8').splitlines()]
    return audit, parts, {p.name:p.read_bytes() for p in out.iterdir()}


@pytest.mark.parametrize('kind', ['gap','conflict','supersede','scoped','incomplete','kill'])
def test_original_policy_semantics(tmp_path,kind):
    edge={'id':'r','type':'Relation','name':'Supersession','subject':'new','predicate':'SUPERSEDES','object':'old'}
    if kind=='gap':
        a,p,_=execute(tmp_path,fixture([verdict(authority=None)]))
        assert a['authority_gaps']==1 and p[0]['resolved_state']=='AUTHORITY_GAP'
    elif kind=='conflict':
        a,p,_=execute(tmp_path,fixture([verdict(),verdict('v2','CLOSED_SCOPED',authority='new')]))
        assert a['authority_conflicts']==1 and p[0]['resolved_state']=='AUTHORITY_CONFLICT'
    elif kind=='supersede':
        a,p,_=execute(tmp_path,fixture([verdict(),verdict('v2','CLOSED_SCOPED',authority='new')],[edge]))
        assert a['authority_conflicts']==0 and p[0]['active_verdicts']==['v2']
    elif kind=='scoped':
        a,p,_=execute(tmp_path,fixture([verdict(),verdict('v2','CLOSED_SCOPED','OTHER',authority='new')],[edge]))
        assert len(p)==2 and a['scoped_set_summaries']==1
    elif kind=='incomplete':
        a,p,_=execute(tmp_path,fixture([verdict(value='PASS_SCOPED',scope=None)]))
        assert a['scope_incomplete']==1 and a['resolver_execution_status']=='FAIL_CLOSED'
    else:
        a,p,_=execute(tmp_path,fixture([verdict(value='KILLED')]))
        assert a['resolver_execution_status']=='FAIL_CLOSED'
        assert a['claim_firewall']['killed_non_finite_instances']==['v']


def test_eight_row_and_key_permutations_identical(tmp_path):
    files=fixture([verdict(),verdict('v2','OPEN',authority='new')])
    _,_,reference=execute(tmp_path/'base',files)
    for seed in range(1,9):
        rng=random.Random(seed)
        mutated={}
        for name,rows in files.items():
            copy=[]
            for row in rows:
                pairs=list(row.items()); rng.shuffle(pairs); copy.append(dict(pairs))
            rng.shuffle(copy);mutated[name]=copy
        _,_,output=execute(tmp_path/f'seed{seed}',mutated)
        assert output==reference
