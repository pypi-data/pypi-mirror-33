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
import tempfile
from typing import List
from uuid import uuid1

import pytest

from e2c.actors.loader import Loader
from e2c.contracts.errors import *


# ======================================================= #
# get_temp_folder
# ======================================================= #

def get_temp_file(content: List[str]):
    dir = os.path.join(tempfile.gettempdir(), 'e2c')
    os.makedirs(dir, exist_ok=True)
    file_name = os.path.join(dir, uuid1().hex)
    with open(file_name, 'x') as f:
        for c in content:
            f.write(c + '\n')
    return file_name


# ======================================================= #
# from_file
# ======================================================= #

def test_from_file__load_data_from_file():
    def result(content: List[str]):
        data.extend(content)

    data = []
    f = get_temp_file(['content', 'content'])
    Loader(result).from_file(f)
    assert len(data) == 2


def test_from_file__raises_exception_if_file_not_exits():
    with pytest.raises(E2CLoaderError):
        Loader(lambda x: None).from_file('xxx')


# ======================================================= #
# from_list
# ======================================================= #

def test_from_list__load_data_from_file():
    def result(content: List[str]):
        data.extend(content)

    data = []
    Loader(result).from_list(['content', ['content']])
    assert len(data) == 2
