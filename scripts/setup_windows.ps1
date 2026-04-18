$ErrorActionPreference = "Stop"

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Setup complete."
Write-Host "Run with: .\.venv\Scripts\Activate.ps1; python CNCwithOpenGLfix2.py"
