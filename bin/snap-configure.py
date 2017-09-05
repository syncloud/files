import logging
import os
from syncloud_app import logger
import shutil
from os import makedirs
from os.path import join, dirname, relpath, isdir, split
import jinja2


def generate_file_jinja(from_path, to_path, variables, variable_tags=('{{', '}}')):
    from_path_dir, from_path_filename = split(from_path)
    loader = jinja2.FileSystemLoader(searchpath=from_path_dir)
    variable_start_tag, variable_end_tag = variable_tags
    env_parameters = dict(
        loader=loader,
        # some files like udev rules want empty lines at the end
        # trim_blocks=True,
        # lstrip_blocks=True,
        undefined=jinja2.StrictUndefined,
        variable_start_string=variable_start_tag,
        variable_end_string=variable_end_tag
    )
    environment = jinja2.Environment(**env_parameters)
    template = environment.get_template(from_path_filename)
    output = template.render(variables)
    to_path_dir = dirname(to_path)
    if not isdir(to_path_dir):
        makedirs(to_path_dir)
    with open(to_path, 'wb+') as fh:
        fh.write(output.encode("UTF-8"))


def generate_files(from_dir, to_dir, variables, variable_tags=('{{', '}}')):
    if isdir(to_dir):
        shutil.rmtree(to_dir)
    for dir_name, subdirs, files in os.walk(from_dir):
        for filename in files:
            from_path = join(dir_name, filename)
            from_rel_path = relpath(from_path, from_dir)
            to_path = join(to_dir, from_rel_path)
            generate_file_jinja(from_path, to_path, variables, variable_tags)


def makepath(path):
    if not isdir(path):
        makedirs(path)


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
generate_files(templates_path, config_dir, variables)

data_dirs = [
    join(app_data, 'log'),
    join(app_data, 'nginx'),
    join(app_data, 'uwsgi')
]

for data_dir in data_dirs:
    makepath(data_dir)


