# Copyright 2012 Google Inc.
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

ifdef VERBOSE
	VERB =
else
	VERB = @
endif

TESTS := $(wildcard *_test.py)

test:
	$(VERB) for t in $(TESTS); do \
		echo -n "Testing $${t} ... "; \
		TEST_OUT=`mktemp /tmp/$${t}.XXXXXX`; \
		./$${t} > $${TEST_OUT} 2>&1; \
		if [[ -n "$$(tail -n 1 $${TEST_OUT} | grep OK)" ]]; then \
			rm -f $${TEST_OUT}; \
			echo "OK."; \
		else \
			echo "failed, see log in $${TEST_OUT}"; \
		fi \
	done

update_testdata:
	$(VERB) ./update_testdata.py
