#!/usr/bin/env python3
"""
Main validation script for student submissions
"""
import json
import sys
import subprocess
import os
from pathlib import Path
import tempfile
import shutil
import argparse
from datetime import datetime

class MilestoneValidator:
    def __init__(self, student_code_path, team, repository, sha, timestamp=None):
        self.student_code_path = Path(student_code_path)
        self.team = team
        self.repository = repository
        self.sha = sha
        # Use provided timestamp or current time as fallback
        self.timestamp = timestamp or datetime.now().isoformat()
        self.results = {
            "team": team,
            "repository": repository,
            "sha": sha,
            "timestamp": self.timestamp,
            "totalPoints": 0,
            "passed": [],
            "failed": [],
            "llmBonus": 0,
            "llmPromptsCount": 0
        }
        
        # Get the script's directory and find milestones relative to it
        script_dir = Path(__file__).parent.absolute()
        repo_root = script_dir.parent  # Go up from scripts/ to repo root
        milestone_file = repo_root / "milestones" / "definitions.json"
        
        # Load milestone definitions
        if not milestone_file.exists():
            raise FileNotFoundError(f"Milestone definitions not found at {milestone_file}")
            
        with open(milestone_file, 'r') as f:
            self.milestones = json.load(f)
    
    def validate(self):
        """Run all validations"""
        # Check if claim file exists
        claim_path = self.student_code_path / "submissions" / "claim.json"
        if not claim_path.exists():
            self.results["error"] = "No claim.json file found"
            print(json.dumps(self.results, indent=2))
            return
        
        # Read claims
        try:
            with open(claim_path, 'r') as f:
                claims = json.load(f)
        except json.JSONDecodeError:
            self.results["error"] = "Invalid JSON in claim.json"
            print(json.dumps(self.results, indent=2))
            return
        
        # Validate each claimed milestone
        for milestone_id in claims.get("milestones", []):
            if milestone_id in self.milestones:
                self.validate_milestone(milestone_id)
            else:
                self.results["failed"].append({
                    "id": milestone_id,
                    "name": f"Unknown milestone: {milestone_id}",
                    "hint": "This milestone ID doesn't exist"
                })
        
        # Check LLM usage bonus
        llm_prompts = claims.get("llm_prompts", [])
        self.results["llmPromptsCount"] = len(llm_prompts)
        if len(llm_prompts) >= 5:
            self.results["llmBonus"] = 10
            self.results["totalPoints"] += 10
        
        # Output ONLY the JSON results
        print(json.dumps(self.results, indent=2))
    
    def validate_milestone(self, milestone_id):
        """Validate a single milestone"""
        milestone = self.milestones[milestone_id]
        
        try:
            if milestone["type"] == "bug_fix":
                success = self.validate_bug_fix(milestone_id, milestone)
            elif milestone["type"] == "test_coverage":
                success = self.validate_test_coverage(milestone_id, milestone)
            elif milestone["type"] == "test_coverage_overall":
                success = self.validate_test_coverage_overall(milestone_id, milestone)
            elif milestone["type"] == "new_card":
                success = self.validate_new_card(milestone_id, milestone)
            elif milestone["type"] == "custom_test":
                # For now, skip custom tests or implement later
                success = False
            else:
                success = False
                
            if success:
                self.results["passed"].append({
                    "id": milestone_id,
                    "name": milestone["name"],
                    "points": milestone["points"],
                    "message": milestone.get("success_message", "Well done!")
                })
                self.results["totalPoints"] += milestone["points"]
            else:
                self.results["failed"].append({
                    "id": milestone_id,
                    "name": milestone["name"],
                    "hint": milestone.get("failure_hint", "Check your implementation")
                })
                
        except Exception as e:
            self.results["failed"].append({
                "id": milestone_id,
                "name": milestone["name"],
                "hint": f"Validation error: {str(e)}"
            })
    
    def validate_bug_fix(self, milestone_id, milestone):
        """Run bug fix tests"""
        # Get proper path to test files
        script_dir = Path(__file__).parent.absolute()
        repo_root = script_dir.parent
        test_file = repo_root / "tests" / "bugs" / f"test_{milestone_id}.py"
        
        if not test_file.exists():
            raise Exception(f"Test file {test_file} not found")
        
        # Create temp directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Copy student code
            shutil.copytree(
                self.student_code_path / "dominion",
                tmpdir / "dominion"
            )
            
            # Run test
            env = os.environ.copy()
            env['PYTHONPATH'] = str(tmpdir)
            
            result = subprocess.run(
                ["poetry", "run", "pytest", str(test_file), "-xvs"],
                capture_output=True,
                text=True,
                env=env,
                cwd=repo_root  # Run from repo root
            )
            
            return result.returncode == 0
    
    def validate_test_coverage(self, milestone_id, milestone):
        """Check test coverage for a module"""
        module = milestone["module"]
        threshold = milestone["threshold"]
        
        # Check if student has test file
        student_test_file = self.student_code_path / f"tests/test_{module}.py"
        if not student_test_file.exists():
            return False
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Copy student code and tests
            shutil.copytree(self.student_code_path, tmpdir / "student")
            
            # Run coverage
            os.chdir(tmpdir / "student")
            
            # Install student dependencies if they use poetry
            if (tmpdir / "student" / "pyproject.toml").exists():
                subprocess.run(["poetry", "install", "--no-interaction"], 
                             capture_output=True)
                coverage_cmd = ["poetry", "run", "coverage", "run", "-m", "pytest", f"tests/test_{module}.py"]
                report_cmd = ["poetry", "run", "coverage", "report", "--include", f"dominion/{module}.py"]
            else:
                coverage_cmd = ["python", "-m", "coverage", "run", "-m", "pytest", f"tests/test_{module}.py"]
                report_cmd = ["python", "-m", "coverage", "report", "--include", f"dominion/{module}.py"]
            
            # Run coverage (suppress output)
            subprocess.run(coverage_cmd, capture_output=True)
            result = subprocess.run(report_cmd, capture_output=True, text=True)
            
            # Parse coverage percentage
            for line in result.stdout.split('\n'):
                if f"dominion/{module}.py" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        coverage_str = parts[-1].rstrip('%')
                        try:
                            coverage_percent = float(coverage_str)
                            return coverage_percent >= threshold
                        except ValueError:
                            pass
            
            return False
    
    def validate_test_coverage_overall(self, milestone_id, milestone):
        """Check overall test coverage for the entire dominion package"""
        threshold = milestone["threshold"]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Copy student code and tests
            shutil.copytree(self.student_code_path, tmpdir / "student")
            
            # Run coverage on entire test suite
            os.chdir(tmpdir / "student")
            
            # Install student dependencies if they use poetry
            if (tmpdir / "student" / "pyproject.toml").exists():
                subprocess.run(["poetry", "install", "--no-interaction"], 
                             capture_output=True)
                coverage_cmd = ["poetry", "run", "coverage", "run", "-m", "pytest"]
                report_cmd = ["poetry", "run", "coverage", "report", "--include", "dominion/*"]
            else:
                coverage_cmd = ["python", "-m", "coverage", "run", "-m", "pytest"]
                report_cmd = ["python", "-m", "coverage", "report", "--include", "dominion/*"]
            
            # Run all tests with coverage
            result = subprocess.run(coverage_cmd, capture_output=True, text=True)
            
            # If tests fail, we still want to check coverage
            # (some tests might fail due to incomplete implementation)
            
            # Get coverage report
            result = subprocess.run(report_cmd, capture_output=True, text=True)
            
            # Parse overall coverage from the TOTAL line
            for line in result.stdout.split('\n'):
                if line.startswith('TOTAL'):
                    parts = line.split()
                    if len(parts) >= 4:
                        # The coverage percentage is usually the last column
                        coverage_str = parts[-1].rstrip('%')
                        try:
                            coverage_percent = float(coverage_str)
                            return coverage_percent >= threshold
                        except ValueError:
                            # Try parsing from a different position
                            for part in reversed(parts):
                                if '%' in part:
                                    coverage_str = part.rstrip('%')
                                    try:
                                        coverage_percent = float(coverage_str)
                                        return coverage_percent >= threshold
                                    except ValueError:
                                        continue
            
            # If we couldn't find the TOTAL line, try to get it from json output
            json_cmd = report_cmd[:-2] + ["coverage", "json", "-o", "-"]
            result = subprocess.run(json_cmd, capture_output=True, text=True)
            try:
                coverage_data = json.loads(result.stdout)
                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                return total_coverage >= threshold
            except:
                pass
            
            return False
    
    def validate_new_card(self, milestone_id, milestone):
        """Validate new card implementation"""
        card_name = milestone["card_name"]
        
        # Get proper path to test files
        script_dir = Path(__file__).parent.absolute()
        repo_root = script_dir.parent
        test_file = repo_root / "tests" / "cards" / f"test_{card_name.lower()}.py"
        
        if not test_file.exists():
            raise Exception(f"Test file {test_file} not found")
        
        # Check if card exists in student code
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Copy student code
            shutil.copytree(
                self.student_code_path / "dominion",
                tmpdir / "dominion"
            )
            
            # First check if card is registered
            env = os.environ.copy()
            env['PYTHONPATH'] = str(tmpdir)
            
            check_cmd = f"""
import sys
sys.path.insert(0, '{tmpdir}')
from dominion.card import Card
try:
    card_type = Card.get_type_with_name('{card_name}')
    # Silent success - no output
except:
    sys.exit(1)
"""
            
            result = subprocess.run(
                ["python", "-c", check_cmd],
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.returncode != 0:
                return False
            
            # Run card-specific tests
            result = subprocess.run(
                ["poetry", "run", "pytest", str(test_file), "-xvs"],
                capture_output=True,
                text=True,
                env=env,
                cwd=repo_root  # Run from repo root
            )
            
            return result.returncode == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--student-code", required=True)
    parser.add_argument("--timestamp", required=False, default=None)
    args = parser.parse_args()
    
    try:
        validator = MilestoneValidator(
            args.student_code,
            args.team,
            args.repo,
            args.sha,
            args.timestamp
        )
        validator.validate()
    except Exception as e:
        # Output error as JSON
        error_result = {
            "team": args.team,
            "repository": args.repo,
            "sha": args.sha,
            "timestamp": args.timestamp or datetime.now().isoformat(),
            "totalPoints": 0,
            "passed": [],
            "failed": [],
            "error": str(e)
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)