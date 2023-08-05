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

import io
import json
import logging

import click
from kamonohashi.dataset import DataSet
from kqicli.util._config import read_config
from kqicli.util._print_helper import table


class DataSetCli(DataSet):
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
        super(DataSetCli, self).__init__(server, token, user, password, tenant, timeout, retry)


@click.group('dataset')
@click.pass_context
def data_set(ctx):
    """Create/Update/Delete/Download your datasets."""
    ctx.obj = DataSetCli()


@data_set.command('list')
@click.option('-c', '--count', type=int, help='A number of dataset you want to retrieve')
@click.option('-q', '--query', type=str, help='A filter condition to dataset name')
@click.pass_obj
def get_list(ctx, count, query):
    """List datasets in your tenant"""
    res = ctx.list(count, query)
    table(res)


@data_set.command(short_help='Get a detaset detail using dataset ID')
@click.argument('id')
@click.option('-j', '--json', 'is_json', is_flag=True, help='Download a json file or print the content to console')
@click.option('-d', '--destination', type=click.File('w', encoding='utf-8'), help='A file path of the output json file')
@click.pass_obj
def get(ctx, id, is_json, destination):
    """Get a dataset detail as a json or printing to console using a dataset ID. If you only specify the file name
    e.g. dataset.json, the command writes a json file to your current directory.
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
        print('created by: {0}'.format(result.created_by))
        print('entries:')
        for entry in result.entries:
            print("    {0}:".format(entry.type))
            for file in entry.files:
                print("        {0}: {1}".format(file.id, file.name))


@data_set.command()
@click.option('-f', '--file', required=True,
              help="""{
  "name": @name,
  "memo": @memo,
  "entries": {
    "additionalProp1": [
      {
        "id": @dataId
      }
    ],
    "additionalProp2": [
      {
        "id": @dataId
      }
    ],
    "additionalProp3": [
      {
        "id": @dataId
      }
    ]
  }
}""")
@click.pass_obj
def create(ctx, file):
    """Create a new dataset"""
    with io.open(file, 'r', encoding='utf-8') as f:
        dic = json.load(f)
    result = ctx.create(dic)
    print('''Created dataset:
    Id: {0}
    Name: {1}'''.format(result.id, result.name))


@data_set.command()
@click.argument('id')
@click.option('-f', '--file', required=True,
              help="""{
  "name": @name,
  "memo": @memo,
  "entries": {
    "additionalProp1": [
      {
        "id": @dataId
      }
    ],
    "additionalProp2": [
      {
        "id": @dataId
      }
    ],
    "additionalProp3": [
      {
        "id": @dataId
      }
    ]
  }
}""")
@click.pass_obj
def update(ctx, id, file):
    """Update a dataset using dataset ID"""
    with io.open(file, 'r', encoding='utf-8') as f:
        dic = json.load(f)
    res = ctx.update(id, dic)
    print('''Updated dataset:
    id: {0}
    name: {1}'''.format(res.id, res.name))


@data_set.command('update-meta-info')
@click.argument('id')
@click.option('-n', '--name', type=str, help='A name you want to update')
@click.option('-m', '--memo', type=str, help='A memo you want to update')
@click.pass_obj
def update_meta_info(ctx, id, name, memo):
    """Update dataset's metadata (name and memo)"""
    res = ctx.update_meta_info(id, name, memo)
    print('''Updated dataset:
    id: {0}
    name: {1}
    memo: {2}'''.format(res.id, res.name, res.memo))


@data_set.command()
@click.argument('id')
@click.pass_obj
def delete(ctx, id):
    """Delete a dataset using dataset ID"""
    ctx.delete(id)


@data_set.command('download-files')
@click.argument('id')
@click.option('-d', '--destination', type=click.Path(exists=True), required=True, help='A file path of the output data')
@click.pass_obj
def download_files(ctx, id, destination):
    """Download dataset's content data using dataset ID"""
    # result = ctx.download_files(id)
    # for entry in result:
    #     dst = path.join(destination, entry.type, entry.key, str(entry.data_id))
    #     save_file(dst, entry.downloaded_file.name, entry.downloaded_file.stream)
    result = ctx.download_and_save_files(id, destination)

@data_set.command('list-data-types')
@click.pass_obj
def list_data_types(ctx):
    """List data types of the dataset. Data type is a concept of dataset group like training, testing and validation.
    You can define any name of dataset type in the future release. Currently we only support training, testing
    and validation"""
    result = ctx.list_datatypes()
    for x in result:
        print('name: {1}'.format(x.id, x.name))
