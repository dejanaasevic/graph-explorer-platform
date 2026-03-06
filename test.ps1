python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install setuptools==81.0.0
pip install pytest
pip install -e ./api
pip install -e ./core
pytest