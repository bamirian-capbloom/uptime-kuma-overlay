"""Failure-safety tests against real small repositories, with no network or packages."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('overlay', Path(__file__).resolve().parents[1] / 'scripts/apply.py')
overlay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overlay)


class ReplaySafety(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.source = self.root / 'source'
        self.source.mkdir()
        self.run_git('init', '-q')
        self.run_git('config', 'user.name', 'Fixture')
        self.run_git('config', 'user.email', 'fixture@localhost')
        (self.source / 'file.txt').write_text('original\n')
        self.run_git('add', '.')
        self.run_git('commit', '-qm', 'base')
        base = self.run_git('rev-parse', 'HEAD')
        before = self.run_git('rev-parse', 'HEAD^{tree}')
        (self.source / 'file.txt').write_text('custom\n')
        self.run_git('add', '.')
        after = self.run_git('write-tree')
        patch = subprocess.check_output(['git', '-C', str(self.source), 'diff', '--cached', '--binary', '--full-index'])
        # Leave the source dirty to prove source working state is not touched/copied.
        (self.source / 'file.txt').write_text('private uncommitted content\n')
        self.bundle = self.root / 'bundle'
        self.bundle.mkdir()
        (self.bundle / 'change.patch').write_bytes(patch)
        (self.bundle / 'unit.md').write_text('Fixture documentation')
        self.module = {'id': 'fixture', 'requires': [], 'baseline': base, 'patches': [
            {'id': '0001', 'file': 'change.patch', 'documentation': 'unit.md',
             'sha256': hashlib.sha256(patch).hexdigest(), 'requires': [],
             'before_tree': before, 'after_tree': after}]}
        self.manifest = {'format_version': 1, 'upstream': {'commit': base, 'tree': before},
                         'reference': {'tree': after}, 'default_features': ['fixture'],
                         'features': [{'id': 'fixture', 'manifest': 'feature.json', 'sha256': ''}]}
        self.save()
        previous = overlay.ROOT
        overlay.ROOT = self.bundle
        self.addCleanup(setattr, overlay, 'ROOT', previous)
        self.dest = self.root / 'output'

    def run_git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.source), *args]).decode().strip()

    def save(self):
        data = json.dumps(self.module).encode()
        (self.bundle / 'feature.json').write_bytes(data)
        self.manifest['features'][0]['sha256'] = hashlib.sha256(data).hexdigest()
        (self.bundle / 'manifest.json').write_text(json.dumps(self.manifest))

    def assert_clean_failure(self):
        with self.assertRaises((ValueError, subprocess.CalledProcessError)):
            overlay.apply(str(self.source), self.dest)
        self.assertFalse(self.dest.exists())
        self.assertEqual(list(self.root.glob('.overlay-*')), [])
        self.assertEqual((self.source / 'file.txt').read_text(), 'private uncommitted content\n')

    def test_exact_replay_and_dirty_source_preserved(self):
        overlay.apply(str(self.source), self.dest)
        self.assertEqual((self.dest / 'file.txt').read_text(), 'custom\n')
        self.assertEqual((self.source / 'file.txt').read_text(), 'private uncommitted content\n')
        self.assertEqual(overlay.git(self.dest, 'status', '--porcelain'), '')
        self.assertEqual(overlay.git(self.dest, 'rev-parse', 'HEAD^{tree}'), self.manifest['reference']['tree'])

    def test_existing_destination_and_symlink_preserved(self):
        self.dest.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(ValueError):
            overlay.apply(str(self.source), self.dest)
        self.assertTrue(self.dest.is_symlink())

    def test_patch_corruption_rejected(self):
        (self.bundle / 'change.patch').write_text('corrupted')
        self.assert_clean_failure()

    def test_feature_manifest_corruption_rejected(self):
        (self.bundle / 'feature.json').write_text('{}')
        self.assert_clean_failure()

    def test_conflict_leaves_no_output(self):
        path = self.bundle / 'change.patch'
        path.write_bytes(path.read_bytes().replace(b'-original', b'-does-not-match'))
        self.module['patches'][0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.save()
        self.assert_clean_failure()

    def test_wrong_output_tree_rejected(self):
        self.module['patches'][0]['after_tree'] = self.module['patches'][0]['before_tree']
        self.manifest['reference']['tree'] = self.module['patches'][0]['before_tree']
        self.save()
        self.assert_clean_failure()

    def test_missing_pin_rejected(self):
        self.manifest['upstream']['commit'] = '0' * 40
        self.module['baseline'] = '0' * 40
        self.save()
        self.assert_clean_failure()

    def test_missing_dependency_and_cycle_rejected(self):
        self.module['requires'] = ['absent']
        self.save()
        self.assert_clean_failure()
        self.module['requires'] = ['fixture']
        self.save()
        self.assert_clean_failure()

    def test_unknown_and_duplicate_selection_rejected(self):
        for selected in [['absent'], ['fixture', 'fixture'], []]:
            with self.assertRaises(ValueError):
                overlay.load_plan(selected)

    def test_document_path_escape_rejected(self):
        self.module['patches'][0]['documentation'] = '../outside.md'
        (self.root / 'outside.md').write_text('outside')
        self.save()
        self.assert_clean_failure()

    def test_wrong_base_tree_rejected(self):
        self.manifest['upstream']['tree'] = '0' * 40
        self.module['patches'][0]['before_tree'] = '0' * 40
        self.save()
        self.assert_clean_failure()


if __name__ == '__main__':
    unittest.main()
