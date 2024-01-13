#!/bin/sh -xe

DIR=$( cd "$( dirname "$0}" )" && pwd )

cd $DIR
BUILD_DIR=${DIR}/../build/files/python
while ! docker build -t python:syncloud . ; do
  echo "retry docker"
done
docker run --rm python:syncloud python --help
docker run --rm python:syncloud uwsgi --help
docker create --name=python python:syncloud
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
docker export python -o python.tar
tar xf python.tar
rm -rf python.tar
docker rm python
docker rmi python:syncloud
cp ${DIR}/bin/* ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
