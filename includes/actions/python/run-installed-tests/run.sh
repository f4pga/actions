#!/usr/bin/env bash
# Copyright (C) 2020-2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -x
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Step name: Install tests requirements
$DIR/get-reqs-txt-and-install-tests-deps.py

# Step name: Run Test
$DIR/get-pytest-ini-and-run-tests.py
