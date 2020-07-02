#!/bin/bash
#
# Copyright 2020 Google LLC
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

# To regenerate expected stdout in response to changes in the code, run this
# test with the arg `regen`.
declare -i regen=0
if [ "${1:-}" == "regen" ]; then
  regen=1
fi

declare -i num_failures=0

# Args:
#   $0: file with expected stdout
#   $*: command-line flags for csv2txf.py for this run
function test_summary() {
  local expected_out="$1"
  shift

  if [ $regen -ne 0 ]; then
    echo "Updating ${expected_out} ..."
    ./csv2txf.py "$@" > "${expected_out}"
    return
  fi

  echo "Testing ${expected_out/.summary.out/} ..."
  local out="$(mktemp /tmp/csv2txf-summary.out.XXXXXX)"
  local err="$(mktemp /tmp/csv2txf-summary.err.XXXXXX)"
  ./csv2txf.py "$@" > "${out}" 2> "${err}"

  diff -u "${expected_out}" "${out}" || {
    cat "${err}"
    (( num_failures += 1 ))
  }
}

test_summary \
    testdata/interactive_brokers.summary.out \
    --broker ib \
    --file testdata/interactive_brokers.csv \
    --year 2011 \
    --outfmt summary

test_summary \
    testdata/vanguard.summary.out \
    --broker vanguard \
    --file testdata/vanguard.csv \
    --year 2011 \
    --outfmt summary

if [ ${regen} -eq 0 ]; then
  if [ ${num_failures} -eq 0 ]; then
    echo "PASSED"
  else
    echo "FAILED"
    exit 1
  fi
fi
