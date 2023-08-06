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
import requests

from kamonohashi.account import Account
from kamonohashi.exception import KqiError
from kqicli.util._config import read_config, get_config, write_config


class AccountCli(Account):
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
        super(AccountCli, self).__init__(server, token, user, password, tenant, timeout, retry)


@click.group(short_help='System account related commands')
@click.pass_context
def account(ctx):
    """System account related commands e.g. login, switch tenant, your account information."""
    #ctx.obj = AccountCli()
    pass


@account.command('login')
@click.option('-s', '--server', prompt=True, confirmation_prompt=False, type=str,
              help='API server name like http://api.kamonohashi.ai/')
@click.option('-u', '--user', prompt=True, confirmation_prompt=False, type=str, help='User name')
@click.option('-p', '--password', prompt=True, confirmation_prompt=False, hide_input=True, type=str, help='Password')
@click.option('-t', '--tenant', type=int, help='A tenant id')
@click.pass_obj
def login(ctx, server, user, password, tenant):
    #def login(server, user, password, tenant):
    """Login to KAMONOHASHI system and generate a CLI's configuration file to ~/.kqi.config."""
    #ctx.server = server
    # TODO use SDK later. But the current sdk has so no way to call it here appropriately.
    server = server if not server.endswith('/') else server[:-1]
    api = '/api/v1/account/login'
    payload = {
        'userName': user,
        'password': password,
        'tenantId': tenant
    }
    config = get_config()
    expire_days = config.get('expireDays')
    if expire_days is not None:
        payload['expireDays'] = expire_days
    response = requests.post(url=server + api, data=json.dumps(payload), headers={'content-type': 'application/json'})
    if response.status_code != 200:
        # TODO better error handling
        status_code = response.status_code
        method = response.request.method
        url = response.request.url
        content = response.text
        message = u'{method} {url}\n{status_code} {reason}\n{content}'.format(method=method, url=url, status_code=status_code, reason=response.reason, content=content)
        raise KqiError(message)

    result = response.json()
    print(u'''
    user: {0}
    tenant: {1}
    expires in: {2} seconds
    token: {3}'''.format(result['userName'], result['tenantId'], result['expiresIn'], result['token']))
    write_config(server=server, token=result['token'])

@account.command('switch-tenant')
@click.argument('tenant-id', type=str)
@click.pass_obj
def switch_tenant(ctx, tenant_id):
    """Switch to another tenant using TENANT_ID"""
    a = AccountCli()
    config = get_config()
    expire_days = config.get('expireDays')
    res = a.switch_tenant(tenant_id, expire_days)
    write_config(token=res['token'])
    a = AccountCli()
    res = a.get()
    print(u'''
    user name: {0}
    selected tenant: {1} ({2})'''.format(res['userName'], res['selectedTenant']['id'], res['selectedTenant']['displayName']))



@account.command()
@click.pass_obj
def get(ctx):
    """Show current account information"""
    a = AccountCli()
    res = a.get()
    print(u'''
    user name: {0}
    selected tenant: {1} ({2})
    assigned tenant:'''.format(res['userName'], res['selectedTenant']['id'], res['selectedTenant']['displayName']))

    for tenant in res['tenants']:
    #for k, v in res.tenants.items():
        selected = u'*' if tenant['id'] == res['selectedTenant']['id'] else u' '
        print(u'        {0} {1} ({2})'.format(selected, tenant['id'], tenant['displayName']))
