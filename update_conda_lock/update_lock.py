#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""Module updating the Conda Lock."""


import io
import os
from os.path import dirname, exists, isdir, join, splitext
import re
import subprocess
import sys
import tempfile
from typing import List, Optional

from ruamel.yaml import YAML


yaml = YAML()
yaml.allow_duplicate_keys = True


def _run(cmd_string: str, multiword_last_arg: str = '',
         return_stdout: bool = False, **kwargs) -> Optional[str]:
    """Runs a subprocess based on a string command.

    It's a wrapper for `subprocess.run` that can be used with a multi-argument
      command passed as a single string.

    The subprocess's exit code is always checked (`check=True`). In case of a
      failure, captured `stdout` is always printed.

    Args:
      cmd_string: Command to be passed to `subprocess.run` after splitting.
      multiword_last_arg: Argument to be passed after `cmd_string`. It will
        be passed as a single argument.
      return_stdout: Whether to capture and return subprocess's `stdout`.
        `encoding='utf-8'` is automatically passed to `subprocess.run`.

    Keyword Args:
      All keyword arguments are passed to `subprocess.run`.

    Returns:
      Optional[str]: Captured output of the subprocess if `return_stdout` was
        `True`; `None` otherwise (the default).
    """

    cmd = cmd_string.split() + (
            [multiword_last_arg] if multiword_last_arg else [])
    if return_stdout:
        try:
            return subprocess.run(
                    cmd, check=True, encoding='utf-8', stdout=subprocess.PIPE,
                    **kwargs).stdout
        except subprocess.CalledProcessError as error:
            print(error.output)
            raise
    else:
        subprocess.run(cmd, check=True, **kwargs)
        return None


def _get_env(env_name: str) -> Optional[str]:
    """Gets the value of an environment variable.

    It's a wrapper for `os.environ[env_name]`. The obtained value is printed.
      The error is only printed if the variable is unset.

    Args:
      env_name: Environment variable's name.

    Returns:
      Optional[str]: The environment variable's value if it's set in `environ`;
        `None` otherwise.
    """

    if env_name not in os.environ:
        print('ERROR: Required environment variable not found: '
              + env_name + '!')
        return None
    env_var = os.environ[env_name]
    print('* ' + env_name + ': ' + env_var)
    return env_var


def try_updating_lock_file(lock_path: str, lock_yml: dict) -> bool:
    """Tries to update Conda Lock.

    The Conda Lock will be created if it doesn't exist.

    Args:
      lock_path: Path to the Conda Lock.
      lock_yml: dict-like ruamel.yaml CommentedMap storing new Conda Lock data.

    Returns:
      bool: True if the Conda Lock has been updated.
        False means it's been up to date already.
    """

    print('Trying to update `' + lock_path + '`...')
    with io.StringIO() as tmp_stream:
        yaml.dump(lock_yml, tmp_stream)
        new_lock_data = tmp_stream.getvalue()

    try:
        with open(lock_path, 'r') as lock_file:
            old_lock_data = lock_file.read()
            if old_lock_data == new_lock_data:
                print(lock_path + ' is up to date.')
                print()
                return False
    except FileNotFoundError:
        print(lock_path + " doesn't exist; it will be created.")

    with open(lock_path, 'w') as lock_file:
        lock_file.write(new_lock_data)
    print(lock_path + ' has been updated successfully!')
    print()
    return True


def analyze_pip_requirement(
        requirement: str, analyzed_file_dir: str) -> List[str]:
    """Analyzes a single line from pip's `requirements.txt` file.

    Such a line can be either a single package or a whole new
    `requirements.txt` file, possibly with many new packages.

    Args:
      requirement: Line from `requirements.txt` file.
      analyzed_file_dir: Parent directory of the file containing `requirement`.

    Returns:
      List[str]: List with all pip packages represented by the `requirement`.

      If it represents a single package, the list will contain only that.
      If it is, e.g., `-r file.txt`, it will contain all packages from the
        `file.txt` and possibly from even more files nested there.
    """

    path_match = re.match(r'-r (file:)?(.*)', requirement)
    if path_match is None:
        # `requirement` doesn't include any additional `requirements.txt` file
        return [requirement]

    # `-r PATH` is relative to the environment file
    req_path = join(analyzed_file_dir, path_match.group(2))
    print('Found additional pip requirements file: ' + req_path)
    with open(req_path, 'r') as req_file:
        file_requirements = []
        for req_line in req_file.readlines():
            file_requirements.extend(
                    analyze_pip_requirement(req_line, dirname(req_path))
            )
        return file_requirements


def flatten_pip_dependencies(
        pip_dependencies: List[str], analyzed_file_dir: str) -> List[str]:
    """Flattens pip dependencies from possible nested `requirements.txt` files.

    Args:
      pip_dependencies: List with a pip dependency (`str`) in each element.
      analyzed_file_dir: Path to directory the dependencies are relative to.
        In practice, this is a parent directory of either a pip requirements
        file or a Conda environment file that contains `pip_dependencies`.

    Returns:
      List[str]: List with a single pip package (`str`) in each element after
        resolving all `-r requirements.txt` dependencies.
    """

    all_pip_dependencies = []
    for pip_dependency in pip_dependencies:
        all_pip_dependencies.extend(
                analyze_pip_requirement(pip_dependency, analyzed_file_dir)
        )
    return all_pip_dependencies


