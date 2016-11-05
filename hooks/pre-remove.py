APP_NAME = 'files'
USER_NAME = 'platform'
SYSTEMD_UWSGI_NAME = 'files-uwsgi'
SYSTEMD_NGINX_NAME = 'files-nginx'

from syncloud_platform.application import api
from syncloud_platform.gaplib import fs

app = api.get_app_setup(APP_NAME)

app.unregister_web()

app.remove_service(SYSTEMD_NGINX_NAME)
app.remove_service(SYSTEMD_UWSGI_NAME)

app_dir = app.get_install_dir()

fs.removepath(app_dir)

