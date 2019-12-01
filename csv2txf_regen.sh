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

for csv in testdata/*.csv; do
  out="${csv%.csv}.out"
  echo -n "Updating ${out} ... "
  $(dirname $0)/csv2txf.py -f "${csv}" -o "${out}" --year 2011 --date "04/15/2012"
  echo "done."
done
