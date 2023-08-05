#
# Copyright 2017 The E2C Authors. All Rights Reserved.
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
# ==============================================================================

from typing import List, Callable

from e2c.contracts.errors import *


# ======================================================= #
# LOADER
# ======================================================= #

class Loader(object):
    """
    Represents a class to load graph mappings.
    """

    def __init__(self, result: Callable[[List[str]], None]):
        """
        Expects the graph and the parser to load
        the configuration via various methods.
        :param parser: The parser to parse.
        """
        self._result = result

    def from_file(self, file_name: str):
        """
         Opens the specified file and builds up the graph.

        :type  file_name: str
        :param file_name: The filename to load from file.
        :return:
        """
        try:
            with open(file_name, 'r') as f:
                self.from_list(f.readlines())
        except Exception as exc:
            raise E2CLoaderError(exc)

    def from_list(self, script: List[str]) -> None:
        """
        Parses the script and builds the graph.

        :type script: List[str]
        :param script: The script to parse.

        :rtype: None
        """
        self._result(script)
