1) LogQL: errors/warns + extract IDs + drop k8s noise
{namespace=~"$ns", app=~"$app"}
|~ "(?i)\\b(error|err|warn|warning)\\b"
!= "GET /health"
!= "GET /healthz"
!= "GET /ready"
!= "GET /readyz"
!= "GET /live"
!= "GET /livez"
!= "kube-probe"
!= "readiness probe"
!= "liveness probe"
!= "startup probe"
!= "TLS handshake error"
!= "context canceled"
| json
| label_format trace_id={{.trace_id}} request_id={{.request_id}}

{namespace=~"$ns", app=~"$app"}
|~ "(?i)\\b(error|err|warn|warning)\\b"
| regexp "(?i)trace[_-]?id[=:\" ]+(?P<trace_id>[0-9a-f]{16,32})"
| regexp "(?i)request[_-]?id[=:\" ]+(?P<request_id>[0-9a-z\\-]{8,64})"

2) “Grouped” output you can actually use: counts by best available ID
topk(50,
  count_over_time(
    {namespace=~"$ns", app=~"$app"}
    |~ "(?i)\\b(error|err|warn|warning)\\b"
    != "kube-probe"
    | json
    | label_format
        grp={{if .trace_id}}{{.trace_id}}{{else}}{{if .request_id}}{{.request_id}}{{else}}{{.pod}}{{end}}{{end}}
    [5m]
  )
) by (grp)


1) API: fetch matching WARN/ERROR-ish log lines (with noise filters)


A) Counts by trace_id (Top 50 in last 5 minutes)
curl -G "$LOKI/loki/api/v1/query" \
  --data-urlencode 'query=topk(50,
    sum by (trace_id) (
      count_over_time(
        {namespace="prod", app="wopr-api"}
        |~ "(?i)\\b(error|err|warn|warning)\\b"
        != "kube-probe"
        | json
        | label_format trace_id={{.trace_id}}
      [5m])
    )
  )'

B) Counts by request_id
curl -G "$LOKI/loki/api/v1/query" \
  --data-urlencode 'query=topk(50,
    sum by (request_id) (
      count_over_time(
        {namespace="prod", app="wopr-api"}
        |~ "(?i)\\b(error|err|warn|warning)\\b"
        != "kube-probe"
        | json
        | label_format request_id={{.request_id}}
      [5m])
    )
  )'

C) Fallback counts by pod (if you don’t have IDs)
curl -G "$LOKI/loki/api/v1/query" \
  --data-urlencode 'query=topk(50,
    sum by (pod) (
      count_over_time(
        {namespace="prod", app="wopr-api"}
        |~ "(?i)\\b(error|err|warn|warning)\\b"
        != "kube-probe"
      [5m])
    )
  )'


