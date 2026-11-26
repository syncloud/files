#!/bin/bash -e

${SNAP}/bin/wait-for-configure.sh

export SSL_CERT_FILE=/var/snap/platform/current/syncloud.ca.crt

/bin/rm -f ${SNAP_DATA}/filebrowser.sock
exec ${SNAP}/filebrowser/filebrowser -c ${SNAP_DATA}/config/config.yaml
