#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip install setuptools==81.0.0
pip install pytest
pip install -e ./api
pip install -e ./core
pytest