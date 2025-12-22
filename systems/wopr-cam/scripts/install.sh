#!/bin/sh

set -eu

BASEDIR="/home/wopr/wopr"
WCAM_DIR="${BASEDIR}/systems/wopr-cam"
WCAM_SHARE="${WCAM_DIR}/share"
SYSTEMD_DIR="/home/wopr/.config/systemd/user/"
SERVICE_NAME="wopr-cam.service"
WCAM_SERVICE="${SYSTEMD_DIR}/${SERVICE_NAME}"
WCAM_TOBEINSTALLED_SERVICE="${WCAM_SHARE}/${SERVICE_NAME}"
WOPR_CORE_PYMOD="git+https://github.com/travismontana/wopr.git#subdirectory=pymods/wopr-core"

# Install Python dependencies
pip3 install --user --upgrade --break-system-packages ${WOPR_CORE_PYMOD}
pip3 install --no-cache-dir --user --break-system-packages -r ${WCAM_DIR}/app/requirements.txt
mkdir -p ${SYSTEMD_DIR}
rm -f ${WCAM_SERVICE}
cp ${WCAM_TOBEINSTALLED_SERVICE} ${WCAM_SERVICE}
chown wopr:wopr ${WCAM_SERVICE}
chmod 644 ${WCAM_SERVICE}
systemctl --user daemon-reload
systemctl --user enable ${SERVICE_NAME}

exit 0