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

kubectl -n wopr run psql-test --rm -it --image=postgres:16-alpine --restart=Never -- psql $(kubectl -n wopr get secret wopr-config-db-cluster-app -o jsonpath='{.data.uri}' | base64 -d) "SELECT 1";

