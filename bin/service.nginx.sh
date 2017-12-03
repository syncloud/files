#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|stop]"
    exit 1
fi

case $1 in
start)
    /bin/rm -f ${SNAP_COMMON}/web.socket
    $DIR/nginx/sbin/nginx -t -c ${SNAP_COMMON}/config/nginx/nginx.conf -p $DIR/nginx
    $DIR/nginx/sbin/nginx -c ${SNAP_COMMON}/config/nginx/nginx.conf -p $DIR/nginx &
    timeout 5 /bin/bash -c 'until [ -f ${SNAP_COMMON}/web.socket ]; do sleep 1; done'
    systemd-notify --ready
    wait
    ;;
reload)
    $DIR/nginx/sbin/nginx -c ${SNAP_COMMON}/config/nginx/nginx.conf -s reload -p $DIR/nginx
    ;;
stop)
    $DIR/nginx/sbin/nginx -c ${SNAP_COMMON}/config/nginx/nginx.conf -s stop -p $DIR/nginx
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac