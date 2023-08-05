""" Command line interface for the OnePanel Machine Learning platform

Entry point for command line interface.
"""

import os
import functools
import configparser
import click
import requests

from onepanel.commands.login import login, login_with_token
from onepanel.commands.projects import projects
from onepanel.commands.datasets import datasets
from onepanel.commands.jobs import jobs
from onepanel.commands.machine_types import machine_types
from onepanel.commands.environments import environments
from onepanel.commands.instances import workspaces
from onepanel.commands.volume_types import volume_types
from onepanel.commands.common import clone, download, push, pull
from onepanel.utilities.git_utility import CheckGitLfsInstalled
from onepanel.constants import *

class Connection:
    """ REST API requests defaults and credentials
    """
    def __init__(self):
        self.URL = os.getenv('BASE_API_URL', 'https://c.onepanel.io/api')
        self.SSL_VERIFY = True
        self.headers = {'Content-Type': 'application/json'}
        self.account_uid = None
        self.user_uid = None
        self.token = None
        self.gitlab_impersonation_token = None

        # wrap requests methods to reduce number of arguments in api queries
        self.get = functools.partial(requests.get, headers=self.headers, verify=self.SSL_VERIFY)
        self.post = functools.partial(requests.post, headers=self.headers, verify=self.SSL_VERIFY)
        self.put = functools.partial(requests.put, headers=self.headers, verify=self.SSL_VERIFY)
        self.delete = functools.partial(requests.delete, headers=self.headers, verify=self.SSL_VERIFY)

    def save_credentials(self, data):
        credentials = configparser.ConfigParser()
        credentials['default'] = {'uid': data['uid'],
                                  'token': data['sessions'][0]['token'],
                                  'gitlab_impersonation_token': data['gitlab_impersonation_token'],
                                  'account_uid': data['account']['uid']}

        onepanel_home = os.path.expanduser(os.path.join('~', '.onepanel'))
        if not os.path.exists(onepanel_home):
            os.makedirs(onepanel_home)

        filename = os.path.join(onepanel_home, 'credentials')
        with open(filename, 'w') as f:
            credentials.write(f)

    def load_credentials(self):
        credentials = configparser.ConfigParser()
        filename = os.path.expanduser(os.path.join('~', '.onepanel', 'credentials'))
        credentials.read(filename)

        self.user_uid = credentials.get('default','uid',fallback=None)
        self.account_uid = credentials.get('default', 'account_uid', fallback=None)
        self.token = credentials.get('default', 'token', fallback=None)
        self.gitlab_impersonation_token = credentials.get('default','gitlab_impersonation_token', fallback=None)

        if self.token:
            self.headers['Authorization'] = 'Bearer {}'.format(self.token)


@click.group()
@click.version_option(version=CLI_VERSION, prog_name='Onepanel CLI')
@click.pass_context
def cli(ctx):
    conn = Connection()
    conn.load_credentials()
    utility = CheckGitLfsInstalled()

    ctx.obj['connection'] = conn
    ctx.obj['git_utility'] = utility
    utility.figure_out_git_installed()
    utility.figure_out_git_lfs_installed()
    if utility.git_installed is False:
        print('Error. Cannot detect git, please verify git is installed.')
        exit(-1)

cli.add_command(login)
cli.add_command(login_with_token)
cli.add_command(clone)
cli.add_command(download)
cli.add_command(push)
cli.add_command(pull)
cli.add_command(projects)
cli.add_command(datasets)
cli.add_command(jobs)
cli.add_command(machine_types)
cli.add_command(environments)
cli.add_command(volume_types)
cli.add_command(workspaces)


def main():
    return cli(obj={})


if __name__ == '__main__':
    cli(obj={})
