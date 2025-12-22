"""
Agent Discovery API Routes
Backend endpoint để discover và tương tác với agents trong MCP
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

# MCP API Server URL
MCP_API_URL = os.getenv("MCP_API_URL", "http://localhost:8001")

# Pydantic models for request validation
class SendMessageRequest(BaseModel):
    agent: str
    message: str
    task_id: Optional[str] = "ADHOC"
    task_title: Optional[str] = None

class BroadcastMessageRequest(BaseModel):
    message: str

@router.get("/agents/active")
async def get_active_agents():
    """
    Lấy danh sách tất cả agents có chat đang mở trong session hiện tại
    
    Returns:
        Dict với danh sách active_agents và metadata
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{MCP_API_URL}/api/active-agents")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"MCP API server không khả dụng: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"MCP API error: {e.response.text}"
        )

@router.get("/agents/active/simple")
async def get_active_agents_simple():
    """
    Lấy danh sách đơn giản: chỉ agent_name và worktree_id
    
    Returns:
        List[Dict] với format: [{"agent_name": "...", "worktree_id": "..."}]
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{MCP_API_URL}/api/active-agents")
            response.raise_for_status()
            data = response.json()
            
            # Simplify response
            simple_list = []
            for agent in data.get("active_agents", []):
                simple_list.append({
                    "agent_name": agent.get("agent_name"),
                    "worktree_id": agent.get("worktree_id"),
                    "model": agent.get("model"),
                    "status": agent.get("status")
                })
            
            return {
                "count": len(simple_list),
                "agents": simple_list
            }
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"MCP API server không khả dụng: {str(e)}"
        )

@router.post("/agents/send")
async def send_message_to_agent(payload: SendMessageRequest):
    """
    Gửi message cho một agent cụ thể
    
    Body:
        {
            "agent": "Architect",  # Tên agent
            "message": "nhat dang test",  # Message cần gửi
            "task_id": "TEST",  # Optional
            "task_title": "Test message"  # Optional
        }
    
    Returns:
        Dict với kết quả gửi
    """
    agent_name = payload.agent
    message = payload.message
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # Lấy thông tin agent để có worktree_id
            agents_response = await client.get(f"{MCP_API_URL}/api/active-agents")
            agents_response.raise_for_status()
            agents_data = agents_response.json()
            
            # Tìm agent
            target_agent = None
            for agent in agents_data.get("active_agents", []):
                if agent.get("agent_name") == agent_name:
                    target_agent = agent
                    break
            
            if not target_agent:
                raise HTTPException(
                    status_code=404,
                    detail=f"Agent '{agent_name}' không có chat đang mở trong session"
                )
            
            # Gửi message
            msg_response = await client.post(
                f"{MCP_API_URL}/api/messages",
                json={
                    "agent": agent_name,
                    "chat_id": target_agent.get("worktree_id"),
                    "message": message,
                    "task_id": payload.task_id or "ADHOC",
                    "task_title": payload.task_title or f"Message to {agent_name}"
                },
                timeout=20.0
            )
            
            if msg_response.status_code == 200:
                result = msg_response.json()
                return {
                    "success": True,
                    "agent": agent_name,
                    "worktree_id": target_agent.get("worktree_id"),
                    "auto_submit": result.get("auto_submit", {}),
                    "message": "Message sent successfully"
                }
            else:
                raise HTTPException(
                    status_code=msg_response.status_code,
                    detail=f"Failed to send message: {msg_response.text}"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"MCP API server không khả dụng: {str(e)}"
        )

@router.post("/agents/broadcast")
async def broadcast_to_agents(payload: BroadcastMessageRequest):
    """
    Gửi message cho tất cả agents có chat đang mở
    
    Body:
        {
            "message": "nhat dang test"  # Message cần gửi
        }
        
    Returns:
        Dict với kết quả gửi cho từng agent
    """
    message = payload.message
    try:
        # Lấy danh sách active agents
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get active agents
            agents_response = await client.get(f"{MCP_API_URL}/api/active-agents")
            agents_response.raise_for_status()
            agents_data = agents_response.json()
            
            active_agents = agents_data.get("active_agents", [])
            
            if not active_agents:
                return {
                    "success": False,
                    "message": "Không có agents nào có chat đang mở",
                    "sent_count": 0
                }
            
            # Gửi message cho từng agent
            results = []
            for agent in active_agents:
                try:
                    msg_response = await client.post(
                        f"{MCP_API_URL}/api/messages",
                        json={
                            "agent": agent["agent_name"],
                            "chat_id": agent["worktree_id"],
                            "message": message,
                            "task_id": "BROADCAST",
                            "task_title": "Broadcast message"
                        },
                        timeout=15
                    )
                    
                    if msg_response.status_code == 200:
                        results.append({
                            "agent": agent["agent_name"],
                            "worktree_id": agent["worktree_id"],
                            "success": True
                        })
                    else:
                        results.append({
                            "agent": agent["agent_name"],
                            "worktree_id": agent["worktree_id"],
                            "success": False,
                            "error": msg_response.text[:100]
                        })
                except Exception as e:
                    results.append({
                        "agent": agent["agent_name"],
                        "worktree_id": agent["worktree_id"],
                        "success": False,
                        "error": str(e)
                    })
            
            success_count = sum(1 for r in results if r.get("success"))
            
            return {
                "success": True,
                "message": f"Đã gửi cho {success_count}/{len(results)} agents",
                "sent_count": success_count,
                "total_count": len(results),
                "results": results
            }
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"MCP API server không khả dụng: {str(e)}"
        )

@router.get("/agents/{agent_name}/info")
async def get_agent_info(agent_name: str):
    """
    Lấy thông tin chi tiết của một agent cụ thể
    
    Args:
        agent_name: Tên agent (Architect, Backend_AI_Dev, etc.)
        
    Returns:
        Dict với thông tin agent
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{MCP_API_URL}/api/active-agents")
            response.raise_for_status()
            data = response.json()
            
            # Tìm agent
            for agent in data.get("active_agents", []):
                if agent.get("agent_name") == agent_name:
                    return agent
            
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' không có chat đang mở trong session"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"MCP API server không khả dụng: {str(e)}"
        )

