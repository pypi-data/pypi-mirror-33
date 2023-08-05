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

from typing import cast, Any, List, Dict

import pytest

from e2c import Graph
from e2c.contracts.actor import Actor
from e2c.contracts.errors import *
from e2c.contracts.event import Event


# ======================================================= #
# new_actor
# ======================================================= #

def new_actor(name: str, callable_obj):
    graph = Graph()
    return Actor(graph, name, callable_obj)


# ======================================================= #
# on
# ======================================================= #

def test_on__empty_name_raises_error():
    actor = new_actor('A', lambda: None)
    with pytest.raises(E2CActorError) as info:
        actor.on('', new_actor('test', lambda: None))

    assert str(info.value) == 'Name cannot be None or empty!'


def test_on__none_name_raises_error():
    actor = new_actor('A', lambda: None)
    with pytest.raises(E2CActorError) as info:
        actor.on(None, new_actor('test', lambda: None))

    assert str(info.value) == 'Name cannot be None or empty!'


def test_on__double_name_is_allowed():
    actor = new_actor('A', lambda: None)
    child_actor1 = new_actor('B', lambda: None)
    child_actor2 = new_actor('C', lambda: None)
    actor.on('B', child_actor1)
    actor.on('B', child_actor2)

    assert len(actor.actors.keys()) == 1
    assert len(actor.actors['B']) == 2


# ======================================================= #
# name
# ======================================================= #

def test_name__each_actor_has_a_name():
    actor = new_actor('A', lambda: None)

    assert actor.name == 'A'


# ======================================================= #
# run
# ======================================================= #


def test_run__raises_error_when_function_is_not_callable():
    actor = new_actor('A', None)
    with pytest.raises(E2CActorError) as info:
        actor.run()
    assert str(info.value) == 'Actor A has no callable function!'


def test_run__calls_a_lambda():
    result = []
    actor = new_actor('A', lambda x: result.append(x))

    assert actor.run(1) == None
    assert result[0] == 1


def test_run__calls_a_function():
    def actor(a):
        result.append(a)

    result = []
    new_actor('A', actor).run(1)

    assert result[0] == 1


def test_run__injects_the_actor_and_call_the_function():
    def actor_a(a):
        result.append(a)

    def actor_b():
        pass

    result = []
    root = new_actor('A', actor_a)
    root.on('a', new_actor('a', actor_b))
    root.run()

    assert isinstance(result[0], Event)
    evt = cast(Event, result[0])
    assert isinstance(evt._actor.callable, type(actor_b))


def test_run__injects_the_actor_with_params_and_call_the_function():
    def actor(a, b, c):
        result.append([a, b, c])

    result = []
    actor = new_actor('A', actor)
    params = [1, True, 'dat']
    actor.run_with_params(*params)

    assert result[0] == [1, True, 'dat']


# ======================================================= #
# spec
# ======================================================= #

def test_spec__returns_the_parameters_from_function_actor():
    def actor(a, b: str, c: int, d: bool, e: float, f: List, g: Dict):
        pass

    params = new_actor('A', actor).specs

    assert len(params) == 7
    assert params['a'] == Any
    assert params['b'] == str
    assert params['c'] == int
    assert params['d'] == bool
    assert params['e'] == float
    assert params['f'] == List
    assert params['g'] == Dict


def test_spec__returns_the_parameters_from_method_actor():
    class Dummy(object):
        def actor(self, a, b: str):
            pass

    params = new_actor('A', Dummy().actor).specs

    assert len(params) == 2
    assert params['a'] == Any
    assert params['b'] == str


# ======================================================= #
# clone
# ======================================================= #

def test_clone__returns_a_deep_clone():
    def actor():
        pass

    cln = new_actor('A', actor)
    cln.on('B', new_actor('B', actor))
    cln.on('C', new_actor('C', actor))
    clone = cln.clone()

    assert clone.name == 'A'
    assert clone.callable == actor
    assert len(clone.actors) == 2

    assert len(clone.actors['B']) == 1
    assert clone.actors['B'][0].callable == actor
    assert clone.actors['C'][0].callable == actor
