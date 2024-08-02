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

# To regenerate expected stdout in response to changes in the code, run this
# test with the arg `regen`.
declare -i regen=0
if [ "${1:-}" == "regen" ]; then
  regen=1
fi

declare -i num_failures=0

# macOS 12+ doesn't provide /usr/bin/python, but provides /usr/bin/python3
PYTHON=""
if ! [[ -f "/usr/bin/python" ]] && [[ -f "/usr/bin/python3" ]]; then
  PYTHON="python3"
fi

# Args:
#   $0: file with expected stdout
#   $*: command-line flags for csv2txf.py for this run
function test_csv2txf() {
  local expected_out="$1"
  shift

  if [ $regen -ne 0 ]; then
    echo "Updating ${expected_out} ..."
    ${PYTHON} ./csv2txf.py "$@" -o "${expected_out}"
    return
  fi

  echo "Testing ${expected_out} ..."
  local base="$(basename ${expected_out})"
  local out="$(mktemp /tmp/csv2txf.${base}.out.XXXXXX)"
  local err="$(mktemp /tmp/csv2txf.${base}.err.XXXXXX)"
  ${PYTHON} ./csv2txf.py "$@" -o "${out}" 2> "${err}"

  diff -u "${expected_out}" "${out}" || {
    cat "${err}"
    (( num_failures += 1 ))
  }
}

test_csv2txf \
    testdata/interactive_brokers.out \
    --broker ib \
    --file testdata/interactive_brokers.csv \
    --year 2011 \
    --date "04/15/2012" \
    --outfmt txf

test_csv2txf \
    testdata/interactive_brokers.summary.out \
    --broker ib \
    --file testdata/interactive_brokers.csv \
    --year 2011 \
    --outfmt summary

test_csv2txf \
    testdata/tdameritrade.out \
    --broker tdameritrade \
    --file testdata/tdameritrade.csv \
    --year 2020 \
    --date "04/15/2021" \
    --outfmt txf

test_csv2txf \
    testdata/tdameritrade.summary.out \
    --broker tdameritrade \
    --file testdata/tdameritrade.csv \
    --year 2020 \
    --outfmt summary

test_csv2txf \
    testdata/vanguard.out \
    --broker vanguard \
    --file testdata/vanguard.csv \
    --year 2011 \
    --date "04/15/2012" \
    --outfmt txf

test_csv2txf \
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
