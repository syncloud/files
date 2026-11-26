from subprocess import check_output

import pytest
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from syncloudlib.http import wait_for_rest
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install

import snapd
from services import assert_no_restarts, wait_for_socket

TMP_DIR = '/tmp/syncloud'
APP = 'files'

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir):
    def module_teardown():
        device.run_ssh('ls -la /var/snap/{0}/current > {1}/var.current.ls.log'.format(APP, TMP_DIR), throw=False)
        device.run_ssh('ls -la /var/snap/{0}/common > {1}/var.common.ls.log'.format(APP, TMP_DIR), throw=False)
        device.run_ssh('cat /var/snap/{0}/current/config/config.yaml > {1}/config.yaml.log'.format(APP, TMP_DIR), throw=False)
        device.run_ssh('systemctl status snap.{0}.* --no-pager > {1}/systemctl.status.log'.format(APP, TMP_DIR), throw=False)
        device.run_ssh('top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ps auxfw > {0}/ps.log'.format(TMP_DIR), throw=False)
        device.run_ssh('netstat -nlp > {0}/netstat.log'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl | tail -3000 > {0}/journalctl.log'.format(TMP_DIR), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), artifact_dir)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, device, device_host, app, domain):
    add_host_alias(app, device_host, domain)
    device.run_ssh('date', retries=100)
    device.run_ssh('mkdir -p {0}'.format(TMP_DIR))
    snapd.settle(device)


@pytest.mark.flaky(retries=50, delay=10)
def test_activate_device(device):
    device.run_ssh('rm -f /var/snap/platform/current/syncloud.crt', throw=False)
    response = device.activate_custom()
    assert response.status_code == 200, response.text


def test_install(app_archive_path, device_host, device_password, device):
    snapd.settle(device)
    local_install(device_host, device_password, app_archive_path)


def test_filebrowser_listening(device):
    wait_for_socket(device, APP)


def test_index(app_domain):
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)


def test_services_started_cleanly(device):
    assert_no_restarts(device, APP)


def test_reinstall(app_archive_path, device_host, device_password, device, app_domain):
    local_install(device_host, device_password, app_archive_path)
    wait_for_socket(device, APP)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)
