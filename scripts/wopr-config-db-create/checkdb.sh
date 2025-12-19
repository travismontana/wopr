kubectl -n wopr run psql-test --rm -it --image=postgres:16-alpine --restart=Never -- psql $(kubectl -n wopr get secret wopr-config-db-cluster-app -o jsonpath='{.data.uri}' | base64 -d) "SELECT 1";

