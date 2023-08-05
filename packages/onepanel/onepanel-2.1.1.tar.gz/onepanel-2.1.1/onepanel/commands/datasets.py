""" Command line interface for the OnePanel Machine Learning platform

'Datasets' commands group.
"""

import os
import configobj
import shutil
import re
import click

import humanize
from onepanel.commands.login import login_required
from onepanel.gitwrapper import GitWrapper
from onepanel.commands.base import APIViewController
from distutils import dir_util


class DatasetViewController(APIViewController):
    """ DatasetViewController data model
    """

    DATASET_FILE = os.path.join('.onepanel','dataset')
    EXCLUSIONS = [os.path.join('.onepanel','dataset')]

    account_uid = None
    dataset_uid = None

    def __init__(self, conn):
        APIViewController.__init__(self, conn)
        self.endpoint = '{}'.format(
            self.conn.URL,
        )

    def init_credentials_retrieval(self):
        # Figure out the account uid and dataset uid
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            print("ERROR.Directory does not exist, cannot carry out all datasets operations.")
            print("DETAILS." + onepanel_dir)
            exit(-1)
        dataset_file = os.path.join(home, DatasetViewController.DATASET_FILE)
        if not os.path.isfile(dataset_file):
            print("ERROR.Dataset file does not exist, cannot carry out all datasets operations.")
            print("DETAILS." + dataset_file)
            exit(-1)

        cfg = configobj.ConfigObj(dataset_file)

        dataset_uid = cfg['uid']
        dataset_account_uid = cfg['account_uid']

        if len(dataset_uid) < 1 or len(dataset_account_uid) < 1:
            print("ERROR.Dataset file has invalid credentials. Verify credentials or re-pull project.")
            exit(-1)
        self.account_uid = dataset_account_uid
        self.dataset_uid = dataset_uid


    def save(self, home):
        if not os.path.exists(home):
            os.makedirs(home)
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            os.makedirs(onepanel_dir)
        dataset_file = os.path.join(home, DatasetViewController.DATASET_FILE)

        cfg = configobj.ConfigObj(dataset_file)
        cfg['uid'] = self.dataset_uid
        cfg['account_uid'] = self.account_uid
        cfg.write()

    @classmethod
    def from_json(cls, data):
        cls.account_uid = data['account']['uid']
        cls.dataset_uid = data['uid']

    @classmethod
    def is_uid_valid(cls,uid):
        pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
        if pattern.match(uid):
            return True
        else:
            return False

    @classmethod
    def exists_local(cls,home):
        dataset_file = os.path.join(home, DatasetViewController.DATASET_FILE)
        if os.path.isfile(dataset_file):
            return True
        else:
            return False

    @classmethod
    def exists_remote(cls,dataset_uid, data):
        exists = False
        if data['uid'] == dataset_uid:
            exists = True
        return exists


def create_dataset(ctx, account_uid, home):
    """ Dataset creation method for 'datasets_init' and 'datasets_create'
    commands
    """
    vc = ctx.obj['vc']

    if not account_uid:
        account_uid = ctx.obj['connection'].account_uid

    dataset_uid = os.path.basename(home)
    if not vc.is_uid_valid(dataset_uid):
        click.echo('Dataset name {} is invalid.'.format(dataset_uid))
        click.echo(
            'Name should be 3 to 25 characters long, lower case alphanumeric or \'-\' and must start and end with an alphanumeric character.')
        return None

    # Check if the dataset already exists remotely
    url_dataset_check = '/accounts/{}/datasets/{}'.format(account_uid, dataset_uid)
    response_data = vc.get(params=url_dataset_check)
    remote_dataset = response_data['data']

    dataset = None
    # If remote returned data, do operations
    if remote_dataset is not None and vc.exists_remote(dataset_uid, remote_dataset):
        if vc.exists_local(home):
            click.echo('Dataset is already initialized')
        else:
            vc.account_uid = account_uid
            vc.dataset_uid = dataset_uid
            vc.save(home)
            git = GitWrapper()
            git.init(onepanel_user_uid=ctx.obj['connection'].user_uid, gitlab_token=vc.conn.gitlab_impersonation_token,
                     home=home,account_uid=account_uid,project_uid=dataset_uid + '_dataset')
            git.exclude(home, DatasetViewController.EXCLUSIONS)
    # If no data from remote, we can create a dataset
    else:
        can_create = True
        if vc.exists_local(home):
            can_create = click.confirm(
                'Dataset exists locally but does not exist in {}, create the dataset and remap local folder?'
                    .format(account_uid))

        if can_create:
            data = {
                'uid': dataset_uid
            }
            url_dataset_create = '/accounts/{}/datasets'.format(account_uid)
            response = vc.post(data,params=url_dataset_create)
            if response['status_code'] == 200:
                vc.from_json(response['data'])
                vc.save(home)
                git = GitWrapper()
                git.init(onepanel_user_uid=ctx.obj['connection'].user_uid, gitlab_token=vc.conn.gitlab_impersonation_token,
                         home=home, account_uid=account_uid, project_uid=dataset_uid + '_dataset')
                git.exclude(home, DatasetViewController.EXCLUSIONS)
    return dataset


