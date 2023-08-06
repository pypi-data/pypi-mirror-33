from cfmonitor import __version__
from setuptools import setup
from os import path

with open(path.join(path.dirname(__file__), 'requirements.txt')) as f:
    reqs = [l for l in f.read().strip().split('\n') if not l.startswith('-')]

setup(
    name='cfspacemonitor',
    version=__version__,
    description='Cloud Foundry Space Monitor',
    long_description=open('README.md').read(),
    license='Apache License Version 2.0',
    author='Adam Jaso',
    author_email='ajaso@hsdp.io',
    packages=['cfmonitor'],
    package_dir={
        'cfmonitor': 'cfmonitor',
    },
    install_requires=reqs,
    url='https://github.com/hsdp/cf-space-monitor',
)
