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

from e2c import Graph
from e2c.actors.resolve import resolve
from e2c.contracts.actor import Actor
from e2c.contracts.event import Event


# ======================================================= #
# new_actor
# ======================================================= #

def new_actor(name: str, callable):
    graph = Graph()
    return Actor(graph, name, callable)


# ======================================================= #
# call
# ======================================================= #

def test_resolve__call_returns_parameter_list():
    def actor(a, b, c, func_a, func_b):
        pass

    actor = new_actor('A', actor)
    result1 = resolve(actor, [1, 'data', True], Event)
    result2 = resolve(actor, [], Event)

    assert len(result1) == 5
    assert result1 == [1, 'data', True, None, None]
    assert result2 == [None, None, None, None, None]
