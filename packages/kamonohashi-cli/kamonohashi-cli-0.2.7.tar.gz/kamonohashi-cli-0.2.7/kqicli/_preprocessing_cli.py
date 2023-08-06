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

import click
from kamonohashi.preprocessing import Preprocessing
from kqicli.util._config import read_config
from kqicli.util._print_helper import table


class PreprocessingCli(Preprocessing):
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
        super(PreprocessingCli, self).__init__(server, token, user, password, tenant, timeout, retry)


@click.group('preprocessing')
@click.pass_context
def preprocessing(ctx):
    """Create/Update/Delete preprocessing"""
    ctx.obj = PreprocessingCli()


@preprocessing.command('list')
@click.option('-c', '--count', type=int, help='A number of data you want to retrieve')
@click.option('-q', '--query', type=str, help='A filter condition to data name')
@click.pass_obj
def get_list(ctx, count, query):
    """List all preprocessings"""
    res = ctx.list(count, query)
    table(res)


@preprocessing.command()
@click.argument('id')
@click.option('-j', '--json', 'is_json', is_flag=True, help='Download a json file or print the content to console')
@click.option('-d', '--destination', type=click.File('wb'), help='A file path of the output json file')
@click.pass_obj
def get(ctx, id, is_json, destination):
    """Get a preprocessing detail as a json or printing to console using a preprocessing ID. If you only specify the
     file name e.g. preprocessing.json, the command writes a json file to your current directory.
    """
    if is_json:
        result = ctx.get_as_json(id)
        print('Output json file to {0}'.format(destination))
        destination.write(result)
    else:
        result = ctx.get(id)
        print('id: {0}'.format(result.id))
        print('name: {0}'.format(result.name))
        print('memo: {0}'.format(result.memo))
        print('created at: {0}'.format(result.created_at))
        print('entry point: {0}'.format(result.entry_point))
        print('is executed: {0}'.format(result.is_executed))
        print('git model:')
        if result.git_model:
            print('    url: {0}'.format(result.git_model.url))
            print('    repository: {0}'.format(result.git_model.repository))
            print('    owner: {0}'.format(result.git_model.owner))
            print('    branch: {0}'.format(result.git_model.branch))
            print('    commit id: {0}'.format(result.git_model.commit_id))
        print('container image:')
        if result.container_image:
            print('    registry id: {0}'.format(result.container_image.registry_id))
            print('    registry Name: {0}'.format(result.container_image.registry_name))
            print('    url: {0}'.format(result.container_image.url))
            print('    image: {0}'.format(result.container_image.image))
            print('    tag: {0}'.format(result.container_image.tag))


@preprocessing.command()
@click.option('-f', '--file', required=True,
              help="""{
  "name": @name,
  "entryPoint": @entryPoint,
  "containerImage": {
    "image": @image,
    "tag": "@tag,
  },
  "gitModel": {
    "repository": @repository,
    "owner": @owner,
    "branch": @branch,
    "commitId": @commitId,
  },
  "memo": @memo
}""")
@click.pass_obj
def create(ctx, file):
    """Create a new preprocessing"""
    with open(file, 'r') as f:
        dic = json.load(f)
    result = ctx.create(dic)
    print('''Created preprocessing:
    Id: {0}
    Name: {1}'''.format(result.id, result.name))


@preprocessing.command()
@click.argument('id')
@click.option('-f', '--file', required=True,
              help="""{
  "name": @name,
  "entryPoint": @entryPoint,
  "containerImage": {
    "image": @image,
    "tag": "@tag,
  },
  "gitModel": {
    "repository": @repository,
    "owner": @owner,
    "branch": @branch,
    "commitId": @commitId,
  },
  "memo": @memo
}""")
@click.pass_obj
def update(ctx, id, file):
    """Update a preprocessing using preprocessing ID"""
    with open(file, 'r') as f:
        dic = json.load(f)
    res = ctx.update(id, dic)
    print('''Updated preprocessing:
    id: {0}
    name: {1}'''.format(res.id, res.name))

@preprocessing.command('update-meta-info')
@click.argument('id')
@click.option('-n', '--name', type=str, help='A name you want to update')
@click.option('-m', '--memo', type=str, help='A memo you want to update')
@click.pass_obj
def update_meta_info(ctx, id, name, memo):
    """Update preprocessing's metadata (name and memo)"""
    res = ctx.update_meta_info(id, name, memo)
    print('''Updated preprocessing:
    id: {0}
    name: {1}
    mamo: {2}'''.format(res.id, res.name, res.memo))


@preprocessing.command()
@click.argument('id')
@click.pass_obj
def delete(ctx, id):
    """Delete a preprocesssing using preprocessing ID"""
    ctx.delete(id)
