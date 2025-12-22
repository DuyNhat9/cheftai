#!/usr/bin/env python3
"""
gemini_server.py

Agent Server cho Gemini_3_Pro.
Port: 8007
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_server_base import AgentServerBase

if __name__ == "__main__":
    server = AgentServerBase(agent_name="Gemini_3_Pro", port=8007)
    server.run()