def separate_pip_deps_from_env_yml(
        env_yml_path: str) -> (dict, Optional[List[str]]):
    """Separates pip dependencies from the whole Conda `environment.yml`.

    The returned `environment.yml` contents is stripped out of pip
      dependencies. The pip dependencies are returned separately.

    Args:
      env_yml_path: Path to the `environment.yml` file.

    Returns:
      Tuple with two elements from `environment.yml` file:
        dict: Contents of `environment.yml` file without pip dependencies.
        Optional[List[str]]: List of the separated pip dependencies; None if
          there were no pip dependencies in the `environment.yml` file.
    """

    with open(env_yml_path, 'r') as env_yml_file:
        env_yml = yaml.load(env_yml_file.read())

    pip_dependencies = None
    for dependency in env_yml['dependencies']:
        # `- pip:` line becomes a dict-like object with `pip` key after parsing
        if isinstance(dependency, dict) and 'pip' in dependency.keys():
            # `pip:` key is replaced with `pip` package to have it installed
            env_yml['dependencies'].remove(dependency)
            env_yml['dependencies'].append('pip')
            pip_dependencies = list(dependency['pip'])

    # At this point `env_yml` doesn't contain any pip dependencies.
    return (env_yml, pip_dependencies)


def get_local_pip_dependencies(
        pip_dependencies: List[str], root_dir: str) -> (List[str], List[str]):
    """Gets only local pip dependencies from the pip dependencies' list.

    Args:
      pip_dependencies: List with pip dependencies.
      root_dir: Root directory for relative pip dependencies.

    Returns:
      Tuple with two lists for pip dependencies that are found to be local:
        List[str]: The dependencies' paths.
        List[str]: The dependencies' names.
    """
    local_pip_dependencies = []
    local_pip_deps_names = []
    for dependency in pip_dependencies:
        dependency = dependency.strip()
        # Handle comments
        if dependency.startswith('#'):
            continue
        only_dependency = re.sub(r'(.*)\s+#.*$', r'\1', dependency)

        # Find core of the dependency line without version etc.
        core_match = re.search(r'(^|\s)([^\s-][^\s=<>~!;]+)', only_dependency)
        if core_match is None:
            continue
        dependency_path = join(root_dir, core_match.group(2))
        if isdir(dependency_path):
            setup_path = join(dependency_path, 'setup.py')
            if not exists(setup_path):
                continue
            try:
                dependency_name = _run(
                        'python3 setup.py --name', cwd=dependency_path,
                        return_stdout=True).strip()
            except subprocess.CalledProcessError:
                print('Running `python3 ' + setup_path + ' --name` failed!')
                # Not so elegant fallback
                print('Trying to find the name in the file...')
                with open(setup_path) as setup_file:
                    name_match = re.search(
                            r'name\s*=\s*[\'\"](\S+)[\'\"]', setup_file.read())
                # No match at this point is and should be fatal
                dependency_name = name_match.group(1)
                print('Found `' + dependency_name + '` name.')
                print()
            local_pip_dependencies.append(dependency)
            local_pip_deps_names.append(dependency_name)
    return (local_pip_dependencies, local_pip_deps_names)


class CondaEnvironmentContext:
    """The with-statement context creating a temporary Conda environment."""
    def __init__(self, name: str, env_path: str):
        """Inits CondaEnvironmentContext.

        Args:
          name: Name to be used for the temporary Conda environment.
          env_path: Path to the Conda `environment.txt` file to be used to
            create the temporary Conda environment.
        """

        self._name = name
        self._env_path = env_path

    def __enter__(self):
        try:
            _run('conda env create -n ' + self._name + ' -f ' + self._env_path)
        except subprocess.CalledProcessError:
            print('ERROR: Creating `' + self._name + '` environment failed!')
            print('Please remove any environment with such name, if exists.')
            print()
            sys.exit(1)

    def __exit__(self, exc_type, exc_value, traceback):
        print('Removing `' + self._name + '` Conda environment... ', end='')
        _run('conda env remove -n ' + self._name, stdout=subprocess.DEVNULL,
             stderr=subprocess.DEVNULL)
        print('done!')
        print()


