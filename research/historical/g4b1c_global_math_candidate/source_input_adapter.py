#!/usr/bin/env python3
"""LOCAL candidate: fail-closed, original-source-authenticated input loader for G4b1b.

No PR39 runtime import, no GitHub original-source receipt, no H/root proof, no
admission to any physics provider.  The caller must validate the source pack
and select a registered mathematical G4b0 Leaf separately.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
import stat
import struct
import zipfile
from fractions import Fraction
from pathlib import Path

SOURCE_KIT_SHA256 = '804fd8e26b208c9837638ceee90998843e29b484aa3e5ca794dd5d81b3988973'
SOURCE_ZIP_SHA256 = '283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
SOURCE_LOCK_SHA256 = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
SOURCE_LEDGER_SHA256 = '4b5746051babaadb0ad61aa61a857ff78a61fd6ac9676cd5513d51273c597701'
DOMAIN = b'native-eset-g4b1b-exact-binary64-nodal-pairs-v1\x00'
LENS_IDS = ('J0822+1828', 'J0915+4211', 'J0930+2855', 'J1021+2028', 'J1111+2234', 'J1135+3720')
NUMERIC_KEYS = ('bulge_mass_msun', 'hernquist_a_kpc', 'disc_mass_msun', 'disc_scale_kpc', 'bulge_q', 'disc_q')
HEX_KEYS = NUMERIC_KEYS + ('z_lens', 'z_source')
MAX_ZIP_SIZE = 5_000_000

class SourceAuthorityError(ValueError):
    pass

def ensure(cond, msg):
    if not cond:
        raise SourceAuthorityError(msg)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')

def canonical_load(data: bytes):
    def pairs(items):
        out = {}
        for k, v in items:
            ensure(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    obj = json.loads(data, object_pairs_hook=pairs,
                     parse_constant=lambda v: (_ for _ in ()).throw(SourceAuthorityError('nonfinite JSON')))
    ensure(data in (canonical_json(obj), canonical_json(obj).rstrip(b'\n')), 'noncanonical JSON')
    return obj

def inventory(z: zipfile.ZipFile):
    infos = z.infolist()
    names = [x.filename for x in infos]
    ensure(len(names) == len(set(names)), 'duplicate ZIP member')
    ensure(all(not x.is_dir() and not stat.S_ISLNK(x.external_attr >> 16)
               and not x.filename.startswith('/') and '\\' not in x.filename
               and all(p not in ('', '.', '..') for p in x.filename.split('/')) for x in infos),
           'invalid ZIP member pathname or mode')
    ensure(z.testzip() is None, 'ZIP CRC failure')
    return names

def input_from_zip(kit: Path, lens_id: str | None = None):
    ensure(kit.is_file() and not kit.is_symlink(), 'source KIT missing or symlink')
    ensure(kit.stat().st_size < MAX_ZIP_SIZE, 'unexpected KIT size')
    ensure(sha(kit.read_bytes()) == SOURCE_KIT_SHA256, 'source KIT SHA mismatch')
    with zipfile.ZipFile(kit) as z:
        names = inventory(z)
        lock = canonical_load(z.read('evidence/source_lock_46plus3.json'))
        original = z.read('source/dma_swells_benchmark_pack_v2_frozen_exact.zip')
        ensure(sha(original) == SOURCE_ZIP_SHA256 == lock['source_zip_sha256'],
               'original March source nested ZIP hash changed')
        ensure(lock['original_46plus3_composite_sha256'] == SOURCE_LOCK_SHA256,
               'original 46+3 source lock declaration changed')
        ensure(len(lock['source_filenames_sha256']) == 46 and
               len(lock['archived_negative_controls_sha256']) == 3,
               '46+3 original source inventory wrong')
        with zipfile.ZipFile(io.BytesIO(original)) as src:
            nested = set(src.namelist())
            for rel, digest in lock['source_filenames_sha256'].items():
                name = 'swells_pack_v2/' + rel
                ensure(name in nested and sha(src.read(name)) == digest,
                       'original March source file changed: ' + rel)
        for name, digest in lock['archived_negative_controls_sha256'].items():
            ensure(sha(z.read('negative_controls/' + name)) == digest,
                   'original archived negative control changed: ' + name)
        raw = z.read('evidence/six_lens_nodal_provenance.json')
        ensure(sha(raw) == SOURCE_LEDGER_SHA256, 'nodal provenance ledger changed')
        ledger = canonical_load(raw)
        ensure(ledger['frozen_original_46_plus_3_source_lock_sha256'] == SOURCE_LOCK_SHA256 and
               ledger['source_zip_sha256'] == SOURCE_ZIP_SHA256 and
               ledger['lens_ids'] == list(LENS_IDS) and
               ledger['source_11520_nodal_density_total_nodes'] == 69120 and
               ledger['original_March_180x120_fitted_passes'] == 6 and
               ledger['distinct_D2d_11520_historical_joint_passes_previously_recorded'] == 3,
               'original source / fitted vs D2d model identity drift')
        ensure(len(ledger['lens_records']) == 6, 'not six source records')
        all_inputs = []
        for lid, record in zip(LENS_IDS, ledger['lens_records']):
            ensure(record['lens_id'] == lid, 'source lens record order drift')
            fname = 'nodes/' + lid.replace('+', 'p') + '.radius_density_interleaved_be64.bin'
            ensure(fname in names, 'missing six-lens source pair binary file')
            blob = z.read(fname)
            ensure(len(blob) == 16 * 11520, 'source pair binary length mismatch')
            ensure(record['nodal_pair_count'] == 11520, 'source 11520-point count drift')
            ensure(set(record['original_baryon_scales_and_q_binary64_hex']) == set(HEX_KEYS),
                   'frozen scalar key-set changed')
            scalars = {k: float.fromhex(record['original_baryon_scales_and_q_binary64_hex'][k])
                       for k in NUMERIC_KEYS}
            redshifts = [float.fromhex(record['original_baryon_scales_and_q_binary64_hex'][k])
                         for k in ('z_lens', 'z_source')]
            ensure(all(math.isfinite(v) and v > 0 for v in list(scalars.values())+redshifts)
                   and all(scalars[k] <= 1.0 for k in ('bulge_q', 'disc_q'))
                   and redshifts[0] < redshifts[1], 'invalid frozen binary64 scalar')
            radius, density = [], []
            h = hashlib.sha256()
            h.update(DOMAIN)
            h.update(struct.pack('>I', 11520))
            rsha = hashlib.sha256()
            dsha = hashlib.sha256()
            last = 0.0
            for off in range(0, len(blob), 16):
                pair = blob[off:off+16]
                r, rho = struct.unpack('>dd', pair)
                ensure(math.isfinite(r) and math.isfinite(rho) and 0 < r and r > last and rho >= 0,
                       'source radius order, density sign or finiteness failed')
                radius.append(r)
                density.append(rho)
                h.update(pair)
                rsha.update(pair[:8]);dsha.update(pair[8:])
                last=r
            ensure(Fraction.from_float(radius[0])==Fraction.from_float(0.02) and
                   Fraction.from_float(radius[-1]) == Fraction(120),
                   'frozen source domain endpoints changed')
            ensure(h.hexdigest() == record['exact_d2d_source_11520_nodal_digest'] and
                   rsha.hexdigest() == record['exact_radius_big_endian_float64_sha256'] and
                   dsha.hexdigest() == record['exact_density_big_endian_float64_sha256'],
                   'full source density / radius SHA mismatch')
            ensure(radius[0].hex() == record['nodal_radius_first_binary64_hex'] and
                   radius[-1].hex() == record['nodal_radius_last_binary64_hex'],
                   'source float hex endpoint change')
            all_inputs.append({
                'lens_id':lid,
                'baryon_scalars':scalars,
                'z_lens':redshifts[0],
                'z_source':redshifts[1],
                'radial_kpc':tuple(radius),
                'density_msun_per_kpc3':tuple(density),
                'expected_nodal_sha256':h.hexdigest(),
                'source_nodal_pair_bytes_sha256':sha(blob),
                'source_provenance_attested_by_separate_loader':True,
                'pr39_helper_itself_does_not_attest_source_provenance':True,
            })
        if lens_id is not None:
            ensure(lens_id in LENS_IDS,'not a registered frozen lens')
            return next(p for p in all_inputs if p['lens_id']==lens_id)
        return all_inputs

def witness(inputs):
    return {
      'schema':'LOCAL_HIST001D_G4B1C_ORIGINAL_SOURCE_BOUND_G4B1B_INPUT_ADAPTER_V1',
      'frozen_original_march_46_plus_3_sha256':SOURCE_LOCK_SHA256,
      'input_kit_sha256':SOURCE_KIT_SHA256,
      'input_ledger_sha256':SOURCE_LEDGER_SHA256,
      'model_identity':'D2D_STYLE_11520_FINITE_NODAL_WITH_CONTINUUM_BARYONS_NOT_ORIGINAL_180X120',
      'source_11520_nodal_count':sum(len(x['radial_kpc']) for x in inputs),
      'lens_records':[{
        'lens_id':x['lens_id'],
        'baryon_scalars_binary64_hex':{k:v.hex() for k,v in x['baryon_scalars'].items()},
        'z_lens_binary64_hex':x['z_lens'].hex(),
        'z_source_binary64_hex':x['z_source'].hex(),
        'G4b1b_expected_nodal_sha256':x['expected_nodal_sha256'],
        'source_nodal_pair_bytes_sha256':x['source_nodal_pair_bytes_sha256'],
        'source_nodes_have_external_original_source_provenance':True,
        'PR39_caller_supplied_digest_itself_does_not_authenticate_source':True,
      } for x in inputs],
      'physical_provider_admitted':False,
      'original_march_180x120_H_root_count_certified':False,
      'all_R_approximation_error_bound_certified':False,
      'root_existence_or_uniqueness_certified_by_this_adapter':False,
      'source_density_continuum_error_bounded':False,
      'empirical_validation':'NOT_ESTABLISHED',
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument('source_kit',type=Path)
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    inputs=input_from_zip(args.source_kit)
    result=canonical_json(witness(inputs))
    if args.out:
        ensure(not args.out.exists() and not args.out.is_symlink(),'destination exists/symlink')
        args.out.write_bytes(result)
    print(result.decode('utf-8'),end='')
if __name__=='__main__':
    main()
