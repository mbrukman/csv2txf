# Copyright 2024 Google LLC
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

from __future__ import annotations

import sys


if (sys.version_info.major, sys.version_info.minor) >= (3, 12):
    # This was added in Python 3.12:
    #
    # * https://docs.python.org/3/library/typing.html#typing.override
    # * https://peps.python.org/pep-0698/
    from typing import override
else:
    from typing import TypeVar

    _F = TypeVar('_F')

    def override(func: _F) -> _F:
        """No-op @override for Python versions prior to 3.12."""
        return func
