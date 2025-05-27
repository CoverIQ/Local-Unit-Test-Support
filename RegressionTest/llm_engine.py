from google import genai
import os
import argparse
from dotenv import load_dotenv 
import json
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
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="get function code and function name")
    parser.add_argument("--function_name", help="Get Function Name")
    parser.add_argument("--function_code", help="Get Function Code")
    args = parser.parse_args()
    suggest_test_changes(args.function_name, args.function_code)