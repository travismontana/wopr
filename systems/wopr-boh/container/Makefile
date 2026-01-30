include .env

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SYSTEM := $(shell echo "$(MAKEFILE_DIR)" | awk -F/ '{print $$(NF-2)}')

test:
	docker build . -t $(SYSTEM)-local
	docker run -p $(PORT):$(PORT) \
		-e API_URL=$(API_URL) \
		-e PGHOST=$(PGHOST) \
		-e PGPORT=$(PGPORT) \
		-e PGUSER=$(PGUSER) \
		-e PGPASSWORD=$(PGPASSWORD) \
		-e PGDATABASE=$(PGDATABASE) \
		$(SYSTEM)-local:latest