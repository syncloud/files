#!/bin/bash -e

export SSL_CERT_FILE=/var/snap/platform/current/syncloud.ca.crt

/bin/rm -f ${SNAP_DATA}/filebrowser.sock

# One-release migration shim (filebrowser 1.4.0 BoltDB -> 2.0.0 SQLite).
# v2 refuses to migrate from a database.db in the working directory, so rename it
# first and point migrateFrom at the copy. Syncloud devices auto-refresh within a
# day, so every device will have upgraded past 1.4.0 by the next release — remove
# this block and the migrateFrom line in config/config.yaml then.
export FILEBROWSER_MIGRATE_FROM=""
if [ ! -f ${SNAP_DATA}/filebrowser.sqlite ]; then
    if [ -f ${SNAP_DATA}/database.db ]; then
        mv ${SNAP_DATA}/database.db ${SNAP_DATA}/database.db.old
    fi
    if [ -f ${SNAP_DATA}/database.db.old ]; then
        export FILEBROWSER_MIGRATE_FROM=${SNAP_DATA}/database.db.old
    fi
fi

exec ${SNAP}/filebrowser/filebrowser -c ${SNAP_DATA}/config/config.yaml
