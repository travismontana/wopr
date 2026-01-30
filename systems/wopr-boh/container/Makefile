include .env

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SYSTEM := $(shell echo "$(MAKEFILE_DIR)" | awk -F/ '{print $$(NF-2)}')

test:
	docker build . -t $(SYSTEM)-local
	docker run -p $(PORT):$(PORT) \
		-e API_URL=$(API_URL) \
		-e DB_HOST=$(DB_HOST) \
		-e DB_PORT=$(DB_PORT) \
		-e DB_USER=$(DB_USER) \
		-e DB_PASSWORD=$(DB_PASSWORD) \
		-e DB_DATABASE=$(DB_DATABASE) \
		$(SYSTEM)-local:latest