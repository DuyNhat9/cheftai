#!/usr/bin/env python3
"""Test script để tạo nhiều PENDING tasks cho nhiều agents"""
import json
from pathlib import Path

state_file = Path('.mcp/shared_state.json')
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Remove old test tasks
tasks = state.get('task_board', [])
tasks = [t for t in tasks if not t.get('id', '').startswith('TEST_')]

# Add multiple PENDING tasks for different agents
test_tasks = [
    {
        'id': 'TEST_B001',
        'title': 'Backend: Implement search API endpoint',
        'owner': 'Backend_AI_Dev',
        'status': 'PENDING',
        'description': 'Implement GET /api/recipes/search endpoint với query params'
    },
    {
        'id': 'TEST_U001',
        'title': 'UI: Update search bar component',
        'owner': 'UI_UX_Dev',
        'status': 'PENDING',
        'description': 'Thêm search bar vào home screen với Material Design'
    },
    {
        'id': 'TEST_Q001',
        'title': 'QA: Write unit tests for search',
        'owner': 'Testing_QA',
        'status': 'PENDING',
        'description': 'Viết test cases cho search API và UI component'
    },
    {
        'id': 'TEST_A001',
        'title': 'Architect: Review search feature design',
        'owner': 'Architect',
        'status': 'PENDING',
        'description': 'Review và approve search feature architecture'
    }
]

tasks.extend(test_tasks)
state['task_board'] = tasks

# Save (this will trigger monitor)
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print('✅ Added 4 test tasks (PENDING) for 4 different agents:')
for task in test_tasks:
    print(f'   - {task["id"]}: {task["owner"]} - {task["title"]}')
print('')
print('🔄 Monitor service should detect and trigger all 4 agents...')

