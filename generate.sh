#!/bin/bash
# Helper script to run the certificate generator easily

# Activate virtual environment and run the generator
cd "$(dirname "$0")"
./venv/bin/python main.py "$@"
