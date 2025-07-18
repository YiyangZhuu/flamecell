#!/bin/bash

# Exit if any command fails
set -e

echo "    Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "    Checking Poetry..."
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "    Installing dependencies with Poetry..."
poetry install

echo "    Setup complete. Activate your environment with:"
echo "    source .venv/bin/activate"
