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
        report += f"**{func}**:\n> {suggestion}\n\n"
    
    return report