MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SYSTEM := $(shell echo "$(MAKEFILE_DIR)" | awk -F/ '{print $$(NF-2)}')

test:
	docker build . -t $(SYSTEM)-local
	docker run -p 8501:8501 $(SYSTEM)-local:latest
