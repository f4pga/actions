#!/bin/bash

# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:	ISC

set -e

thisDir=$(dirname "$0")

"$thisDir"/check_license.sh

"$thisDir"/check_python_script.sh
