import openai
from flask import current_app
import logging

class AIEvaluator:
    def __init__(self):
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            logging.warning("OPENAI_API_KEY is not configured. AI evaluation will be simulated.")
            self.api_key = None
        else:
            openai.api_key = api_key
            self.api_key = api_key

    def evaluate(self, task_submission):
        """
        Evaluates a BTEC task submission using OpenAI's API
        Returns a grade and detailed feedback
        """
        if not self.api_key:
            # Simulate AI evaluation if API key is not available
            return f"Simulated BTEC Grade: Merit. \nThis is a simulated evaluation as OpenAI API key is missing."
        
        try:
            # Use the OpenAI client for API v1.0.0+
            client = openai.OpenAI(api_key=self.api_key)
            
            # Create the AI completion using ChatGPT
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                messages=[
                    {"role": "system", "content": """You are a BTEC evaluator. You assess submissions based on UK BTEC criteria. 
                     Grade submissions as: Pass, Merit, or Distinction. 
                     Provide detailed feedback explaining why the grade was given.
                     Format your response as:
                     
                     GRADE: [Pass/Merit/Distinction]
                     
                     FEEDBACK:
                     [Detailed feedback with bullet points]
                     
                     AREAS FOR IMPROVEMENT:
                     [List specific areas where the student could improve]"""},
                    {"role": "user", "content": f"Evaluate the following BTEC task submission:\n\n{task_submission}"}
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return f"Error during AI evaluation: {str(e)}"