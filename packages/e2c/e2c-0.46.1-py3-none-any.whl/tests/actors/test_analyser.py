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

from e2c import Graph
from e2c.actors.analyser import Analyser
from e2c.contracts.actor import Actor
from e2c.contracts.errors import *


# ======================================================= #
# run
# ======================================================= #

def test_run__raises_error_without_actor():
    graph = Graph()
    analyser = Analyser({'A': Actor(graph, "A", None)})
    with pytest.raises(E2CAnalyserError) as info:
        analyser.run(quiet=True)

    assert str(info.value) == 'Actor A has no callable function!'


def test_run__raises_error_if_actor_not_callable():
    graph = Graph()
    analyser = Analyser({'A': Actor(graph, "A", 'xxx')})
    with pytest.raises(E2CAnalyserError) as info:
        analyser.run(quiet=False)

    assert str(info.value) == 'Actor A is not a callable function!'


def test_run__raises_error_if_actor_has_unknow_parameter():
    graph = Graph()
    actor_a = Actor(graph, "A", lambda x: None)
    actor_a.on('b', Actor(graph, "B", lambda: None))
    analyser = Analyser({'A': actor_a})
    with pytest.raises(E2CAnalyserError) as info:
        analyser.run(quiet=False)

    assert str(info.value) == 'b on actor A is not a parameter in the callable function!'
