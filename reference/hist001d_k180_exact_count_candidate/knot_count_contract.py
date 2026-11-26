"""Fail-closed structural claims for exact sixteen selected-Mstar quadrature zeros.

This schema guard checks geometry, signs, coverage and claim flags. It does not
re-evaluate the Bessel/Peano arithmetic; independent_knot_verify.py does that.
"""
from __future__ import annotations
from fractions import Fraction as F
EXPECTED=('J0822+1828','J0915+4211','J0930+2855',
          'J1021+2028','J1111+2234','J1135+3720')
COUNTS=(3,2,3,3,2,3)
ORIGINAL_SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PARENT_SHA='23251d6c5a153e8cb149143f7fcf25f02c21097e6f625b3c46fdb9645fef96e1'

def fail(code):raise ValueError(code)
def needs(cond,code):
    if not cond:fail(code)
def signed(lo,hi):
    if F(lo)>F(hi):fail('invalid interval')
    return 1 if F(lo)>0 else -1 if F(hi)<0 else 0

def covers(spans,left,right,label):
    needs(bool(spans),'empty '+label)
    arr=sorted((F(a),F(b)) for a,b in spans)
    needs(arr[0][0]==F(left) and arr[-1][1]==F(right),label+' endpoints')
    needs(all(a<b for a,b in arr),label+' collapsed')
    needs(all(x[1]==y[0] for x,y in zip(arr,arr[1:])),label+' gaps or overlaps')

def verify_one(inp,local,exclude,independent,j):
    lens=EXPECTED[j];count=COUNTS[j]
    for z in (inp,local,exclude,independent):
        needs(z.get('lens')==lens,'lens identity')
        needs(z.get('physical_provider_admitted') is False,'physical claim')
        needs(z.get('empirical_validation')=='NOT_ESTABLISHED','empirical claim')
    needs(inp.get('schema')=='HIST001D_SOURCE_LOCKED_MSTAR_KNOT_AUDIT_INPUTS_V1','input schema')
    needs(inp.get('source_46plus3_sha256')==ORIGINAL_SOURCE_SHA and inp.get('protected_parent_sha256')==PARENT_SHA,'source SHA')
    needs(inp.get('selected_mathematical_mass_only') is True,'source scope')
    needs(inp.get('original_180_node_sha256')==local.get('original_source_node_sha256')==exclude.get('original_node_sha256'),'node chain')
    needs(local.get('schema')=='HIST001D_SELECTED_MSTAR_D_KNOT_FREE_16_LOCAL_UNIQUENESS_CANDIDATE_V1','local schema')
    needs(exclude.get('schema')=='HIST001D_SELECTED_MSTAR_D_KNOT_SAFE_SIGN_EXCLUSION_CANDIDATE_V1','exclude schema')
    needs(local.get('exact_full_band_zero_count_proved') is False and local.get('all_other_band_subintervals_excluded') is False,'local stage overclaims')
    needs(exclude.get('all_gaps_excluded') is True and exclude.get('source_all_real_selected_Mprime_positive') is True,'gap stage')
    needs(independent.get('all_real_A_band_excluded_outside_unique_brackets') is True,'independent arithmetic status')
    needs(local.get('source_mathematical_model')=='SELECTED_ACCELERATION_EQUIVALENT_MSTAR_ONLY','physical source confusion')
    A0,A1=map(F,inp['A_band']);needs(A0>0 and A0<A1,'aperture band')
    roots=local['roots'];gaps=exclude['gap_blocks'];knots=[F(k) for k in exclude['source_knots_in_band']]
    needs(len(inp['nodes'])==180 and len(inp['leaves'])>=179,'radial source cardinality')
    needs(len(roots)==local.get('certified_nonoverlapping_local_unique_zero_brackets')==count,'local root number')
    needs(len(roots)==exclude.get('exact_zero_count_with_prior_local_uniqueness')==independent.get('selected_mathematical_D_exact_zero_count')==independent.get('root_brackets'),'exact count alignment')
    needs(independent.get('lens')==lens,'independent lens')
    nodes=[F(z['r']) for z in inp['nodes']]
    needs(all(nodes[k]<nodes[k+1] for k in range(179)),'node order')
    needs([r for r in nodes if A0<r<A1]==knots,'knot index')
    allspans=[];n_deriv=0;n_gap=0;methods={'P':0,'D':0,'X':0}
    for i,root in enumerate(roots):
        a,b=F(root['a']),F(root['b']);sg=root['expected_monotone_derivative']
        needs(sg in (-1,1),'missing derivative sign')
        needs(A0<=a<b<=A1 and not any(a<r<=b for r in knots),'root crosses knot/band')
        needs(signed(*root['D_a'])==-sg and signed(*root['D_b'])==sg,'root strict endpoint sign')
        panels=root['derivative_panels']
        needs(len(panels)==root.get('accepted_panels') and len(panels)>0,'root proof panels')
        covers([(p['a'],p['b']) for p in panels],a,b,'root panels')
        for q in panels:
            needs(q['depth']>=0 and q['depth']<=16,'root dyadic depth')
            v,w=q['Dprime_lower_integer_Msun_per_kpc'],q['Dprime_upper_integer_Msun_per_kpc']
            needs(type(v) is int and type(w) is int and v<=w,'root derivative witness')
            needs((sg==1 and v>0) or (sg==-1 and w<0),'root derivative wrong sign')
        allspans.append((a,b));n_deriv+=len(panels)
    for block in gaps:
        a,b=F(block['a']),F(block['b']);sg=block['sign']
        needs(sg in (-1,1),'gap strict sign')
        pieces=block['subpanels']
        needs(len(pieces)==block.get('accepted_subpanels') and len(pieces)>0,'gap panel count')
        covers([(q['a'],q['b']) for q in pieces],a,b,'gap panels')
        for q in pieces:
            needs(q['sign']==sg,'mixed signs in gap')
            lo,hi=q['bound_integer_msun']
            needs(type(lo) is int and type(hi) is int and lo<=hi,'gap witness integer')
            needs((sg==1 and lo>0) or (sg==-1 and hi<0),'gap witness not strict')
            method=q['method']
            needs(method in ('MONOTONE_Q_L_PROJECTION','DERIVATIVE_MONOTONE','DERIVATIVE_ENVELOPE'),'unknown proof type')
            methods[{'MONOTONE_Q_L_PROJECTION':'P','DERIVATIVE_MONOTONE':'D','DERIVATIVE_ENVELOPE':'X'}[method]]+=1
        allspans.append((a,b));n_gap+=len(pieces)
    covers(allspans,A0,A1,'entire aperture band')
    needs(n_deriv==independent['derivative_panels'] and n_gap==independent['exclusion_panels'],'independent panel count')
    needs(methods==independent['proof_methods']==exclude['methods'],'independent method count')
    needs(independent['knots']==len(knots),'source knot count')
    return {'lens':lens,'exact_local_mathematical_zero_count':count,
      'derivative_panels':n_deriv,'excluded_panels':n_gap,'source_knots_in_band':len(knots)}

def verify_all(inputs,locals_,exclusions,independents):
    needs(all(len(x)==6 for x in (inputs,locals_,exclusions,independents)),'six lens arrays')
    rows=[verify_one(inputs[j],locals_[j],exclusions[j],independents[j],j) for j in range(6)]
    needs(sum(r['exact_local_mathematical_zero_count'] for r in rows)==16,'non-sixteen total')
    return rows
