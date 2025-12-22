#!/usr/bin/env python3
"""
architect_server.py

Agent Server cho Architect (Planner).
Port: 8002
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_server_base import AgentServerBase

if __name__ == "__main__":
    server = AgentServerBase(agent_name="Architect", port=8002)
    server.run()

