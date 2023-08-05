"""
Job commands
"""
import os
import shutil
import stat
import sys
import json
import subprocess
import threading
import base64
import configobj

import click
import websocket

from onepanel.commands.projects import ProjectViewController
from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required
from distutils import dir_util


class JobViewController(APIViewController):
    project_account_uid = None
    project_uid = None

    def __init__(self, conn):
        APIViewController.__init__(self, conn)

    def init_credentials_retrieval(self):
        # Figure out the  account uid and project uid from file
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            print("ERROR.Directory does not exist, cannot carry out all jobs operations.")
            print("DETAILS." + onepanel_dir)
            exit(-1)
        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        if not os.path.isfile(project_file):
            print("ERROR.Project file does not exist, cannot carry out all jobs operations.")
            print("DETAILS." + project_file)
            exit(-1)

        cfg = configobj.ConfigObj(project_file)

        project_uid = cfg['uid']
        project_account_uid = cfg['account_uid']

        if len(project_uid) < 1 or len(project_account_uid) < 1:
            print("ERROR.Project file has invalid credentials. Verify credentials or re-pull project.")
            exit(-1)
        self.project_account_uid = project_account_uid
        self.project_uid = project_uid

    def init_endpoint(self):
        # Generate the endpoint
        self.endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/jobs'.format(
            root=self.conn.URL,
            account_uid=self.project_account_uid,
            project_uid=self.project_uid
        )


@click.group(help='Job commands group')
@click.pass_context
def jobs(ctx):
    ctx.obj['vc'] = JobViewController(ctx.obj['connection'])
    project_vc = ProjectViewController(ctx.obj['connection'])
    path = os.getcwd()
    if project_vc.exists_local(path):
        project_vc.from_directory(path)
        ctx.obj['project'] = project_vc
    else:
        # Return error before reaching other CLI commands:
        print('This project is not initialized, type "onepanel init" to initialize this project')
        sys.exit(1)


@jobs.command('create', help='Execute a command on a remote machine in the current project')
@click.argument(
    'command',
    type=str
)
@click.option(
    '-m', '--machine-type',
    type=str,
    required=True,
    help='Machine type ID'
)
@click.option(
    '-e', '--environment',
    type=str,
    required=True,
    help='Instance template ID'
)
@click.pass_context
@login_required
def create_job(ctx, command, machine_type, environment):
    new_job = {
        'command': command,
        'machineType': {
            'uid': machine_type
        },
        'instanceTemplate': {
            'uid': environment
        }
    }

    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    response = vc.post(post_object=new_job)

    if response['status_code'] == 200:
        print('New job created: {}'.format(response['data']['uid']))
    else:
        print("An error occurred: {}".format(response['data']))

    return


@jobs.command('list', help='Show commands executed on remote machines')
@click.option(
    '-a', '--all',
    type=bool,
    is_flag=True,
    default=False,
    help='Include finished commands'
)
@click.pass_context
@login_required
def list_jobs(ctx, all):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    items = vc.list(params='?running=true' if not all else '')

    if items is None or len(items) == 0:
        print('No jobs found. Use "--all" flag to retrieve completed jobs.')
        return

    vc.print_items(items, fields=['uid', 'command'], field_names=['ID', 'COMMAND'])


@jobs.command('stop', help='Stop a job')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def kill_job(ctx, job_uid):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    ctx.obj['vc'].delete(job_uid, field_path='/active', message_on_success='Job stopped',
                         message_on_failure='Job not found')


