import os
import json
import logging
from flask import current_app
from openai import OpenAI

class AIEvaluator:
    def __init__(self):
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            logging.error("OpenAI API key is missing!")
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=api_key)
    
    def evaluate(self, task_submission):
        """
        Evaluates a BTEC task submission using OpenAI's API
        Returns a grade and detailed feedback
        """
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": (
                        "You are a BTEC evaluation expert. You need to grade the following task submission "
                        "based on BTEC criteria. Provide a grade (Distinction, Merit, Pass, or Fail) "
                        "and detailed feedback explaining your evaluation. Focus on the content, "
                        "structure, evidence of research, technical accuracy, and overall quality."
                    )},
                    {"role": "user", "content": task_submission}
                ],
                max_tokens=1000
            )
            
            evaluation = response.choices[0].message.content
            
            # Log success but not the actual content for privacy
            logging.info(f"Successfully evaluated task with {len(task_submission)} characters")
            
            return evaluation
            
        except Exception as e:
            logging.error(f"AI evaluation failed: {e}")
            return "Evaluation failed due to a technical issue. Please try again later."
