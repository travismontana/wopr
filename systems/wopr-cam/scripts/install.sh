#!/bin/sh

set -eu

BASEDIR="/home/wopr/wopr"
WCAM_DIR="${BASEDIR}/systems/wopr-cam"
WCAM_SHARE="${WCAM_DIR}/share"
SYSTEMD_DIR="/home/wopr/.config/systemd/user/"
WCAM_SERVICE="${SYSTEMD_DIR}/wopr-cam.service"
WCAM_TOBEINSTALLED_SERVICE="${WCAM_SHARE}/wopr-cam.service"
WOPR_CORE_PYMOD="git+https://github.com/travismontana/wopr.git#subdirectory=pymods/wopr-core"

# Install Python dependencies
pip3 install --user --upgrade --break-system-packages ${WOPR_CORE_PYMOD}

mkdir -p ${SYSTEMD_DIR}
cp ${WCAM_TOBEINSTALLED_SERVICE} ${WCAM_SERVICE}
chown wopr:wopr ${WCAM_SERVICE}
chmod 644 ${WCAM_SERVICE}
systemctl --user daemon-reload
systemctl --user enable wopr-cam.service

exit 0