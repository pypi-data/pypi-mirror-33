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
from typing import Dict
from subprocess import check_call

from e2c.contracts.actor import Actor
from e2c.contracts.const import *
from e2c.contracts.errors import *


# ======================================================= #
# VISUALIZER
# ======================================================= #

class Visualizer(object):
    """
    The class to visualize actors and relations.
    """

    def __init__(self, actors: Dict[str, Actor]):
        """
        The class to visualize actors and relations.

        :type actors: :class:`Dict[str, Actor]`
        :param actors: The actors to analyse.
        """
        self._actors = actors

    def run(self, folder: str or None, **config):
        """
        Starts the visualizing.

        :type folder: str or None
        :param folder: The folder to store the output.

        :rtype: None
        """
        script = self._create_script(config)
        self._write_graph(folder, script, config)

    def _create_script(self, config) -> str:
        """
         Creates the script to builds the graph.

        :param config: The configuration.
        :return: Returns the script as a string.
        """
        script, any_actor = [], False
        for left_actor_name, left_actor in self._actors.items():
            for left_param, right_actors in left_actor.actors.items():

                any_actor = True
                if left_actor_name == SELF:
                    script.append(self._node(left_actor_name, 'color=orange'))

                for relation_actor in right_actors:
                    if relation_actor.name == OUT:
                        script.append(self._node(relation_actor.name, 'color=orange'))

                    attribute = 'label={0}'.format(left_param)
                    if left_param == ERR:
                        attribute += " color=red fontcolor=red"
                    if left_param == TRC:
                        attribute += " color=darkorchid1 fontcolor=darkorchid1"

                    script.append(
                        self._edge(left_actor_name, relation_actor.name, attribute))

                    if relation_actor.doc:
                        comment_node_name = relation_actor.name + '_comment'
                        node_attr = 'shape=note color=gray fontcolor=gray30 label="{0}"'.format(relation_actor.doc)
                        script.append(self._node(comment_node_name, node_attr))
                        edge_attr = 'color=gray style=dashed arrowtail=none'
                        script.append(self._edge(comment_node_name, relation_actor.name, edge_attr))

        if not any_actor:
            raise E2CVisualizeError('Graph is empty!')

        template = self._get_template()
        template = template.replace('[LABEL]', config.get(LABEL, ''))
        template = template.replace('[DIR]', config.get(DIR, 'LR'))
        return template.replace('[SCRIPT]', ''.join(script))

    @staticmethod
    def _node(name: str, attribute: str):
        """
        Creates an node.

        :param name: The name of the node.
        :param attribute: The attributes.
        :return: A string to represents the node.
        """
        return '"{0}" [{1}]\n'.format(name, attribute)

    @staticmethod
    def _edge(node1: str, node2: str, attribute: str):
        """
        Creates an edge to link nodes.

        :param node1: The first node.
        :param node2: The second node.
        :param attribute: The attributes.
        :return: A string to represents the edge.
        """
        return '"{0}" -> "{1}" [{2}]\n'.format(node1, node2, attribute)

    @staticmethod
    def _get_template():
        """
        Gets the graph template.

        :return:
        """
        return """ 
            digraph {
                graph [label="[LABEL]" fontcolor=gray30, rankdir=[DIR] labeljust=r]
                node [color=gray fontcolor=gray30 penwidth=2.0 shape=box style=rounded]
                edge [color=gray fontcolor=gray30 penwidth=2.0 arrowtail=dot arrowhead=normal dir=both]
                [SCRIPT]
            }"""

    @staticmethod
    def _write_graph(folder: str, graph_source: str, config) -> None:
        """
        Writes the graph in specified folder.

        :param folder: The folder to write in.
        :param graph_source: The source of the graph.
        :param config: The configuration.
        :return: None
        """

        if folder:
            os.makedirs(folder, exist_ok=True)
        else:
            folder = os.getcwd()

        format = config.get('format', 'png')
        name = config.get(NAME, DEFAULT)
        file_name = '{0}.{1}'.format(os.path.join(folder, name), format)
        dot_file = '{0}.dot'.format(file_name)
        with open(dot_file, "w+") as f:
            f.write(graph_source)
        try:
            params = ['dot', '-T{0}'.format(format), dot_file, '-o', file_name]
            check_call(params)
        finally:
            if os.path.exists(dot_file):
                os.remove(dot_file)