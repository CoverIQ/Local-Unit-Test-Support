import os
import json
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List, Literal
from rag_augmentation import augment_test_suggestion_prompt, augment_coverage_suggestion_prompt

class SuggestionSchema(BaseModel):
    suggestion_type: Literal["add", "remove", "update"]
    test_function_name: str
    description: str
    original_code: str
    updated_code: str

class SuggestionResponse(BaseModel):
    suggestions: List[SuggestionSchema]

class GeminiSuggester:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        
    def get_coverage_suggestions(self, function_name: List[str], code: str, git_diff_message: str) -> dict:
        prompt = augment_coverage_suggestion_prompt(function_name, code, git_diff_message)
        response = self.client.models.generate_content(
            model='gemini-2.5-flash-preview-04-17',  
            contents=prompt,
            config={
                "response_mime_type": "application/json", 
                "response_schema": SuggestionResponse,    
            }
        )
        return json.loads(response.text)
    
    def get_test_suggestions(self, affect_test_function_metadata: List[dict], whole_test_code: str, git_diff_message: str) -> dict:
        prompt = augment_test_suggestion_prompt(affect_test_function_metadata, whole_test_code, git_diff_message)
        response = self.client.models.generate_content(
            model='gemini-2.5-flash-preview-04-17',  
            contents=prompt,
            config={
                "response_mime_type": "application/json", 
                "response_schema": SuggestionResponse,    
            }
        )
        return json.loads(response.text) 