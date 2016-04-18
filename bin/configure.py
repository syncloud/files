import os
from os.path import join, dirname, isdir, abspath, relpath, exists
from string import Template

from syncloud_platform.gaplib import fs, linux


def makefile(path, filename):
    fs.makepath(path)
    filepath = join(path, filename)
    createfile(filepath)

def createfile(filepath):
    try:
        f = open(filepath, 'w+')
        f.close()
    except:
        pass

def generate_file(from_path, to_path, variables):
    from_file = open(from_path, 'r')
    from_text = from_file.read()
    from_file.close()
    t = Template(from_text)
    to_text = t.substitute(variables)
    fs.makepath(dirname(to_path))
    to_file = open(to_path, 'w+')
    to_file.write(to_text)
    to_file.close()

def generate_files(from_dir, to_dir, variables):
    for dir_name, subdirs, files in os.walk(from_dir):
        for filename in files:
            from_path = join(dir_name, filename)
            from_rel_path = relpath(from_path, from_dir)
            to_path = join(to_dir, from_rel_path)
            generate_file(from_path, to_path, variables)

def configure(app_dir, app_data_dir):
    log_path = join(app_data_dir, 'log')

    fs.makepath(log_path)

    client_body_temp_path = join(app_data_dir, 'nginx', 'client_body_temp')
    proxy_temp_path = join(app_data_dir, 'nginx', 'proxy_temp')
    fastcgi_temp_path = join(app_data_dir, 'nginx', 'fastcgi_temp')
    uwsgi_temp_path = join(app_data_dir, 'nginx', 'uwsgi_temp')
    scgi_temp_path = join(app_data_dir, 'nginx', 'scgi_temp')

    fs.makepath(client_body_temp_path)
    fs.makepath(proxy_temp_path)
    fs.makepath(fastcgi_temp_path)
    fs.makepath(uwsgi_temp_path)
    fs.makepath(scgi_temp_path)

    uwsgi_path = join(app_data_dir, 'uwsgi')
    fs.makepath(uwsgi_path)

    createfile(join(uwsgi_path, 'files.wsgi'))
    createfile(join(uwsgi_path, 'files.wsgi.sock'))

    variables = {'app_dir': app_dir, 'app_data_dir': app_data_dir}

    templates_path = join(app_dir, 'templates')
    config_path = join(app_dir, 'config')

    generate_files(templates_path, config_path, variables)


if __name__ == '__main__':
    app_dir = abspath(join(dirname(__file__), '..'))
    app_data_dir = join(app_dir, 'data')
    configure(app_dir, app_data_dir)