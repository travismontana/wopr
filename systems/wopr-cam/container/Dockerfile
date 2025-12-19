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
RUN pip install --no-cache-dir --user -r /app/requirements.txt

COPY --chown=2222:2222 app.py /app/app.py
COPY --chown=2222:2222 wopr-pymod/ /app/wopr-pymod/
RUN pip install --no-cache-dir --user -e /app/wopr-pymod
COPY --chown=2222:2222 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
