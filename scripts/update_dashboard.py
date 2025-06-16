#!/usr/bin/env python3
"""
Update the dashboard with latest results
"""
import json
import argparse
from datetime import datetime
from pathlib import Path

def update_dashboard(results_file, output_file):
    # Load new results
    with open(results_file, 'r') as f:
        new_results = json.load(f)
    
    # Load existing dashboard data
    output_path = Path(output_file)
    if output_path.exists():
        with open(output_path, 'r') as f:
            dashboard_data = json.load(f)
    else:
        dashboard_data = {
            "teams": {},
            "lastUpdate": None,
            "milestoneStats": {},
            "timeline": []
        }
    
    # Update team data
    team = new_results["team"]
    if team not in dashboard_data["teams"]:
        dashboard_data["teams"][team] = {
            "totalPoints": 0,
            "completedMilestones": [],
            "submissions": [],
            "lastSubmission": None
        }
    
    team_data = dashboard_data["teams"][team]
    team_data["totalPoints"] = new_results["totalPoints"]
    team_data["completedMilestones"] = [m["id"] for m in new_results["passed"]]
    team_data["lastSubmission"] = new_results["timestamp"]
    
    # Add to submissions history
    team_data["submissions"].append({
        "timestamp": new_results["timestamp"],
        "points": new_results["totalPoints"],
        "passed": len(new_results["passed"]),
        "failed": len(new_results["failed"])
    })
    
    # Update milestone statistics
    for milestone in new_results["passed"]:
        mid = milestone["id"]
        if mid not in dashboard_data["milestoneStats"]:
            dashboard_data["milestoneStats"][mid] = {
                "name": milestone["name"],
                "points": milestone["points"],
                "completedBy": []
            }
        if team not in dashboard_data["milestoneStats"][mid]["completedBy"]:
            dashboard_data["milestoneStats"][mid]["completedBy"].append(team)
    
    # Add to timeline
    for milestone in new_results["passed"]:
        dashboard_data["timeline"].append({
            "timestamp": new_results["timestamp"],
            "team": team,
            "event": f"Completed {milestone['name']}",
            "points": milestone["points"]
        })
    
    # Sort timeline by timestamp (newest first)
    dashboard_data["timeline"].sort(key=lambda x: x["timestamp"], reverse=True)
    dashboard_data["timeline"] = dashboard_data["timeline"][:50]  # Keep last 50 events
    
    # Update timestamp
    dashboard_data["lastUpdate"] = datetime.now().isoformat()
    
    # Save updated data
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    update_dashboard(args.results, args.output)
