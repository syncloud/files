import os
import shutil
from os.path import dirname, join

import pytest
import requests
from syncloudlib.integration.hosts import add_host_alias_by_ip
from syncloudlib.integration.installer import local_install, local_remove, wait_for_installer
from syncloudlib.integration.ssh import run_scp, run_ssh

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, platform_data_dir, data_dir, artifact_dir, device):
    def module_teardown():

        platform_log_dir = join(artifact_dir, 'platform_log')
        os.mkdir(platform_log_dir)
        device.scp_from_device('{0}/log/*'.format(platform_data_dir), platform_log_dir)

        app_log_dir = join(artifact_dir, 'files_log')
        os.mkdir(app_log_dir)

        device.run_ssh('mkdir {0}'.format(TMP_DIR), throw=False)

        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl -u snap.files.uwsgi > {0}/journalctl.uwsgi.log'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl -u snap.files.nginx > {0}/journalctl.nginx.log'.format(TMP_DIR), throw=False)

        device.scp_from_device('{0}/log/*'.format(data_dir), app_log_dir)
        device.scp_from_device('{0}/*.log'.format(TMP_DIR), app_log_dir)

    request.addfinalizer(module_teardown)


def test_start(module_setup, device_host, app, domain, device):
    add_host_alias_by_ip(app, domain, device_host)
    print(check_output('date', shell=True))
    device.run_ssh('date', retries=20)


def test_activate_device(device):
    response = device.activate()
    assert response.status_code == 200, response.text


def test_install(app_archive_path, device_host, device_password, device_session):
    local_install(device_host, device_password, app_archive_path)
    wait_for_installer(device_session, device_host)


def test_remove(device_session, device_host):
    response = device_session.get('https://{0}/rest/remove?app_id=mail'.format(device_host),
                                  allow_redirects=False, verify=False)
    assert response.status_code == 200, response.text
    wait_for_installer(device_session, device_host)


def test_reinstall(app_archive_path, app_domain, device_password):
    local_install(app_domain, device_password, app_archive_path)


def test_login(app_domain, device_user, device_password):
    session = requests.session()
    response = session.post('https://{0}/rest/login'.format(app_domain),
                            data={'name': device_user,' password': device_password},
                            verify=False)
    assert response.status_code == 200, response.text


def test_browse_root(app_domain, device_user, device_password):
    session = requests.session()
    response = session.post('https://{0}/rest/login'.format(app_domain),
                            data={'name': device_user, 'password': device_password},
                            verify=False)
    assert response.status_code == 200, response.text
    
    response = session.get('https://{0}/rest/files/'.format(app_domain),
                           verify=False)
    assert response.status_code == 200, response.text
