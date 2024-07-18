import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import platform
import logging
from groq import Groq

# Set the API key directly in the script
GROQ_API_KEY = ''

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

# Setup logging
logging.basicConfig(filename='cloud_defense.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

class CloudDefenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CloudDefense Terminal")

        # Configure AWS CLI default region and output
        self.configure_aws_cli()

        # Create UI components
        self.create_widgets()

    def configure_aws_cli(self):
        # Set AWS region and output format
        aws_region = "ap-south-1"
        aws_output = "json"
        
        # Configure AWS CLI with the specified region and output format
        subprocess.run(['aws', 'configure', 'set', 'region', aws_region])
        subprocess.run(['aws', 'configure', 'set', 'output', aws_output])

    def create_widgets(self):
        # Create text area for displaying commands and results
        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Create entry for command input
        self.command_entry = tk.Entry(self.root, width=80)
        self.command_entry.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.command_entry.focus_set()  # Set focus on the command entry

        # Bind Enter key to execute command
        self.command_entry.bind('<Return>', self.execute_command)

    def execute_command(self, event):
        command = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)  # Clear command entry

        if command.lower() in ['exit', 'quit']:
            self.root.quit()
            return

        # Send the command to LLM for analysis
        suggestions, modified_command = self.send_to_llm(command)

        # Log the command and suggestions
        logging.info(f"Command: {command}")
        logging.info(f"Suggestions: {suggestions}")

        # Display suggestions
        self.output_text.insert(tk.END, "Suggestions:\n")
        self.output_text.insert(tk.END, suggestions + "\n")

        # Automatically use the recommended command if provided
        if modified_command:
            self.output_text.insert(tk.END, f"Using Recommended Command: {modified_command}\n")
            command = modified_command

        # Confirm execution if high risk
        if 'High risk' in suggestions:
            if not messagebox.askyesno("High Risk Command", "Do you want to proceed with the recommended command?"):
                return

        # Execute the command
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stdout:
                self.output_text.insert(tk.END, stdout.decode('utf-8') + "\n")
            if stderr:
                self.output_text.insert(tk.END, stderr.decode('utf-8') + "\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error executing command: {str(e)}\n")

    def send_to_llm(self, command):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant who answers user questions in brief and to the point."
                },
                {
                    "role": "user",
                    "content": f"Identify security issues with this AWS CLI command and suggest up to 3 improvements, including an updated command if necessary: {command}",
                }
            ],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        suggestions, modified_command = response.split('Recommended Command: ') if 'Recommended Command:' in response else (response, None)
        return suggestions.strip(), modified_command.strip() if modified_command else None

def main():
    root = tk.Tk()
    app = CloudDefenseApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
