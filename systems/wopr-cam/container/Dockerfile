# Build stage
# Use official Python image as base
FROM python:3.13-slim as builder
ARG DOTRACE
RUN apt-get update \
&& apt-get install -y --no-install-recommends netcat-openbsd \
&& rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 wopr
USER 1000:1000
WORKDIR /app
COPY --chown=1000:1000 requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --user -r /app/requirements.txt

COPY --chown=1000:1000 app.py /app/app.py
COPY --chown=1000:1000 wopr-pymod/ /app/wopr-pymod/
RUN pip install --no-cache-dir --user -e /app/wopr-pymod
COPY --chown=1000:1000 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
