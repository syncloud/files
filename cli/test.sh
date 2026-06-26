#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

go test ./...

BUILD_DIR=${DIR}/../build/snap
${BUILD_DIR}/bin/cli --help
