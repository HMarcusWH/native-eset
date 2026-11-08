"""Source-free, deliberately adversarial tests for the PR58 v1r2 attestor.

SYNTHETIC_TEST_ONLY: no original 46+3 March source, fitted arrays or
historical H residuals are used to exercise these structural requirements.
"""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[2]
SCRIPT=HERE/'reference/hist001d_upstream_bessel_candidate/attested_replay_v1r2.py'
spec=importlib.util.spec_from_file_location('hist001d_pr58_attestor_for_tests',SCRIPT)
att=importlib.util.module_from_spec(spec)
spec.loader.exec_module(att)


def make_zip(members:dict[str,bytes], manifest:dict|None=None)->bytes:
    blob=io.BytesIO()
    with zipfile.ZipFile(blob,'w',compression=zipfile.ZIP_DEFLATED) as z:
        if manifest is not None:
            z.writestr('MANIFEST_SHA256.json',json.dumps(manifest,sort_keys=True).encode())
        for path,data in members.items():z.writestr(path,data)
    return blob.getvalue()


class AttestationSourceFreeTests(unittest.TestCase):
    def test_sha_exact(self):
        self.assertEqual(att.sha(b'abc'),hashlib.sha256(b'abc').hexdigest())

    def test_digest_strict(self):
        self.assertTrue(att.valid_digest('a'*64))
        for x in ('','a'*63,'A'*64,'g'*64,None,23,True,'a'*64+'\n'):
            with self.subTest(x=x):self.assertFalse(att.valid_digest(x))

    def test_good_file_paths(self):
        for path in ('reference/a.py','inputs/sample.be64','results/finite.json','foo.txt'):
            self.assertTrue(att.safe_path(path))
        for path in ('','../source.py','a/../b','a//b','./a','/root','a\\b','a/./b','C:\\file.py','C:relative.py','CON.txt','nested/aux.log','trailing.','a/\x00null'):
            with self.subTest(path=path):self.assertFalse(att.safe_path(path))

    def test_valid_small_archive_inventory(self):
        with zipfile.ZipFile(io.BytesIO(make_zip({'a.py':b'x=1\n'}))) as z:
            self.assertEqual(att.check_member_inventory(z),('a.py',))

    def test_duplicate_zip_members_rejected(self):
        buf=io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            with zipfile.ZipFile(buf,'w') as z:
                z.writestr('a.py',b'x');z.writestr('a.py',b'y')
        with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as z:
            with self.assertRaisesRegex(ValueError,'duplicate'):
                att.check_member_inventory(z)

    def test_unsafe_member_rejected(self):
        for name in ('../../escape.py','/etc/test.py','a/./b','a//b','a\\b'):
            with self.subTest(name=name),zipfile.ZipFile(io.BytesIO(make_zip({name:b'bad'}))) as z:
                with self.assertRaises(ValueError):att.check_member_inventory(z)

    def test_symlink_rejected(self):
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            link=zipfile.ZipInfo('fake.py')
            link.create_system=3
            link.external_attr=(stat.S_IFLNK|0o777)<<16
            z.writestr(link,b'/tmp/source.py')
        with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as z:
            with self.assertRaisesRegex(ValueError,'symlink'):
                att.check_member_inventory(z)

    def test_directory_member_rejected(self):
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('source/',b'')
        with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as z:
            with self.assertRaises(ValueError):
                att.check_member_inventory(z)

    def test_casefold_alias_collision_rejected_on_all_platforms(self):
        with zipfile.ZipFile(io.BytesIO(make_zip({'proof.py':b'safe', 'PROOF.py':b'fake'}))) as z:
            with self.assertRaisesRegex(ValueError,'alias'):
                att.check_member_inventory(z)

    def test_symlinked_extracted_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'real';out.mkdir()
            link=Path(tmp)/'alias'
            try:link.symlink_to(out,target_is_directory=True)
            except (NotImplementedError,OSError):self.skipTest('symlink unavailable')
            with self.assertRaisesRegex(ValueError,'symlinked'):
                att.verify_extracted(Path(tmp)/'inert.zip',link,{'files':{}},True)

    def test_unpacked_size_budget(self):
        with zipfile.ZipFile(io.BytesIO(make_zip({'source.py':b'12345'}))) as z:
            with patch.object(att,'MAX_DECOMPRESSED',4):
                with self.assertRaisesRegex(ValueError,'budget'):
                    att.check_member_inventory(z)

    def test_member_count_budget(self):
        with zipfile.ZipFile(io.BytesIO(make_zip({'a':b'1','b':b'2'}))) as z:
            with patch.object(att,'MAX_MEMBERS',1):
                with self.assertRaisesRegex(ValueError,'budget'):
                    att.check_member_inventory(z)

    def test_verify_requires_external_whole_zip_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fixture.zip';p.write_bytes(make_zip({'source.py':b'original'}))
            for hashval in (None,'', 'not-a-hash','a'*63):
                with self.subTest(hashval=hashval):
                    with self.assertRaises(ValueError):att.verify_release(p,hashval)

    def test_self_rehashed_zip_cannot_override_external_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'rehashed.zip'
            files={'checker.py':b'pass\n'}
            manifest={'schema':att.SCHEMA,'release_version':'v1r2','files':{'checker.py':att.sha(files['checker.py'])}}
            raw=make_zip(files,manifest);p.write_bytes(raw)
            p2=Path(tmp)/'mutated.zip'; files['checker.py']=b'print("forged proof")\n'
            manifest['files']['checker.py']=att.sha(files['checker.py'])
            p2.write_bytes(make_zip(files,manifest))
            with self.assertRaisesRegex(ValueError,'pinned full ZIP SHA'):
                att.verify_release(p2,att.sha(raw))

    def test_wrong_claim_never_passes_with_self_rehash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'self-signed.zip'
            manifest={'schema':att.SCHEMA,'release_version':'v1r2','files':{},
                      'physical_provider_admitted':True}
            data=make_zip({},manifest);p.write_bytes(data)
            with self.assertRaises(ValueError):att.verify_release(p,att.sha(data))

    def test_invalid_source_manifest_not_enough(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'small.zip'
            manifest={'schema':att.SCHEMA,'release_version':'v1r2','files':{},
                      'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
                      'scientific_authority_promoted':False,
                      'claim_status':'SOURCE_CONDITIONAL_MATHEMATICAL_NONPROMOTING',
                      'source_original_46plus3_sha256':att.SOURCE_SHA,
                      'input_saturation_sha256':att.SAT_SHA,'source_execution_attested':True}
            b=make_zip({},manifest);p.write_bytes(b)
            with self.assertRaisesRegex(ValueError,'incomplete'):
                att.verify_release(p,att.sha(b))

    def test_local_executable_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'root';root.mkdir();archive=Path(tmp)/'zip.zip'
            data={'a.py':b'print("safe")\n'}
            b=make_zip(data,{'schema':att.SCHEMA,'files':{'a.py':att.sha(data['a.py'])}})
            archive.write_bytes(b); (root/'a.py').write_bytes(b'print("fake")\n')
            with zipfile.ZipFile(archive) as z:(root/'MANIFEST_SHA256.json').write_bytes(z.read('MANIFEST_SHA256.json'))
            with self.assertRaisesRegex(ValueError,'local executable'):
                att.verify_extracted(archive,root,{'files':{'a.py':att.sha(data['a.py'])}},True)

    def test_local_manifest_rehash_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'root';root.mkdir();archive=Path(tmp)/'zip.zip'
            data={'a.py':b'print("safe")\n'}
            b=make_zip(data,{'schema':att.SCHEMA,'files':{'a.py':att.sha(data['a.py'])}})
            archive.write_bytes(b); (root/'a.py').write_bytes(data['a.py'])
            (root/'MANIFEST_SHA256.json').write_text('{"forged":true}')
            with self.assertRaisesRegex(ValueError,'local manifest'):
                att.verify_extracted(archive,root,{'files':{'a.py':att.sha(data['a.py'])}},True)

    def test_local_extra_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'root';root.mkdir();archive=Path(tmp)/'zip.zip'
            data={'a.py':b'print("safe")\n'}
            b=make_zip(data,{'schema':att.SCHEMA,'files':{'a.py':att.sha(data['a.py'])}})
            archive.write_bytes(b); (root/'a.py').write_bytes(data['a.py'])
            (root/'bad.py').write_bytes(b'bad')
            with zipfile.ZipFile(archive) as z:(root/'MANIFEST_SHA256.json').write_bytes(z.read('MANIFEST_SHA256.json'))
            with self.assertRaisesRegex(ValueError,'missing/extra'):
                att.verify_extracted(archive,root,{'files':{'a.py':att.sha(data['a.py'])}},True)

    def test_local_symlink_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'root';root.mkdir();archive=Path(tmp)/'zip.zip'
            data={'a.py':b'print("safe")\n'}
            b=make_zip(data,{'schema':att.SCHEMA,'files':{'a.py':att.sha(data['a.py'])}})
            archive.write_bytes(b)
            target=Path(tmp)/'outside.py';target.write_bytes(data['a.py'])
            try:(root/'a.py').symlink_to(target)
            except (NotImplementedError,OSError):self.skipTest('symlink creation not permitted')
            with zipfile.ZipFile(archive) as z:(root/'MANIFEST_SHA256.json').write_bytes(z.read('MANIFEST_SHA256.json'))
            with self.assertRaisesRegex(ValueError,'redirected'):
                att.verify_extracted(archive,root,{'files':{'a.py':att.sha(data['a.py'])}},True)

    def test_scoped_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'budget'):
            att.replay(Path('/missing.zip'),'a'*64,budget_seconds=0)

    def test_cli_missing_pin_exit_2_under_optimized_python(self):
        for opt in ('-O','-OO'):
            with self.subTest(opt=opt):
                p=subprocess.run([sys.executable,opt,str(SCRIPT)],capture_output=True,text=True)
                self.assertEqual(p.returncode,2)
                self.assertIn('UNRESOLVED',p.stdout)

    def test_cli_invalid_budget_exit_2(self):
        p=subprocess.run([sys.executable,'-OO',str(SCRIPT),'--archive','/none','--expected-sha256','a'*64,'--budget-seconds','0'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertIn('UNRESOLVED',p.stdout)

    def test_wrapper_no_unpinned_positive_output(self):
        p=subprocess.run([sys.executable,'-OO',str(SCRIPT.with_name('verify_release.py')),'--root','/tmp','--full'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertIn('UNRESOLVED',p.stdout)

    def test_no_unpinned_success_through_disabled_asserts(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake=Path(tmp)/'fake.zip';fake.write_bytes(b'not even a ZIP')
            for opt in ('-O','-OO'):
                p=subprocess.run([sys.executable,opt,str(SCRIPT),'--archive',str(fake),'--expected-sha256','a'*64],capture_output=True,text=True)
                self.assertEqual(p.returncode,2)
                self.assertIn('UNRESOLVED',p.stdout)


if __name__=='__main__':unittest.main()
