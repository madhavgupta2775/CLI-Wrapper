import ctypes
from tkinter import *
from tkterm import Terminal
import os

# Load the shared library
libshell = ctypes.CDLL('./libshell.so')
libshell.execute_command.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

BUFFER_SIZE = 1024

def execute_command():
    command = terminal.get_command()
    output = ctypes.create_string_buffer(BUFFER_SIZE)
    libshell.execute_command(command.encode('utf-8'), output)
    terminal.write(output.value.decode('utf-8'))

root = Tk()
root.title("Shell")

terminal = Terminal(root)
# change the execute_command function to the one defined above
terminal.execute_command = execute_command

terminal.pack(fill=BOTH, expand=True)

root.mainloop()

