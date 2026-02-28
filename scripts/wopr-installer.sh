#!/bin/bash

set -e

# Dont run this from a curl/wget/fetch
pppid=$(ps -o comm= -p $(ps -o ppid= -p $$ | tr -d ' ' ))
web_getters=("curl" "wget" "fetch")
for web_getter in "${web_getters[@]}"; do
    if [[ ${pppid} == ${web_getter} ]]; then
        echo "Don't curl | $0, it's bad juju"
        exit 1
    fi
done

declare -A commands_to_check_for
commands_to_check_for["helm"]=helm
commands_to_check_for["kubectl"]=kubectl

echo "Checking for commands"
for key in "${!commands_to_check_for[@]}"; do
    installer=${commands_to_check_for[$key]}
    if ! command -v $key &> /dev/null; then
        echo "Command: ${key} is not installed, attempting to install..."
        pamac install ${installer}
    fi
done

echo "All required commands are installed."

# make sure there are 3 disks of 250G each available.

# make sure we have sudo
sudo -T 10 -l > /dev/null 2>&1
SUDO_STATUS=$?

if [ $SUDO_STATUS -ne 0 ]; then
    echo "This script requires sudo privileges. Please run as a user with sudo access."
    exit 1
fi

