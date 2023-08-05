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

import os
import tempfile
from typing import Dict

import pytest

from e2c import Graph
from e2c.actors.visualizer import Visualizer
from e2c.contracts.actor import Actor
from e2c.contracts.const import *
from e2c.contracts.errors import *


# ======================================================= #
# get_graph_file
# ======================================================= #

def get_graph_file(file_name):
    graph_folder = os.path.join(
        os.path.dirname(__file__), 'graph')
    return os.path.join(graph_folder, file_name)


# ======================================================= #
# get_temp_folder
# ======================================================= #

def get_temp_folder():
    dir = os.path.join(tempfile.gettempdir(), 'e2c')
    os.makedirs(dir, exist_ok=True)
    return dir


# ======================================================= #
# run
# ======================================================= #


def test_run__raises_error_when_configuration_is_missing():
    graph = Graph()
    root = Actor(graph, SELF, None)

    folder = get_temp_folder()
    vis = Visualizer({SELF: root})
    with pytest.raises(E2CVisualizeError) as info:
        vis.run(folder)
    assert str(info.value) == 'Graph is empty!'


def test_run__builds_the_visualisation():
    graph = Graph()
    actors: Dict[str, Actor] = {}

    b_actor = Actor(graph, 'B', None, 'comment B')
    actors['B'] = b_actor

    a_actor = Actor(graph, 'A', None, 'comment A')
    a_actor.on('write', Actor(graph, OUT, None))
    a_actor.on('write', b_actor)
    actors['A'] = a_actor

    root = Actor(graph, SELF, None)
    root.on(RUN, a_actor)
    root.on(ERR, Actor(graph, 'E', None))
    root.on(TRC, Actor(graph, 'T', None))
    actors[SELF] = root

    folder = get_temp_folder()
    vis = Visualizer(actors)
    vis.run(folder, name='py-name')
    assert os.path.exists(
        os.path.join(folder, 'py-name.png'))

    # folder could be None or empty -> store to current working dir.
    vis.run(None, name='py-name')
    folder = os.getcwd()
    filename = os.path.join(folder, 'py-name.png')
    assert os.path.exists(filename)
    os.remove(filename)

