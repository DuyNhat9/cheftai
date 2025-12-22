#!/bin/bash
# Test script để verify auto_submit scripts hoạt động đúng

set -e

PROJECT_DIR="/Users/davidtran/Documents/cheftAi"
cd "$PROJECT_DIR"

echo "🧪 Testing auto_submit scripts..."
echo ""

# Test 1: Check scripts exist and are executable
echo "✅ Test 1: Checking scripts exist..."
[ -f "scripts/auto_submit_backend.sh" ] && echo "  ✓ auto_submit_backend.sh exists" || echo "  ✗ auto_submit_backend.sh missing"
[ -f "scripts/auto_submit.sh" ] && echo "  ✓ auto_submit.sh exists" || echo "  ✗ auto_submit.sh missing"
[ -x "scripts/auto_submit_backend.sh" ] && echo "  ✓ auto_submit_backend.sh is executable" || echo "  ✗ auto_submit_backend.sh not executable"
[ -x "scripts/auto_submit.sh" ] && echo "  ✓ auto_submit.sh is executable" || echo "  ✗ auto_submit.sh not executable"
echo ""

# Test 2: Check Python service exists
echo "✅ Test 2: Checking Python service..."
[ -f ".mcp/auto_submit_service.py" ] && echo "  ✓ auto_submit_service.py exists" || echo "  ✗ auto_submit_service.py missing"
python3 -c "import sys; sys.path.insert(0, '.mcp'); from auto_submit_service import resolve_prompt_text" 2>/dev/null && echo "  ✓ Python service imports successfully" || echo "  ✗ Python service import failed"
echo ""

# Test 3: Check prompt file exists
echo "✅ Test 3: Checking prompt files..."
[ -f ".mcp/pending_prompts/Backend_AI_Dev.md" ] && echo "  ✓ Backend_AI_Dev.md exists" || echo "  ✗ Backend_AI_Dev.md missing"
[ -f ".mcp/shared_state.json" ] && echo "  ✓ shared_state.json exists" || echo "  ✗ shared_state.json missing"
echo ""

# Test 4: Check agent info in shared_state.json
echo "✅ Test 4: Checking agent info..."
if [ -f ".mcp/shared_state.json" ]; then
    WORKTREE_ID=$(python3 -c "import json; data=json.load(open('.mcp/shared_state.json')); print(data['agents']['Backend_AI_Dev']['worktree_id'])" 2>/dev/null)
    if [ -n "$WORKTREE_ID" ]; then
        echo "  ✓ Backend_AI_Dev worktree_id: $WORKTREE_ID"
    else
        echo "  ✗ Backend_AI_Dev worktree_id not found"
    fi
else
    echo "  ✗ Cannot check agent info (shared_state.json missing)"
fi
echo ""

# Test 5: Test prompt text extraction
echo "✅ Test 5: Testing prompt text extraction..."
if [ -f ".mcp/pending_prompts/Backend_AI_Dev.md" ]; then
    EXTRACTED=$(python3 -c "import sys; sys.path.insert(0, '.mcp'); from auto_submit_service import resolve_prompt_text; src, text = resolve_prompt_text('.mcp/pending_prompts/Backend_AI_Dev.md'); print(text[:50] if text else 'EMPTY')" 2>/dev/null)
    if [ -n "$EXTRACTED" ] && [ "$EXTRACTED" != "EMPTY" ]; then
        echo "  ✓ Prompt text extracted: ${EXTRACTED}..."
    else
        echo "  ✗ Failed to extract prompt text"
    fi
else
    echo "  ✗ Cannot test extraction (prompt file missing)"
fi
echo ""

# Test 6: Dry-run script syntax
echo "✅ Test 6: Dry-run script execution (syntax check)..."
bash -n scripts/auto_submit_backend.sh && echo "  ✓ auto_submit_backend.sh syntax OK" || echo "  ✗ auto_submit_backend.sh syntax error"
bash -n scripts/auto_submit.sh && echo "  ✓ auto_submit.sh syntax OK" || echo "  ✗ auto_submit.sh syntax error"
echo ""

echo "🎉 All tests completed!"
echo ""
echo "📝 Usage:"
echo "  ./scripts/auto_submit_backend.sh          # Submit to Backend_AI_Dev"
echo "  ./scripts/auto_submit.sh <agent_name>    # Submit to any agent"




