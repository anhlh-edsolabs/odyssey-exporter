#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the Python script with all command-line arguments passed to the bash script
python main.py "$@"

# Deactivate the virtual environment
deactivate 