#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install ./api
pip install ./core
pip install ./json_data_source
pip install ./xml_data_source
pip install ./simple_visualizer
pip install ./block_visualizer
python3 ./graph_explorer/manage.py runserver