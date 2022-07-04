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

# Set up a Python environment to run the actions_include tool on.
ENV_DIR = venv
PYTHON = $(ENV_DIR)/bin/python3
ACTIVATE = source $(ENV_DIR)/bin/activate;

env: requirements.txt
	rm -rf $(ENV_DIR)
	virtualenv --copies $(ENV_DIR)
	$(ACTIVATE) pip install -r $<
	touch --reference=$< $(PYTHON)

.PHONY: env

$(PYTHON): requirements.txt
	make env

enter: | $(PYTHON)
	$(ACTIVATE) bash

# Generate the output files
SRC_YAML = $(wildcard workflows/*.yml)

build: | $(PYTHON)
	@true

info:
	@echo 'Output files: $(OUT_YAML)'

.PHONY: info
