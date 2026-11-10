#!/usr/bin/env python3
"""Fresh replay followed by real feature tests and build. Fail at the first failing check."""
import argparse
from pathlib import Path
import subprocess
from apply import apply, git, git_environment

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source')
parser.add_argument('destination')
parser.add_argument('--features')
parser.add_argument('--reuse-dependencies', type=Path,
                    help='Local convenience only; symlink installed node_modules (not npm ci evidence)')
parser.add_argument('--install-browser', action='store_true', help='Install Chromium and OS dependencies before full browser suite')
parser.add_argument('--full', action='store_true', help='Full backend/container and browser suites plus lint')
args = parser.parse_args()
repo = apply(args.source, args.destination, args.features.split(',') if args.features else None)
env = dict(git_environment(), TEST_BACKEND='1', HEADLESS_E2E_TESTS='1')
env.pop('SKIP_TESTCONTAINER', None)


def check(*command, **kwargs):
    print('+', ' '.join(command), flush=True)
    subprocess.run(command, cwd=repo, env=kwargs.get('env', env), check=True)


if args.reuse_dependencies:
    dependencies = args.reuse_dependencies.resolve()
    if not dependencies.is_dir():
        raise ValueError('Missing installed dependency directory')
    (repo / 'node_modules').symlink_to(dependencies, target_is_directory=True)
else:
    check('npm', 'ci', '--no-audit', '--no-fund')
# Integration servers require dist/index.html even before browser checks.
check('npm', 'run', 'build')
files = sorted({*repo.glob('test/backend-test/test-*dependency*.ts'),
                *repo.glob('test/frontend-test/test-*dependency*.ts')})
# Includes MariaDB; never silently disable containers in the regression command.
check('node', '--import=tsx', '--import=./test/setup.ts', '--test', '--test-concurrency=1',
      *[str(f.relative_to(repo)) for f in files])
if args.full:
    check('npm', 'run', 'test-backend')
    check('npm', 'run', 'lint')
    if args.install_browser:
        check('npx', '--no-install', 'playwright', 'install', '--with-deps', 'chromium')
    browser_env = dict(env, SKIP_TESTCONTAINER='1')
    browser_env.pop('TEST_BACKEND', None)
    check('npm', 'run', 'test-e2e', '--', '--max-failures=0', env=browser_env)
if git(repo, 'status', '--porcelain', '--untracked-files=all'):
    raise ValueError('Tests/build modified the tracked tree or left unignored artifacts')
print('PASS: exact replay, regression tests, production build' + (' and full suites' if args.full else ''))
