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
from typing import Awaitable
from typing import Callable

import pytest

from e2c.actors.async.graph import BaseGraph
from e2c.contracts.errors import *
from e2c.integrations.async.graph import Graph


# ======================================================= #
# get_graph_file
# ======================================================= #

def get_graph_file(file_name):
    graph_folder = os.path.join(
        os.path.dirname(__file__), '../../graph')
    return os.path.join(graph_folder, file_name)


# ======================================================= #
# analyse
# ======================================================= #

@pytest.mark.asyncio
async def test_analyse__analyse_runs_the_analyser():
    def analyse(quit=True):
        data.append(quit)

    data = []
    graph = BaseGraph({}, analyse, None, None, None, None)
    graph.analyse(quiet=True)

    assert data[0] == True


# ======================================================= #
# visualize
# ======================================================= #

@pytest.mark.asyncio
async def test_visualize__runs_the_visualizer():
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
        data.append(folder)
        data.append(config)

    data = []
    graph = BaseGraph({}, None, None, None, visualize, None)
    graph.actor('A', lambda a: None, 'The document string')
    graph.visualize('test_folder')

    assert graph.get_actor('A').doc == 'The document string'


# ======================================================= #
# actor
# ======================================================= #
@pytest.mark.asyncio
async def test_actor__call_raise_error_on_double_name():
    async def out():
        pass

    graph = Graph()
    graph.actor('A', out)
    with pytest.raises(E2CGraphError) as info:
        await graph.actor('A', out)
    assert str(info.value) == 'Actor A was already registered!'


# ======================================================= #
# parse
# ======================================================= #
@pytest.mark.asyncio
async def test_parse__raise_error_if_graph_empty():
    with pytest.raises(E2CParserError) as info:
        Graph(['', ])
    assert str(info.value) == 'No data to parse!'


@pytest.mark.asyncio
async def test_parse__raise_error_when_line_not_found():
    with pytest.raises(E2CParserError) as info:
        Graph(['.run', ''])
    assert str(info.value) == 'Missing -- in line 1!'


@pytest.mark.asyncio
async def test_parse__raise_error_when_target_not_found():
    with pytest.raises(E2CParserError) as info:
        Graph(['.run --', ''])
    assert str(info.value) == 'Missing actor in line 1!'


@pytest.mark.asyncio
async def test_parse__raise_error_when_file_not_found():
    graph = Graph()
    with pytest.raises(E2CLoaderError):
        graph.from_file('graph/xx.e2c')


# ======================================================= #
# run
# ======================================================= #
@pytest.mark.asyncio
async def test_run__raise_custom_error_when_operation_is_invalid():
    config = (
        '.run -- A',)

    def raise_error():
        raise Exception('Invalid operation')

    graph = Graph(config)
    graph.actor('A', raise_error)
    with pytest.raises(Exception) as info:
        await graph.run()
    assert str(info.value) == 'Invalid operation'


@pytest.mark.asyncio
async def test_run__raise_error_when_run_is_missing():
    config = (
        '.trace -- trace',)

    async def trace(name: str):
        pass

    graph = Graph(config)
    graph.actor('trace', trace)
    with pytest.raises(E2CGraphError) as info:
        await graph.run()
    assert str(info.value) == 'Missing .run -- ? in graph!'


@pytest.mark.asyncio
async def test_run__raise_error_when_start_actor_is_not_defined():
    async def output(val, out):
        pass

    graph = Graph()
    graph.actor('A', output)
    graph.actor('B', output)
    graph.from_file(get_graph_file('t1.e2c'))
    with pytest.raises(E2CGraphError) as info:
        await graph.run(2, actor="X")
    assert str(info.value) == 'X is not a registered actor!'


@pytest.mark.asyncio
async def test_run__catch_the_exception_on_actor_when_error_actor_was_defined():
    config = (
        '.err -- error',
        '.run -- A')

    async def raise_error():
        raise Exception('Invalid operation')

    async def error_handler():
        error['error'] = 1

    error = {}
    graph = Graph(config)
    graph.actor('A', raise_error)
    graph.actor('error', error_handler)
    await graph.run()

    assert error


@pytest.mark.asyncio
async def test_run__starts_the_pipeline_and_run_lambdas():
    config = (
        'A.out -- B',
        '.run -- A')

    async def output(val, out: Callable[[int], Awaitable]):
        await out(val)

    async def append(val):
        data.append(val)

    data = []
    graph = Graph(config)
    graph.actor('A', output)
    graph.actor('B', append)
    await graph.run(1)

    assert data[0] == 1


@pytest.mark.asyncio
async def test_run__starts_the_pipeline_and_run_methods():
    # class method as actor
    class Dummy():
        async def operation(self, value, out: Callable[[int], Awaitable]):
            await out(value + 5)

    # function as actor
    async def operation(value, out: Callable[[int], Awaitable]):
        await out(value * 2)

    graph = Graph()
    graph.actor('A', Dummy().operation)
    graph.actor('B', operation)
    graph.from_file(get_graph_file('t1.e2c'))

    assert await graph.run(3) == 16
    assert await graph.run(3, actor="A") == 16
    assert await graph.run(3, actor="B") == 6
    assert await graph.run(2, actor="A") == 14

#
# @pytest.mark.asyncio
# async def test_run__starts_the_pipeline_and_run_events():
#     config = (
#         '.run -- A',
#         'A.out -- B',
#         'B.out -- .out')
#
#     async def operation_a(value, out):
#         sub_graph = Graph(config)
#         sub_graph.actor('A', out)
#         sub_graph.actor('B', operation_c)
#         result = await sub_graph.run([value, 1, 2])
#         await out(result)
#
#     async def operation_b(value, out):
#         await out(value)
#
#     async def operation_c(value, out):
#         await out(value)
#
#     graph = Graph(config)
#     graph.actor('A', operation_a)
#     graph.actor('B', operation_b)
#     data = await graph.run(1)
#
#     assert data == [1, 1, 2]


@pytest.mark.asyncio
async def test_run__calls_the_end_actor_when_actor_was_defined():
    async def plus_one(val, out: Callable[[int], Awaitable]):
        await out(val + 1)

    async def append(val):
        data.append(val)

    data = []
    graph = Graph()
    graph.actor('A', plus_one)
    graph.actor('B', plus_one)
    graph.actor('C', append)
    graph.from_file(get_graph_file('t2.e2c'))

    start_value = 1
    assert await graph.run(start_value) == 3
    assert data[0] == start_value


@pytest.mark.asyncio
async def test_run__calls_the_trace_actor_when_actor_was_defined():
    data = []

    async def output(val, out: Callable[[int], Awaitable]):
        await out(val)

    async def trace(val):
        data.append(val)

    graph = Graph()
    graph.actor('A', output)
    graph.actor('B', output)
    graph.actor('Trace', trace)
    graph.from_file(get_graph_file('t3.e2c'))

    await graph.run(None)
    assert data == ['A', 'B']


# ======================================================= #
# run_continues
# ======================================================= #

@pytest.mark.asyncio
async def test_run_continues__continues_the_pipeline():
    data = []

    async def plus_1(val, out: Callable[[int], Awaitable]):
        await out(val + 1)

    async def mult_3(val, out: Callable[[int], Awaitable]):
        await out(val * 3)

    async def append(val):
        data.append(val)

    graph = Graph()
    graph.actor('A', plus_1)
    graph.actor('B', mult_3)
    graph.from_file(get_graph_file('t4.e2c'))

    await graph.run_continues(3, append)
    assert data == [12, 12, 12]
