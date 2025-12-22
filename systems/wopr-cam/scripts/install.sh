#!/bin/sh

set -eu

BASEDIR="/home/wopr/wopr"
WCAM_DIR="$BASEDIR/systems/wopr_cam"
WCAM_SHARE="$WCAM_DIR/share"
WCAM_SERVICE="/etc/systemd/system/wopr-cam.service"
WCAM_TOBEINSTALLED_SERVICE="$WCAM_SHARE/wopr-cam.service"

cp ${WCAM_TOBEINSTALLED_SERVICE} ${WCAM_SERVICE}
chown root:root ${WCAM_SERVICE}
chmod 644 ${WCAM_SERVICE}
systemctl daemon-reload
systemctl enable wopr-cam.service

exit 0