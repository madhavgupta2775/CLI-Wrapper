import ctypes
from tkinter import *
import os
import sys
import subprocess

sys.path.insert(0, "./TkTerm")
from tkterm import Terminal

def configure_aws_cli():
    # Set AWS region and output format
    aws_region = "ap-south-1"
    aws_output = "json"
    
    # Configure AWS CLI with the specified region and output format
    subprocess.run(['aws', 'configure', 'set', 'region', aws_region])
    subprocess.run(['aws', 'configure', 'set', 'output', aws_output])


root = Tk()
# Hide root window during initialization
root.withdraw()

# Set title
root.title("Terminal")

# Create terminal
term = Terminal(root)
term.pack(expand=True, fill="both")

# Set minimum size and center app
root.update_idletasks()

# Get minimum size
minimum_width = 800
minimum_height = 600

# Get center of screen based on minimum size
x_coords = int(root.winfo_screenwidth() / 2 - minimum_width / 2)
y_coords = int(root.wm_maxsize()[1] / 2 - minimum_height / 2)

# Place app and make the minimum size the actual minimum size (non-infringable)
root.geometry(f"{minimum_width}x{minimum_height}+{x_coords}+{y_coords}")
root.wm_minsize(minimum_width, minimum_height)

# Configure AWS CLI
configure_aws_cli()

# Show root window
root.deiconify()

# Start mainloop
root.mainloop()
