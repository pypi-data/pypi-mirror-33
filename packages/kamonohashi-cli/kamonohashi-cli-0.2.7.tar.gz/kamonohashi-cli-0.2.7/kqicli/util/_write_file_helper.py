# -*- coding: utf-8 -*-
# Copyright 2018 NS Solutions Corporation.
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
from __future__ import print_function, absolute_import, with_statement

import os
import math
import json
from os import path
from tqdm import tqdm

from kamonohashi.util._encoder import resolve_encode


def save_file(dst, name, stream):
    """save a file from stream data

    :param str dst: destination path to save file
    :param name:
    :param stream:
    :return:
    """
    # Pythonの最低な仕様のため、2ではxが使えないため上書きを許可するwを使うこととする
    # with open(path.join(dst, model.name), 'xb') as f:
    chunk_size = 1024
    p = path.abspath(dst)
    if not path.exists(p):
        os.makedirs(p)
    print('Downloading {0}'.format(name))
    with tqdm(total=math.ceil(len(stream.content)*1.0/chunk_size)) as pbar:
        with open(path.join(resolve_encode(p), name), 'wb') as f:
            for chunk in stream.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                pbar.update(1)


def serialize_json(dst, model):
    """Write to json file

    :param dst:
    :param model:
    :return:
    """
    p = path.abspath(dst)
    if not path.exists(p):
        os.makedirs(p)
    with open(path.join(p, model.name)+'.json', 'w') as f:
        json.dump(model, f)
