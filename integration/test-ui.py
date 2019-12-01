import os
import shutil
from os.path import dirname, join, exists

import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from syncloudlib.integration.hosts import add_host_alias_by_ip
from syncloudlib.integration.screenshots import screenshots

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud/ui'

@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode):
    def module_teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.ui.{1}.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.ui.{1}.log'.format(TMP_DIR, ui_mode), throw=False)
      
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, 'log'))

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, device_host, domain):
    add_host_alias_by_ip(app, domain, device_host)


def test_web(driver, app_domain, device_domain, ui_mode, device_user, device_password, screenshot_dir):

    driver.get("https://{0}".format(app_domain))
    
    time.sleep(2)
    screenshots(driver, screenshot_dir, 'login-' + ui_mode)

    user = driver.find_element_by_id("user")
    user.send_keys(device_user)
    password = driver.find_element_by_id("password")
    password.send_keys(device_password)
   
    screenshots(driver, screenshot_dir, 'login-filled-' + ui_mode)
  
    password.send_keys(Keys.RETURN)

    time.sleep(10)
    screenshots(driver, screenshot_dir, 'login_progress-' + ui_mode)
    time.sleep(10)
    
    screenshots(driver, screenshot_dir, 'main-' + ui_mode)
    