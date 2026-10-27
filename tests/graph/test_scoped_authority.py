import pytest
from native_eset.gates import Admission,AdmissionError,ClaimStatus
from native_eset.graph.resolver_adapter import _evaluate_scoped_admission
from native_eset.graph.statement_contract import StatementContract,compatibility


def test_caller_claim_never_admits():
    with pytest.raises(AdmissionError):
        Admission('fake',ClaimStatus.PHYSICAL_PROVIDER_ADMITTED,('CMB_TT',),'a'*64).authorize('CMB_TT')


def test_synthetic_scoped_positive_and_negative_not_all_denied():
    provider={'type':'Provider','id':'prov','provider_admitted':True,
              'production_scoring_authorized':False,'physical_outputs_authorized':['Y_p']}
    verdict={'id':'v','type':'Verdict','subject':'prov','axis':'provider_state','value':'PROVIDER_ADMITTED',
             'scope':'BBN_ONLY','authority_refs':['auth']}
    partition={'subject':'prov','axis':'provider_state','scope':'BBN_ONLY','resolved_state':'PROVIDER_ADMITTED',
               'resolution_status':'RESOLVED','scope_quality':'EXPLICIT_OR_GLOBAL',
               'active_verdicts':['v'],'authority_basis':{'v':[{'authority':'auth'}]},'blocked_by':[]}
    physical={'subject':'prov','axis':'physical_claim_state','scope':'BBN_PRODUCTS_ONLY',
              'resolved_state':'PHYSICAL_OUTPUTS_ADMITTED_NARROW','resolution_status':'RESOLVED',
              'scope_quality':'EXPLICIT_OR_GLOBAL','active_verdicts':['vp'],'blocked_by':[]}
    def check(**overrides):
        kw={'provider':provider,'source_verdict':verdict,'partition':partition,
            'product_partition':physical,'provider_id':'prov','observable':'Y_p','scope':'BBN_ONLY'}
        kw.update(overrides)
        return _evaluate_scoped_admission(**kw)
    assert check()
    assert not check(observable='CMB_TT')
    assert not check(scope='GLOBAL')
    assert not check(partition={**partition,'blocked_by':[{'active_by_declared_state':True}]})
    assert not check(source_verdict={**verdict,'authority_refs':[]})
    assert not check(product_partition={**physical,'resolved_state':'NOT_ADMITTED'})


def test_statement_metadata_is_not_equivalence():
    kwargs={'theory_id':'NATIVE_ESET_V172','frame':'NATIVE','gauge':'COVARIANT','validity_domain':'P1R',
            'field_set':('g','chi','phi','Pi'),'quantifier_scope':'FRW','normalization':'MP_FIXED',
            'units':'1'}
    a=StatementContract('A',source_sha256='a'*64,**kwargs)
    b=StatementContract('B',source_sha256='a'*64,**kwargs)
    assert compatibility(a,b)['automatic_inheritance'] is False
    c=StatementContract('C',source_sha256='a'*64,**{**kwargs,'frame':'VARIABLE_F'})
    assert compatibility(a,c)['state']=='INCOMPATIBLE_OR_UNDERIVED_MAPPING'
