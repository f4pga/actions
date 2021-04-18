#!/bin/bash

# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:	ISC

set -e

echo
echo "==========================="
echo "Check SPDX identifier"
echo "==========================="
echo

ERROR_FILES=""
FIND_CMD_FILE=$(mktemp) || exit
trap "rm -f -- '$FIND_CMD_FILE'" EXIT

cat > $FIND_CMD_FILE <<EOF
find .
 -type f
 \( -name '*.sh' -o -name '*.py' -o -name 'Makefile' -o -name '*.v' \)
EOF
for EXCLUDE in $INPUT_LICENSEEXCLUDE; do
    echo " \( -not path '$EXCLUDE' \)" >> $FIND_CMD_FILE
done

if [ "$INPUT_DEBUG" = "true" ]; then
    echo "::group::Find command"
    echo "-------------------------------------------------"
    cat $FIND_CMD_FILE
    echo "-------------------------------------------------"
    echo "::endgroup::"
    echo
fi


eval $(cat $FIND_CMD_FILE) | sort | while IFS= read -r file; do
    echo "Checking '$file'"
    grep -q "SPDX-License-Identifier" "$file" || ERROR_FILES="$ERROR_FILES '$file'"
done

if [ ! -z "$ERROR_FILES" ]; then
    for file in $ERROR_FILES; do
        echo "ERROR: $file does not have license information."
    done
    exit 1
fi

THIRD_PARTY_DIRS=$(shopt -s nullglob; echo third_party/*)
ERROR_NO_LICENSE=""

if [ -z "$THIRD_PARTY_DIRS" ]; then
	exit 0
fi

echo
echo "==========================="
echo "Check third party LICENSE"
echo "==========================="
echo

function check_if_submodule {
    for submodule in `git submodule --quiet foreach 'echo $sm_path'`; do
        if [ "$1" == "$submodule" ]; then
            return 1
        fi
    done
}

for dir in $THIRD_PARTY_DIRS; do
    # Checks if we are not in a submodule
    if check_if_submodule $dir; then
        echo "Checking $dir"
        [ -f $dir/LICENSE ] || ERROR_NO_LICENSE="$ERROR_NO_LICENSE $dir"
    fi
done

if [ ! -z "$ERROR_NO_LICENSE" ]; then
    for dir in $ERROR_NO_LICENSE; do
        echo "ERROR: $dir does not have the LICENSE file."
    done
    exit 1
fi
