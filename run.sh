
#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export RAPIDAPI_KEY="3435a5f168mshb549ceeea51143fp1d3b32jsne1210f22ecb0"
python -m houseguess
