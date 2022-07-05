#!/bin/bash
#
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
