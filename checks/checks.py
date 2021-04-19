#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:	ISC


import logging
import os
import pathlib
import pprint
import re
import sys
import tempfile


__path__ = pathlib.Path(__file__).resolve().parent


ON_GITHUB_ACTIONS = (
    os.environ.get('GITHUB_ACTIONS', 'false').lower() in ('1', 'true'))

OUTPUT_ANNOTATIONS = (
    os.environ.get('INPUT_ANNOTATIONS', 'false').lower() in ('1', 'true'))


def relpath(fpath):
    """Convert the path to be relative to the current working directory."""
    assert isinstance(fpath, pathlib.Path), (fpath, type(fpath))
    fpath = fpath.resolve()
    return os.path.relpath(fpath)


def fdebug(fpath, msg, *args, **kw):
    return logging.debug('%s: '+msg, relpath(fpath), *args, **kw)


def finfo(fpath, msg, *args, **kw):
    return logging.info('%s: '+msg, relpath(fpath), *args, **kw)


def fwarn(fpath, msg, *args, **kw):
    return logging.warning('%s: '+msg, relpath(fpath), *args, **kw)


def excludes(etype, dirs=False, _cache={}):
    if etype not in _cache:
        if etype == 'third_party':
            env_name = 'INPUT_THIRD_PARTY'
        else:
            env_name = 'INPUT_EXCLUDE_{}'.format(etype.upper())
        raw_input_exclude = os.environ.get(env_name, '')
        logging.debug("%s = %r", env_name, raw_input_exclude)

        input_exclude = [i.strip() for i in raw_input_exclude.split()]

        if dirs:
            # When dealing with directories, make sure the '*/third_party/*'
            # pattern also matches the '*/third_party' directory itself.
            for e in list(input_exclude):
                if e.endswith('/*'):
                    input_exclude.append(e[:-2])
            input_exclude.sort()
        else:
            # When dealing with files, make sure the '*/exclude' pattern also
            # matches anything under an `exclude` directory by adding pattern
            # '*/exclude/*'
            for e in list(input_exclude):
                if not e.endswith('/*'):
                    input_exclude.append(e + '/*')
            input_exclude.sort()

        logging.debug('Excludes for %s are %s', etype, input_exclude)
        _cache[etype] = input_exclude

    return _cache[etype]


def read_header(pname):
    assert isinstance(pname, pathlib.Path), (pname, type(pname))
    assert pname.is_file(), (pname, pname.stat())

    # Read the first 4 kbytes
    with open(pname) as f:
        data = f.read(1024*4)

    lines = data.splitlines(keepends=True)
    # Remove the last element if it isn't a full line.
    if len(lines) > 1:
        if lines[-1][-1] != '\n':
            lines.pop(-1)

    return lines


def report_file_error(error_message, filename, lineno=1, wanted=None, found=None):
    assert lineno > 0, f'Line numbers start at 1, got {lineno}'
    if wanted is not None:
        assert found is not None, (wanted, found)
        full_error = '{} - Wanted: {!r}, Found: {!r}'.format(error_message, wanted, found)
    else:
        full_error = error_message

    if isinstance(filename, pathlib.Path) and filename.is_absolute():
        filename = pathlib.Path(os.path.relpath(filename))

    fwarn(filename, 'Error on line %s: %s', lineno, full_error)
    if ON_GITHUB_ACTIONS:
        print(':error file={},line={},col=0:{}'.format(filename, lineno, full_error))
    return [full_error]


def report_error(error_message):
    logging.warning(error_message)
    print(f'::error::{error_message}')
    return [error_message]


def python_check_shebang(filename, header_lines):
    r"""Checks using correct python3 shebang line.

    >>> P = pathlib.Path

    No shebang needed on __init__.py file if it is an empty file.
    >>> python_check_shebang(P('__init__.py'), [])
    []

    Otherwise we shouldn't have an empty python file
    >>> python_check_shebang(P('a.py'), [])
    ["Incorrect shebang (#!) line - Wanted: '#!/usr/bin/env python3\\n', Found: ''"]


    Correct shebang
    >>> python_check_shebang(P('a.py'), ['#!/usr/bin/env python3\n'])
    []

    Incorrect shebang line
    >>> python_check_shebang(P('a.py'), ['#!/usr/bin/env python\n'])
    ["Incorrect shebang (#!) line - Wanted: '#!/usr/bin/env python3\\n', Found: '#!/usr/bin/env python\\n'"]


    """
    # Skip empty '__init__.py' files
    if filename.match('__init__.py') and not header_lines:
        return []

    # Need to have at least one line for the rest of the checks to fail.
    while len(header_lines) < 1:
        header_lines.append('')

    shebang_line = '#!/usr/bin/env python3\n'
    if header_lines[0] != shebang_line:
        return report_file_error(
            'Incorrect shebang (#!) line',
            filename, 1,
            shebang_line, header_lines[0],
        )

    return []


