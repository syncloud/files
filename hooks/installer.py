import logging
import os
from os.path import join

from syncloudlib import fs, linux, gen, logger

USER_NAME="files"

class Installer:
    def __init__(self):
        if not logger.factory_instance:
            logger.init(logging.DEBUG, True)
        self.log = logger.get_logger('files')

        self.install_dir = os.environ['SNAP']
        self.app_data = os.environ['SNAP_COMMON']
        self.templates_path = join(self.install_dir, 'config.templates')
        self.config_dir = join(self.app_data, 'config')

    def install(self):
        linux.useradd(USER_NAME)
        self.regenerate_configs()

    def post_refresh(self):
        self.regenerate_configs()

    def regenerate_configs(self):
        variables = {
            'app_dir': self.install_dir,
            'app_data': self.app_data
        }
        
        gen.generate_files(self.templates_path, self.config_dir, variables)
        
        data_dirs = [
            join(self.app_data, 'log'),
            join(self.app_data, 'nginx'),
            join(self.app_data, 'uwsgi')
        ]

        for data_dir in data_dirs:
            fs.makepath(data_dir)
            fs.chownpath(data_dir, USER_NAME)
