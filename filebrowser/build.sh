#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

VERSION=$1
if [[ -z "${VERSION}" ]]; then
    echo "usage $0 version"
    exit 1
fi

BUILD_DIR=${DIR}/../build/snap/filebrowser
mkdir -p ${BUILD_DIR}

ARCH=$(dpkg --print-architecture)
[ "${ARCH}" = "armhf" ] && ARCH=armv7

${DIR}/../apt.sh wget ca-certificates

${DIR}/../download-retry.sh \
    https://github.com/gtsteffaniak/filebrowser/releases/download/v${VERSION}/linux-${ARCH}-filebrowser \
    ${BUILD_DIR}/filebrowser
chmod +x ${BUILD_DIR}/filebrowser
