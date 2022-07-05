# F4PGA Actions

This repository contains [Actions](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/introduction-to-github-actions#actions)
to be reused in [GitHub Actions](https://github.com/features/actions) Continuous Integration (CI) [workflows](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/introduction-to-github-actions#workflows),
either for development purposes or by final users.

## [f4pga/actions/checks](checks)

Runs license and python linting checks.

## [f4pga/actions/update_conda_lock](update_conda_lock)

Simplifies maintaining Conda Locks, i.e. stable Conda environment files with precise Conda and Pip package versions
based on a given Conda environment file.

Running this action only updates the provided Conda Lock file, leaving to the caller action the creation of the Pull
Request (PR).

### Action inputs

The inputs to this action are:

* `conda_lock_file` (default: `conda_lock.yml`):
  * Path to the Conda Lock file (needs to have txt/yml/yaml extension).

* `environment_file` (default: `environment.yml`):
  * Path to the base `environment.yml` file.

### Avoiding conflicts with inter-dependent git-based pip packages

In certain circumstances pip, internally run when Conda creates the environment, might fail due to an alleged conflict
in Conda Lock git-based packages.
Until [the pip issue](https://github.com/pypa/pip/issues/10002) is fixed, it can be avoided by making pip install
packages without their dependencies.
With Conda Lock it's absolutely safe to do so since all pip packages, including the dependencies of packages specified
directly, are always included in the Conda Lock.
What's more, the package versions are all locked in Conda Lock so these dependencies can't change.

Therefore currently the safest way to create Conda environment using the Conda Lock is:

```bash
env PIP_NO_DEPS="true" conda env create -f $CONDA_LOCK_FILE`
```

# Examples

These are examples of using "includable" workflows.
Put these in `.github/workflow-src/XXXX.yml` and then use the [`actions-includes`](https://github.com/mithro/actions-includes)
library to expand it into `.github/workflow/XXXX.yml`.

* [`examples/build-and-upload-for-pypi-bin.yml`](./examples/build-and-upload-for-pypi-bin.yml) -
  Example workflow for building and publishing a Python package which **has binary parts** to PyPI.

* [`examples/build-and-upload-for-pypi-pure.yml`](./examples/build-and-upload-for-pypi-pure.yml) -
  Example workflow for building and publishing a *pure* Python package to PyPI.

* [`examples/install-and-test.yml`](./examples/install-and-test.yml) -
  Example workflow for making sure that a Python package runs correctly no matter how it is installed.

# "Includable" Workflows

* [`includes/workflows/python/build-and-upload-for-pypi-bin`](./includes/workflows/python/build-and-upload-for-pypi-bin/workflow.yaml) -
  Workflow to build and publish (binary) package (source + wheels) on PyPI.

* [`includes/workflows/python/build-and-upload-for-pypi-pure`](./includes/workflows/python/build-and-upload-for-pypi-pure/workflow.yaml) -
  Workflow to build and publish (pure python) package (source + wheels) on PyPI.

* [`includes/workflows/python/install-and-test`](./includes/workflows/python/install-and-test/workflow.yaml) -
  Make sure that a Python package installs correctly (directly from GitHub, via pip, via setup.py, etc).

# "Includable" Actions

* [`includes/actions/python/publish-to-pypi-src`](./includes/actions/python/publish-to-pypi-src/action.yaml) -
  Action to push a `sdist` package to PyPI.

* [`includes/actions/python/publish-to-pypi-wheels-bin-linux`](./includes/actions/python/publish-to-pypi-wheels-bin-linux/action.yaml) -
  Action to push binary wheel packages for Linux to PyPI.

* [`includes/actions/python/publish-to-pypi-wheels-bin-other`](./includes/actions/python/publish-to-pypi-wheels-bin-other/action.yaml) -
  Action to push binary wheel packages for Mac & Windows to PyPI.

* [`includes/actions/python/system-setup`](./includes/actions/python/system-setup/action.yaml) -
  Action to setup a system with Python and dependencies.

* [`includes/actions/python/check-upload-publish-packages`](./includes/actions/python/check-upload-publish-packages/action.yaml) -
  Action which uploads already built packages (from the other `python-to-pypi-XXXX` actions).

* [`includes/actions/python/run-installed-tests`](./includes/actions/python/run-installed-tests/action.yaml) -
  Action which runs tests which have been installed as part of a Python package (downloads `requirements.txt` and `pytest.ini` from source repository).
