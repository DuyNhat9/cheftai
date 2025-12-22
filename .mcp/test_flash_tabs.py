#!/usr/bin/env python3
"""Test flash all agent tabs"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.')))

import importlib.util
spec = importlib.util.spec_from_file_location('auto_submit_service', Path('.mcp/auto_submit_service.py'))
auto_submit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_submit)

print('✨ Testing Flash All Agent Tabs')
print('=' * 60)

success = auto_submit.flash_all_agent_tabs(delay_between=0.5)

if success:
    print('\n✅ Flash completed successfully!')
    print('💡 Tất cả các tabs đã được focus lần lượt để làm nháy')
else:
    print('\n❌ Flash failed')

