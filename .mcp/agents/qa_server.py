#!/usr/bin/env python3
"""
qa_server.py

Agent Server cho Testing_QA.
Port: 8005
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_server_base import AgentServerBase

if __name__ == "__main__":
    server = AgentServerBase(agent_name="Testing_QA", port=8005)
    server.run()

