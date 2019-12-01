#!/bin/bash -u
#
# Copyright 2019 Google LLC
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

for csv in testdata/*.csv; do
  echo -n "Testing ${csv} ... "
  base_csv="$(basename "${csv}")"
  actual_out="$(mktemp "/tmp/csv2txf_test.${base_csv}.out.XXXXXX")"
  actual_err="$(mktemp "/tmp/csv2txf_test.${base_csv}.err.XXXXXX")"
  output_diff="$(mktemp "/tmp/csv2txf_test.${base_csv}.out_diff.XXXXXX")"
  expected_out="${csv%.csv}.out"

  $(dirname $0)/csv2txf.py -f "${csv}" -o "${actual_out}" \
      --year 2011 --date "04/15/2012" \
      2> "${actual_err}"

  diff -u "${expected_out}" "${actual_out}" > "${output_diff}" 2>&1
  if [[ $? -eq 0 ]]; then
    echo "PASSED."
  else
    echo "FAILED."
    cat "${output_diff}"
    if [[ $(wc -l < "${actual_err}") -gt 0 ]]; then
      echo "Additional warnings & errors:"
      cat "${actual_err}"
    fi
    success=1
  fi

  rm -f "${actual_out}" "${actual_err}" "${output_diff}"
done

exit ${success}
