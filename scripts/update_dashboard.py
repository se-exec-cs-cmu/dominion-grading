#!/usr/bin/env python3
"""
Update the dashboard with latest results
"""
import json
import argparse
from datetime import datetime
from pathlib import Path
import sys

def update_dashboard(results_file, output_file):
    # Check if results file exists
    if not Path(results_file).exists():
        print(f"Error: Results file '{results_file}' not found")
        # Create a minimal error result
        new_results = {
            "team": "unknown",
            "repository": "unknown",
            "sha": "unknown",
            "timestamp": datetime.now().isoformat(),
            "totalPoints": 0,
            "passed": [],
            "failed": [],
            "error": f"Results file {results_file} not found"
        }
    else:
        try:
            # Load new results
            with open(results_file, 'r') as f:
                content = f.read()
                if not content.strip():
                    raise json.JSONDecodeError("Empty file", "", 0)
                new_results = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in results file: {e}")
            new_results = {
                "team": "unknown",
                "repository": "unknown", 
                "sha": "unknown",
                "timestamp": datetime.now().isoformat(),
                "totalPoints": 0,
                "passed": [],
                "failed": [],
                "error": f"Invalid JSON in results file: {str(e)}"
            }
        except Exception as e:
            print(f"Error reading results file: {e}")
            new_results = {
                "team": "unknown",
                "repository": "unknown",
                "sha": "unknown",
                "timestamp": datetime.now().isoformat(),
                "totalPoints": 0,
                "passed": [],
                "failed": [],
                "error": f"Error reading results: {str(e)}"
            }
    
    # Load existing dashboard data
    output_path = Path(output_file)
    if output_path.exists():
        try:
            with open(output_path, 'r') as f:
                dashboard_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load existing dashboard data: {e}")
            dashboard_data = {
                "teams": {},
                "lastUpdate": None,
                "milestoneStats": {},
                "timeline": []
            }
    else:
        print(f"Creating new dashboard data file at {output_path}")
        dashboard_data = {
            "teams": {},
            "lastUpdate": None,
            "milestoneStats": {},
            "timeline": []
        }
    
    # Update team data
    team = new_results.get("team", "unknown")
    
    # Initialize team data if not exists
    if team not in dashboard_data["teams"]:
        dashboard_data["teams"][team] = {
            "totalPoints": 0,
            "completedMilestones": [],
            "submissions": [],
            "lastSubmission": None
        }
    
    team_data = dashboard_data["teams"][team]
    
    # Update points and milestones
    team_data["totalPoints"] = new_results.get("totalPoints", 0)
    team_data["completedMilestones"] = [m["id"] for m in new_results.get("passed", [])]
    team_data["lastSubmission"] = new_results.get("timestamp", datetime.now().isoformat())
    
    # Add to submissions history
    submission_record = {
        "timestamp": new_results.get("timestamp", datetime.now().isoformat()),
        "points": new_results.get("totalPoints", 0),
        "passed": len(new_results.get("passed", [])),
        "failed": len(new_results.get("failed", []))
    }
    
    # Add error info if present
    if "error" in new_results:
        submission_record["error"] = new_results["error"]
    
    team_data["submissions"].append(submission_record)
    
    # Keep only last 50 submissions per team
    team_data["submissions"] = team_data["submissions"][-50:]
    
    # Update milestone statistics
    for milestone in new_results.get("passed", []):
        mid = milestone.get("id", "unknown")
        if mid not in dashboard_data["milestoneStats"]:
            dashboard_data["milestoneStats"][mid] = {
                "name": milestone.get("name", mid),
                "points": milestone.get("points", 0),
                "completedBy": []
            }
        if team not in dashboard_data["milestoneStats"][mid]["completedBy"]:
            dashboard_data["milestoneStats"][mid]["completedBy"].append(team)
    
    # Add to timeline
    if new_results.get("passed"):
        for milestone in new_results["passed"]:
            dashboard_data["timeline"].append({
                "timestamp": new_results.get("timestamp", datetime.now().isoformat()),
                "team": team,
                "event": f"Completed {milestone.get('name', 'Unknown milestone')}",
                "points": milestone.get("points", 0)
            })
    elif "error" in new_results:
        dashboard_data["timeline"].append({
            "timestamp": new_results.get("timestamp", datetime.now().isoformat()),
            "team": team,
            "event": "Submission failed - see logs",
            "points": 0
        })
    
    # Sort timeline by timestamp (newest first)
    dashboard_data["timeline"].sort(key=lambda x: x["timestamp"], reverse=True)
    dashboard_data["timeline"] = dashboard_data["timeline"][:100]  # Keep last 100 events
    
    # Update timestamp
    dashboard_data["lastUpdate"] = datetime.now().isoformat()
    
    # Save updated data
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        print(f"Successfully updated dashboard data at {output_path}")
    except Exception as e:
        print(f"Error saving dashboard data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Path to results JSON file")
    parser.add_argument("--output", required=True, help="Path to output dashboard data file")
    args = parser.parse_args()
    
    update_dashboard(args.results, args.output)
