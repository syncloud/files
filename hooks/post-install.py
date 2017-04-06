APP_NAME = 'files'
SYSTEMD_UWSGI_NAME = 'files-uwsgi'
SYSTEMD_NGINX_NAME = 'files-nginx'

from os.path import join

from syncloud_platform.application import api
from syncloud_platform.gaplib import fs, linux, gen

app = api.get_app_setup(APP_NAME)
app_dir = app.get_install_dir()
app_data_dir = app.get_data_dir()

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

variables = {'app_dir': app_dir, 'app_data_dir': app_data_dir}

templates_path = join(app_dir, 'config.templates')
config_path = join(app_dir, 'config')

gen.generate_files(templates_path, config_path, variables)

app.add_service(SYSTEMD_UWSGI_NAME)
app.add_service(SYSTEMD_NGINX_NAME)

app.register_web(1111)

