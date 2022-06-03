#!/usr/bin/env bash

sudo apt update && sudo apt install python3
sudo -H pip install -U pipenv
pipenv sync # syncs virtual environment
pipenv shell

sudo docker build -t rec_sys:latest .
