include .env
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SYSTEM := $(shell echo "$(MAKEFILE_DIR)" | awk -F/ '{print $$(NF-2)}')

test:
	docker build . -t $(SYSTEM)-local
	docker run -p 8000:8000 -e DIRECTUS_HOST=$(DIRECTUS_HOST) $(SYSTEM)-local:latest
