#!/bin/bash
virtualenv -p /usr/bin/python3 env
source env/bin/activate
env/bin/pip install -r pip.txt
export FLASK_APP=nemu_cli.py
env/bin/flask run
deactivate
