import pytest
import requests
from subprocess import check_output
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install
from syncloudlib.http import wait_for_rest

TMP_DIR = '/tmp/syncloud'
APP = 'files'

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir):
    def module_teardown():
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('cat /var/snap/{0}/current/config/config.yaml > {1}/upgrade.config.yaml.log'.format(APP, TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/upgrade.journalctl.log'.format(TMP_DIR), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), artifact_dir, throw=False)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, device_host, domain, device):
    add_host_alias(app, device_host, domain)
    device.activated()
    device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)


def test_install_from_store(device, app_domain):
    device.run_ssh('snap remove {0}'.format(APP), throw=False)
    device.run_ssh('snap install {0}'.format(APP), retries=10)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 50)


def test_upgrade(device_host, device_password, app_archive_path, app_domain):
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)


def test_filebrowser_listening(device):
    device.run_ssh('test -S /var/snap/files/current/filebrowser.sock', retries=20)
