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
from typing import Dict
from typing import Generic
from typing import List

from e2c.actors.graph import Response, Request
from e2c.contracts.async.actor import Actor
from e2c.contracts.async.event import Event
from e2c.contracts.const import *
from e2c.contracts.errors import *


# ======================================================= #
# RESULT
# ======================================================= #


class Result(object):
    """ The result class to represents the result.
    """

    def __init__(self):
        self.value = None
        self.value_callback = None

    async def set(self, data: object) -> None:
        """
        The method to set the value.

        :type data: object
        :param data: Any data.
        :rtype: None
        """
        if self.value_callback:
            await self.value_callback(data)
        else:
            self.value = data


class BaseGraph(Generic[Request, Response]):
    """ 
    The core graph brings all components together.
    """

    def __init__(self,
                 actors: Dict[str, Actor],
                 analyse: Callable[[bool], None],
                 from_list: Callable[[List[str]], None],
                 from_file: Callable[[str], None],
                 visualize: Callable[[str, dict], None],
                 script: List[str] = None):
        """
        Creates a new graph.

        :type actors: :class:`Dict[str, Actor]`
        :param actors: The actors to work with.

        :type analyse: :class:`Callable[[bool], None]`
        :param analyse: The function to analyse.

        :type from_list: :class:`Callable[[List[str]], None]`
        :param from_list: The function to load data from list.

        :type from_file: :class:`Callable[[str], None]`
        :param from_file: The function to load data from file.

        :type visualize: :class:`Callable[[str, dict], None]`
        :param visualize: The function to visualize the graph.

        :type script: :class:`List[str]`
        :param script: The string list of the graph to parse.
        """
        self._analyse = analyse
        self._from_list = from_list
        self._from_file = from_file
        self._visualize = visualize
        self._result = Result()
        self._tracer = None
        self._end = None
        self._actors = actors
        self._settings = {}
        self.actor(SELF, self._process)
        self.actor(OUT, self._result.set)
        self.activate_trace = True
        if script:
            self.from_list(script)

    async def _process(
            self,
            request: Request,
            run: Callable,
            end: Callable = None,
            err: Callable = None,
            trace: Callable = None) -> None:
        """
        The method to start the first actor after call 'run'.

        :type request: 'Request'
        :param request: The data to be transmitted.

        :type run: Callable
        :param run: The run function.

        :type end: Callable
        :param end: The end function.

        :type err: Callable
        :param err: The error function.

        :type trace: Callable
        :param trace: The trace function.

        :rtype: None
        """
        try:
            self._tracer = trace
            self._end = end
            if not run:
                raise E2CGraphError(
                    'Missing .{} -- ? in graph!'.format(RUN))
            await run(request)
        except Exception as exc:
            if not err: raise exc
            await err(exc)

    async def on_trace(self, name: str) -> None:
        """
        The method to track the trace path.

        :type name: str
        :param name: The name of the running actor.
        :rtype: None
        """
        if self._tracer:
            try:
                # deactivate trace in tracing process
                # to avoid recursion
                self.activate_trace = False
                if name != OUT:
                    await self._tracer(name)
            finally:
                self.activate_trace = True

    def settings(self, **values) -> None:
        """
        Updates the settings of the graph.

        :param values: The values of the settings.
        :rtype: None
        """
        self._settings.update(**values)

    def actor(self, name: str, callable: Callable, doc: str = '') -> None:
        """
        Registers a new actor by specified name and the callable function or method or class.

        :type name: str
        :param name: The name under which the function can be called..

        :type callable: Callable
        :param callable: The callable function or method or class.

        :type doc: str
        :param doc: The document string of the actor.

        :rtype: None
        """
        if isinstance(callable, Event) and callable._actor:
            callable = callable._actor.callable
        if name in self._actors and self._actors[name].callable:
            raise E2CGraphError(
                'Actor {} was already registered!'.format(name))
        if name not in self._actors:
            self._actors[name] = Actor(self, name, None, doc)
        self._actors[name].callable = callable

    def get_actor(self, name: str) -> Actor:
        """
        Returns the actor by specified name or None
        :param name: The name of the actor.
        :return: The actor.
        """
        return self._actors.get(name, None)

    def analyse(self, quiet=True) -> None:
        """
        Starts the analyser.

        :type quiet: bool
        :param quiet: True to print out messages.
        :rtype: None
        """
        self._analyse(quiet)

    def visualize(self, folder: str = None) -> None:
        """
        Starts the visualiser.

        :type folder: str
        :param folder: The directory where the graph is written.

        :rtype: None
        """
        self._visualize(folder, **self._settings)

    def from_list(self, list: List[str]):
        """
        Loads the graph mappings from list.
        :param list: The mapping data.
        :return: None
        """
        return self._from_list(list)

    def from_file(self, file_name: str):
        """
        Loads the graph mappings from file.
        :param file_name: The filename to load.
        :return:
        """
        return self._from_file(file_name)

    async def run(self, request: Request = None, actor: str = None) -> Response:
        """
        Runs the graph and returns the return value.

        :type request: Request
        :param request: The data to be transmitted

        :type actor: str
        :param actor: The optional name of the actor to start.

        :rtype: Response
        :return: The return value.
        """
        self.analyse(True)
        if not actor:
            await self._actors[SELF].run(request)
        else:
            if actor not in self._actors:
                raise E2CGraphError(
                    '{} is not a registered actor!'.format(actor))
            runner = self._actors[SELF].clone()
            runner.actors[RUN].clear()
            runner.on(RUN, self._actors[actor])
            await runner.run(request)
        if self._end:
            await self._end._actor.run(request)
        return self._result.value

    async def run_continues(
            self, request: Request = None,
            result: Callable[[Response], None] = None, actor: str = None) -> None:
        """
        Runs the graph and calls a result callback.

        :type request: Request
        :param request: The data to be transmitted.

        :type result: Callable[[Response], None]
        :param result: The result callback.

        :type actor: str
        :param actor: The optional name of the actor to start.

        :rtype: None
        """
        self._result.value_callback = result
        await self.run(request, actor)