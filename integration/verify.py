import os
import sys
from os import listdir
from os.path import dirname, join, abspath, isdir
import time

import pytest
import shutil

from integration.util.ssh import run_scp, ssh_command, SSH, run_ssh, set_docker_ssh_port

app_path = join(dirname(__file__), '..')
sys.path.append(join(app_path, 'src'))

lib_path = join(app_path, 'lib')
libs = [abspath(join(lib_path, item)) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda x: sys.path.append(x), libs)

import requests

SYNCLOUD_INFO = 'syncloud.info'
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')


@pytest.fixture(scope="session")
def module_setup(request):
    request.addfinalizer(module_teardown)


def module_teardown():
    os.mkdir(LOG_DIR)
    platform_log_dir = join(LOG_DIR, 'platform_log')
    os.mkdir(platform_log_dir)
    run_scp('root@localhost:/opt/data/platform/log/* {0}'.format(platform_log_dir), password=LOGS_SSH_PASSWORD)

    print('-------------------------------------------------------')
    print('syncloud docker image is running')
    print('connect using: {0}'.format(ssh_command(DEVICE_PASSWORD, SSH)))
    print('-------------------------------------------------------')


@pytest.fixture(scope='module')
def user_domain(auth):
    email, password, domain, release, _ = auth
    return 'files.{0}.{1}'.format(domain, SYNCLOUD_INFO)


@pytest.fixture(scope='function')
def syncloud_session():
    session = requests.session()
    session.post('http://localhost/rest/login', data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    return session


def test_start(module_setup):
    shutil.rmtree(LOG_DIR, ignore_errors=True)


def test_activate_device(auth):
    email, password, domain, release, _ = auth

    run_ssh('/opt/app/sam/bin/sam update --release {0}'.format(release), password=DEFAULT_DEVICE_PASSWORD)
    run_ssh('/opt/app/sam/bin/sam --debug upgrade platform', password=DEFAULT_DEVICE_PASSWORD)

    response = requests.post('http://localhost:81/rest/activate',
                             data={'main_domain': SYNCLOUD_INFO, 'redirect_email': email, 'redirect_password': password,
                                   'user_domain': domain, 'device_username': DEVICE_USER, 'device_password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text
    global LOGS_SSH_PASSWORD
    LOGS_SSH_PASSWORD = DEVICE_PASSWORD


def test_install(app_archive_path):
    __local_install(app_archive_path)


def test_remove(syncloud_session):
    response = syncloud_session.get('http://localhost/rest/remove?app_id=files', allow_redirects=False)
    assert response.status_code == 200, response.text


def test_reinstall(app_archive_path):
    __local_install(app_archive_path)

def test_login():
    session = requests.session()
    response = session.post('http://localhost:1111/rest/login', data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text

def test_browse_root():
    session = requests.session()
    response = session.post('http://localhost:1111/rest/files', data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text


def __local_install(app_archive_path):
    email, password, domain, release, version, arch = auth
    run_scp('{0} root@localhost:/app.tar.gz'.format(app_archive_path), password=DEVICE_PASSWORD)
    run_ssh('/opt/app/sam/bin/sam --debug install /app.tar.gz', password=DEVICE_PASSWORD)
    set_docker_ssh_port(DEVICE_PASSWORD)
    time.sleep(3)