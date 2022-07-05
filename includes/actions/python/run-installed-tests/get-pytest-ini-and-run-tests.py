#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

from __future__ import print_function

import pprint
import urllib
import urllib.request
import os
import os.path
import sys

from pkg_resources import get_distribution

module_name = os.environ['PYTHON_MODULE']

# Download pytest.ini
if not os.path.exists('pytest.ini'):
    dry_run = os.environ.get('CI') != 'true'
    repo = os.environ['GITHUB_REPOSITORY']
    sha = os.environ['GITHUB_SHA']
    url = 'https://raw.githubusercontent.com/{repo}/{sha}/pytest.ini'.format(**locals())
    print('Downloading', url)

    data = urllib.request.urlopen(url).read().decode('utf-8')
    print('Got following data')
    print('-'*75)
    pprint.pprint(data.splitlines())
    print('-'*75)

    with open('pytest.ini', 'w') as f:
        f.write(data)

# Print info about installed module
module = get_distribution(module_name)
version = '.'.join(module.version.split('.'))
print()
print(module_name, 'version:', version)
print(module_name, 'location:', module.location)
print()

sys.stdout.flush()
sys.stderr.flush()
# Run pytest against the library
import pytest
sys.exit(pytest.main())
