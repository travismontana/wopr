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

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-trixie AS builder-image

ARG DEBIAN_FRONTEND=noninteractive
ARG THUMBOR_VERSION

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y autoremove && \
    apt-get install --no-install-recommends -y \
        curl \
        libssl-dev \
        libcurl4-openssl-dev \
        libjpeg-dev \
        libwebp-dev \
        libjpeg-progs \
        zlib1g-dev \
        gifsicle \
        gcc \
        libcairo2-dev \
        build-essential && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/thumbor_dist
COPY dist/* /tmp/thumbor_dist

RUN python3 -m venv /home/thumbor/venv
ENV PATH="/home/thumbor/venv/bin:$PATH"

RUN pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir --find-links=/tmp/thumbor_dist thumbor[all]==${THUMBOR_VERSION}

FROM python:${PYTHON_VERSION}-slim-trixie AS runner-image

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        gifsicle \
        libcairo2 \
        libjpeg-turbo-progs && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home thumbor
COPY --from=builder-image /home/thumbor/venv /home/thumbor/venv

USER thumbor

EXPOSE 8888

ENV PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/home/thumbor/venv
ENV PATH="/home/thumbor/venv/bin:$PATH"

ENTRYPOINT ["thumbor"]