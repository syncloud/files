#!/bin/bash -e
DIR=$( cd "$( dirname "$0" )" && pwd )

${DIR}/../apt.sh sshpass openssh-client wget
pip install -r ${DIR}/requirements.txt
