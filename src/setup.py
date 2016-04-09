from setuptools import setup
from os.path import join, dirname

requirements = [
    'urllib3==1.10.4',
    'requests==2.7.0',
    'beautifulsoup4==4.3.2',
    'massedit==0.66',
    'Flask==0.10.1',
    'flask-login==0.2.10',
    'syncloud-lib==2'
]


version = open(join(dirname(__file__), 'version')).read().strip()

setup(
    name='syncloud-files',
    version=version,
    packages=['syncloud_files'],
    install_requires=requirements,
    description='Syncloud Files Browser',
    long_description='Syncloud Files Browser',
    license='GPLv3',
    author='Syncloud',
    author_email='support@syncloud.org',
    url='https://github.com/syncloud/files')
