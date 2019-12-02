import os
from os.path import join, isfile

from syncloudlib import logger

class Browser:

    def __init__(self, browser_config):
        self.log = logger.get_logger('browser')
        self.browser_config = browser_config
        self.www_root = self.browser_config.www_root()

    def browse(self, filesystem_path):
        entries = sorted(os.listdir(filesystem_path))
        return [{'name': entry, 'is_file': isfile(join(filesystem_path, entry))} for entry in entries]