def python_check_coding(filename, header_lines):
    r"""Check utf-8 encoding line appears in header.

    >>> P = pathlib.Path

    No coding needed on __init__.py file if it is an empty file.
    >>> python_check_coding(P('__init__.py'), [])
    []

    Otherwise we shouldn't have an empty python file
    >>> python_check_coding(P('a.py'), [])
    ["utf-8 coding not set - Wanted: '^#.*coding: utf-8.*$', Found: ''"]

    Correct coding line
    >>> python_check_coding(P('a.py'), ['', '# -*- coding: utf-8 -*-\\n', ''])
    []

    Missing coding line
    >>> python_check_coding(P('a.py'), ['#!/usr/bin/env python\\n', 'print("hello")\\n'])
    ['utf-8 coding not set - Wanted: \'^#.*coding: utf-8.*$\', Found: \'print("hello")\\\\n\'']


    """
    # Skip empty '__init__.py' files
    if filename.match('__init__.py') and not header_lines:
        return []

    # Need to have at least two lines for the rest of the checks to fail.
    while len(header_lines) < 2:
        header_lines.append('')

    coding_line = '^#.*coding: utf-8.*$'
    if not re.match(coding_line, header_lines[1]):
        return report_file_error(
            'utf-8 coding not set',
            filename, 2,
            coding_line, header_lines[1],
        )

    return []


def python_checks(pname):
    """Checks python files are valid.

    Checks performed:
     * Has the correct shebang (`#!`) starting the file.
     * Has the utf-8 coding line at start of the file.
    """
    assert isinstance(pname, pathlib.Path), (pname, type(pname))
    assert pname.is_file(), (pname, pname.stat())

    pattern = exclude_match(pname, 'python')
    if pattern:
        finfo(pname, 'Skipping python checks as matches %r.', pattern)
        return []

    fdebug(pname, 'Running python checks.')
    data = read_header(pname)

    errors = []
    errors += python_check_shebang(pname, data)
    errors += python_check_coding(pname, data)
    return errors


def license_check_spdx(filename, header_lines):
    r"""

    >>> P = pathlib.Path

    No SPDX line
    >>> license_check_spdx(P('__init__.py'), ['a', 'b', 'c'])
    ['Missing SPDX-License-Identifier line in header']

    Valid SPDX line
    >>> license_check_spdx(P('__init__.py'), ['a', 'SPDX-License-Identifier: Apache-2', 'c'])
    []

    """

    spdx_id = "SPDX-License-Identifier"

    found_spdx = False
    for l in header_lines:
        if spdx_id not in l:
            continue

        fdebug(filename, 'Found spdx_id line %r', l)
        found_spdx = True
        break

    if found_spdx:
        return []

    return report_file_error(f'Missing {spdx_id} line in header', filename)


def license_checks(pname):
    """Checks licensing in files is valid.

    Checks performed:
     * Check a `SPDX-License-Identifier` is found in the header.

    TODO: Checks to be added:
     * Check the copyright line.
     * Check the license header

    """
    assert isinstance(pname, pathlib.Path), (pname, type(pname))
    assert pname.is_file(), (pname, pname.stat())

    pattern = exclude_match(pname, 'license')
    if pattern:
        finfo(pname, 'Skipping license checks as matches %r.', pattern)
        return []

    fdebug(pname, 'Running license checks.')
    data = read_header(pname)

    errors = []
    errors += license_check_spdx(pname, data)
    return errors


LICENSE_FILES = [
    'LICENSE',
    'LICENCE',
    'COPYING',
]


def thirdparty_checks(pname):
    """Check a directory containing third party contents.

    Checks performed:
     * Checks there is a LICENSE file in each directory.

    """
    assert isinstance(pname, pathlib.Path), (pname, type(pname))
    assert pname.is_dir(), (pname, pname.stat())

    fdebug(pname, 'Running third_party directory checks.')

    errors = {}
    for dpath in pname.glob('*'):
        if not dpath.is_dir():
            continue

        license_files = []
        for lname in LICENSE_FILES:
            lpath = dpath / lname
            if lpath.exists():
                license_files.append(lpath)

        if not license_files:
            reldpath = relpath(dpath)

            errors[dpath] = report_error(
                '%s: A license file was not found (tried %s)' % (
                    reldpath, LICENSE_FILES))

        for l in license_files:
            fdebug(dpath, 'Found LICENSE file %s', l)

    return errors


def detect_file_type(pname):
    if not pname.is_file():
        return None

    if pname.match('*.py'):
        return 'python'

    if pname.match('Makefile') or pname.match('*.mk'):
        return 'make'

    if pname.match('*.yaml') or pname.match('*.yml'):
        return 'yaml'

    if pname.match('*.sh'):
        return 'shell'

    return None


