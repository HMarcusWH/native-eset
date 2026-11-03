"""Independent source-claim guard; metadata and interval-order checks only.

Do not mistake this QA for recomputation of Bessel integrals. The full
source-only mathematical verification and protected replay are separate.
"""
from fractions import Fraction as F
from source_audit import SAT_SHA, SOURCE_SHA, LENS

def validate(reports, summary, cross):
    if not isinstance(reports,list) or len(reports)!=6:raise ValueError('six protected receipts required')
    if summary.get('schema')!='HIST001D_INDEPENDENT_K_REAL_INTEGRAL_ALL180_STENCIL_VERIFICATION_V1':raise ValueError('summary schema')
    if summary.get('original_source_46plus3_sha256')!=SOURCE_SHA or summary.get('saturation_parent_sha256')!=SAT_SHA:raise ValueError('summary source')
    if summary.get('physical_provider_admitted') is not False or summary.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('promotion claim')
    if summary.get('six_lenses_all_180_nodes') is not True or summary.get('bound_uniform_all_A_ge0') is not True:raise ValueError('scope')
    if len(summary.get('lenses',[]))!=6 or [x.get('lens_id') for x in summary['lenses']]!=LENS:raise ValueError('summary lenses')
    if cross.get('schema')!='HIST001D_BESSEL_INTEGRAL_TWO_RESOLUTIONS_AND_WRONSKIAN_V1' or cross.get('source_saturation_sha256')!=SAT_SHA or cross.get('two_grid_cross_checks')!=6:raise ValueError('cross-resolution schema/identity')
    if cross.get('physical_provider_admitted') is not False or cross.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('cross claim')
    if len(cross.get('checks',[]))!=6 or [x.get('lens_id') for x in cross['checks']]!=LENS:raise ValueError('cross lens IDs')
    for v in cross['checks']:
        if any(v.get(k) is not True for k in ('I0K1_plus_I1K0_contains_exact_inverse_y_on_both_grids','F_two_grid_intersection','Fprime_two_grid_intersection')):raise ValueError('cross mismatch')
        if v.get('two_grid_step_h')!=['1/32','1/64']:raise ValueError('cross grid changed')
    for k,item in enumerate(reports):
        if item.get('schema')!='HIST001D_INDEPENDENT_K0K1_REAL_INTEGRAL_SOURCE_CERT_V1' or item.get('engine')!='INFINITE_TRAPEZOID_STRIP_ANALYTIC_INTEGER_INTERVAL_512BITS_NO_K_BESSEL_SERIES':raise ValueError('engine/schema')
        if item.get('source_saturation_SHA256')!=SAT_SHA or item.get('source_original_46plus3_SHA256')!=SOURCE_SHA:raise ValueError('receipt source')
        if item.get('physical_provider_admitted') is not False or item.get('empirical_validation')!='NOT_ESTABLISHED' or item.get('status')!='MATHEMATICAL_SELECTED_MSTAR_ONLY_NONPROMOTING':raise ValueError('receipt claim')
        if item.get('all180_nodes_certified') is not True or item.get('all_six_lenses_in_this_receipt') is not False:raise ValueError('node scope')
        if len(item.get('lenses',[]))!=1:raise ValueError('receipt lens list')
        lens=item['lenses'][0]
        if lens.get('lens_id')!=LENS[k] or lens.get('mode')!='all' or lens.get('evaluated_nodes')!=180 or len(lens.get('nodes',[]))!=180:raise ValueError('lens node count')
        if lens.get('node_file_sha256')!=summary['lenses'][k].get('node_file_sha256'):
            raise ValueError('node ID mismatch')
        for i,n in enumerate(lens['nodes']):
            if n.get('index')!=i or not isinstance(n.get('grid_points_used'),int) or n['grid_points_used']<1 or n['grid_points_used']>1600:raise ValueError('node index/mesh')
            for field in ('selected_M_interval','selected_Mprime_interval','Bessel_F_interval','Bessel_Fprime_interval'):
                d=n.get(field)
                if not isinstance(d,list) or len(d)!=2 or F(d[0])>F(d[1]):raise ValueError('interval invalid')
            if F(n['selected_Mprime_interval'][0])<=0:raise ValueError('Mprime not strictly positive')
            if F(n.get('trapezoid_K_upper_bound','-1'))<=0 or F(n.get('tail_K_upper_bound','-1'))<0:raise ValueError('missing error budget')
            if len(n.get('old_512_source_grad_minus_Mprime_integer_msun_per_kpc',[]))!=2:raise ValueError('old comparison missing')
        row=summary['lenses'][k]
        if not isinstance(row.get('new_integral_K_all_aperture_source_to_ideal_stencil_bound_micro_Msun'),int) or row['new_integral_K_all_aperture_source_to_ideal_stencil_bound_micro_Msun']<=0:raise ValueError('bound missing')
        if row.get('new_bound_below_inherited_micro_ceiling') is not True or row['new_integral_K_all_aperture_source_to_ideal_stencil_bound_micro_Msun']>row['inherited_512_integral_source_to_ideal_stencil_bound_micro_Msun']:raise ValueError('bound hierarchy')
    return True
