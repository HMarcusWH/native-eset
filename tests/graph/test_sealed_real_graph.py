"""Opt-in private full-graph cold replay. CI does not fetch Drive/need credentials."""
import os
from pathlib import Path
import pytest
from native_eset.graph.snapshot import GraphSnapshot
from native_eset.graph.resolver_adapter import run_pinned_resolver,authorize_physical_output,UnauthorizedPhysicalOutput

REPO=Path(__file__).resolve().parents[2]


@pytest.mark.skipif(not os.environ.get('ESET_SNAPSHOT_DIR'),reason='sealed graph not bundled into public/bootstrap releases')
def test_real_sealed_exact_source_and_resolver():
    snap=GraphSnapshot.load(os.environ['ESET_SNAPSHOT_DIR'],REPO/'config/graph_snapshot.lock.json',
                            vocabulary_file=REPO/'src/native_eset/graph/vocabulary_v0_7_2.json')
    assert snap.graph_sha256=='163de068decc50d5339daa0a3fa4d38441f2441bf414a3131267ea02b312bc31'
    assert len(snap.nodes)+len(snap.relations)==7030 and len(snap.relations)==3003
    r=run_pinned_resolver(snap)
    assert len(r.partitions)==219 and len(r.summaries)==202
    good=authorize_physical_output(r,'eset:provider:bg8-current-bbn-composition-v0.1',
                                   'Y_p','CURRENT_BG8_BBN_COMPOSITION_OUTPUTS_ONLY')
    assert good['claim_boundary']=='SCOPED_PROVIDED_OUTPUT_ONLY_NOT_VALIDATED_OR_PRODUCTION_SCORING'
    with pytest.raises(UnauthorizedPhysicalOutput):
        authorize_physical_output(r,'eset:provider:bg8-current-bbn-composition-v0.1',
                                  'CMB_TT','CURRENT_BG8_BBN_COMPOSITION_OUTPUTS_ONLY')
    with pytest.raises(UnauthorizedPhysicalOutput):
        authorize_physical_output(r,'eset:provider:bg8-current-bbn-composition-v0.1',
                                  'Y_p','ALL_COSMOLOGY')


@pytest.mark.skipif(not os.environ.get('ESET_SNAPSHOT_DIR'),reason='sealed graph deliberately external')
def test_actual_p1r_scope_and_constructed_result_tamper():
    from native_eset.graph.resolver_adapter import VerifiedResolver
    snap=GraphSnapshot.load(os.environ['ESET_SNAPSHOT_DIR'],REPO/'config/graph_snapshot.lock.json')
    actual=run_pinned_resolver(snap)
    provider='eset:provider:current-t1r-t3r-p1r-narrow-background-v0.1'
    good=authorize_physical_output(actual,provider,'H_z_background_table','CURRENT_V1_7_2_T1R_T3R_P1R_NARROW_BACKGROUND_V0_1')
    assert good['provider_scope']=='CURRENT_V1_7_2_T1R_T3R_P1R_NARROW_BACKGROUND_V0_1'
    changed=list(actual.partitions)
    changed[0]={**changed[0],'resolved_state':'VALIDATED'}
    forged=VerifiedResolver(snap,changed,actual.summaries,actual.audit)
    with pytest.raises(UnauthorizedPhysicalOutput):
        authorize_physical_output(forged,provider,'H_z_background_table','CURRENT_V1_7_2_T1R_T3R_P1R_NARROW_BACKGROUND_V0_1')
    with pytest.raises(UnauthorizedPhysicalOutput):
        authorize_physical_output(actual,provider,'CMB_TT','CURRENT_V1_7_2_T1R_T3R_P1R_NARROW_BACKGROUND_V0_1')
