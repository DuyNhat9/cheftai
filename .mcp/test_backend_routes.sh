#!/bin/bash
# Test Backend routes (nếu backend đang chạy)

echo "🧪 Testing Backend Agent Routes"
echo "============================================================"

BACKEND_URL="http://localhost:8000"

# Test 1: GET /api/agents/active
echo ""
echo "1️⃣  Testing GET /api/agents/active"
echo "-----------------------------------"
curl -s "${BACKEND_URL}/api/agents/active" | python3 -m json.tool 2>/dev/null || echo "   ⚠️  Backend không chạy hoặc endpoint chưa available"

# Test 2: GET /api/agents/active/simple
echo ""
echo "2️⃣  Testing GET /api/agents/active/simple"
echo "-----------------------------------"
curl -s "${BACKEND_URL}/api/agents/active/simple" | python3 -m json.tool 2>/dev/null || echo "   ⚠️  Backend không chạy hoặc endpoint chưa available"

# Test 3: GET /api/agents/Architect/info
echo ""
echo "3️⃣  Testing GET /api/agents/Architect/info"
echo "-----------------------------------"
curl -s "${BACKEND_URL}/api/agents/Architect/info" | python3 -m json.tool 2>/dev/null || echo "   ⚠️  Backend không chạy hoặc endpoint chưa available"

echo ""
echo "============================================================"
echo "💡 Để test đầy đủ, cần:"
echo "   1. Start Backend: cd backend && uvicorn app.main:app --reload"
echo "   2. Start MCP API: python3 .mcp/api_server.py"
echo ""

