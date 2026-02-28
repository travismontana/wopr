#!/bin/bash

set -e

# Dont run this from a curl/wget/fetch
pppid=$(ps -o comm= -p $(ps -o ppid= -p $$ | tr -d ' ' ))
web_getters = ("curl", "wget", "fetch")
for web_getter in "${web_getters[@]}"; do
    if [[ ${pppid} == ${web_getter} ]]; then
        echo "Don't curl | $0, it's bad juju"
        exit 1
    fi
done

declare -A commands_to_check_for
commands_to_check_for["helm"]=helm
commands_to_check_for["kubectl"]=kubectl

for key in "${!commands_to_check_for[@]}"; do
    installer=${commands_to_check_for[$key]}
    if ! command -v $key &> /dev/null; then
        echo "Command: ${key} is not installed, attempting to install..."
        pamac install ${installer}
    fi
done

