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
from e2c.contracts.actor import Actor
from e2c.contracts.event import Event


# ======================================================= #
# new_actor
# ======================================================= #

def new_actor(name: str, callable):
    graph = Graph()
    return Actor(graph, name, callable)


# ======================================================= #
# __repr___
# ======================================================= #

def test_repr__returns_name_of_actor():
    data = []
    actor = new_actor('A', lambda val: data.append(val))
    evt = Event(actor, [])
    assert "-- {} {}".format(actor.name, str(type(evt))).strip() == str(evt)


# ======================================================= #
# call
# ======================================================= #

def test_call__runs_callable_function():
    data = []
    actor = new_actor('A', lambda val: data.append(val))
    evt = Event(actor, [])
    evt(1)
    assert data[0] == 1


def test_call__runs_callable_function_and_continue():
    data = []
    actor_a = new_actor('A', lambda val: data.append(val))
    actor_b = new_actor('B', lambda val: data.append(val))
    evt = Event(actor_a, [actor_b])
    evt('a')

    assert data[0] == 'a'
    assert data[1] == 'a'
