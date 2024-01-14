import os
from os.path import dirname, join
from subprocess import check_output

import pytest
import requests
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, platform_data_dir, data_dir, artifact_dir, device):
    def module_teardown():
        platform_log_dir = join(artifact_dir, 'platform_log')
        os.mkdir(platform_log_dir)
        device.scp_from_device('{0}/log/*'.format(platform_data_dir), platform_log_dir)

        app_log_dir = join(artifact_dir, 'log')
        os.mkdir(app_log_dir)

        device.run_ssh('mkdir {0}'.format(TMP_DIR), throw=False)

        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl -u snap.files.uwsgi > {0}/journalctl.uwsgi.log'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl -u snap.files.nginx > {0}/journalctl.nginx.log'.format(TMP_DIR), throw=False)

        device.scp_from_device('{0}/log/*'.format(data_dir), app_log_dir)
        device.scp_from_device('{0}/*.log'.format(TMP_DIR), app_log_dir)
        check_output('chmod -R a+r {0}'.format(app_log_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, device, app, domain, device_host):
    add_host_alias(app, device_host, domain)
    device.run_ssh('date', retries=100, throw=True)
    device.run_ssh('mkdir {0}'.format(TMP_DIR))


def test_activate_device(device):
    response = device.activate_custom()
    assert response.status_code == 200, response.text


def test_install(app_archive_path, device_host, device_password, device_session):
    local_install(device_host, device_password, app_archive_path)
    

def test_index(app_domain, files_session):
    response = files_session.get('https://{0}'.format(app_domain), verify=False)
    assert response.status_code == 200, response.text


def test_remove(device, app):
    response = device.app_remove(app)
    assert response.status_code == 200, response.text


def test_reinstall(app_archive_path, app_domain, device_password):
    local_install(app_domain, device_password, app_archive_path)


@pytest.fixture(scope='function')
def files_session(app_domain, device_user, device_password):
    session = requests.session()
    response = session.post('https://{0}/rest/login'.format(app_domain),
                            json={'name': device_user, 'password': device_password},
                            verify=False)
    assert response.status_code == 200, response.text
    return session


def test_browse_root(app_domain, files_session):
    response = files_session.get('https://{0}/rest/list?dir=/'.format(app_domain),
                                 verify=False)
    assert response.status_code == 200, response.text


def test_browse_dir_with_space(app_domain, files_session, device):
    device.run_ssh('mkdir /files\ space\ test')
    device.run_ssh('ls -la /')

    response = files_session.get('https://{0}/rest/list'.format(app_domain),
                                 params={'dir': '/files space test'},
                                 verify=False)
    assert response.status_code == 200, response.text


def test_browse_dir_with_plus(app_domain, files_session, device):
    device.run_ssh('mkdir /files+test')
    device.run_ssh('ls -la /')

    response = files_session.get('https://{0}/rest/list'.format(app_domain),
                                 params={'dir': '/files+test'},
                                 verify=False)
    assert response.status_code == 200, response.text
