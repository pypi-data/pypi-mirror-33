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
from logging import getLogger, Formatter, INFO
from logging.handlers import TimedRotatingFileHandler

import six

from kamonohashi.util._file_helper import create_folder

LOG_DIR = os.path.expanduser('~') + '/.kqi/'

create_folder(LOG_DIR)

def config_logger():
    logger = getLogger()
    logger.setLevel(INFO)
    file_formatter = Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
    if six.PY2:
        file_handler = TimedRotatingFileHandler(filename=LOG_DIR+'debug.log', when='D', backupCount=10)
    else:
        file_handler = TimedRotatingFileHandler(filename=LOG_DIR+'debug.log', when='D', backupCount=10, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
