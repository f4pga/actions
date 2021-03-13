# SymbiFlow actions

This repository contains [actions](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/introduction-to-github-actions#actions) to be reused in [GitHub Actions](https://github.com/features/actions) continuous integration [workflows](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/introduction-to-github-actions#workflows), either for development purposes or by final users.

✔️ [symbiflow/actions/checks](checks)

Runs license and python linting checks.

# Include Actions

 * `includes/python/publish-to-pypi-src` - Action to push a `sdist` package to PyPI.
 * `includes/python/publish-to-pypi-wheels-bin-linux` - Action to push binary wheel packages for Linux to PyPI.
 * `includes/python/publish-to-pypi-wheels-bin-other` - Action to push binary wheel packages for Mac & Windows to PyPI.
 * `includes/python/system-setup` - Action to setup a system with Python and dependencies.
 * `includes/python/check-upload-publish-packages` - Action which uploads already built packages (from the other `python-to-pypi-XXXX` actions).

# Example workflows

 * `workflows/build-and-upload-for-pypi-bin.yml` - Example workflow for building and publishing a Python package which **has binary parts** to PyPI.
 * `workflows/build-and-upload-for-pypi-pure.yml` - Example workflow for building and publishing a *pure* Python package to PyPI.