@click.group(help='Dataset commands group')
@click.pass_context
def datasets(ctx):
    ctx.obj['vc'] = DatasetViewController(ctx.obj['connection'])


@datasets.command('list', help='Display a list of all datasets.')
@click.pass_context
@login_required
def datasets_list(ctx):
    vc = ctx.obj['vc']
    data = vc.list(params='/datasets')
    if data is None:
        print("No datasets found.")
    else:
        data_print = []
        for datum in data:
            uid = datum['uid']
            version_count = datum['statistics']['versionCount']
            size = datum['statistics']['size']
            size_formatted = humanize.naturalsize(size, binary=True)
            data_print.append({'uid': uid,
                               'version_count': version_count,
                               'size': size_formatted
                               })

        empty_message = "No datasets found."
        fields = ['uid', 'version_count', 'size']
        field_names = ['NAME', 'VERSIONS', 'SIZE']
        DatasetViewController.print_items(data_print, fields, field_names, empty_message)


@datasets.command('init', help='Initialize dataset in current directory.')
@click.pass_context
@login_required
def datasets_init(ctx):
    vc = ctx.obj['vc']
    home = os.getcwd()
    if not vc.is_uid_valid(os.path.basename(home)):
        dataset_uid = click.prompt('Please enter a valid dataset name')
        home = os.path.join(home, dataset_uid)

    if create_dataset(ctx, None, home):
        click.echo('Dataset is initialized in current directory.')


@datasets.command('create', help='Create dataset in new directory.')
@click.argument('name', type=str)
@click.pass_context
@login_required
def datasets_create(ctx, name):
    home = os.path.join(os.getcwd(), name)
    if create_dataset(ctx, None, home):
        click.echo('Dataset is created in directory {}.'.format(home))


def datasets_clone(ctx, path, directory, include, exclude):
    conn = ctx.obj['connection']
    vc = DatasetViewController(conn)

    values = path.split('/')

    if len(values) == 3:
        try:
            account_uid, datasets_dir, dataset_uid = values
            assert (datasets_dir == 'datasets')
        except:
            click.echo('Invalid dataset path. Please use <account_uid>/datasets/<uid>')
            return
    else:
        click.echo('Invalid dataset path. Please use <account_uid>/datasets/<uid>')
        return

    # check dataset path, account_uid, dataset_uid
    if directory is None:
        home = os.path.join(os.getcwd(), dataset_uid)
    elif directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    # check if the dataset exisits
    url_dataset_check = '/accounts/{}/datasets/{}'.format(account_uid, dataset_uid)
    response_data = vc.get(uid='', field_path='',params=url_dataset_check)
    response_code = response_data['status_code']
    if response_code == 200:
        remote_dataset = response_data['data']
    elif response_code == 401 or response_code == 404:
        print('Project does not exist.')
        return
    else:
        print('Error: {}'.format(response_code))
        return None

    if not vc.exists_remote(dataset_uid, remote_dataset):
        click.echo('There is no dataset {}/datasets/{} on the server'.format(account_uid, dataset_uid))
        return

    can_create = True
    if vc.exists_local(home):
        can_create = click.confirm('Dataset already exists, overwrite?')
    if not can_create:
        return

    # git clone
    git = GitWrapper()
    if ctx.obj['git_utility'].git_lfs_installed:
        code = git.lfs_clone(onepanel_user_uid=ctx.obj['connection'].user_uid,
                             gitlab_token=conn.gitlab_impersonation_token,
                             home=home,account_uid=account_uid,
                             project_uid=dataset_uid, ext='_dataset',
                             include=include, exclude=exclude)
        if code == 0:
            vc.account_uid = account_uid
            vc.dataset_uid = dataset_uid
            vc.save(home)
            git.exclude(home, vc.EXCLUSIONS)
        # Change back to previous directory
        return code
    elif ctx.obj['git_utility'].git_lfs_installed is False:
        print('ERROR. Cannot run git-lfs pull despite presence of git-lfs in repo. Please install git-lfs.')


def datasets_download(ctx, path, directory):
    if directory is None or directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    onepanel_download_path = home + "/.onepanel_download"
    if os.path.isdir(onepanel_download_path):
        shutil.rmtree(onepanel_download_path)

    code = datasets_clone(ctx, path, onepanel_download_path, include='*', exclude='')
    if code != 0:
        print("Unable to download!")
        return False

    dir_util.copy_tree(onepanel_download_path,home)
    shutil.rmtree(onepanel_download_path)

    print('The files have been downloaded to: {dir}'.format(dir=home))
    return True