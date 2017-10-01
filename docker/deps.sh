#!/bin/bash -xe

apt-get update
apt-get install -y squashfs-tools python-dev build-essential libsasl2-dev libldap2-dev libssl-dev sshpass curl netcat xvfb wget unzip libfontconfig libgtk-3-0 libasound2 libdbus-glib-1-2

wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
pip install -U pytest
pip install coin
ARCH=$(uname -m)
if [ ${ARCH} == "x86_64" ]; then
  wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 --progress dot:giga
  tar xjvf phantomjs-2.1.1-linux-x86_64.tar.bz2
  cp ./phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/bin
else
  wget http://artifact.syncloud.org/3rdparty/phantomjs-2.1.1-armhf
  cp phantomjs-2.1.1-armhf /usr/bin/phantomjs
fi
chmod +x /usr/bin/phantomjs
./install-sam.sh 85 stable
./install-s3cmd.sh
