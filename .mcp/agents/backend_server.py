#!/usr/bin/env python3
"""
backend_server.py

Agent Server cho Backend_AI_Dev.
Port: 8003
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_server_base import AgentServerBase

if __name__ == "__main__":
    server = AgentServerBase(agent_name="Backend_AI_Dev", port=8003)
    server.run()

