#!/bin/bash

# Compile shell.c to create libshell.so
gcc -shared -o libshell.so -fPIC shell.c

# Run shell_GUI.py using Python 3
python3 shell_GUI.py
