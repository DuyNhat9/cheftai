#!/usr/bin/env python3
"""
ui_server.py

Agent Server cho UI_UX_Dev.
Port: 8004
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_server_base import AgentServerBase

if __name__ == "__main__":
    server = AgentServerBase(agent_name="UI_UX_Dev", port=8004)
    server.run()

