#!/usr/bin/env python3
"""
Worktree Analytics - Track detailed information from each worktree.

Tận dụng worktree để track:
1. File changes per agent (files đang edit)
2. Git status (uncommitted changes, commits)
3. Activity stats (số file edit, số dòng code thay đổi)
4. Task completion detection (detect khi agent hoàn thành task)
5. Activity heatmap (activity theo thời gian)
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Paths
PROJECT_NAME = "cheftAi"
WORKTREES_BASE = Path.home() / ".cursor" / "worktrees" / PROJECT_NAME
MAIN_PROJECT = Path.home() / "Documents" / PROJECT_NAME
STATE_FILE = MAIN_PROJECT / ".mcp" / "shared_state.json"


def get_git_status(worktree_path):
    """Get git status for a worktree."""
    try:
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return {
                "has_changes": len(lines) > 0,
                "modified_files": [line[3:] for line in lines if line.startswith(' M')],
                "new_files": [line[3:] for line in lines if line.startswith('??')],
                "deleted_files": [line[3:] for line in lines if line.startswith(' D')],
                "total_changes": len(lines)
            }
    except Exception as e:
        return {"error": str(e)}
    return {}


def get_recent_commits(worktree_path, hours=24):
    """Get recent commits from a worktree."""
    try:
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "log", 
             "--since", f"{hours} hours ago",
             "--pretty=format:%h|%an|%ad|%s",
             "--date=iso"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            return commits
    except Exception as e:
        return []
    return []


def get_file_stats(worktree_path):
    """Get file statistics for a worktree."""
    stats = {
        "total_files": 0,
        "modified_files": 0,
        "new_files": 0,
        "deleted_files": 0,
        "lines_added": 0,
        "lines_deleted": 0
    }
    
    try:
        # Get diff stats
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "diff", "--stat", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            # Parse git diff --stat output
            for line in result.stdout.strip().split('\n'):
                if '|' in line and 'file changed' not in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        file_part = parts[0].strip()
                        change_part = parts[1].strip()
                        
                        # Count files
                        if '+' in change_part or '-' in change_part:
                            stats["modified_files"] += 1
                        
                        # Parse lines changed (e.g., "5 +" or "3 -")
                        if '+' in change_part:
                            try:
                                added = int(change_part.split('+')[0].strip())
                                stats["lines_added"] += added
                            except:
                                pass
                        if '-' in change_part:
                            try:
                                deleted = int(change_part.split('-')[0].strip())
                                stats["lines_deleted"] += deleted
                            except:
                                pass
        
        # Count untracked files
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            stats["new_files"] = len([f for f in result.stdout.strip().split('\n') if f])
        
        stats["total_files"] = stats["modified_files"] + stats["new_files"]
        
    except Exception as e:
        stats["error"] = str(e)
    
    return stats


def get_activity_heatmap(worktree_path, days=7):
    """Get activity heatmap for a worktree (commits per day)."""
    heatmap = defaultdict(int)
    
    try:
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "log",
             "--since", f"{days} days ago",
             "--pretty=format:%ad",
             "--date=format:%Y-%m-%d"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    heatmap[line] += 1
    except Exception as e:
        pass
    
    return dict(heatmap)


def analyze_worktree(worktree_id, worktree_path):
    """Analyze a single worktree and return comprehensive stats."""
    if not Path(worktree_path).exists():
        return None
    
    analysis = {
        "worktree_id": worktree_id,
        "worktree_path": worktree_path,
        "analyzed_at": datetime.now().isoformat(),
        "git_status": get_git_status(worktree_path),
        "file_stats": get_file_stats(worktree_path),
        "recent_commits": get_recent_commits(worktree_path, hours=24),
        "activity_heatmap": get_activity_heatmap(worktree_path, days=7)
    }
    
    return analysis


def analyze_all_worktrees():
    """Analyze all worktrees from shared_state.json."""
    if not STATE_FILE.exists():
        print("⚠️ shared_state.json not found")
        return {}
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    analytics = {}
    
    for chat in detected_chats:
        wt_id = chat.get("worktree_id")
        wt_path = chat.get("worktree_path")
        
        if wt_id and wt_path:
            print(f"📊 Analyzing {wt_id}...")
            analysis = analyze_worktree(wt_id, wt_path)
            if analysis:
                analytics[wt_id] = analysis
    
    return analytics


def update_shared_state_with_analytics(analytics):
    """Update shared_state.json with worktree analytics."""
    if not STATE_FILE.exists():
        print("⚠️ shared_state.json not found")
        return
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    # Add analytics to each detected chat
    for chat in state.get("detected_chats", []):
        wt_id = chat.get("worktree_id")
        if wt_id in analytics:
            chat["analytics"] = analytics[wt_id]
    
    # Also update agents with summary stats
    for agent_name, agent_data in state.get("agents", {}).items():
        wt_id = agent_data.get("worktree_id")
        if wt_id in analytics:
            analysis = analytics[wt_id]
            agent_data["analytics"] = {
                "has_uncommitted_changes": analysis["git_status"].get("has_changes", False),
                "modified_files": analysis["file_stats"].get("modified_files", 0),
                "new_files": analysis["file_stats"].get("new_files", 0),
                "lines_added": analysis["file_stats"].get("lines_added", 0),
                "lines_deleted": analysis["file_stats"].get("lines_deleted", 0),
                "recent_commits_count": len(analysis["recent_commits"]),
                "last_analyzed": analysis["analyzed_at"]
            }
    
    state["worktree_analytics"] = {
        "last_updated": datetime.now().isoformat(),
        "analytics": analytics
    }
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated shared_state.json with analytics for {len(analytics)} worktree(s)")


def detect_task_completion(analytics, task_patterns=None):
    """
    Detect potential task completion based on file changes.
    
    task_patterns: dict mapping task_id to list of file patterns
    Example: {"T100": ["*.py", "api_server.py"], "T101": ["*.md"]}
    """
    if not task_patterns:
        return {}
    
    completions = {}
    
    for wt_id, analysis in analytics.items():
        git_status = analysis.get("git_status", {})
        modified_files = git_status.get("modified_files", [])
        new_files = git_status.get("new_files", [])
        all_files = modified_files + new_files
        
        for task_id, patterns in task_patterns.items():
            matches = []
            for pattern in patterns:
                for file in all_files:
                    if pattern in file or file.endswith(pattern.replace('*', '')):
                        matches.append(file)
            
            if matches:
                completions[task_id] = {
                    "worktree_id": wt_id,
                    "matched_files": matches,
                    "confidence": "medium"  # Could be improved with ML
                }
    
    return completions


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        print("🔍 Analyzing all worktrees...\n")
        analytics = analyze_all_worktrees()
        
        if analytics:
            print(f"\n📊 Analytics Summary:")
            for wt_id, analysis in analytics.items():
                git_status = analysis.get("git_status", {})
                file_stats = analysis.get("file_stats", {})
                print(f"\n  📁 {wt_id}:")
                print(f"     Uncommitted changes: {git_status.get('has_changes', False)}")
                print(f"     Modified files: {file_stats.get('modified_files', 0)}")
                print(f"     New files: {file_stats.get('new_files', 0)}")
                print(f"     Lines added: {file_stats.get('lines_added', 0)}")
                print(f"     Lines deleted: {file_stats.get('lines_deleted', 0)}")
                print(f"     Recent commits (24h): {len(analysis.get('recent_commits', []))}")
            
            # Update shared_state.json
            update_shared_state_with_analytics(analytics)
        else:
            print("⚠️ No worktrees found to analyze")
    else:
        print("Usage:")
        print("  python3 worktree_analytics.py analyze  # Analyze all worktrees and update shared_state.json")

