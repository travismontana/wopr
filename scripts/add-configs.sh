#!/bin/sh

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
  eval $CMD
done < <(echo "$LISTOFTHINGS")