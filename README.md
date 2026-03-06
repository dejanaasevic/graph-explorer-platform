# Graph Explorer

A web-based platform for graph visualization and exploration, supporting multiple data sources and visualization styles.

---

## Team

| Student        | Index     |
|----------------|-----------|
| Dejana Šević   | SV63/2023 |
| Vuk Đorđević   | SV32/2023 |
| Nikša Čvorović | SV14/2023 |
| Nađa Lučić     | SV50/2023 |

---

## Prerequisites

- Python 3.10+
- pip
- virtualenv (installed automatically by the run scripts)

---

## Setup and Running

The run scripts will automatically:
1. Create and activate a virtual environment (`.venv`)
2. Install all required dependencies from `requirements.txt`
3. Install all plugins and the platform
4. Start the Django development server

### Linux / macOS

```bash
chmod +x run.sh
./run.sh
```

### Windows (PowerShell)

```powershell
.\run.ps1
```

The application will be available at: **http://127.0.0.1:8000**

---

## Manual Setup (alternative)

If you prefer to set up manually:

```bash
# Create and activate virtual environment
python -m venv .venv

# Linux
source .venv/bin/activate
# Windows
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install platform and plugins
pip install ./api
pip install ./core
pip install ./json_data_source
pip install ./xml_data_source
pip install ./simple_visualizer
pip install ./block_visualizer

# Run the Django application
python ./graph_explorer/manage.py runserver
```

---

## Running Tests

### Linux / macOS

```bash
chmod +x test.sh
./test.sh
```

### Windows (PowerShell)

```powershell
.\test.ps1
```

The test scripts will install `api` and `core` in editable mode (`-e`) and run `pytest`.

---