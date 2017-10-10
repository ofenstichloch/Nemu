#!/bin/bash
PYTHON=$(which python3)
virtualenv -p $PYTHON env
source env/bin/activate
env/bin/pip install -r pip.txt
docker pull ofenstichloch/nemu
export FLASK_APP=nemu_cli.py
env/bin/flask run --host=0.0.0.0
deactivate
