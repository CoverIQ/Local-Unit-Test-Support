from typing import Dict, Any
def generate_markdown_report(file_name:str,changes: dict, related_tests: list, suggestions: dict) -> str:
    report = f"# Regression Test Maintenance Report For {file_name}\n\n"
    
    report += "## Function Changes\n"
    report += f"- Added: {', '.join(changes.get('added', []))}\n"
    report += f"- Modified: {', '.join(changes.get('modified', []))}\n"
    report += f"- indirect_dependents: {', '.join(changes.get('indirect_dependents', []))}\n"
    report += f"- Removed: {', '.join(changes.get('removed', []))}\n\n"

    report += "## Affected Tests\n"
    for test in related_tests:
        report += f"- {test}\n"
    
    report += "\n## LLM Suggestions\n"
    for func, suggestion in suggestions.items():
        # report += f"**{func}**:\n> {suggestion}\n\n"
        report += f"**{func}**:\n"
        for each_suggestion in suggestion:
            report += f"- {each_suggestion}\n"
    
    return report

def generate_suggestion_markdown(suggestions: Dict[str, Any]) -> str:
    """Generate markdown content for suggestions"""
    all_suggestions = suggestions["suggestions"]
    report = ""
    id = 1
    for suggestion in all_suggestions:
        report += f'## Suggestion {id}\n'
        report += f"#### Suggestion type: {suggestion['suggestion_type']}\n"
        report += f"#### Test function name: {suggestion['test_function_name']}\n"
        report += "### Description\n"
        report += f"{suggestion['description']}\n"
        report += "### Original Code\n"
        report += f"```python\n{suggestion['original_code']}\n```\n"
        report += "### Updated Code\n"
        report += f"```python\n {suggestion['updated_code']}\n```\n"
        id += 1
    return report