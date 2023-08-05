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

from typing import Dict
from typing import Generic
from typing import List
from typing import Tuple

from e2c.actors.analyser import Analyser
from e2c.actors.graph import BaseGraph
from e2c.actors.graph import Response, Request
from e2c.actors.loader import Loader
from e2c.actors.parser import Parser
from e2c.actors.visualizer import Visualizer
from e2c.contracts.actor import Actor

GRAPHS = {}

# ======================================================= #
# GRAPH
# ======================================================= #

class Graph(Generic[Request, Response], BaseGraph[Request, Response]):
    """
    A class for running E2C operations.
    A `Graph` object encapsulates the environment in which `Actor`
    objects are executed.
    """

    def __init__(self, script: Tuple[str] or List[str] = None):
        """
        A class for running E2C operations.

        :type script: Tuple[str] or List[str]
        :param script: The script to builds the graph.
        """
        actors: Dict[str, Actor] = {}
        analyser = Analyser(actors)
        visualizer = Visualizer(actors)
        parser = Parser(self.get_actor, self.actor, self.settings)
        loader = Loader(parser.run)

        super(Graph, self).__init__(
            actors,
            analyser.run,
            loader.from_list,
            loader.from_file,
            visualizer.run,
            script)
