import os
import sys
from os import listdir
from os.path import dirname, join, abspath, isdir
import time

import pytest
import shutil

from integration.util.ssh import run_scp, run_ssh
import requests

SYNCLOUD_INFO = 'syncloud.info'
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')


@pytest.fixture(scope="session")
def module_setup(request, user_domain):
    request.addfinalizer(lambda: module_teardown(user_domain))


def module_teardown(user_domain):

    platform_log_dir = join(LOG_DIR, 'platform_log')
    os.mkdir(platform_log_dir)
    run_scp('root@{0}:/opt/data/platform/log/* {1}'.format(user_domain, platform_log_dir), password=LOGS_SSH_PASSWORD)
    run_scp('root@{0}:/var/log/sam.log {1}'.format(user_domain, platform_log_dir), password=LOGS_SSH_PASSWORD)

    
    app_log_dir = join(LOG_DIR, 'files_log')
    os.mkdir(app_log_dir)
    run_scp('root@{0}:/opt/data/files/log/* {1}'.format(user_domain, app_log_dir), password=LOGS_SSH_PASSWORD)


@pytest.fixture(scope='function')
def syncloud_session(device_host):
    session = requests.session()
    session.post('http://{0}/rest/login'.format(device_host), data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    return session


def test_start(module_setup):
    shutil.rmtree(LOG_DIR, ignore_errors=True)
    os.mkdir(LOG_DIR)

def test_activate_device(auth, user_domain):
    email, password, domain, release = auth

    run_ssh(user_domain, '/opt/app/sam/bin/sam update --release {0}'.format(release), password=DEFAULT_DEVICE_PASSWORD)
    run_ssh(user_domain, '/opt/app/sam/bin/sam --debug upgrade platform', password=DEFAULT_DEVICE_PASSWORD)

    response = requests.post('http://{0}:81/rest/activate'.format(user_domain),
                             data={'main_domain': SYNCLOUD_INFO, 'redirect_email': email, 'redirect_password': password,
                                   'user_domain': domain, 'device_username': DEVICE_USER, 'device_password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text
    global LOGS_SSH_PASSWORD
    LOGS_SSH_PASSWORD = DEVICE_PASSWORD


def test_install(app_archive_path, device_host):
    __local_install(app_archive_path, device_host)


def test_remove(syncloud_session, device_host):
    response = syncloud_session.get('http://{0}/rest/remove?app_id=files'.format(device_host), allow_redirects=False)
    assert response.status_code == 200, response.text


def test_reinstall(app_archive_path, device_host):
    __local_install(app_archive_path, device_host)

def test_login(user_domain):
    session = requests.session(user_domain)
    response = session.post('http://{0}/rest/login'.format(user_domain), data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text

def test_browse_root(user_domain):
    session = requests.session()
    response = session.post('http://{0}/rest/files'.format(user_domain), data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text


def __local_install(app_archive_path, device_host):
    run_scp('{0} root@{1}:/app.tar.gz'.format(app_archive_path, device_host), password=DEVICE_PASSWORD)
    run_ssh(device_host, '/opt/app/sam/bin/sam --debug install /app.tar.gz', password=DEVICE_PASSWORD)
    time.sleep(3)