# SymbiFlow actions

This repository contains [actions](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/introduction-to-github-actions#actions) to be reused in [GitHub Actions](https://github.com/features/actions) continuous integration [workflows](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/introduction-to-github-actions#workflows), either for development purposes or by final users.

✔️ [symbiflow/actions/checks](checks)

Runs license and python linting checks.

# Examples

These are examples of using "includable" workflows. Put these in
`.github/workflow-src/XXXX.yml` and then use the
[`actions-includes`](https://github.com/mithro/actions-includes) library
to expand it into `.github/workflow/XXXX.yml`.

 * [`examples/build-and-upload-for-pypi-bin.yml`](./examples/build-and-upload-for-pypi-bin.yml) -
    Example workflow for building and publishing a Python package which **has
    binary parts** to PyPI.

 * [`examples/build-and-upload-for-pypi-pure.yml`](./examples/build-and-upload-for-pypi-pure.yml) -
    Example workflow for building and publishing a *pure* Python package to
    PyPI.

# "Includable" Workflows

 * [`includes/workflows/python/build-and-upload-for-pypi-bin`](./includes/workflows/python/build-and-upload-for-pypi-bin/workflow.yaml) -
   Workflow to build and publish (binary) package (source + wheels) on PyPI.

 * [`includes/workflows/python/build-and-upload-for-pypi-pure`](./includes/workflows/python/build-and-upload-for-pypi-pure/workflow.yaml) -
   Workflow to build and publish (pure python) package (source + wheels) on
   PyPI.

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
   Action which uploads already built packages (from the other
   `python-to-pypi-XXXX` actions).


