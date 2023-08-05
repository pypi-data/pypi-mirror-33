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
from os import path

import click
from kamonohashi.data import Data
from kqicli.util._config import read_config
from kqicli.util._print_helper import table
from kqicli.util._write_file_helper import save_file


class DataCli(Data):
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
        super(DataCli, self).__init__(server, token, user, password, tenant, timeout, retry)


@click.group(short_help='Handling data related information')
@click.pass_context
def data(ctx):
    """Handling various types of information related to data e.g. Create, Upload, Download, Delete, List. """
    ctx.obj = DataCli()


@data.command('list')
@click.option('-c', '--count', help='A number of data you want to retrieve')
@click.option('-q', '--query', help='A filter condition to data name')
@click.pass_obj
def get_list(ctx, count, query):
    """
    List data of your tenant using count and query if you need
    """
    res = ctx.list(count, query)
    table(res)


@data.command()
@click.argument('id')
@click.pass_obj
def get(ctx, id):
    """
    Get the detail of the data specified by ID
    """
    res = ctx.get(id)
    print('id: {0}'.format(res.id))
    print('name: {0}'.format(res.name))
    print('memo: {0}'.format(res.memo))
    print('created at: {0}'.format(res.created_at))
    print('created by: {0}'.format(res.created_by))
    print('image: {0}'.format(res.image_name))
    print('annotation: {0}'.format(res.annotation_name))
    print('tags: {0}'.format(res.tags))


@data.command()
@click.option('-n', '--name', type=str, required=True, help='The name of this data. Name must be unique in a tenant.')
@click.option('-d', '--data-file', type=click.Path(exists=True),
              help="The path string to the data file you want to upload", required=True)
@click.option('-a', '--annotation-file', type=click.Path(exists=True),
              help="The path string to the annotation file you want to upload")
@click.option('-m', '--memo', type=str, help='Free text that can helpful to explain the data')
@click.option('-t', '--tags', multiple=True, type=str,
              help='Attributes to the data. You can specify multiples tags using -t option several times. e.g. -t tag1 -t tag2')
@click.pass_obj
def create(ctx, name, data_file, annotation_file, memo, tags):
    """Create a data with name and data file. You can also upload an annotation file."""
    res = ctx.create(name=name, data_file=data_file, annotation_file=annotation_file,
                     memo=memo, tags=tags)
    print('''created data:
    id: {0}
    name: {1}'''.format(res.id, res.name))


@data.command()
@click.argument('id')
@click.option('-m', '--memo', type=str, help='Free text that can helpful to explain the data')
@click.option('-t', '--tags', multiple=True, type=str,
              help='Free text that can helpful to explain the data')
@click.pass_obj
def update(ctx, id, attribute, memo, tags):
    """Update the date properties using data ID"""
    res = ctx.update(id, memo, attribute, tags)
    print('''updated data:
    id: {0}
    name: {1}'''.format(res.id, res.name))


@data.command()
@click.argument('id')
@click.pass_obj
def delete(ctx, id):
    """Delete the data using data ID"""
    ctx.delete(id)


@data.command('list-files')
@click.argument('id')
@click.pass_obj
def list_files(ctx, id):
    """List file information using data ID"""
    res = ctx.list_files(id)
    table(res)


@data.command('download-file')
@click.argument('id')
@click.option('-d', '--destination', type=str, required=True)
@click.option('-k', '--key', type=click.Choice(['Image', 'Annotation']), required=True)
@click.pass_obj
def download_file(ctx, id, destination, key):
    """
    Download a file attached to data
    """
    res = ctx.download_file(id, key)
    ctx.logger.info('Saving the file to {0}.'.format(destination))
    try:
        save_file(destination, res.name, res.stream)
        ctx.logger.info('Done')
    except IOError:
        ctx.logger.error('{0} is already exist'.format(path.join(destination, res.name)))


@data.command('upload-file', short_help='Upload an annotation file to specified data ID')
@click.argument('id')
@click.option('-f', '--file', type=click.Path(exists=True), required=True)
@click.pass_obj
def upload_file(ctx, id, file):
    """Upload an annotation file to specified data ID. This command only works when the annotation data is not uploaded yet."""
    # Current REST API 1.0 only accepts annotation files. Hence, upload_file's key is hard corded below.
    res = ctx.upload_file(id, file, 'Annotation')
    print('''Uploaded and registered data file:
    id: {0}
    fileId: {1}
    key: {2}
    fileName: {3}
    
    '''.format(res.id, res.file_id, res.key, res.fileName))
