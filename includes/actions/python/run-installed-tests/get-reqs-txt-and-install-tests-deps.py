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

import os
import pprint
import urllib
import urllib.request
import subprocess
import sys

on_ci = os.environ.get('CI', 'false')

# Get the requirements.txt file contents.
if os.path.exists('requirements.txt'):
    with open('requirements.txt') as f:
        data = f.readlines()
else:
    # Download the requirements.txt file
    assert on_ci == 'true', on_ci
    repo = os.environ['GITHUB_REPOSITORY']
    sha = os.environ['GITHUB_SHA']

    url = 'https://raw.githubusercontent.com/{repo}/{sha}/requirements.txt'.format(**locals())
    print('Downloading', url)
    data = urllib.request.urlopen(url).read().decode('utf-8').splitlines()

print('Got following data')
print('-'*75)
pprint.pprint(data)
print('-'*75)

while not data[0].startswith('# Test'):
    data.pop(0)

data.pop(0)

test_reqs = []
while data and not data[0].strip().startswith('#'):
    r = data.pop(0)
    if '#' in r:
        r = r.split('#', 1)[0]
    r = r.strip()
    if r:
        test_reqs.append(r)

print()
print('Testing requires:')
for r in test_reqs:
    print(' *', repr(r))
print()

cmd = [sys.executable, '-m', 'pip', 'install']+test_reqs
if on_ci == 'true':
    print('::group::'+" ".join(cmd))
    sys.stdout.flush()
    sys.stderr.flush()
    subprocess.check_call(cmd, stderr=subprocess.STDOUT)
    sys.stdout.flush()
    sys.stderr.flush()
    print('::endgroup::')
else:
    print('Skipping command as CI =', repr(on_ci))
    print("Run pip command would be:", " ".join(cmd))
