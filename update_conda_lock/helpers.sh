# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:  ISC


function gstart {
  echo "::group::$1"
  set -x
}

function gend {
  set +x
  echo "::endgroup::"
}
