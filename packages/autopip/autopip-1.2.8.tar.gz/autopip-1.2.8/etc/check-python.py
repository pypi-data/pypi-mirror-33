#!/usr/bin/env python

import platform
import shutil
import subprocess
import sys


IS_LINUX = platform.system() == 'Linux'
PY_VERSION = '3.6'


def check_python():
    print('Checking Python...')
    py3_path = run('which python' + PY_VERSION, return_output=True)
    if not py3_path:
        error('! Python ' + PY_VERSION + ' is not installed.')
        print('  Please install Python ' + PY_VERSION +
              ' per http://docs.python-guide.org/en/latest/starting/installation/')
        sys.exit(1)


def check_pip():
    print('\nChecking pip...')

    if not run('which pip3', return_output=True):
        error('! pip3 does not seem to be installed.')
        print('  Try installing it with: curl https://bootstrap.pypa.io/get-pip.py | sudo python' + PY_VERSION)
        if IS_LINUX:
            print('  If your package repo (e.g. apt) has a *-pip package for Python ' + PY_VERSION +
                  ', then install it from there.')
            print('  E.g. For Debian/Ubuntu, try: apt install python3-pip')
        sys.exit(1)

    version_full = run('pip3 --version', return_output=True)
    version_str = version_full.split()[1]
    version = tuple(map(_int_or, version_str.split('.', 2)))
    if version < (9, 0, 3):
        error('! Version is', version_str, 'but should be 9.0.3+')
        print('  Try upgrading it: sudo pip3 install -U pip==9.0.3')
        sys.exit(1)

    if 'python' + PY_VERSION not in version_full:
        error('! pip3 seems to be for another Python version and not Python ' + PY_VERSION)
        print('  See output: ' + version_full.strip())
        print('  Try re-installing it with: curl https://bootstrap.pypa.io/get-pip.py | sudo python' + PY_VERSION)
        sys.exit(1)


def check_venv():
    print('\nChecking venv...')
    test_venv_path = '/tmp/check-python-venv'

    try:
        try:
            run('python' + PY_VERSION + ' -m venv ' + test_venv_path, stderr=subprocess.STDOUT, return_output=True,
                raises=True)

        except Exception:
            error('! Could not create virtual environment. Please make sure *-venv package is installed.')
            if IS_LINUX:
                print('  For Debian/Ubuntu, try: sudo apt install python' + PY_VERSION + '-venv')
            sys.exit(1)

    finally:
        shutil.rmtree(test_venv_path, ignore_errors=True)


def run(cmd, return_output=False, raises=False, **kwargs):
    print('+ ' + str(cmd))
    if isinstance(cmd, str):
        cmd = cmd.split()

    check_call = subprocess.check_output if return_output else subprocess.check_call

    try:
        output = check_call(cmd, **kwargs)

        if isinstance(output, bytes):
            output = output.decode()

        return output

    except Exception:
        if return_output and not raises:
            return
        else:
            raise


def _int_or(value):
    try:
        return int(value)
    except Exception as e:
        return value


def error(*msg):
    msg = ' '.join(map(str, msg))
    echo(msg, color='red')


def echo(msg, color=None):
    if sys.stdout.isatty() and color:
        if color == 'red':
            color = '\033[0;31m'
        elif color == 'green':
            color = '\033[92m'

        msg = color + msg + '\033[0m'

    print(msg)


check_python()
check_pip()
check_venv()

echo('\nPython is alive and well. Good job!', color='green')
