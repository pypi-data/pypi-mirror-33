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

import click
from kamonohashi.container import Container
from kqicli.util._config import read_config


class ContainerCli(Container):
    def __init__(self):
        """Set logger and user_info"""
        self.logger = logging.getLogger()
        config = read_config()
        server = config.get('server', None)
        token = config.get('token', None)
        user = config.get('user', None)
        password = config.get('password', None)
        tenant = config.get('tenant', None)
        timeout = config.get('timeout', 60)
        retry = config.get('retry', 5)
        super(ContainerCli, self).__init__(server, token, user, password, tenant, timeout, retry)


@click.group(short_help='Retrieve docker images information')
@click.pass_context
def container(ctx):
    """Retrieve docker images information"""
    ctx.obj = ContainerCli()


@container.command('images')
@click.pass_obj
def get_images(ctx):
    """List all docker images in the registry"""
    result = ctx.get_images()
    [print(x) for x in result]


@container.command('tags')
@click.option('-i', '--image', type=str, required=True, help='A name of the image you want to list all tags')
@click.pass_obj
def get_tags(ctx, image):
    """List all tags of the docker image"""
    result = ctx.get_tags(image)
    [print(x) for x in result]
