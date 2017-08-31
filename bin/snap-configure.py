import logging
import os
from os.path import isdir, join
from syncloud_app import logger
import shutil

logger.init(logging.DEBUG, console=True, line_format='%(message)s')
log = logger.get_logger('files')

install_dir = os.environ['SNAP']
app_data = os.environ['SNAP_COMMON']
templates_path = join(install_dir, 'config.templates')
config_dir = join(app_data, 'config')

variables = {
    'app_dir': install_dir,
    'app_data': app_data
}
gen.generate_files(templates_path, config_dir, variables)

data_dirs = [
    join(app_data, 'log'),
    join(app_data, 'nginx'),
    join(app_data, 'uwsgi')
]

for data_dir in data_dirs:
    fs.makepath(data_dir)

app.register_web(1111)
