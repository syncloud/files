import os
import sys
from os import listdir
from os.path import dirname, join, abspath, isdir
import time

import pytest
import shutil

from syncloudlib.integration.ssh import run_scp, run_ssh
from syncloudlib.integration.installer import local_install, wait_for_sam, wait_for_rest, local_remove

import requests

SYNCLOUD_INFO = 'syncloud.info'
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')
APP='files'


@pytest.fixture(scope="session")
def platform_data_dir(installer):
    return syncloudlib.integration.instaler.platform_data_dir(installer)
        
@pytest.fixture(scope="session")
def data_dir(installer):
    return syncloudlib.integration.instaler.data_dir(installer, APP)
         

@pytest.fixture(scope="session")
def app_dir(installer):
    return syncloudlib.integration.instaler.app_dir(installer, APP)


@pytest.fixture(scope="session")
def service_prefix(installer):
    return syncloudlib.integration.instaler.service_prefix(installer)


@pytest.fixture(scope="session")
def ssh_env_vars(installer):
    return syncloudlib.integration.instaler.ssh_env_vars(installer)


@pytest.fixture(scope='function')
def syncloud_session(device_domain):
    session = requests.session()
    session.post('http://{0}/rest/login'.format(device_domain), data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    return session


@pytest.fixture(scope="session")
def module_setup(request, user_domain, platform_data_dir):
    request.addfinalizer(lambda: module_teardown(user_domain, platform_data_dir))


def module_teardown(user_domain, platform_data_dir, data_dir):

    platform_log_dir = join(LOG_DIR, 'platform_log')
    os.mkdir(platform_log_dir)
    run_scp('root@{0}:{1}/log/* {2}'.format(user_domain, platform_data_dir, platform_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    run_scp('root@{0}:/var/log/sam.log {1}'.format(user_domain, platform_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    
    app_log_dir = join(LOG_DIR, 'files_log')
    os.mkdir(app_log_dir)
    run_scp('root@{0}:{1}/log/* {2}'.format(user_domain, data_dir, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(user_domain, 'journalctl | tail -200', password=LOGS_SSH_PASSWORD, throw=False)


def test_start(module_setup):
    shutil.rmtree(LOG_DIR, ignore_errors=True)
    os.mkdir(LOG_DIR)


def test_activate_device(auth, device_domain):
    email, password, domain, release = auth

    response = requests.post('http://{0}:81/rest/activate'.format(device_domain),
                             data={'main_domain': SYNCLOUD_INFO, 'redirect_email': email, 'redirect_password': password,
                                   'user_domain': domain, 'device_username': DEVICE_USER, 'device_password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text
    global LOGS_SSH_PASSWORD
    LOGS_SSH_PASSWORD = DEVICE_PASSWORD


def test_activate_password(device_domain):
    print('default password')
    run_ssh(device_domain, 'date', password=DEFAULT_DEVICE_PASSWORD, throw=False)
    print('activate password')
    run_ssh(device_domain, 'date', password=DEVICE_PASSWORD)
    

def test_install(app_archive_path, device_domain, installer):
    local_install(device_domain, DEVICE_PASSWORD, app_archive_path, installer)


def test_remove(syncloud_session, device_domain):
    response = syncloud_session.get('http://{0}/rest/remove?app_id=files'.format(device_domain), allow_redirects=False)
    assert response.status_code == 200, response.text


def test_reinstall(app_archive_path, device_domain, installer):
    local_install(device_domain, DEVICE_PASSWORD, app_archive_path, installer)

def test_login(user_domain):
    session = requests.session()
    response = session.post('http://{0}/rest/login'.format(user_domain), data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text

def test_browse_root(user_domain):
    session = requests.session()
    response = session.post('http://{0}/rest/login'.format(user_domain), data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text
    
    response = session.get('http://{0}/rest/files/'.format(user_domain))
    assert response.status_code == 200, response.text
