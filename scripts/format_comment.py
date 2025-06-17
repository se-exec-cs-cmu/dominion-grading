#!/usr/bin/env python3
"""
Format validation results as a GitHub comment using a template
"""
import json
import argparse
from pathlib import Path
from datetime import datetime


def format_comment(results_file, template_file):
    """Format validation results using the comment template"""
    
    # Load results
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Load template
    with open(template_file, 'r') as f:
        template = f.read()
    
    # Format passed milestones
    passed_text = ""
    if results.get("passed"):
        for milestone in results["passed"]:
            passed_text += f"- ✅ **{milestone['name']}** ({milestone['points']} points): {milestone.get('message', 'Completed!')}\n"
    else:
        passed_text = "- None yet - keep working!"
    
    # Format failed milestones
    failed_text = ""
    if results.get("failed"):
        for milestone in results["failed"]:
            failed_text += f"- ❌ **{milestone['name']}**: {milestone.get('hint', 'Check your implementation')}\n"
    else:
        failed_text = "- Great job! All claimed milestones passed!"
    
    # Format custom milestones section
    custom_text = ""
    if results.get("customMilestones"):
        custom_text = "\n### ⭐ Custom Achievements\n\n"
        for custom in results["customMilestones"]:
            custom_text += f"- ⭐ **{custom['name']}** ({custom['points']} point)\n"
            custom_text += f"  - {custom['description']}\n"
    
    # Format LLM bonus section
    llm_bonus_text = ""
    if results.get("llmBonus", 0) > 0:
        llm_bonus_text = f"\n### 🤖 LLM Usage Bonus\n\nGreat job documenting {results.get('llmPromptsCount', 0)} LLM prompts! You earned **{results['llmBonus']} bonus points**."
    
    # Format timestamp
    timestamp = results.get("timestamp", datetime.now().isoformat())
    try:
        formatted_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        formatted_time = timestamp
    
    # Replace placeholders
    comment = template.replace("{{TEAM}}", results.get("team", "Unknown"))
    comment = comment.replace("{{TOTAL_POINTS}}", str(results.get("totalPoints", 0)))
    comment = comment.replace("{{PASSED_MILESTONES}}", passed_text.strip())
    comment = comment.replace("{{FAILED_MILESTONES}}", failed_text.strip())
    comment = comment.replace("{{CUSTOM_ACHIEVEMENTS}}", custom_text)
    comment = comment.replace("{{LLM_BONUS}}", llm_bonus_text)
    comment = comment.replace("{{TIMESTAMP}}", formatted_time)
    
    # Add error message if present
    if results.get("error"):
        error_section = f"\n### ⚠️ Validation Error\n\n```\n{results['error']}\n```\n"
        comment = comment.replace("---\n*Validated at:", error_section + "---\n*Validated at:")
    
    print(comment)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Path to results JSON file")
    parser.add_argument("--template", required=True, help="Path to comment template file")
    args = parser.parse_args()
    
    format_comment(args.results, args.template)