def exclude_match(path, exclude_type):
    for pattern in excludes(exclude_type, dirs=path.is_dir()):
        if not path.match(pattern):
            fdebug(path, "Doesn't match %r for %s", pattern, exclude_type)
        else:
            fdebug(path, "Matches %r for %s", pattern, exclude_type)
            return pattern
    return None


class OutputGroup:
    def __init__(self, title):
        self.title = title

    def __enter__(self):
        print()
        if ON_GITHUB_ACTIONS:
            print('::group::'+self.title)
        else:
            print(self.title)
        print('-'*75)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('-'*75)
        if ON_GITHUB_ACTIONS:
            print('::endgroup::')
        print()




def main(args):
    root_dir = pathlib.Path().resolve()
    logging.debug('Starting search in: %s', root_dir)

    errors = {}
    for root, dirs, files in os.walk(root_dir):
        rpath = pathlib.Path(root).resolve()
        fdebug(rpath, 'Searching')
        fdebug(rpath, 'dirs=%r files=%r', dirs, files)

        # Treat the third_party directories special
        # FIXME: Should probably support the `linguist-vendored` properties
        #  https://github.com/github/linguist/blob/master/docs/overrides.md
        pattern = exclude_match(rpath, 'thirdparty')
        if pattern:
            finfo(rpath, 'Considering thirdparty as matches %r', pattern)
            derrors = thirdparty_checks(rpath)
            if derrors:
                for k, v in derrors.items():
                    assert k not in errors, (k, v, errors)
                    errors[k] = v

            # Don't enter further into the third_party directory.
            dirs.clear()
            continue


        # Filter out
        to_remove_dirs = []
        for dname in dirs:
            dpath = (rpath / dname).resolve()
            assert dpath.is_dir(), (dname, dpath)
            pattern = exclude_match(dpath, 'directory')
            if pattern:
                finfo(dpath, 'Skipping directory as matches %r', pattern)
                to_remove_dirs.append(dname)

        for dname in to_remove_dirs:
            dirs.remove(dname)

        # Search the directories in sorted order
        dirs.sort()

        # Run the checks on files
        # FIXME: Should probably use linguist for file type detection?
        for fname in sorted(files):
            fpath = (rpath / fname).resolve()
            if not fpath.is_file():
                fwarn(fpath, 'Skipping nonfile')
                continue

            ftype = detect_file_type(fpath)
            if ftype is None:
                finfo(fpath, 'Skipping unknown file type')
                continue

            ferrors = []
            ferrors += license_checks(fpath)

            if ftype == 'python':
                ferrors += python_checks(fpath)

            if ferrors:
                errors[fpath] = ferrors

    if errors:
        with OutputGroup('Error summary'):
            for fpath in sorted(errors):
                frelpath = fpath.relative_to(root_dir)
                print()
                print(frelpath)
                for e in sorted(errors[fpath]):
                    print(' *', e)
                print()

    return len(errors)


# Extra functionality targeted at github actions

MATCHER_OWNER = 'symbiflow-checks'


def matcher_add():
    """
    See https://github.com/actions/toolkit/blob/main/docs/commands.md#problem-matchers

    The matcher json must be available in the **current** workspace.
    See https://github.community/t/problem-matcher-not-found-in-docker-action/16814/2

    Hence we read the matcher data from the docker container and then write it
    out into the workspace before outputting the `::add-matcher` command.
    """
    if not OUTPUT_ANNOTATIONS:
        return

    # Read in the problem_matcher.json data
    infile = __path__ / 'problem_matcher.json'
    with open(infile) as f:
        data = f.read()

    assert MATCHER_OWNER in data, (MATCHER_OWNER, data)

    # Write out the problem_matcher.json data to a file in the local directory.
    fname = 'symbiflow_checks.json'
    inside_docker = pathlib.Path('/github/workflow')
    if inside_docker.exists():
        logging.debug('Running inside GitHub Action docker container!')
        outside_docker = pathlib.Path(os.environ['RUNNER_TEMP']) / '_github_workflow'
    else:
        logging.debug('Running outside docker container!')
        inside_docker = pathlib.Path(tempfile.gettempdir())
        outside_docker = inside_docker

    logging.debug('Matcher will be written to: %s', inside_docker)
    logging.debug('Matcher will be found at: %s', outside_docker)

    with open(inside_docker / fname, 'w') as f:
        f.write(data)

    print('::add-matcher::{}'.format(outside_docker / fname))


def matcher_remove():
    if not OUTPUT_ANNOTATIONS:
        return
    print('::remove-matcher owner={},::'.format(MATCHER_OWNER))


def github_actions_main(args):
    matcher_add()
    try:
        return main(args)
    finally:
        matcher_remove()


if __name__ == "__main__":
    if os.environ.get('INPUT_DEBUG', 'false').lower() in ('true', '1'):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if ON_GITHUB_ACTIONS:
        sys.exit(github_actions_main(sys.argv))
    else:
        sys.exit(main(sys.argv))
