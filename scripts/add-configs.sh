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


# tracing.enabled

LISTOFTHINGS="tracing.enabled: true
  tracing.host: https://tempo.monitoring.abode.tailandtraillabs.org
  tracing.port: 6831
  tracing.service_name: wopr-unknown
  tracing.sampling_rate: 1.0"

while IFS= read -r i ; do
  KEY=$(echo $i | cut -d: -f1)
  VALUE=$(echo $i | cut -d: -f2- | sed 's/^ //')
  # PUT /set/${KEY}
  # { "value": "${VALUE}", description: "Added by add-configs.sh", updated_by: "add-configs.sh" }
  CMD="curl -X PUT https://wopr-config.studio.abode.tailandtraillabs.org/set/${KEY} -H 'Content-Type: application/json' -d '{ \"value\": \"${VALUE}\", \"description\": \"Added by add-configs.sh\", \"updated_by\": \"add-configs.sh\" }'"
  echo "Executing: $CMD"
#  eval $CMD
done < <(echo "$LISTOFTHINGS")
