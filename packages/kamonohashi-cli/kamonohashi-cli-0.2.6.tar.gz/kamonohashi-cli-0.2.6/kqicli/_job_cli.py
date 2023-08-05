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

import logging
from os.path import join

import click
from kamonohashi.job import Job
from kqicli.util._config import read_config
from kqicli.util._print_helper import table
from kqicli.util._write_file_helper import save_file


class JobCli(Job):
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
        super(JobCli, self).__init__(server, token, user, password, tenant, timeout, retry)


@click.group('job', short_help='A job related commands. You can create, complete or halt a job.')
@click.pass_context
def job(ctx):
    """
    A job related commands. You can create, complete or halt a job. Also you can retrieve past and current
    job information like status or log files.
    """
    ctx.obj = JobCli()


@job.command('list')
@click.option('-c', '--count', type=int, help='A number of job you want to retrieve')
@click.option('-q', '--query', type=str, help='A filter condition to you job name')
@click.pass_obj
def get_list(ctx, count, query):
    """List all jobs"""
    res = ctx.list(count, query)
    table(res)


@job.command()
@click.argument('id')
@click.pass_obj
def get(ctx, id):
    """Get a job detail using job ID"""
    result = ctx.get(id)
    print('id: {0}'.format(result.id))
    print('name: {0}'.format(result.name))
    print('dataset: {0}'.format(result.dataset.name))
    print('job argument: {0}'.format(result.train_argument)) #TODO rename to job argument once the train argument is renamed.
    print('eval argument: {0}'.format(result.eval_argument))
    print('git model:')
    if result.git_model:
        print('    url: {0}'.format(result.git_model.url))
        print('    repository: {0}'.format(result.git_model.repository))
        print('    owner: {0}'.format(result.git_model.owner))
        print('    branch: {0}'.format(result.git_model.branch))
        print('    commit id: {0}'.format(result.git_model.commit_id))
    print('container image:')
    if result.container:
        print('    registry id: {0}'.format(result.container.registry_id))
        print('    registry Name: {0}'.format(result.container.registry_name))
        print('    url: {0}'.format(result.container.url))
        print('    image: {0}'.format(result.container.image))
        print('    tag: {0}'.format(result.container.tag))
    print('CompletedAt: {0}'.format(result.completed_at))
    print('logSummary: {0}'.format(result.log_summary))
    print('memo: {0}'.format(result.memo))
    print('cpu: {0}'.format(result.cpu))
    print('memory: {0}'.format(result.memory))
    print('gpu: {0}'.format(result.gpu))
    print('partition: {0}'.format(result.partition))
    print('status: {0}'.format(result.status))


@job.command('download-log')
@click.argument('id')
@click.option('-d', '--destination', type=click.Path(exists=True), required=True)
@click.pass_obj
def download_log(ctx, id, destination):
    """Download log files of job ID. You can only download running job's log files."""
    result = ctx.download_log(id)
    save_file(destination, "log_{0}.txt".format(id), result)


@job.command()
@click.option('-n', '--name', type=str, required=True, help='A name of the job. Job name must be unique.')
@click.option('-rim', '--registry-image', type=str, required=True, help='A docker image name you want to run')
@click.option('-rt', '--registry-tag', type=str, required=True, help='A tag of the docker image')
@click.option('-d', '--dataset-id', type=int, required=True, help='A dataset id you want to use for the job')
@click.option('-ta', '--job-argument', type=str, help='Arguments to this job. Each argument must be split by ";".'
                                                      'e.g. --max_step=100;--epoch=20;')
@click.option('-ea', '--eval-argument', type=str, help='Arguments to a eval.py program. Each argument must be '
                                                       'split by ";" e.g. --max_step=100;--epoch=20;')
@click.option('-go', '--git-owner', type=str, required=True,
              help="The owner of the repository which contains source codes you want to execute. Usually owner is the "
                   "first path of the repository's url. In case of this url, "
                   "https://github.com/kamonohashi/kamonohashi-cli, kamonohashi is a owner name.")
@click.option('-gr', '--git-repository', type=str, required=True,
              help="The repository name of the repository whichi contains your source codes. Usually repository name is"
                   " the second path of the repository's url. In case of this url,"
                   " https://github.com/kamonohashi/kamonohashi-cli, kamonohashi-cli is a repository name.")
@click.option('-gb', '--git-branch', type=str, help='The branch of your git repository. If you omit this option,'
                                                    'master branch is used.')
@click.option('-gc', '--git-commit', type=str, help='The git commit of your source code. If you omit this option,'
                                                    'the latest one is used.')
@click.option('-c', '--cpu', type=str, required=True, help='A number of core you want to assign to this job')
@click.option('-mem', '--memory', type=str, required=True, help='How much memory(GB) you want to assign to this job ')
@click.option('-g', '--gpu', type=int, required=True, help='A number of GPUs you want to assign to this job')
@click.option('-p', '--partition', type=str, help='A cluster partition. Partition is an arbitrary string but typically'
                                                  'this is a type of GPU or cluster.')
@click.option('-m', '--memo', type=str, help='A memo of this job.')
@click.option('-pid', '--parent-id', type=str, help='A parent id of this job. Currently, the system only makes a '
                                                    'relationship to the parent job but do nothing.')
@click.option('-o', '--options', type=(str, str), multiple=True, help='Options of this job. The options are stored in '
                                                                      'the environment variables')
