def generate_markdown_report(changes: dict, related_tests: list, suggestions: dict) -> str:
    report = "# Regression Test Maintenance Report\n\n"
    
    report += "## Function Changes\n"
    report += f"- Added: {', '.join(changes.get('added', []))}\n"
    report += f"- Removed: {', '.join(changes.get('removed', []))}\n\n"

    report += "## Affected Tests\n"
    for test in related_tests:
        report += f"- {test}\n"
    
    report += "\n## LLM Suggestions\n"
    for func, suggestion in suggestions.items():
        report += f"**{func}**:\n> {suggestion}\n\n"
    
    return report