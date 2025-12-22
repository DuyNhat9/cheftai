#!/usr/bin/env python3
"""
Ví dụ tích hợp Backend với MCP API để discover và tương tác với agents
"""
import httpx
import asyncio
from typing import List, Dict, Optional

MCP_API_URL = "http://localhost:8001"

async def get_active_agents() -> List[Dict]:
    """
    Lấy danh sách agents có chat đang mở trong session
    
    Returns:
        List[Dict]: Danh sách agents với thông tin chi tiết
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{MCP_API_URL}/api/active-agents")
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return data.get('active_agents', [])
            return []
    except Exception as e:
        print(f"❌ Error getting active agents: {e}")
        return []

async def send_message_to_agent(agent_name: str, chat_id: str, message: str) -> bool:
    """
    Gửi message cho một agent cụ thể
    
    Args:
        agent_name: Tên agent
        chat_id: Chat ID (worktree_id)
        message: Message cần gửi
        
    Returns:
        bool: True nếu thành công
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{MCP_API_URL}/api/messages",
                json={
                    "agent": agent_name,
                    "chat_id": chat_id,
                    "message": message,
                    "task_id": "ADHOC",
                    "task_title": "Message from Backend"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                auto_submit = result.get('auto_submit', {})
                return auto_submit.get('success', False)
            return False
    except Exception as e:
        print(f"❌ Error sending message to {agent_name}: {e}")
        return False

async def broadcast_to_all_agents(message: str) -> Dict:
    """
    Gửi message cho tất cả agents có chat đang mở
    
    Args:
        message: Message cần gửi
        
    Returns:
        Dict: Kết quả gửi cho từng agent
    """
    active_agents = await get_active_agents()
    
    if not active_agents:
        return {
            "success": False,
            "message": "Không có agents nào có chat đang mở",
            "sent_count": 0
        }
    
    results = []
    for agent in active_agents:
        success = await send_message_to_agent(
            agent['agent_name'],
            agent['worktree_id'],
            message
        )
        results.append({
            "agent": agent['agent_name'],
            "worktree_id": agent['worktree_id'],
            "success": success
        })
    
    success_count = sum(1 for r in results if r['success'])
    
    return {
        "success": True,
        "message": f"Đã gửi cho {success_count}/{len(results)} agents",
        "sent_count": success_count,
        "total_count": len(results),
        "results": results
    }

async def find_agent_by_role(role_keyword: str) -> Optional[Dict]:
    """
    Tìm agent theo role
    
    Args:
        role_keyword: Từ khóa để tìm (ví dụ: "Backend", "UI", "Testing")
        
    Returns:
        Optional[Dict]: Agent info nếu tìm thấy
    """
    active_agents = await get_active_agents()
    
    for agent in active_agents:
        role = agent.get('role', '')
        if role_keyword.lower() in role.lower():
            return agent
    return None

async def main():
    """Demo sử dụng"""
    print("🔍 Discovering active agents...")
    active_agents = await get_active_agents()
    
    print(f"\n📊 Tìm thấy {len(active_agents)} agents có chat đang mở:")
    for agent in active_agents:
        print(f"   - {agent['agent_name']:20} → {agent['worktree_id']} ({agent['model']})")
    
    if active_agents:
        print("\n📤 Gửi message 'Hello from Backend' cho tất cả agents...")
        result = await broadcast_to_all_agents("Hello from Backend")
        print(f"   ✅ Đã gửi cho {result['sent_count']}/{result['total_count']} agents")
        
        print("\n🔍 Tìm Backend agent...")
        backend_agent = await find_agent_by_role("Backend")
        if backend_agent:
            print(f"   ✅ Found: {backend_agent['agent_name']} → {backend_agent['worktree_id']}")

if __name__ == "__main__":
    asyncio.run(main())