def lock_pip_dependencies(
        pip_cmd: str, root_dir: str, pip_deps: List[str]) -> List[str]:
    """Locks pip dependencies' versions.

    Args:
      pip_cmd: Command to be used to run pip subprocess.
      root_dir: Root directory to resolve all relative paths with.
      pip_deps: Pip dependencies to lock.

    Returns:
      List[str]: List of pip dependencies with locked versions formatted
        according to the `requirements.txt` style.
    """

    all_pip_deps = flatten_pip_dependencies(pip_deps, root_dir)

    # Local pip deps will be removed and copied in the original form as
    # freezing breaks them (git handles their versioning after all).
    (local_deps, local_deps_names) = get_local_pip_dependencies(
            all_pip_deps, root_dir)

    print('Installing pip dependencies...')
    print()
    tmp_requirements_file = tempfile.NamedTemporaryFile(
            'w', delete=False)
    tmp_requirements_path = tmp_requirements_file.name
    try:
        tmp_requirements_file.write('\n'.join(all_pip_deps))
        tmp_requirements_file.close()

        # Paths in `requirements.txt` are relative to the `root_dir`
        _run(pip_cmd + 'install -r ' + tmp_requirements_path,
             cwd=root_dir or '.')
    finally:
        if exists(tmp_requirements_path):
            os.remove(tmp_requirements_path)
    print()

    # Uninstall local packages
    if local_deps and local_deps_names:
        print('Uninstalling local pip packages (they were installed '
              + "only to lock their dependencies' versions)...")
        print()
        for local_pkg in local_deps_names:
            _run(pip_cmd + 'uninstall --yes ' + local_pkg)
        print()

    pip_locked_pkgs = []
    for pip_spec in _run(pip_cmd + 'freeze', return_stdout=True).splitlines():
        if pip_spec:
            # Ignore pip packages installed by Conda
            # (lines: 'NAME @ file://PATH/work')
            conda_pkg_match = re.match(r'(\S+) @ file://.*/work.*', pip_spec)
            if conda_pkg_match is not None:
                print('Ignoring pip package installed by Conda: '
                      + conda_pkg_match.group(1))
                continue
            pip_locked_pkgs.append(pip_spec)

    # Add local packages
    if local_deps:
        pip_locked_pkgs.extend(local_deps)

    return pip_locked_pkgs


def render_conda_lock_contents(env_yml_path: str) -> dict:
    """Renders Conda Lock contents based on the Conda `environment.yml` file.

    Conda Lock is an `environment.yml`-like file with locked dependencies which
      can be used to create a Conda environment with `conda env create -f`.

    Args:
      env_yml_path: Path to the `environment.yml` file to be the base for the
        Conda Lock.

    Returns:
      dict: Conda Lock contents in a ruamel.yaml.comments.CommentedMap, i.e.,
        dict-like type. It can be dumped with ruamel.yaml to create an
        `environment.yml`-like file.
    """

    (pipless_env_yml, pip_deps) = separate_pip_deps_from_env_yml(env_yml_path)
    env_name = pipless_env_yml['name']

    pipless_env_file = tempfile.NamedTemporaryFile(
            'w', suffix='.yml', delete=False)
    pipless_env_path = pipless_env_file.name
    try:
        yaml.dump(pipless_env_yml, pipless_env_file)
        pipless_env_file.close()

        with CondaEnvironmentContext(env_name, pipless_env_path):
            conda_lock = _run('conda run -n ' + env_name + ' conda env export',
                              return_stdout=True)
            conda_lock_yaml = yaml.load(conda_lock)
            print('Conda packages captured.')
            print()

            # Lock pip dependencies
            if pip_deps:
                pip_command = ('conda run --no-capture-output -n ' + env_name
                               + ' python3 -I -m pip ')

                pip_locked_pkgs = lock_pip_dependencies(
                        pip_command, dirname(env_yml_path), pip_deps)

                # Add locked pip packages to the `conda env export` yaml output
                if pip_locked_pkgs:
                    conda_lock_yaml['dependencies'].append(
                            {'pip': pip_locked_pkgs})

                print()
                print('Pip packages captured.')
                print()

            return conda_lock_yaml
    finally:
        if exists(pipless_env_path):
            os.remove(pipless_env_path)


def is_conda_lock_extension_correct(conda_lock_path: str) -> bool:
    """Tests whether Conda Lock has a proper extension.

    It is going to be used to create a Conda environment but only `.txt`,
      `.yml` and `.yaml` files are supported by `conda env create -f `.

    Args:
      conda_lock_path: Path to the Conda Lock file.

    Returns:
      bool: True if the extension is correct; False otherwise.
    """

    _, conda_lock_ext = splitext(conda_lock_path)
    if conda_lock_ext in ['.txt', '.yml', '.yaml']:
        return True

    print('ERROR: Invalid conda lock extension (`' + conda_lock_ext
          + '`); it must be `.txt`, `.yml` or `.yaml`!')
    return False


def main():
    """Creates or updates Conda Lock."""

    print('Environment variables used are:')
    conda_lock_path = _get_env('BOT_CONDA_LOCK')
    env_yml_path = _get_env('BOT_ENV_YML')
    print()
    if None in [conda_lock_path, env_yml_path]:
        sys.exit(1)

    if not is_conda_lock_extension_correct(conda_lock_path):
        sys.exit(1)

    conda_lock_yaml = render_conda_lock_contents(env_yml_path)

    # Apply yaml offset used by `conda env export`
    yaml.indent(offset=2)
    if try_updating_lock_file(conda_lock_path, conda_lock_yaml):
        sys.exit(0)
    else:
        sys.exit(3)


if __name__ == '__main__':
    main()
