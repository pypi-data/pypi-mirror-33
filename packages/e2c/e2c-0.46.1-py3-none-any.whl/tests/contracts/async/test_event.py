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

from e2c.contracts.async.actor import Actor
from e2c.contracts.async.event import Event
from e2c.integrations.async.graph import Graph


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

@pytest.mark.asyncio
async def test_event__call_runs_callable_function():
    data = []

    async def do_call(val):
        data.append(val)

    actor = new_actor('A', do_call)
    evt = Event(actor, [])
    await evt(1)

    assert data[0] == 1


@pytest.mark.asyncio
async def test_event__call_runs_callable_function_and_continue():
    data = []

    async def append(val):
        data.append(val)

    actor_a = new_actor('A', append)
    actor_b = new_actor('B', append)
    evt = Event(actor_a, [actor_b])
    await evt('a')

    assert data[0] == 'a'
    assert data[1] == 'a'
