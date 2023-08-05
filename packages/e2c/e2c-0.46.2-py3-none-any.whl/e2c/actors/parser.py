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

from typing import Callable
from typing import List, Tuple

from e2c.contracts.actor import Actor
from e2c.contracts.const import *
from e2c.contracts.errors import *


# ======================================================= #
# PARSER
# ======================================================= #

class Parser(object):
    """
    Represents a class to parse the graph and build relations between them.
    """

    def __init__(self,
                 get_actor: Callable[[str], Actor],
                 add_actor: Callable[[str, Callable or None, str], None],
                 settings: Callable[[dict], None]):
        """
        Represents a class to parse the graph and build relations between them.

        :type get_actor: Callable[[str], Actor]
        :param get_actor: The function to get an actor by name.

        :type add_actor: Callable[[str, Callable, str], None]
        :param add_actor: The function to add an actor.

        :type settings: Callable[[dict], None]
        :param settings: The function to updates the settings.

        """
        self._get_actor = get_actor
        self._add_actor = add_actor
        self._settings = settings

    def run(self, script: List[str] or Tuple[str]):
        """
        Starts the parsing.

        :type script: List[str]
        :param script: The script to parse.

        :rtype: None
        """
        if not ''.join(script):
            raise E2CParserError('No data to parse!')

        for index, line in enumerate(script, 1):
            line = line.strip()
            pos = line.find(COMMENT)
            if pos >= 0:
                line = line[:pos] if line else None
            if not line:
                continue

            diagram_settings = get_diagram_settings(line)
            if diagram_settings:
                self._settings(**diagram_settings)
                continue

            info_pos = line.find('[')
            actor_line = line[0:info_pos] if info_pos > 0 else line
            actor_line = actor_line.replace('\n', '').replace(' ', '').strip()

            if EDGE not in line:
                raise E2CParserError(
                    'Missing {} in line {}!'.format(EDGE, index))

            left_actor_name_and_param, right_actor_name = actor_line.split(EDGE)
            if not right_actor_name:
                raise E2CParserError(
                    'Missing actor in line {}!'.format(index))

            items = left_actor_name_and_param.split('.')
            left_actor_name, left_param = '.'.join(items[0:-1]), items[-1]
            left_actor_name = left_actor_name or SELF

            if not self._get_actor(left_actor_name):
                self._add_actor(left_actor_name, None, '')
            if not self._get_actor(right_actor_name):
                actor_settings = get_actor_settings(line)
                self._add_actor(right_actor_name, None, actor_settings.get(DOC))

            self._get_actor(left_actor_name).on(
                left_param, self._get_actor(right_actor_name))


# ======================================================= #
# GET_DIAGRAM_SETTINGS
# ======================================================= #

def get_diagram_settings(line: str) -> dict:
    data = {}
    start_pos = end_pos = line.find('[')
    while start_pos > -1:
        end_pos = line.find(']', end_pos + 1)
        if start_pos > -1 and end_pos > 0:
            key, value = line[start_pos + 1: end_pos].split('=')
            key, value = key.strip(), value.strip()
            if key == NAME:
                data[NAME] = value
            elif key == LABEL:
                data[LABEL] = value
            elif key == DIR:
                data[DIR] = value.upper()
            elif key == FORMAT:
                data[FORMAT] = value.lower()
        start_pos = line.find('[', start_pos + 1)
    return data

# ======================================================= #
# GET_ACTOR_SETTINGS
# ======================================================= #

def get_actor_settings(line: str) -> dict:
    data = {}
    start_pos = end_pos = line.find('[')
    while start_pos > -1:
        end_pos = line.find(']', end_pos + 1)
        if start_pos > -1 and end_pos > 0:
            key, value = line[start_pos + 1: end_pos].split('=')
            key, value = key.strip(), value.strip()
            if key == 'doc':
                data[DOC] = value
        start_pos = line.find('[', start_pos + 1)
    return data

