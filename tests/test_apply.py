"""Failure-safety tests against real small repositories, with no network or packages."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

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

    def source_snapshot(self):
        return {str(path.relative_to(self.source)): path.read_bytes()
                for path in self.source.rglob('*') if path.is_file()}

    def test_inherited_repository_context_preserves_newer_clean_source(self):
        self.run_git('reset', '--hard', 'HEAD')
        (self.source / 'newer.txt').write_text('committed work after the pinned base\n')
        self.run_git('add', '.')
        self.run_git('commit', '-qm', 'later source revision')
        before = self.source_snapshot()
        with patch.dict(os.environ, {'GIT_DIR': str(self.source / '.git'),
                                     'GIT_WORK_TREE': str(self.source),
                                     'GIT_COMMON_DIR': str(self.source / '.git')}):
            overlay.apply(str(self.source), self.dest)
        self.assertEqual(self.source_snapshot(), before)
        self.assertTrue((self.dest / '.git').is_dir())
        self.assertEqual((self.dest / 'file.txt').read_text(), 'custom\n')
        self.assertEqual(overlay.git(self.dest, 'status', '--porcelain'), '')

    def test_inherited_external_index_cannot_affect_reference_verification(self):
        external_index = self.root / 'caller-index'
        external_index.write_bytes((self.source / '.git/index').read_bytes())
        index_before = external_index.read_bytes()
        source_before = self.source_snapshot()
        # Exercise both the driver's private alternate index and deterministic commit.
        self.manifest['intended'] = {'tree': self.manifest['reference']['tree'], 'correction_units': ['0001'],
                                     'difference_from_reference': {'files': ['file.txt']}}
        self.manifest['reference']['tree'] = self.manifest['upstream']['tree']
        self.save()
        with patch.dict(os.environ, {'GIT_INDEX_FILE': str(external_index)}):
            overlay.apply(str(self.source), self.dest)
        self.assertEqual(external_index.read_bytes(), index_before)
        self.assertEqual(self.source_snapshot(), source_before)
        self.assertEqual(overlay.git(self.dest, 'rev-parse', 'HEAD^{tree}'), self.manifest['intended']['tree'])

    def test_inherited_config_and_object_store_overrides_are_ignored(self):
        before = self.source_snapshot()
        inherited = {'GIT_OBJECT_DIRECTORY': str(self.root / 'missing-objects'),
                     'GIT_ALTERNATE_OBJECT_DIRECTORIES': str(self.root / 'missing-alternates'),
                     'GIT_SHALLOW_FILE': str(self.root / 'missing-shallow'),
                     'GIT_NAMESPACE': 'caller-namespace',
                     'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'core.worktree',
                     'GIT_CONFIG_VALUE_0': str(self.source),
                     'GIT_CONFIG_PARAMETERS': f"'core.worktree={self.source}'"}
        with patch.dict(os.environ, inherited):
            overlay.apply(str(self.source), self.dest)
        self.assertEqual(self.source_snapshot(), before)
        self.assertEqual((self.dest / 'file.txt').read_text(), 'custom\n')

    def test_failed_replay_preserves_inherited_source_and_index(self):
        external_index = self.root / 'caller-index'
        external_index.write_bytes((self.source / '.git/index').read_bytes())
        index_before = external_index.read_bytes()
        source_before = self.source_snapshot()
        file = self.bundle / 'change.patch'
        file.write_bytes(file.read_bytes().replace(b'-original', b'-does-not-match'))
        self.module['patches'][0]['sha256'] = hashlib.sha256(file.read_bytes()).hexdigest()
        self.save()
        with patch.dict(os.environ, {'GIT_DIR': str(self.source / '.git'),
                                     'GIT_WORK_TREE': str(self.source),
                                     'GIT_INDEX_FILE': str(external_index)}):
            self.assert_clean_failure()
        self.assertEqual(external_index.read_bytes(), index_before)
        self.assertEqual(self.source_snapshot(), source_before)

    def test_git_environment_covers_local_variables_and_preserves_transport(self):
        names = overlay.run_git('rev-parse', '--local-env-vars').splitlines()
        inherited = dict.fromkeys(names, 'caller-context')
        inherited.update({'GIT_CONFIG_KEY_0': 'core.worktree', 'GIT_CONFIG_VALUE_0': 'caller',
                          'GIT_SSH_COMMAND': 'ssh -i caller-key', 'GIT_ASKPASS': 'caller-askpass',
                          'GIT_SSL_CAINFO': 'caller-ca.pem'})
        with patch.dict(os.environ, inherited):
            clean = overlay.git_environment()
        for name in names + ['GIT_CONFIG_KEY_0', 'GIT_CONFIG_VALUE_0']:
            self.assertNotIn(name, clean)
        for name in ['GIT_SSH_COMMAND', 'GIT_ASKPASS', 'GIT_SSL_CAINFO']:
            self.assertEqual(clean[name], inherited[name])

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

    def test_explicit_intended_tree_can_differ_from_reference(self):
        self.manifest['intended'] = {'tree': self.manifest['reference']['tree'], 'correction_units': ['0001'],
                                     'difference_from_reference': {'files': ['file.txt']}}
        self.manifest['reference']['tree'] = self.manifest['upstream']['tree']
        self.save()
        overlay.apply(str(self.source), self.dest)
        self.assertEqual((self.dest / 'file.txt').read_text(), 'custom\n')

    def test_undocumented_reference_divergence_rejected(self):
        self.manifest['intended'] = {'tree': self.manifest['reference']['tree'], 'correction_units': ['0001'],
                                     'difference_from_reference': {'files': ['wrong.txt']}}
        self.manifest['reference']['tree'] = self.manifest['upstream']['tree']
        self.save()
        self.assert_clean_failure()

    def test_wrong_base_tree_rejected(self):
        self.manifest['upstream']['tree'] = '0' * 40
        self.module['patches'][0]['before_tree'] = '0' * 40
        self.save()
        self.assert_clean_failure()


if __name__ == '__main__':
    unittest.main()
