import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter.font import Font
import os
import sys
import json
import subprocess
import logging

# Add to system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.TerminalTab import TerminalTab
from src.Interpreter import Interpreter
from src.ExitDiaglogBox import ExitDiaglogBox
from src.Utils import get_absolute_path
from src.Config import TkTermConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Terminal(tk.Frame):
    """ Terminal widget """

    def __init__(self, parent, text=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.splashText = text

        # Initialised all interpreter backends
        Interpreter.init_backends()

        ########################################################################
        # Load setting profile
        ########################################################################
        self.TerminalConfig = TkTermConfig.get_default()

        if "Cascadia Code SemiLight" in font.families():
            self.TerminalConfig["fontfamily"] = "Cascadia Code SemiLight"
        else:
            self.TerminalConfig["fontfamily"] = "Consolas"

        TkTermConfig.set_default(self.TerminalConfig)

        # Load settings from file
        if os.path.isfile(TkTermConfig.CONFIG_FILE):
            with open(TkTermConfig.CONFIG_FILE, "r") as f:
                try:
                    data = json.load(f)

                    for k in data.keys():
                        if k in self.TerminalConfig.keys():
                            self.TerminalConfig[k] = data[k]
                except Exception as e:
                    logging.error("Error loading configuration: %s", str(e))

        TkTermConfig.set_config(self.TerminalConfig)

        ########################################################################
        # Create terminal tabs using notebook
        ########################################################################
        self.notebook = TerminalTab(self, self.splashText)
        self.notebook.pack(expand=True, fill=BOTH)

    def add_interpreter(self, *args, **kwargs):
        """ Add a new interpreter and optionally set as default """
        Interpreter.add_interpreter(*args, **kwargs)

    def run_command(self, cmd):
        """ Run command on current terminal tab with security checks """
        # Get the selected tab
        tab_id = self.notebook.select()

        # Get the associated terminal widget
        terminal = self.notebook.nametowidget(tab_id)
        if terminal:
            # Perform security checks before executing the command
            safe_command = self.secure_command(cmd)
            if safe_command:
                terminal.run_command(safe_command)

    def secure_command(self, cmd):
        """ Securely process the command before execution """
        logging.info("Processing command: %s", cmd)

        # Example of command validation and adjustment
        if cmd.startswith('aws'):
            # Example security check: Ensure command is safe
            if not self.validate_aws_command(cmd):
                logging.warning("Command validation failed.")
                return None

        # Return the safe command
        return cmd

    def validate_aws_command(self, cmd):
        """ Validate AWS commands to ensure they are safe """
        # Here you can integrate with Groq or other security analysis tools
        # For now, it will be a placeholder for validation logic
        logging.info("Validating AWS command: %s", cmd)
        # Placeholder for Groq analysis or other security checks
        return True

    def on_resize(self, event):
        """ Auto scroll to bottom when resize event happens """
        first_visible_line = self.TerminalScreen.index("@0,0")

        if self.scrollbar.get()[1] >= 1:
            self.TerminalScreen.see(END)
        # elif float(first_visible_line) >  1.0:
        #     self.TerminalScreen.see(float(first_visible_line)-1)

        # self.statusText.set(self.TerminalScreen.winfo_height())

def main():
    """ Main function """
    root = tk.Tk()
    root.title("TkTerm - Terminal Emulator")
    root.geometry("700x400")

    terminal = Terminal(root)
    terminal.pack(expand=True, fill=BOTH)

    icon = PhotoImage(file=get_absolute_path(__file__, "icon.png"))
    root.iconphoto(False, icon)

    ExitDiaglogBox(root, icon)
    root.mainloop()

if __name__ == "__main__":
    main()
