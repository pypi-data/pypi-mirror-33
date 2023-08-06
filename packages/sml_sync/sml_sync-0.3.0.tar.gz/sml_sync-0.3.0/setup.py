import os
from distutils.core import setup

here = os.path.dirname(os.path.abspath(__file__))

version_ns = {}
with open(os.path.join(here, 'sml_sync', 'version.py')) as f:
    exec(f.read(), {}, version_ns)

packages = [
    'sml_sync',
    'sml_sync.screens',
    'sml_sync.cli',
    'sml_sync.screens.components'
]

setup(
    name='sml_sync',
    version=version_ns['version'],
    description='SherlockML file synchronizer',
    author='ASI Data Science',
    packages=packages,
    entry_points={
        'console_scripts': ['sml-sync=sml_sync:run']
    },
    install_requires=[
        'sml',
        'daiquiri',
        'paramiko',
        'watchdog',
        'semantic_version',
        'prompt_toolkit>=2.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]

)
