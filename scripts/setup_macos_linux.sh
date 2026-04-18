#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Setup complete."
echo "Run with: source .venv/bin/activate && python CNCwithOpenGLfix2.py"
