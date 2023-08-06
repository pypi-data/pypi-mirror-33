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

import logging
import sys

import click
from pkg_resources import get_distribution

from kqicli._account_cli import account
from kqicli._container_cli import container
from kqicli._data_cli import data
from kqicli._dataset_cli import data_set
from kqicli._job_cli import job
from kqicli._preprocessing_cli import preprocessing
from kqicli.util._get_logger import config_logger

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
NAME = "kamonohashi-cli"
version = get_distribution(NAME).version

@click.group(context_settings=CONTEXT_SETTINGS,
             help='KAMONOHASHI CLI. version: {version}'.format(version=version))
def kqi():
    config_logger()

kqi.add_command(container)
kqi.add_command(data)
kqi.add_command(account)
kqi.add_command(data_set)
kqi.add_command(job)
kqi.add_command(preprocessing)

def kqi_main():
    try:
        kqi()
    except Exception as error:
        print('[ERROR]', error)
        logger = logging.getLogger()
        logger.exception(error)

if __name__ == "__main__":
# for pydevd & python2 glitch
    sys.exit(kqi(sys.argv[1:]))
