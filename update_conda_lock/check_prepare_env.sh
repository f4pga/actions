#!/bin/bash

# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:  ISC


# gstart and gend functions
source $GITHUB_ACTION_PATH/helpers.sh
set -e

gstart "Check git"
which git
git --version
gend

gstart "Check Conda"
which conda
conda -V
echo
echo "Packages in the current environment:"
conda list
gend

gstart "Check Python"
which python3
python3 -V
echo
echo "Python modules installed in pip:"
python3 -m pip list
gend

gstart "Check curl"
which curl
curl -V
gend

gstart "List Current Directory"
ls -l
gend

gstart "Install ruamel.yaml"
python3 -m pip install ruamel.yaml
gend
