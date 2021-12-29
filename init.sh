#!/usr/bin/env bash

sudo -H pip install -U pipenv
pipenv sync # syncs virtual environment
pipenv shell