from setuptools import setup
from os.path import join, dirname

version = open(join(dirname(__file__), 'version')).read().strip()

setup(
    name='syncloud-files',
    version=version,
    packages=['syncloud_files'],
    description='Syncloud Files Browser',
    long_description='Syncloud Files Browser',
    license='GPLv3',
    author='Syncloud',
    author_email='support@syncloud.org',
    url='https://github.com/syncloud/files')
