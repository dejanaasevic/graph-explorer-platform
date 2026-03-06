python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install .\api
pip install .\core
pip install .\json_data_source
pip install .\xml_data_source
pip install .\simple_visualizer
pip install .\block_visualizer
python .\graph_explorer\manage.py runserver