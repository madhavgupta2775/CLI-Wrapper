import ctypes
from tkinter import *
import os
import sys
import subprocess
import platform
import logging
from typing import Optional, Dict, Any
from groq import Groq
from tkinter import messagebox, scrolledtext

sys.path.insert(0, "./TkTerm")
from tkterm import Terminal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Groq client
GROQ_API_KEY = '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'  # Replace with your actual API key
groq_client = Groq(api_key=GROQ_API_KEY)

def analyze_with_groq(parsed_command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Analyze the parsed command using Groq's LLM.
    """
    try:
        response = groq_client.analyze(parsed_command)
        if response.get("status") == "success":
            return response.get("data")
        else:
            logging.error("Groq analysis failed: %s", response.get("error"))
            return None
    except Exception as e:
        logging.error("Error while communicating with Groq: %s", str(e))
        return None

def parse_command(command: str) -> Optional[Dict[str, str]]:
    """
    Parse the AWS CLI command into its components.
    """
    parts = command.strip().split()
    if len(parts) < 3:
        return None  # Invalid command format
    provider = parts[0].lower()  # Assuming provider like 'aws' is in lowercase
    service = parts[1].lower()
    action = parts[2].lower()
    resource = ' '.join(parts[3:])
    return {
        "provider": provider,
        "service": service,
        "action": action,
        "resource": resource
    }

def get_user_choice(suggested_safe_command: str, command: str) -> Optional[str]:
    """
    Get user choice on how to handle the command based on the risk level.
    """
    print(f"\nSuggested Safe Command:\n{suggested_safe_command}")
    choice = input("\nChoose an option:\n1. Execute Safe Command\n2. Proceed with Original Command\n3. Abort\n")
    if choice == '1':
        logging.info("User chose to execute safe command: %s", suggested_safe_command)
        return suggested_safe_command
    elif choice == '2':
        logging.info("User chose to proceed with original command: %s", command)
        return command
    elif choice == '3':
        logging.info("User chose to abort command execution.")
        return None
    else:
        logging.warning("Invalid choice.")
        return None

def process_aws_command(command: str) -> None:
    """
    Process the AWS command by analyzing it and taking action based on the risk assessment.
    """
    parsed_command = parse_command(command)
    if not parsed_command:
        logging.warning("Invalid AWS command format")
        return

    analysis_result = analyze_with_groq(parsed_command)
    if not analysis_result:
        logging.error("Failed to get analysis result from Groq")
        return

    risk_level = analysis_result.get("risk_level")
    explanation = analysis_result.get("explanation", [])
    suggested_safe_command = analysis_result.get("suggested_safe_command")

    # Log analysis details
    logging.info("Risk Level: %s", risk_level)
    logging.info("Explanation: %s", ', '.join(explanation))
    logging.info("Suggested Safe Command: %s", suggested_safe_command)

    if risk_level == "Low":
        logging.info("Risk level is Low. Proceeding with the command execution safely.")
        # Direct execution after user confirmation
        os.system(command)
    elif risk_level == "Medium":
        user_choice = get_user_choice(suggested_safe_command, command)
        if user_choice:
            logging.info("Executing user choice: %s", user_choice)
            os.system(user_choice)
    elif risk_level == "High":
        logging.error("Risk level is High. Aborting command execution.")
    else:
        logging.warning("Unexpected risk level.")

def execute_command(command: str):
    """
    Execute a given command, either directly or through Groq analysis if it's an AWS command.
    """
    parsed_command = parse_command(command)
    if parsed_command and parsed_command.get("provider") == "aws":
        logging.info("AWS command detected, processing with Groq analysis.")
        process_aws_command(command)
    else:
        logging.info("Non-AWS command detected, executing directly.")
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stdout:
                print(stdout.decode('utf-8'))
            if stderr:
                print(stderr.decode('utf-8'))
        except Exception as e:
            logging.error(f"Error executing command: {str(e)}")

# Tkinter setup
def setup_tkinter():
    root = Tk()
    root.withdraw()
    root.title("Terminal")

    term = Terminal(root)
    term.pack(expand=True, fill="both")

    root.update_idletasks()
    minimum_width = 800
    minimum_height = 600

    x_coords = int(root.winfo_screenwidth() / 2 - minimum_width / 2)
    y_coords = int(root.winfo_screenheight() / 2 - minimum_height / 2)

    root.geometry(f"{minimum_width}x{minimum_height}+{x_coords}+{y_coords}")
    root.wm_minsize(minimum_width, minimum_height)

    root.deiconify()

    def handle_command_input(event):
        command = event.widget.get("1.0", "end-1c")  # Get command from the terminal widget
        logging.info("Received command: %s", command)
        execute_command(command)
        event.widget.delete("1.0", "end")  # Clear the command after execution

    term.bind("<Return>", handle_command_input)
    root.mainloop()

if __name__ == "__main__":
    setup_tkinter()
