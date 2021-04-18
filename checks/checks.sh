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

if [ "$INPUT_DEBUG" = "true" ]; then
	echo
	echo "::group::Command Arguments"
	echo "-------------------------------------------------"
	# store arguments in a special array
	ARGS=("$@")
	# get number of elements
	ELEMENTS=${#ARGS[@]}
	# Output the arguments
	for (( i=0;i<$ELEMENTS;i++)); do
		echo "arg[$i]='${ARGS[${i}]}'"
	done
	echo "-------------------------------------------------"
	echo "::endgroup::"
	echo
	echo "::group::Shell Environment"
	echo "-------------------------------------------------"
	export
	echo "-------------------------------------------------"
	echo "::endgroup::"
fi

"$thisDir"/check_license.sh
"$thisDir"/check_python_script.sh
