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

import json
import logging
import os

DEFAULT_CONFIG_FILE = os.path.expanduser('~/.kqi.config')

logger = logging.getLogger()

def read_config():
    """Read config

    Return:
        config (dict): read config
    """
    logger.info('Start to read config file')

    if os.path.exists(DEFAULT_CONFIG_FILE):
        with open(DEFAULT_CONFIG_FILE, 'r') as f:
            logger.info('Finished to read a config file')
            return json.loads(f.read())
    else:
        raise Exception("No configuration file(~/.kqi.config) is found. Log into KAMONOHASHI first to use 'account login' command.")


def get_config():
    """Read config file. If not exists, return an empty dictionary."""
    try:
        with open(DEFAULT_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (OSError, IOError):
        return {}


def write_config(**kwargs):
    config = get_config()
    config.update(kwargs)
    with open(DEFAULT_CONFIG_FILE, 'w+') as f:
        logger.info('Writing a config file')
        json.dump(config, f, indent=4)
        logger.info('Overwrote a config file')
