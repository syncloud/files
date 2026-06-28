#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ROOT=$( cd "${DIR}/../.." && pwd )

PROJECT="${1:-desktop}"
NAME=files
export PLAYWRIGHT_DOMAIN="${PLAYWRIGHT_DOMAIN:-bookworm.com}"
export PLAYWRIGHT_USER="${PLAYWRIGHT_USER:-user}"
export PLAYWRIGHT_PASSWORD="${PLAYWRIGHT_PASSWORD:-Password1}"
export PLAYWRIGHT_PROJECT="${PROJECT}"
export PLAYWRIGHT_DEVICE_HOST="${NAME}.${PLAYWRIGHT_DOMAIN}"
export PLAYWRIGHT_SSH_PASSWORD="${PLAYWRIGHT_PASSWORD}"
export PLAYWRIGHT_ARTIFACT_DIR="${ROOT}/artifact"

DOMAIN="$PLAYWRIGHT_DOMAIN"
APP_DOMAIN="${NAME}.${DOMAIN}"
getent hosts $APP_DOMAIN | sed "s/$APP_DOMAIN/auth.$DOMAIN/g" | tee -a /etc/hosts
cat /etc/hosts

apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq sshpass openssh-client >/dev/null 2>&1 || true

cd ${DIR}
npm ci
npx playwright test --project="${PROJECT}"
