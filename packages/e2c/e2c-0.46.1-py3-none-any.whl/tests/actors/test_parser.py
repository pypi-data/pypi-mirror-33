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

from e2c.actors.parser import Parser
from e2c.contracts.actor import Actor


# ======================================================= #
# run
# ======================================================= #

def test_run__call_callbacks():
    def get_actor(name) -> Actor:
        return actors.get(name)

    def add_actor(name, callback, doc):
        actors[name] = Actor(None, name, callback, doc)

    def settings(**values):
        sett.update(**values)

    config = [
        '[rankdir = TB]',
        '[format = png]',
        '[name=test] [label=The label]',

        '.run -- action [doc=This is the docstring]',
        'action.out -- print']

    sett, actors = {}, {}
    Parser(get_actor, add_actor, settings).run(config)

    assert len(actors) == 3
    assert actors['action'].doc == 'This is the docstring'

    assert len(sett) == 4
    assert sett['format'] == 'png'
    assert sett['name'] == 'test'
    assert sett['label'] == 'The label'
    assert sett['rankdir'] == 'TB'
