#!/bin/bash
source venv/bin/activate

# Fresh terminal output
clear

# Run cli script
python3 ./launchlivestreamchats/cli.py

# Check the exit status ($? holds the status of the last command)
if [ $? -eq 0 ]; then
    echo "Python script completed successfully."
    # Optionally close the terminal
    exec exit 0
else
    echo "Python script failed with exit code $?. Check the output for details."
    # Optionally keep the terminal open or exit with an error code
    exit 1
fi
