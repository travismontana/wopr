include .env

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SYSTEM := $(shell echo "$(MAKEFILE_DIR)" | awk -F/ '{print $$(NF-2)}')

test:
	docker build . -t $(SYSTEM)-local
	docker run --user 2222:2222 -p $(PORT):$(PORT) -v /remote/wopr:/remote/wopr -e API_URL=$(API_URL) $(SYSTEM)-local:latest
