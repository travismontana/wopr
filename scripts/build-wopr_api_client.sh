#!/usr/bin/env bash

DEBUG="1" # set to "1" enable

function debugit {
    if [ "$DEBUG" == "1" ]; then
        thing="$1"
        message="$2"
        echo "Thing: (${thing}), Message: (${message})"
    fi
}

SYSTEMS=( "wopr-api" "wopr-web" "wopr-cam" "wopr-model" )

# grab the current directory the script lives in
CURRENT_DIR=$(dirname "$(realpath "$0")")
debugit "CURRENT_DIR" "${CURRENT_DIR}"

# the .env we need is one level up
ENV_FILE="$CURRENT_DIR/../.env"
source ${ENV_FILE}
debugit "ENV_FILE" "${ENV_FILE}"

OPC="/usr/bin/openapi-python-client"
OPCDirectory="${CURRENT_DIR}/../pymods"
OPCJson="${OPCDirectory}/openapi-python-client-config.json"
SYSTEMS_DIR="${CURRENT_DIR}/../systems"

CLIENT_NAME="wopr_api_client"

debugit "OPCJSON" "${OPCJson}"
debugit "SYSTEMS_DIR" "${SYSTEMS_DIR}"

if [ ! -f ${OPC} ]; then
    echo "OpenAPI Python Client not found at ${OPC}. Please install it before running this script."
    exit 1
fi
if [ ! -f ${OPCJson} ]; then
    CONFIG="--config ${OPCJson}"
fi

rm -rf ${OPCDirectory}/${CLIENT_NAME}
${OPC} generate --url "${API_URL}/openapi.json" --output-path "${OPCDirectory}/${CLIENT_NAME}" ${CONFIG}

if [ ! "${?}" -eq 0 ]; then
    echo "Failed to generate API client"
    exit 2
fi

for SYS in "${SYSTEMS[@]}"; do
    echo "Processing system: ${SYS}"

    debugit "Old lib removed"  "a"
    LIBDIR="${SYSTEMS_DIR}/${SYS}/container/app/lib"
    if [ ! -d "${LIBDIR}" ]; then
        mkdir -p ${LIBDIR}
        debugit "Created " "${LIBDIR}"
    fi
    CLIENT="${OPCDirectory}/${CLIENT_NAME}/${CLIENT_NAME}"
    debugit "Copying " "${CLIENT}"
    debugit "To " "${LIBDIR}"
    cp -r ${CLIENT} ${LIBDIR}
    ls ${LIBDIR}/${CLIENT_NAME}
done

exit 0