@jobs.command('logs', help='Show a log of the command')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def job_logs(ctx, job_uid):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    project = ctx.obj['project']

    job_data = vc.get('/' + job_uid, field_path='/logs')

    if job_data['status_code'] != 400:
        if job_data['data'] is None:
            print('Job not found.')
            return
        log = vc.get('/' + job_uid, field_path='/logs')
        print(log)
    else:
        # Streaming via WebSocket
        # See https://pypi.python.org/pypi/websocket-client/

        def on_message(ws, message):
            if message[0] == '0':
                message = base64.b64decode(message[1:]).decode('utf-8', 'ignore')
                sys.stdout.write(message)
                sys.stdout.flush()

        def on_error(ws, error):
            if isinstance(error, websocket.WebSocketConnectionClosedException):
                return

            if isinstance(error, KeyboardInterrupt):
                return

            if error.status_code == 502 or error.status_code == 503:
                print('Job {} is preparing'.format(job_uid))
            else:
                print(error)

        def on_close(ws):
            print('connection closed')

        def on_open(ws):
            def send_auth_token(*args):
                ws.send(json.dumps({'Authtoken': ''}))

            threading.Thread(target=send_auth_token).start()

        ws_url = '{ws_root}/{account_uid}/projects/{project_uid}/jobs/{job_uid}/logs/ws?id_token={token}'.format(
            ws_root='wss://c.onepanel.io',
            account_uid=project.account_uid,
            project_uid=project.project_uid,
            job_uid=job_uid,
            token=ctx.obj['connection'].token
        )

        ws = websocket.WebSocketApp(
            url=ws_url,
            on_message=on_message,
            on_open=on_open,
            on_error=on_error
        )

        ws.run_forever()

    return False


# todo if git-lfs is not setup but a .gitattributes file is present
# then we need to tell user to install git-lfs.
# If git-lfs is not setup, do a git clone regular.
def jobs_download_output(ctx, path, directory):
    #
    # Resource
    #
    dirs = path.split('/')
    git_utility = ctx.obj['git_utility']

    # Job output: Method 2
    # <account_uid>/projects/<project_uid>/jobs/<job_uid>
    if len(dirs) == 5:
        try:
            account_uid, projects_dir, project_uid, jobs_dir, job_uid = dirs
            assert (projects_dir == 'projects') and (jobs_dir == 'jobs')
        except:
            print('Incorrect job path')
            return None
    else:
        print('Incorrect job uid')
        return None

    #
    # Directory
    #
    if directory is None or directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    #
    # Clone
    #
    onepanel_download_path = '.onepanel_download'
    if os.path.isdir(onepanel_download_path):
        shutil.rmtree(onepanel_download_path,
                      onerror=remove_readonly)  # Cleaning after previous errors to avoid "is not an empty directory" error
    cmd = (
            git_utility.get_git_clone_str() + ' -b job-{job_uid} https://{user_uid}:{gitlab_token}@{host}/{account_uid}/{project_uid}-output.git '
                                              '.onepanel_download'
    ).format(
        host=os.getenv('GITLAB_GIT_HOST', 'git.onepanel.io'),
        user_uid = ctx.obj['connection'].user_uid,
        gitlab_token=ctx.obj['connection'].gitlab_impersonation_token,
        account_uid=account_uid,
        project_uid=project_uid,
        job_uid=job_uid,
        dir=home
    )
    p = subprocess.Popen(cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.wait()
    status_code = p.returncode
    if status_code == 128:
        print("Could not find the remote git repository.")
        exit(0)

    jobs_path = '/jobs/{job_uid}/output/'.format(job_uid=job_uid)
    copy_from_dir = onepanel_download_path + jobs_path
    if not os.path.exists(copy_from_dir):
        print('This job did not create any output or output was not saved\n'
              'If you want to save and version control your output, modify your script to save all output to the '
              '\'/home/onepanel/output\' or \'~/output\' directory.')
        if os.path.isdir(onepanel_download_path):
            shutil.rmtree(onepanel_download_path,
                          onerror=remove_readonly)
        exit(0)
    else:
        dir_util.copy_tree(copy_from_dir, home)

    if os.path.isdir(onepanel_download_path):
        shutil.rmtree(onepanel_download_path, onerror=remove_readonly)

    if p.returncode == 0:
        print('Job output downloaded to: {dir}'.format(dir=home))
        return True
    else:
        print('Unable to download')
        return False


@jobs.command('delete', help='Delete a job')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def delete_job(ctx, job_uid):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    ctx.obj['vc'].delete(job_uid, message_on_success='Job deleted', message_on_failure='Job not found')


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)
