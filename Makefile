# Copyright 2012 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

VERB = @
ifeq ($(VERBOSE),1)
	VERB =
endif

test:
	$(VERB) ./run_all_tests.sh

regen:
	$(VERB) ./update_testdata.py
	$(VERB) ./csv2txf_test.sh regen

THIRD_PARTY_PYTHON = third_party/python
PIP := $(shell which pip || which pip3)
PYTHON_VERSION ?= $(shell python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')")

install-dev:
	$(VERB) $(PIP) install -r requirements-dev.txt -t $(THIRD_PARTY_PYTHON)

# Requires having installed dependencies first via `make install-dev`.
autopep8:
	$(VERB) find . -name \*\.py \
	        | xargs -I {} python $(THIRD_PARTY_PYTHON)/autopep8.py --in-place {}

mypy-test:
	$(VERB) python -m mypy --python-version=$(PYTHON_VERSION) --ignore-missing-imports `find . -name 'third_party' -prune -o -name '*.py' -print`

pytype-test:
	$(VERB) python -m pytype --python-version=$(PYTHON_VERSION) -k `find . -name 'third_party' -prune -o -name '*.py' -print`

clean:
	$(VERB) rm -rf `find . -name \*\.pyc` $(THIRD_PARTY_PYTHON)/*
