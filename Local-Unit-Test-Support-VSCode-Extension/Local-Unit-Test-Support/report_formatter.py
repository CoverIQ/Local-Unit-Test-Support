from typing import List, Dict

def generate_suggestion_markdown(suggestions: List[Dict]) -> str:
    """Generate markdown report from suggestions."""
    if not suggestions:
        return "No suggestions generated."
    all_suggestions = suggestions["suggestions"]
    report = ""
    id = 1
    for suggestion in all_suggestions:
        report += f'## Suggestion {id}\n'
        report += f"#### Suggestion type: {suggestion['suggestion_type']}\n"
        report += f"#### Test function name: {suggestion['test_function_name']}\n"
        report += "### Description\n"
        report += f"{suggestion['description']}\n"
        if suggestion['original_code']:
            report += "### Original Code\n"
            report += f"```python\n{suggestion['original_code']}\n```\n"
        if suggestion['updated_code']:
            report += "### Updated Code\n"
            report += f"```python\n {suggestion['updated_code']}\n```\n"
        id += 1
    return report