@click.pass_obj
def create(ctx, name, registry_image, registry_tag, dataset_id, job_argument,
           git_owner, git_repository, cpu, memory, gpu, partition, memo,
           eval_argument, git_branch, git_commit, parent_id, options):
    """Submit a new job to KAMONOHASHI cluster."""
    # optionsが指定されていれば、dict型に詰め直す
    option_dict = None
    if options is not None:
        option_dict = {}
        for option in options:
            option_dict[option[0]] = option[1]
    result = ctx.create(name, registry_image, registry_tag, dataset_id, job_argument,
                        git_owner, git_repository, cpu, memory, gpu, partition,
                        memo, eval_argument, git_branch, git_commit, parent_id, option_dict)
    print('''Created a job:
    id: {0}
    name: {1}
    status: {2}'''.format(result.id, result.name, result.status))


@job.command()
@click.argument('id')
@click.option('-m', '--memo', type=str, required=True, help='A memo you want to update')
@click.pass_obj
def update(ctx, id, memo):
    """Update a memo of the job using job ID"""
    result = ctx.update(id, memo)
    print('''Updated training:
    id: {0}
    name: {1}
    memo: {2}
    status: {3}'''.format(result.id, result.name, result.memo, result.status))


@job.command('upload-files')
@click.argument('id')
@click.option('-trl', '--job-log', required=True, help='The result files of TensorFlow or other frameworks')
@click.option('-tp', '--trained-parameter', required=True, help='The result of trained model')
@click.option('-tel', '--test-log', help='The result of test log file')
@click.option('-l', '--log-summary', help='Summary of the log file')
@click.option('-g', '--gpu-driver', help='The version number of GPU driver')
@click.pass_obj
def upload_files(ctx, id, job_log, trained_parameter, test_log, log_summary, gpu_driver):
    """Finish the job and upload necessary data"""
    result = ctx.upload_files(id, job_log, trained_parameter, test_log, log_summary, gpu_driver)
    print('Done training: {0}'.format(result.id))


@job.command('list-files')
@click.argument('id')
@click.pass_obj
def list_files(ctx, id):
    """List output files of the job ID"""
    res = ctx.list_attached_files(id, False)
    table(res)


@job.command('download-files')
@click.argument('id')
@click.option('-d', '--destination', type=click.Path(exists=True), required=True,
              help='A path to the output files')
@click.option('-k', '--key', type=click.Choice(['TrainLogs', 'TestLogs', 'TrainedParameters']), multiple=True,
              help="Specify a file type key. Currently, the system defines three keys 'TrainLogs', 'TestLogs' and 'TrainedParameters'."
              "The command accept multiple keys. e.g. -k TrainLogs, -k TestLogs. If you omit a --key option, the command "
              "downloads all files. In the future version you can specify arbitrary keys.")
@click.pass_obj
def download_files(ctx, id, destination, key):
    """Download files of the job ID you specified"""
    result = ctx.download_attached_files(id)
    for x in result:
        # keyが指定されたものと一致する or そもそもkeyが指定されていないなら出力
        if x.metadata.key in key or not key:
            print("{0}'s file name is {1}".format(x.metadata.key, x.metadata.file_name))
            save_file(join(destination, x.metadata.key), x.metadata.file_name, x.stream)


@job.command('download-result-files')
@click.argument('id')
@click.option('-d', '--destination', type=click.Path(exists=True), required=True,
              help='A path to the output files')
@click.pass_obj
def download_result_files(ctx, id, destination):
    """Download result files related to a job. Files are usually a log file like TensorFlow's tfevents."""
    result = ctx.download_attached_files(id)
    # At this point, I hard coded following two types to specify log file type.
    # TODO Should refactor to better way to handle the file types.
    keys = ('TrainLogs', 'TestLogs')
    for x in result:
        # keyが指定されたものと一致する or そもそもkeyが指定されていないなら出力
        if x.metadata.key in keys:
            print("{0}'s file name is {1}".format(x.metadata.key, x.metadata.file_name))
            save_file(join(destination, x.metadata.key), x.metadata.file_name, x.stream)

@job.command('attach-file')
@click.argument('id')
@click.option('-f', '--file-path', type=click.Path(exists=True), help='A file path you want to attach')
@click.pass_obj
def attach_file(ctx, id, file_path):
    """Attach a file to the job using job ID."""
    result = ctx.upload_attached_file(id, file_path)
    print('Registered file id: {0}'.format(result.id))


@job.command('delete-attached-file')
@click.argument('id')
@click.option('-f', '--file-id', type=int, required=True, help='A file id you want to delete')
@click.pass_obj
def delete_file(ctx, id, file_id):
    """Delete an attached file of the job using job ID"""
    ctx.delete_attached_file(id, file_id)
    print('Delete file id: {0}'.format(file_id))


@job.command('halt')
@click.argument('id')
@click.pass_obj
def halt(ctx, id):
    """Halt a job of ID"""
    result = ctx.halt(id)
    print('''Stop training:
    id: {0}
    name: {1}
    status: {2}'''.format(result.id, result.name, result.status))


@job.command('complete')
@click.argument('id')
@click.pass_obj
def complete(ctx, id):
    """Complete a job of ID"""
    result = ctx.complete(id)
    print('''Complete training:
    id: {0}
    name: {1}
    status: {2}'''.format(result.id, result.name, result.status))

@job.command('list-partitions')
@click.pass_obj
def list_partitions(ctx):
    """List partitions of the tenant"""
    result = ctx.list_partitions()
    for x in result:
        print(x)
