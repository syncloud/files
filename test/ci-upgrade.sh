#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

DISTRO=$1
ARCH=$2
NAME=files
DOMAIN="${DISTRO}.com"
APP_DOMAIN="${NAME}.${DOMAIN}"

getent hosts $APP_DOMAIN | sed "s/$APP_DOMAIN/auth.$DOMAIN/g" | tee -a /etc/hosts
cat /etc/hosts

APP_ARCHIVE_PATH=$(realpath $(cat ${DIR}/package.name))

cd ${DIR}/test
./deps.sh
py.test -x -s upgrade.py --distro=$DISTRO --app-archive-path=$APP_ARCHIVE_PATH --app=$NAME --arch=$ARCH
