#!/usr/bin/env python3
"""Replay trusted overlay patches into a NEW checkout; never mutate an existing tree."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, stderr=subprocess.STDOUT).decode().strip()


def git(where, *args):
    return run('git', '-c', 'core.autocrlf=false', '-c', 'core.hooksPath=/dev/null', '-C', str(where), *args)


def checked_file(name, checksum=None):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'Invalid overlay file: {name}')
    if checksum and hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
        raise ValueError(f'Checksum mismatch: {name}')
    return path


def load_plan(selected=None):
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    if manifest['format_version'] != 1:
        raise ValueError('Unsupported manifest format')
    selected = manifest['default_features'] if selected is None else selected
    if len(set(selected)) != len(selected) or not selected:
        raise ValueError('Select unique, nonempty features')
    modules = {}
    for entry in manifest['features']:
        module = json.loads(checked_file(entry['manifest'], entry['sha256']).read_text())
        if module['id'] != entry['id'] or entry['id'] in modules:
            raise ValueError('Duplicate or mismatched feature ID')
        modules[entry['id']] = module
    unknown = set(selected) - modules.keys()
    if unknown:
        raise ValueError(f'Unknown features: {sorted(unknown)}')
    plan, done, active = [], set(), set()

    def visit(name):
        if name in active:
            raise ValueError('Feature dependency cycle')
        if name in done:
            return
        active.add(name)
        module = modules[name]
        if module['baseline'] != manifest['upstream']['commit']:
            raise ValueError('Feature baseline mismatch')
        for dependency in module['requires']:
            if dependency not in selected:
                raise ValueError(f'{name} requires explicit selection of {dependency}')
            visit(dependency)
        plan.extend(module['patches'])
        active.remove(name)
        done.add(name)

    for name in selected:
        visit(name)
    ids = set()
    tree = manifest['upstream']['tree']
    for patch in plan:
        if patch['id'] in ids or not set(patch['requires']).issubset(ids):
            raise ValueError('Duplicate patch or unsatisfied patch dependency')
        if patch['before_tree'] != tree:
            raise ValueError(f"Tree chain mismatch at {patch['id']}")
        checked_file(patch['file'], patch['sha256'])
        checked_file(patch['documentation'])
        ids.add(patch['id'])
        tree = patch['after_tree']
    if set(selected) == set(manifest['default_features']) and tree != manifest['reference']['tree']:
        raise ValueError('Default plan does not reproduce reference tree')
    return manifest, plan


def apply(source, destination, selected=None):
    manifest, plan = load_plan(selected)
    destination = Path(destination).absolute()
    if os.path.lexists(destination):
        raise ValueError('Destination already exists; refusing to modify it')
    if not destination.parent.is_dir():
        raise ValueError('Destination parent must already exist')
    temporary = Path(tempfile.mkdtemp(prefix='.overlay-', dir=destination.parent))
    try:
        # Fetch only the pinned revision into an independent object store. This
        # also works with a local partial clone without copying unrelated history.
        run('git', 'init', '--quiet', str(temporary))
        base = manifest['upstream']['commit']
        git(temporary, 'fetch', '--depth=1', '--no-tags', '--', str(Path(source).resolve()) if Path(source).exists() else source, base)
        git(temporary, 'checkout', '--detach', base)
        if git(temporary, 'rev-parse', 'HEAD^{tree}') != manifest['upstream']['tree']:
            raise ValueError('Pinned upstream tree mismatch')
        for patch in plan:
            if git(temporary, 'write-tree') != patch['before_tree']:
                raise ValueError(f"Unexpected input tree at {patch['id']}")
            file = checked_file(patch['file'], patch['sha256'])
            git(temporary, 'apply', '--check', '--index', str(file))
            # No fuzzy three-way merge, rejects, or conflict resolution.
            git(temporary, 'apply', '--index', str(file))
            if git(temporary, 'write-tree') != patch['after_tree']:
                raise ValueError(f"Unexpected output tree at {patch['id']}")
        # Preserve exact tree in a deterministic commit, without using the user's identity.
        env = dict(os.environ, GIT_AUTHOR_NAME='Uptime Kuma Overlay', GIT_AUTHOR_EMAIL='overlay@localhost',
                   GIT_COMMITTER_NAME='Uptime Kuma Overlay', GIT_COMMITTER_EMAIL='overlay@localhost',
                   GIT_AUTHOR_DATE='2000-01-01T00:00:00Z', GIT_COMMITTER_DATE='2000-01-01T00:00:00Z')
        commit = subprocess.check_output(['git', '-C', str(temporary), 'commit-tree', plan[-1]['after_tree'],
                                         '-p', base, '-m', 'Reproduce pinned Uptime Kuma overlay'], env=env).decode().strip()
        git(temporary, 'reset', '--hard', commit)
        if git(temporary, 'status', '--porcelain', '--untracked-files=all'):
            raise ValueError('Replay produced a dirty tree')
        # Atomic publication; existing destinations have already been rejected.
        # mkdir reserves the path so a concurrent run cannot replace another checkout.
        destination.mkdir()
        try:
            os.rename(temporary, destination)
        except BaseException:
            destination.rmdir()
            raise
        print(json.dumps({'destination': str(destination), 'baseline': base,
                          'tree': plan[-1]['after_tree'], 'patches': [x['id'] for x in plan]}, indent=2))
        return destination
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='Official upstream URL or local Git clone containing the pinned SHA')
    parser.add_argument('destination', help='New directory; must not exist')
    parser.add_argument('--features', help='Comma-separated explicit feature selection (dependencies required)')
    args = parser.parse_args()
    try:
        apply(args.source, args.destination, args.features.split(',') if args.features else None)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        detail = error.output.decode(errors='replace') if isinstance(error, subprocess.CalledProcessError) else str(error)
        parser.exit(1, f'Overlay refused: {detail}\n')


if __name__ == '__main__':
    main()
