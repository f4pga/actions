#!/bin/bash

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

gstart "Update Conda Lock"
EXIT_CODE=0
# Uses BOT_CONDA_LOCK and BOT_ENV_YML env. vars
python3 $GITHUB_ACTION_PATH/update_lock.py || EXIT_CODE=$?
gend

gstart "Check Updating Result"
echo "Script returned code: $EXIT_CODE"
if [ $EXIT_CODE -eq 0 ]; then
  echo "Conda Lock has been updated."
elif [ $EXIT_CODE -eq 3 ]; then
  echo "Conda Lock is up to date."
else
  echo "Error ocurred. See above for details!"
  exit $EXIT_CODE
fi
gend
