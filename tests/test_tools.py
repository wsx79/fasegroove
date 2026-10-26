#!/usr/bin/env python3
"""Regression checks for sync/provenance and translation-key guards."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'common' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = load('VerifyModule')
translations = load('CheckTranslations')


class Tools(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.canonical = self.root / 'fasegroove'
        self.source = self.canonical / 'common'
        self.source.mkdir(parents=True)
        (self.source / 'a.h').write_bytes(b'first\nsecond\n')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.commit()
        self.module = self.root / 'product/ThirdParty/fasegroove-common'
        shutil.copytree(self.source, self.module)
        self.lock = self.module.with_name('fasegroove-common.lock.json')
        verify.write_lock(self.module, self.lock, self.canonical)

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.canonical), *args], check=True,
                              capture_output=True, text=True)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'Fixture')

    def test_pinned_source_and_crlf(self):
        verify.validate(self.module, self.lock, self.canonical)
        (self.module / 'a.h').write_bytes(b'first\r\nsecond\r\n')
        verify.validate(self.module, self.lock, self.canonical)

    def test_missing_added_modified_files(self):
        for kind in ['missing', 'extra', 'modified']:
            with self.subTest(kind=kind):
                shutil.rmtree(self.module)
                shutil.copytree(self.source, self.module)
                if kind == 'missing':
                    (self.module / 'a.h').unlink()
                elif kind == 'extra':
                    (self.module / 'unexpected.h').write_text('extra')
                else:
                    (self.module / 'a.h').write_text('modified')
                with self.assertRaises(ValueError):
                    verify.validate(self.module, self.lock)

    def test_forged_hashes_still_fail_canonical_check(self):
        (self.module / 'a.h').write_text('local patch')
        data = json.loads(self.lock.read_text())
        data['files'] = verify.inventory(self.module)
        self.lock.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'pinned canonical'):
            verify.validate(self.module, self.lock, self.canonical)

    def test_wrong_source_revision(self):
        data = json.loads(self.lock.read_text())
        data['revision'] = '0' * 40
        self.lock.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'pinned revision'):
            verify.validate(self.module, self.lock, self.canonical)

    def test_dirty_source_does_not_rewrite_lock(self):
        before = self.lock.read_bytes()
        (self.source / 'a.h').write_text('not committed')
        with self.assertRaisesRegex(ValueError, 'Commit common'):
            verify.write_lock(self.module, self.lock, self.canonical)
        self.assertEqual(before, self.lock.read_bytes())

    def test_default_sync_and_check_include_lead(self):
        shutil.copytree(ROOT / 'common', self.source, dirs_exist_ok=True)
        scripts = self.canonical / 'scripts'
        scripts.mkdir()
        for name in ['sync.sh', 'check.sh']:
            shutil.copy2(ROOT / 'scripts' / name, scripts / name)
        self.commit()
        products = ['piano', 'drums', 'guitar', 'arranger', 'lead']
        for name in products:
            (self.root / ('fasegroove' + name)).mkdir()
        synced = subprocess.run(['bash', str(scripts / 'sync.sh')], capture_output=True, text=True)
        self.assertEqual(synced.returncode, 0, synced.stderr)
        self.assertIn('synced fasegroovelead', synced.stdout)
        checked = subprocess.run(['bash', str(scripts / 'check.sh')], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        (self.root / 'fasegroovelead/ThirdParty/fasegroove-common/LinkClient.h').write_text('drift')
        checked = subprocess.run(['bash', str(scripts / 'check.sh')], capture_output=True, text=True)
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn('DIFFERS  fasegroovelead', checked.stdout)

    def test_catalog_duplicate_and_intentional_common_override(self):
        common = self.module / 'CommonTranslations.inc'
        row = '{ ' + ', '.join(json.dumps(v) for v in ['Key', 'IT', 'ES', 'FR', 'DE', 'PT']) + ' },\n'
        common.write_text(row)
        product = self.root / 'product'
        (product / 'Source').mkdir()
        own = product / 'Source/Translations.inc'
        own.write_text(row.replace('IT', 'Product IT'))
        cmd = [sys.executable, str(ROOT / 'common/CheckTranslations.py'), '--product', str(product)]
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        (product / 'Source/ArrangerTranslations.inc').write_text(row)
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('duplicate key', result.stderr)
        own.write_text(row + row)
        with self.assertRaisesRegex(ValueError, 'duplicate key'):
            translations.rows([own])


if __name__ == '__main__':
    unittest.main()
