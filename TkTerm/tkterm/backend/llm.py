from groq import Groq
import json

class LLMAnalyzer:
    def __init__(self):
        # Initialize the Groq client with your API key
        self.client = Groq(api_key='')

    def analyze_command(self, cmd):
        """
        Analyzes an AWS command for potential risks and suggests a safer alternative.

        Args:
            cmd (str): The AWS command to analyze.

        Returns:
            dict: A dictionary containing the analysis results with keys:
                  - risk_level (str): "Low", "Medium", or "High"
                  - explanation (list): List of explanations for the risk level
                  - suggested_safe_command (str): A safer alternative command (if applicable)
        """
        system_message = (
            "You are a security analyst who evaluates AWS CLI commands for potential risks."
            " Provide a risk assessment in JSON format."
        )
        user_message = (
            f"Evaluate the security risks of the following AWS CLI command and provide a risk assessment in the following JSON format:\n"
            f"Command: {cmd}\n\n"
            "JSON Format:\n"
            '{"risk_level": "High/Medium/Low", "explanation": ["reason1", "reason2"], "suggested_safe_command": "command"}\n\n'
            "Response:"
        )

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                model="llama3-8b-8192",
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=1024,
                top_p=1
            )

            # Extract the response
            response_text = chat_completion.choices[0].message.content
            
            # Parse the JSON response
            analysis_dict = self.parse_llm_response(response_text)
        except Exception as e:
            analysis_dict = {"error": str(e)}

        return analysis_dict

    def parse_llm_response(self, response):
        """
        Parses the JSON response from the Groq API.

        Args:
            response (str): The raw response from the Groq API.

        Returns:
            dict: A dictionary containing the parsed JSON result.
        """
        try:
            # Extract the JSON part from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx].strip()
            
            # Load the JSON response
            if not json_str:
                raise ValueError("No JSON-like structure found in the response")
            
            result = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            result = {
                "risk_level": "Unknown",
                "explanation": ["Unable to parse LLM response."],
                "suggested_safe_command": ""
            }
        
        return result
