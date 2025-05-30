from google import genai
import os
import argparse
from dotenv import load_dotenv 
import json
from pydantic import BaseModel, ConfigDict
from typing import Dict
from typing import Literal
class suggestion_schema(BaseModel) :
    suggestion_type : Literal["add", "remove", "update"]
    test_function_name : str
    description : str
    original_code : str
    updated_code : str
class SuggestionResponse(BaseModel):
    suggestions: list[suggestion_schema]
def suggest_test_changes(function_name: str, function_code: str) -> str:
    load_dotenv()
    # Replace this with actual LLM call
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model='gemini-2.5-flash-preview-04-17',  
        contents=f"""
        Given the following function name {function_name} and function code {function_code},
        please suggest 2-3 test cases that should be written or updated.
        Respond in JSON format:
        [
        "suggestion 1",
        "suggestion 2"
        ]
        """,
        config={
            "response_mime_type": "application/json",          
        }
    )
    print(json.loads(response.text))
    return json.loads(response.text)
    return f"Suggested change for `{function_name}`: Add more edge case assertions."
class GeminiSuggester():
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        
    def get_coverage_suggestions(self, function_name: list, code: str, git_diff_message: str) -> dict:
        response = self.client.models.generate_content(
            model='gemini-2.5-flash-preview-04-17',  
            contents=f"""
            You are a helpful AI assistant tasked with analyzing changes in test code.

            Given:
            - Function name list: {function_name}
            - Git diff message: {git_diff_message}
            - Code: {code}
            Please analyze the changes and return one or more suggestions if needed.

            Each suggestion must fall into one of the following categories **based on actual code change**:

            - **"add"**: A test function was added in the new code but did not exist before.
            - **"remove"**: A test function was deleted and no longer exists in the new code.
            - **"update"**: An existing test function remains in both versions, but its content was changed.

            **Examples**:
            - If a new function is added like `def test_new_case(): ...`, use `"suggestion_type": "add"`.
            - If a function is entirely deleted, use `"remove"`.
            - If an existing function’s body was edited (e.g., added asserts), use `"update"`.
            """,
            config={
                "response_mime_type": "application/json", 
                "response_schema": SuggestionResponse,    
            }
        )
        return json.loads(response.text)
    
    def get_test_suggestions(self, affect_test_function_metadata: list, whole_test_code: str, git_diff_message: str) -> dict:
        response = self.client.models.generate_content(
            model='gemini-2.5-flash-preview-04-17',  
            contents=f"""
            You are a software testing assistant.

            Given:
            - List of metadata of test function affected by git diff: {affect_test_function_metadata}
            - Git diff message: {git_diff_message}
            - All test Code: {whole_test_code}
            Suggest if any test should be added, modified, or deleted.
            """,
            config={
                "response_mime_type": "application/json", 
                "response_schema": SuggestionResponse,    
            }
        )
        return json.loads(response.text)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="get function code and function name")
    parser.add_argument("--function_name", help="Get Function Name")
    parser.add_argument("--function_code", help="Get Function Code")
    args = parser.parse_args()
    suggest_test_changes(args.function_name, args.function_code)