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

import pytest

from e2c.actors.graph import BaseGraph
from e2c.contracts.errors import *


# ======================================================= #
# analyse
# ======================================================= #


def test_analyse__runs_the_analyser():
    def analyse(quit=True):
        data.append(quit)

    data = []
    graph = BaseGraph({}, analyse, None, None, None, None)
    graph.analyse(quiet=True)

    assert data[0] == True


# ======================================================= #
# visualize
# ======================================================= #

def test_visualize__runs_the_visualizer():
    def visualize(folder: str, **config):
        data.append(folder)
        data.append(config)

    data = []
    graph = BaseGraph({}, None, None, None, visualize, None)
    graph.settings(name='test')
    graph.visualize('test_folder')

    assert data[0] == 'test_folder'
    assert data[1]['name'] == 'test'


# ======================================================= #
# comments
# ======================================================= #

def test_comments__runs_the_visualizer_with_comments():
    def visualize(folder: str, **config):
        pass

    graph = BaseGraph({}, None, None, None, visualize, None)
    graph.actor('A', lambda a: None, 'The document string')
    graph.visualize('test_folder')

    assert graph.get_actor('A').doc == 'The document string'


# ======================================================= #
# actor
# ======================================================= #

def test_actor__call_raises_error_on_double_name():
    graph = BaseGraph({}, None, None, None, None, None)
    graph.actor('A', lambda: None)
    with pytest.raises(E2CGraphError) as info:
        graph.actor('A', lambda: None)

    assert str(info.value) == 'Actor A was already registered!'
