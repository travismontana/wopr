#!/bin/sh
# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
#mkdir -p ${SYSTEMD_DIR}
#rm -f ${WCAM_SERVICE}
#cp ${WCAM_TOBEINSTALLED_SERVICE} ${WCAM_SERVICE}
#chown wopr:wopr ${WCAM_SERVICE}
#chmod 644 ${WCAM_SERVICE}
systemctl --user daemon-reload
systemctl --user enable ${SERVICE_NAME}
systemctl --user restart ${SERVICE_NAME}
exit 0