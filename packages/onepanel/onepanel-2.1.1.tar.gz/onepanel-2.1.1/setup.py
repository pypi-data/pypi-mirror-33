from setuptools import setup
from onepanel.constants import *

setup(
    name="onepanel",
    version=CLI_VERSION,
    packages = ['onepanel', 'onepanel.commands','onepanel.utilities'],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=[
        'requests',
        'click',
        'PTable',
        'configobj',
        'websocket-client',
        'humanize'
    ],
    entry_points='''
        [console_scripts]
        onepanel=onepanel.cli:main
    ''',
)
