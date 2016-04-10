#!/bin/sh
APP_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

echo ${APP_DIR}

PYTHONHOME=${APP_DIR}/python
LD_LIBRARY_PATH=${APP_DIR}/python/lib

${APP_DIR}/uwsgi/bin/uwsgi --ini ${APP_DIR}/config/uwsgi/files.ini &

${APP_DIR}/nginx/sbin/nginx -t -c ${APP_DIR}/config/nginx/nginx.conf
${APP_DIR}/nginx/sbin/nginx -c ${APP_DIR}/config/nginx/nginx.conf