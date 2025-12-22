#!/bin/bash
# Generic script to auto-submit prompt to any agent
# Usage: ./scripts/auto_submit.sh <agent_name> [prompt_file]

AGENT="${1:-Backend_AI_Dev}"
PROMPT_FILE="${2:-.mcp/pending_prompts/${AGENT}.md}"

cd /Users/davidtran/Documents/cheftAi
python3 .mcp/auto_submit_service.py "$AGENT" "$PROMPT_FILE"




