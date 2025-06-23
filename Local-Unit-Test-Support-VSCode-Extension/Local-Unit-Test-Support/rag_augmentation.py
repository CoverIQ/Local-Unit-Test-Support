from typing import List, Dict

def augment_test_suggestion_prompt(affected_metadata_list: List[Dict], whole_test_code: str, git_diff_message: str) -> str:
    """Augment the prompt for test suggestion generation."""
    return f"""
    You are a software testing assistant.

    Given:
    - List of metadata of test function affected by git diff: {affected_metadata_list}
    - Git diff message: {git_diff_message}
    - All test Code: {whole_test_code}
    Suggest if any test should be added, modified, or deleted.
    """

def augment_coverage_suggestion_prompt(function_name: List[str], code: str, git_diff_message: str) -> str:
    """Augment the prompt for coverage suggestion generation."""
    return f"""
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
    - If an existing function's body was edited (e.g., added asserts), use `"update"`.
    """ 