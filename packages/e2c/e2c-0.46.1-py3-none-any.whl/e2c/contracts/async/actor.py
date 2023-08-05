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
from typing import List

from e2c.actors.resolve import resolve
from e2c.contracts.actor import Actor as _Actor
from e2c.contracts.async.event import Event
from e2c.contracts.errors import *


# ======================================================= #
# ACTOR
# ======================================================= #

class Actor(_Actor):
    """
    A wrapper around a callable function.
    """

    def __init__(self, graph, name: str, callable: None or Callable, doc: str = '') -> None:
        """
        A wrapper around a callable function.

        :type graph: :class:`e2c.graph.Graph`
        :param graph: The graph to that the actor belong.

        :type name: str
        :param name: The name of the actor to register on the graph.

        :type callable: Callable
        :param callable: Any callable function.

        :type doc: str
        :param doc: The document string of the actor.
        """
        super(Actor, self).__init__(graph, name, callable, doc)

    async def run(self, *args) -> object:
        """
        Runs the callable internal function with specified arguments.

        :type args: *args
        :param args: A list of arguments.

        :rtype: object
        :return: The result of the callable function.
        """
        params = resolve(self, [*args], Event)
        if self.graph.activate_trace:
            await self.graph.on_trace(self.name)
        if not self.callable:
            raise E2CActorError(
                'Actor {0} has no callable function!'.format(self.name))
        return await self.callable(*params)

    async def run_with_params(self, *params) -> object:
        """
        Runs the callable internal function with specified parameters.

        :type params: List[Callable]
        :param params: A list of parameters

        :rtype: object
        :return: The result of the callable function.
        """
        if self.graph.activate_trace:
            await self.graph.on_trace(self.name)
        return await self.callable(*params)
