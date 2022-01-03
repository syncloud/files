#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

export LD_LIBRARY_PATH=$DIR/python/lib

exec $DIR/python/bin/uwsgi --ini ${SNAP_COMMON}/config/uwsgi/files.ini


