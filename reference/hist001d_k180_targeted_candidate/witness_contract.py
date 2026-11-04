"""Source-free fail-closed CONTRACT for selected-M* targeted quadrature sign witnesses.

This verifies identities, outward bounds, strict endpoint signs, and distinct
IVT brackets. It does NOT independently rederive Bessel intervals, and cannot
replace the separate verify_targeted.py exact-Fraction source-dependent audit.
"""
from fractions import Fraction as F

SCHEMA = 'HIST001D_SELECTED_MSTAR_TARGETED_PEANO_SIGN_REVERSALS_V1'
SOURCE = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PARENT = '639ee5973a59a63c14e63d59522c03d659de10dd6d7c195586de13e8186159c9'
INTER = '63c4df7dcc4e5493fe9e2ea667ebb1a7d8ec418a8d03400096eb5fedf53d4691'
LENSES = ('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
INDICES = ((0,89,118,128),(0,61,128),(0,61,93,128),(0,92,114,128),(0,53,119,128),(0,83,107,128))
EXPECTED_MIN_ZEROS = (1,2,3,1,2,1)

def floor(x):
    return x.numerator // x.denominator

def ceil(x):
    return -((-x.numerator) // x.denominator)

def require(test, label):
    if not test:
        raise ValueError(label)

def span(values):
    require(type(values) is list and len(values)==2, 'invalid interval shape')
    lo,hi=F(values[0]),F(values[1])
    require(lo<=hi, 'reversed interval')
    return lo,hi

def validate_receipt(d, j):
    require(type(j) is int and 0<=j<6, 'lens index')
    require(d.get('schema')==SCHEMA, 'wrong schema')
    require(d.get('lens')==LENSES[j], 'wrong lens identity')
    require(d.get('source_46plus3_sha256')==SOURCE and d.get('protected_cancel_parent_sha256')==PARENT
            and d.get('protected_inter_node_parent_sha256')==INTER, 'wrong source provenance')
    require(type(d.get('source_node_sha256')) is str and len(d['source_node_sha256'])==64,
            'missing frozen node provenance')
    require(type(d.get('parent_signed_lens_sha256')) is str and len(d['parent_signed_lens_sha256'])==64,
            'missing signed parent provenance')
    require(d.get('physical_provider_admitted') is False and d.get('empirical_validation')=='NOT_ESTABLISHED'
            and d.get('Einstein_residual_root_count_certified') is False
            and d.get('selected_smooth_quadrature_one_sign') is False
            and d.get('all_sign_definite_whole_band') is False
            and d.get('mathematical_scope')=='SELECTED_ACCELERATION_EQUIVALENT_MSTAR_ONLY', 'claim promotion')
    require(d.get('positive_radial_Mstarprime_everywhere') is True, 'radial source scope')
    for key in ('global_selected_smooth_root_uniqueness_proved', 'physical_shadow_source_admitted',
                'blind_D3D4_validated', 'original_March_offgrid_H_proved',
                'quadrature_zero_uniqueness_proved', 'external_peer_review_passed'):
        require(d.get(key) is not True, 'forbidden promotion claim '+key)
    lo,hi=span(d['A_band'])
    require(0<lo<hi,'invalid positive aperture band')
    require(type(d.get('initial_radial_panels')) is int and d['initial_radial_panels']>=179, 'radial panel count')
    require(d.get('added_integral_Bessel_midpoints')==128 and
            d.get('refined_radial_panels')==d['initial_radial_panels']+128,
            'refinement count')
    require(len(d['split_history'])==128 and len(d['leaves'])==d['refined_radial_panels'],
            'split/leaf count')
    mids=set()
    for s in d['split_history']:
        require(type(s['origin']) is int and 0<=s['origin']<d['initial_radial_panels'], 'split origin')
        a,b,m=F(s['a']),F(s['b']),F(s['mid'])
        require(0<a<m<b and m==(a+b)/2 and type(s['depth']) is int and s['depth']>=1,
                'noncanonical midpoint')
        require(m not in mids, 'duplicate new Bessel point')
        mids.add(m)
        for field in ('F','Fp','M','Mp'):
            v0,v1=span(s[field])
            if field in ('F','M','Mp'):
                require(v0>0, 'nonpositive new midpoint')
            else:
                require(v1<0, 'nonnegative Fprime')
    leaf_keys=set()
    for t in d['leaves']:
        require(type(t['origin']) is int and 0<=t['origin']<d['initial_radial_panels']
                and type(t['depth']) is int and t['depth']>=0, 'leaf identity')
        a,b=F(t['a']),F(t['b'])
        require(0<a<b, 'radial leaf geometry')
        key=(t['origin'],a,b,t['depth'])
        require(key not in leaf_keys,'duplicate leaf')
        leaf_keys.add(key)
        require(type(t['C_integer_Msecond_abs']) is int and t['C_integer_Msecond_abs']>=0,
                'invalid curvature ceiling')
        ll,uu=span(t['signed_Msecond'])
        require(max(-ll,uu)<=t['C_integer_Msecond_abs'],'curvature ceiling understated')
        require(F(t['positive_Mprime_lower'])>0, 'nonpositive real-radial derivative')
        require(F(t['W_upper'])>=0, 'negative Peano kernel mass')
    # Coverage and derivative/curvature validity require the separate full
    # source-dependent independent exact-Fraction verifier.
    E=F(d['E_symmetric_exact'])
    require(0<E<=d['E_symmetric_ceiling_integer_Msun'] and
            d['E_symmetric_ceiling_integer_Msun']<d['inherited_prior_symmetric_ceiling_integer_Msun'],
            'symmetric Peano reduction')
    anchors=d['anchors']
    require([x['index'] for x in anchors]==list(INDICES[j]),'missing/duplicate/wrong aperture anchors')
    last=None;zeros=[]
    for x in anchors:
        idx=x['index']
        A=lo+(hi-lo)*F(idx,128)
        require(F(x['A'])==A, 'wrong exact aperture')
        qlo,qhi=span(x['Q']);plo,phi=span(x['Lrefined']);dlo,dhi=span(x['signed_D'])
        require(dlo==qlo-phi-E and dhi==qhi-plo+E, 'signed difference not outward')
        require(type(x['integer_D']) is list and len(x['integer_D'])==2 and
                type(x['integer_D'][0]) is int and type(x['integer_D'][1]) is int and
                x['integer_D'][0]<=floor(dlo) and x['integer_D'][1]>=ceil(dhi),
                'integer outward interval understated')
        correct_sign=1 if dlo>0 else (-1 if dhi<0 else 0)
        require(x['strict_sign']==correct_sign and correct_sign!=0, 'false strict sign')
        if last and correct_sign!=last['strict_sign']:
            zeros.append({'left_index':last['index'],'right_index':idx,
                          'A_left':last['A'],'A_right':x['A'],
                          'left_sign':last['strict_sign'],'right_sign':correct_sign})
        last=x
    require(zeros==d['certified_zero_intervals'] and len(zeros)>=EXPECTED_MIN_ZEROS[j] and
            d['certified_distinct_zero_lower_bound']==len(zeros), 'false zero-existence count')
    # Independent small QA: ensure each interval is nonoverlapping, and the
    # signs differ at its strictly nonzero endpoints.
    for i,z in enumerate(zeros):
        require(F(z['A_left'])<F(z['A_right']), 'degenerate zero interval')
        if i:
            require(F(zeros[i-1]['A_right'])<=F(z['A_left']), 'overlapping distinct zeros')
    return {'lens':LENSES[j],'zeros_at_least':len(zeros),
            'Peano_ceil_Msun':d['E_symmetric_ceiling_integer_Msun'],
            'prior_Peano_ceil_Msun':d['inherited_prior_symmetric_ceiling_integer_Msun'],
            'refined_radial_panels':len(d['leaves']), 'anchors':len(anchors)}
