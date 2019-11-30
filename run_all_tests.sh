#!/bin/bash -u
#
# Copyright 2019 Google Inc.
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

declare -i success=0

for t in *_test.py ; do
  echo -n "Testing ${t} ... "
  test_out="$(mktemp "/tmp/csv2txf.${t}.XXXXXX")"
  ./${t} > "${test_out}" 2>&1
  if [[ $? -eq 0 ]]; then
    echo "PASSED."
  else
		echo "FAILED."
    cat "${test_out}"
    success=1
  fi
  rm -f "${test_out}"
done

exit ${success}
