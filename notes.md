name: Docker Image CI - wopr-config_service

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:

  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Build the Docker image
      run: cd wopr/systems/wopr-config-system/config-service/docker build . --file Dockerfile --tag wopr-config_service:$(date +%Y%m%d-%H%M%S)
