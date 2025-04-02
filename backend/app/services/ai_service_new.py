from openai import OpenAI
from flask import current_app
import logging
import json
import time
import os
import httpx

class AIEvaluator:
    def __init__(self):
        """Initialize the AI evaluator with OpenAI API key"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            logging.warning("OPENAI_API_KEY is not configured. AI evaluation will be simulated.")
            self.api_key = None
        else:
            self.api_key = api_key
            logging.info("AI Evaluator initialized with valid API key")

    def evaluate(self, task_submission):
        """
        Evaluates a BTEC task submission using OpenAI's API
        Returns a grade and detailed feedback in text format
        
        Args:
            task_submission (str): The text of the submission to evaluate
            
        Returns:
            str: Formatted evaluation text with grade and feedback
        """
        if not self.api_key:
            # Simulate AI evaluation if API key is not available
            logging.warning("Using simulated AI evaluation (no API key)")
            return (
                "GRADE: Merit\n\n"
                "FEEDBACK:\n"
                "• This is a simulated evaluation as OpenAI API key is missing.\n"
                "• The submission demonstrates good understanding of the subject.\n"
                "• Some key concepts are well explained but lack depth.\n\n"
                "AREAS FOR IMPROVEMENT:\n"
                "• Add more critical analysis\n"
                "• Include more industry examples\n"
                "• Expand on theoretical frameworks"
            )
        
        try:
            # Use the OpenAI client for API v1.0.0+
            api_key = os.environ.get('OPENAI_API_KEY') or self.api_key
            logging.debug(f"Creating OpenAI client with API key (masked): {api_key[:4] if api_key else 'None'}...")
            
            # Create client with only the required parameter
            client = OpenAI(api_key=api_key)
            start_time = time.time()
            
            # Create the AI completion using ChatGPT
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": """You are a BTEC evaluator with expertise in UK vocational qualifications. 
                     Grade submissions strictly as: Pass, Merit, or Distinction based on BTEC criteria.
                     
                     Follow these BTEC grading guidelines:
                     - Pass: Basic understanding, meets minimum requirements, limited analysis
                     - Merit: Good understanding, well-structured, some critical analysis, good application of theory
                     - Distinction: Excellent understanding, comprehensive, insightful critical analysis, creative application of theory to practice
                     
                     Format your response EXACTLY as:
                     
                     GRADE: [Pass/Merit/Distinction]
                     
                     FEEDBACK:
                     • [Key point 1]
                     • [Key point 2]
                     • [Key point 3]
                     • [Key point 4]
                     
                     AREAS FOR IMPROVEMENT:
                     • [Improvement 1]
                     • [Improvement 2]
                     • [Improvement 3]
                     
                     Ensure your feedback is specific, actionable, and aligned with BTEC standards."""},
                    {"role": "user", "content": f"Evaluate the following BTEC task submission:\n\n{task_submission}"}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"OpenAI API evaluation completed in {elapsed_time:.2f} seconds")
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return f"Error during AI evaluation: {str(e)}"
            
    def evaluate_with_json(self, task_submission):
        """
        Evaluates a BTEC task submission and returns structured JSON response
        
        Args:
            task_submission (str): The text of the submission to evaluate
            
        Returns:
            dict: Structured evaluation with grade, feedback, and improvement areas
        """
        if not self.api_key:
            # Simulate AI evaluation if API key is not available
            logging.warning("Using simulated AI evaluation (no API key)")
            return {
                "grade": "Merit",
                "feedback": [
                    "This is a simulated evaluation as OpenAI API key is missing.",
                    "The submission demonstrates good understanding of the subject.",
                    "Some key concepts are well explained but lack depth."
                ],
                "improvement_areas": [
                    "Add more critical analysis",
                    "Include more industry examples",
                    "Expand on theoretical frameworks"
                ],
                "criteria_met": {
                    "knowledge": 80,
                    "application": 75,
                    "analysis": 65,
                    "evaluation": 60
                }
            }
        
        try:
            # Use the OpenAI client for API v1.0.0+
            api_key = os.environ.get('OPENAI_API_KEY') or self.api_key
            logging.debug(f"Creating OpenAI client with API key (masked): {api_key[:4] if api_key else 'None'}...")
            
            # Create client with only the required parameter
            client = OpenAI(api_key=api_key)
            start_time = time.time()
            
            # Create the AI completion using ChatGPT with JSON output
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": """You are a BTEC evaluator with expertise in UK vocational qualifications.
                     Grade submissions strictly as: Pass, Merit, or Distinction based on BTEC criteria.
                     
                     Follow these BTEC grading guidelines:
                     - Pass: Basic understanding, meets minimum requirements, limited analysis (50-59%)
                     - Merit: Good understanding, well-structured, some critical analysis (60-79%)
                     - Distinction: Excellent understanding, comprehensive, insightful analysis (80-100%)
                     
                     Return your evaluation in the following JSON format:
                     {
                       "grade": "Pass/Merit/Distinction",
                       "feedback": ["Point 1", "Point 2", "Point 3", "Point 4"],
                       "improvement_areas": ["Area 1", "Area 2", "Area 3"],
                       "criteria_met": {
                         "knowledge": 0-100,
                         "application": 0-100,
                         "analysis": 0-100,
                         "evaluation": 0-100
                       }
                     }
                     
                     Ensure your feedback is specific, actionable, and aligned with BTEC standards.
                     The percentages in criteria_met should reflect performance in each area from 0-100.
                     """}, 
                    {"role": "user", "content": f"Evaluate the following BTEC task submission:\n\n{task_submission}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"OpenAI API JSON evaluation completed in {elapsed_time:.2f} seconds")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"OpenAI API error in JSON evaluation: {e}")
            return {
                "grade": "Error",
                "feedback": [f"Error during AI evaluation: {str(e)}"],
                "improvement_areas": ["Try again later"],
                "criteria_met": {
                    "knowledge": 0,
                    "application": 0,
                    "analysis": 0,
                    "evaluation": 0
                }
            }
    
    def evaluate_with_rubric(self, task_submission, rubric=None):
        """
        Evaluates a submission using a specific rubric
        
        Args:
            task_submission (str): The text of the submission to evaluate
            rubric (dict, optional): Custom evaluation rubric. If None, default BTEC rubric is used.
            
        Returns:
            dict: Detailed evaluation with scores for each rubric criterion
        """
        if not rubric:
            # Default BTEC rubric
            rubric = {
                "sections": [
                    {
                        "name": "Knowledge and Understanding",
                        "weight": 25,
                        "criteria": ["Accurate use of concepts", "Coverage of key topics", "Depth of understanding"]
                    },
                    {
                        "name": "Application of Theory",
                        "weight": 25,
                        "criteria": ["Relevant examples", "Practical application", "Industry context"]
                    },
                    {
                        "name": "Analysis",
                        "weight": 25,
                        "criteria": ["Critical thinking", "Evaluation of evidence", "Logical arguments"]
                    },
                    {
                        "name": "Communication",
                        "weight": 25,
                        "criteria": ["Structure", "Clarity", "Academic writing"]
                    }
                ]
            }
            
        if not self.api_key:
            # Simulate AI evaluation with rubric
            logging.warning("Using simulated AI evaluation with rubric (no API key)")
            
            # Generate simulated scores for each section
            sections_result = []
            total_score = 0
            
            for section in rubric["sections"]:
                section_score = min(85, max(60, 70 + hash(section["name"]) % 20))  # Random-ish but stable score
                criteria_scores = {}
                
                for criterion in section["criteria"]:
                    criteria_scores[criterion] = min(90, max(55, section_score + hash(criterion) % 15))
                
                section_result = {
                    "name": section["name"],
                    "score": section_score,
                    "criteria_scores": criteria_scores,
                    "feedback": f"Simulated feedback for {section['name']}"
                }
                sections_result.append(section_result)
                total_score += section_score * section["weight"] / 100
            
            # Determine grade based on total score
            grade = "Pass"
            if total_score >= 80:
                grade = "Distinction"
            elif total_score >= 60:
                grade = "Merit"
                
            return {
                "grade": grade,
                "total_score": round(total_score, 1),
                "sections": sections_result,
                "overall_feedback": "This is a simulated rubric-based evaluation (no API key)",
                "simulated": True
            }
            
        try:
            # Convert rubric to string format for the prompt
            rubric_str = json.dumps(rubric, indent=2)
            api_key = os.environ.get('OPENAI_API_KEY') or self.api_key
            logging.debug(f"Creating OpenAI client with API key (masked): {api_key[:4] if api_key else 'None'}...")
            
            # Create client with only the required parameter
            client = OpenAI(api_key=api_key)
            start_time = time.time()
            
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": f"""You are a BTEC evaluator using a specific rubric to evaluate submissions.
                     
                     Use this evaluation rubric:
                     {rubric_str}
                     
                     For each section:
                     1. Evaluate the submission against each criterion
                     2. Provide a score from 0-100 for each criterion
                     3. Calculate an overall score for the section (average of criteria)
                     4. Provide specific feedback for the section
                     
                     Calculate the final score as the weighted average of section scores.
                     
                     Determine the grade as follows:
                     - Distinction: 80-100
                     - Merit: 60-79
                     - Pass: 40-59
                     - Fail: 0-39
                     
                     Return your evaluation as a JSON object with this structure:
                     {{
                       "grade": "Pass/Merit/Distinction/Fail",
                       "total_score": number (0-100),
                       "sections": [
                         {{
                           "name": "section name",
                           "score": number (0-100),
                           "criteria_scores": {{ "criterion1": score, "criterion2": score, ... }},
                           "feedback": "specific feedback for this section"
                         }},
                         ...
                       ],
                       "overall_feedback": "summary feedback addressing strengths and weaknesses"
                     }}
                     """}, 
                    {"role": "user", "content": f"Evaluate the following submission using the provided rubric:\n\n{task_submission}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"OpenAI API rubric evaluation completed in {elapsed_time:.2f} seconds")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"OpenAI API error in rubric evaluation: {e}")
            return {
                "grade": "Error",
                "total_score": 0,
                "sections": [],
                "overall_feedback": f"Error during AI evaluation: {str(e)}",
                "error": True
            }