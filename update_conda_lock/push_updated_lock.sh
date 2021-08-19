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

gstart "Create New Branch"
git checkout -b "$PR_HEAD"
gend

gstart "Update Conda Lock"
EXIT_CODE=0
# Uses BOT_CONDA_LOCK and BOT_ENV_YML env. vars
python3 $GITHUB_ACTION_PATH/update_lock.py || EXIT_CODE=$?
gend

gstart "Check Updating Result"
echo "Script returned code: $EXIT_CODE"
if [ $EXIT_CODE -eq 0 ]; then
  echo "CONDA_LOCK_UPDATED=true" >> $GITHUB_ENV
  echo "Conda Lock has been updated."
elif [ $EXIT_CODE -eq 3 ]; then
  echo "CONDA_LOCK_UPDATED=false" >> $GITHUB_ENV
  echo "Conda Lock is up to date."
  exit 0
else
  echo "Error ocurred. See above for details!"
  exit $EXIT_CODE
fi
gend

gstart "Add And Commit Changes"
git config user.name "$USER_NAME"
git config user.email "$USER_EMAIL"
git add "$BOT_CONDA_LOCK"
git commit -m "$COMMIT_MESSAGE"
gend

gstart "Push Changes"
git push -u origin "$PR_HEAD"
gend
