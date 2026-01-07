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

# Build stage
# Use official Python image as base
FROM python:3.13-slim as builder
ARG DOTRACE
RUN apt-get update \
&& apt-get install -y --no-install-recommends netcat-openbsd \
&& rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 2222 wopr
USER 2222:2222
WORKDIR /app
COPY --chown=2222:2222 requirements.txt /app/requirements.txt
COPY --chown=2222:2222 app.py /app/app.py
COPY --chown=2222:2222 wopr-pymod/ /app/wopr-pymod/
COPY --chown=2222:2222 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN pip install --no-cache-dir --user -r /app/requirements.txt
RUN pip install --no-cache-dir --user -e /app/wopr-pymod
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
