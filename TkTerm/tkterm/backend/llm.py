from transformers import pipeline

class LLMAnalyzer:
    def __init__(self):
        self.analyzer = pipeline("text-generation", model="distilgpt2")

    def analyze_command(self, cmd):
        """Analyzes an AWS command for potential risks and suggests a safer alternative.

        Args:
            cmd (str): The AWS command to analyze.

        Returns:
            dict: A dictionary containing the analysis results with keys:
                - risk_level (str): "Low", "Medium", or "High"
                - explanation (list): List of explanations for the risk level
                - suggested_safe_command (str): A safer alternative command (if applicable)
        """

        prompt = f"""
        Analyze the following AWS command for potential risks and suggest a safer alternative if applicable:
        Command: '{cmd}'
        Output in the following format:
        {{
          "risk_level": "Low/Medium/High",
          "explanation": ["Explanation of potential risks..."],
          "suggested_safe_command": "Safe alternative command if applicable..."
        }}
        """

        analysis_result = self.analyzer(prompt, max_length=1024, num_return_sequences=1)[0]['generated_text']

        # Convert the JSON string to a Python dictionary
        analysis_dict = eval(analysis_result)

        return analysis_dict

    def display_analysis(self, analysis_dict):
        """Prints the analysis results in a user-friendly format.

        Args:
            analysis_dict (dict): The dictionary containing the analysis results.
        """

        print("Risk Level:", analysis_dict.get("risk_level", "N/A"))
        print("Explanation:")
        for item in analysis_dict.get("explanation", []):
            print(item)
        print("Suggested Safe Command:", analysis_dict.get("suggested_safe_command", "N/A"))

