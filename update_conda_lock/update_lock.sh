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
