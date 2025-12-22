#!/usr/bin/env python3
"""
supervisor_server.py

Agent Server cho Supervisor.
Port: 8006
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_server_base import AgentServerBase

if __name__ == "__main__":
    server = AgentServerBase(agent_name="Supervisor", port=8006)
    server.run()

