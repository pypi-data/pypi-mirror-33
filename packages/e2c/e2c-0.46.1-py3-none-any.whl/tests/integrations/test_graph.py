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

import pytest

from e2c import Graph
from e2c.contracts.errors import *


# ======================================================= #
# get_graph_file
# ======================================================= #

def get_graph_file(file_name):
    graph_folder = os.path.join(
        os.path.dirname(__file__), '../graph')
    return os.path.join(graph_folder, file_name)


# ======================================================= #
# parse
# ======================================================= #

def test_parse__raises_error_if_graph_empty():
    with pytest.raises(E2CParserError) as info:
        Graph(['', ])

    assert str(info.value) == 'No data to parse!'


def test_parse__raises_error_when_line_not_found():
    with pytest.raises(E2CParserError) as info:
        Graph(['.run', ''])

    assert str(info.value) == 'Missing -- in line 1!'


def test_parse__raises_error_when_target_not_found():
    with pytest.raises(E2CParserError) as info:
        Graph(['.run --', ''])

    assert str(info.value) == 'Missing actor in line 1!'


def test_parse__raises_error_when_file_not_found():
    graph = Graph()
    with pytest.raises(E2CLoaderError):
        graph.from_file('graph/xxx.e2c')


# ======================================================= #
# run
# ======================================================= #

def test_run__raises_custom_error_when_operation_is_invalid():
    config = (
        '.run -- A',)

    def raise_error():
        raise Exception('Invalid operation')

    graph = Graph(config)
    graph.actor('A', raise_error)
    with pytest.raises(Exception) as info:
        graph.run()

    assert str(info.value) == 'Invalid operation'


def test_run__raises_error_when_run_is_missing():
    config = (
        '.trace -- trace',)

    def trace(name: str):
        pass

    graph = Graph(config)
    graph.actor('trace', trace)
    with pytest.raises(E2CGraphError) as info:
        graph.run()

    assert str(info.value) == 'Missing .run -- ? in graph!'


def test_run__raises_error_when_start_actor_is_not_defined():
    graph = Graph()
    graph.actor('A', lambda value, out: None)
    graph.actor('B', lambda value, out: None)
    graph.from_file(get_graph_file('t1.e2c'))
    with pytest.raises(E2CGraphError) as info:
        graph.run(2, actor="X")

    assert str(info.value) == 'X is not a registered actor!'


def test_run__catch_the_exception_on_actor_when_error_actor_was_defined():
    config = (
        '.err -- error',
        '.run -- A')

    def raise_error():
        raise Exception('Invalid operation')

    def error_handler():
        error['error'] = 1

    error = {}
    graph = Graph(config)
    graph.actor('A', raise_error)
    graph.actor('error', error_handler)
    graph.run()

    assert error


def test_run__starts_the_pipeline_and_run_lambdas():
    config = (
        'A.out -- B',
        '.run -- A')

    data = []
    graph = Graph(config)
    graph.actor('A', lambda data, out: out(data))
    graph.actor('B', lambda d: data.append(d))
    graph.run(1)

    assert data[0] == 1


def test_run__starts_the_pipeline_and_run_methods():
    # class method as actor
    class Dummy():
        def operation(self, value, out):
            out(value + 5)

    # function as actor
    def operation(value, out):
        out(value * 2)

    graph = Graph()
    graph.actor('A', Dummy().operation)
    graph.actor('B', operation)
    graph.from_file(get_graph_file('t1.e2c'))

    assert graph.run(3) == 16
    assert graph.run(3, actor="A") == 16
    assert graph.run(3, actor="B") == 6
    assert graph.run(2, actor="A") == 14

#
# def test_run__starts_the_pipeline_and_run_events():
#     config = (
#         '.run -- A',
#         'A.out -- B',
#         'B.out -- .out'
#     )
#     sub_config = (
#         '.run -- X',
#         'X.out -- Y',
#         'Y.out -- .out'
#     )
#     def operation_a(value, out):
#         sub_graph = Graph(sub_config)
#         sub_graph.name = "subgraph"
#         sub_graph.actor('X', out)
#         sub_graph.actor('Y', operation_y)
#         result = sub_graph.run([value, 1, 2])
#         out(value)
#
#     def operation_b(value, out):
#         out(value)
#
#     def operation_x(value, out):
#         out(value)
#
#     def operation_y(value, out):
#         out(value)
#
#     graph = Graph(config)
#     graph.name = 'rootgraph'
#     graph.actor('A', operation_a)
#     graph.actor('B', operation_b)
#     data = graph.run(1)
#
#     assert data == [1, 1, 2]


def test_run__calls_the_end_actor_when_actor_was_defined():
    data = []
    graph = Graph()
    graph.actor('A', lambda value, out: out(value))
    graph.actor('B', lambda value, out: out(value + 2))
    graph.actor('C', lambda value: data.append(value))
    graph.from_file(get_graph_file('t2.e2c'))
    start_value = 1

    assert graph.run(start_value) == 3
    assert data[0] == start_value


def test_run__calls_the_trace_actor_when_actor_was_defined():
    data = []
    graph = Graph()
    graph.actor('A', lambda value, out: out(value))
    graph.actor('B', lambda value, out: out(value))
    graph.actor('Trace', lambda value: data.append(value))
    graph.from_file(get_graph_file('t3.e2c'))
    graph.run(None)

    assert data == ['A', 'B']


# ======================================================= #
# run_continues
# ======================================================= #

def test_run_continues__continues_the_pipeline():
    data = []
    graph = Graph()
    graph.actor('A', lambda value, out: out(value + 1))
    graph.actor('B', lambda value, out: out(value * 3))
    graph.from_file(get_graph_file('t4.e2c'))
    graph.run_continues(3, lambda value: data.append(value))

    assert data == [12, 12, 12]

# ======================================================= #
# extend
# ======================================================= #
#
# def test_extend__connect_to_remote_actor():
#     data = 'THIS IS THE UPPER TEXT TO TRANSFORM'
#
#     config = (
#         '.run -- action',
#         'action.to_lower -- to_lower'
#     )
#
#     def action(data, to_lower):
#         assert to_lower(data) == data.lower()
#
#     def run_server_to_lower():
#         context = zmq.Context()
#         socket = context.socket(zmq.REP)
#         socket.bind("tcp://*:%s" % 8001)
#         result = json.loads(socket.recv()).lower()
#         socket.send(json.dumps(result).encode())
#
#     def run_graph():
#         graph = Graph(config)
#         graph.actor('action', action)
#         graph.extend('to_lower', Host.tcp('127.0.0.1', 8001))
#         graph.run(data)
#
#     thread1 = Thread(target=run_server_to_lower)
#     thread1.start()
#     thread2 = Thread(target=run_graph)
#     thread2.start()
#     thread1.join()
#     thread2.join()
