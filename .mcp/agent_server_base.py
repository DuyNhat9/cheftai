#!/usr/bin/env python3
"""
agent_server_base.py

Base class cho Agent Servers sử dụng FastAPI.
Mỗi agent server sẽ extend class này và implement agent-specific logic.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / '.mcp' / 'shared_state.json'
AUTO_SUBMIT_SCRIPT = PROJECT_DIR / '.mcp' / 'auto_submit_service.py'
PENDING_PROMPTS_DIR = PROJECT_DIR / '.mcp' / 'pending_prompts'


class ProcessTaskRequest(BaseModel):
    task_id: str


class SendMessageRequest(BaseModel):
    message: str
    task_id: Optional[str] = None
    task_title: Optional[str] = None


class AgentServerBase:
    """
    Base class cho Agent Servers.
    Mỗi agent server extend class này và set agent_name, port.
    """
    
    def __init__(self, agent_name: str, port: int):
        self.agent_name = agent_name
        self.port = port
        self.app = FastAPI(title=f"{agent_name} Agent Server")
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register common routes cho tất cả agent servers"""
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "agent": self.agent_name,
                "port": self.port
            }
        
        @self.app.get("/status")
        async def get_status():
            """Get agent status từ shared_state.json"""
            try:
                state = self._load_shared_state()
                agent_info = state.get('agents', {}).get(self.agent_name, {})
                return {
                    "agent": self.agent_name,
                    "status": agent_info.get('status', 'Unknown'),
                    "current_task": agent_info.get('current_task'),
                    "model": agent_info.get('model'),
                    "role": agent_info.get('role'),
                    "worktree_id": agent_info.get('worktree_id')
                }
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/process_task")
        async def process_task(request: ProcessTaskRequest):
            """Process a task for this agent"""
            try:
                state = self._load_shared_state()
                tasks = state.get('task_board', [])
                
                # Find task
                task = next(
                    (t for t in tasks 
                     if t.get('id') == request.task_id and t.get('owner') == self.agent_name),
                    None
                )
                
                if not task:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Task {request.task_id} not found for {self.agent_name}"
                    )
                
                # Update task status to IN_PROGRESS
                task['status'] = 'IN_PROGRESS'
                
                # Update agent status
                if self.agent_name in state.get('agents', {}):
                    state['agents'][self.agent_name]['status'] = 'Working'
                    state['agents'][self.agent_name]['current_task'] = (
                        f"{task.get('id')} - {task.get('title', '')}"
                    )
                
                # Save shared_state
                self._save_shared_state(state)
                
                # Trigger auto-submit to Cursor chat
                self._trigger_auto_submit(task)
                
                logger.info(f"[{self.agent_name}] Processed task {request.task_id}")
                
                return {
                    "success": True,
                    "message": f"Task {request.task_id} started",
                    "task": task
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error processing task: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/send_message")
        async def send_message(request: SendMessageRequest):
            """Send message to this agent"""
            try:
                state = self._load_shared_state()
                agent_info = state.get('agents', {}).get(self.agent_name, {})
                worktree_id = agent_info.get('worktree_id')
                
                if not worktree_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No worktree_id found for {self.agent_name}"
                    )
                
                # Create prompt file
                PENDING_PROMPTS_DIR.mkdir(exist_ok=True)
                prompt_file = PENDING_PROMPTS_DIR / f"{self.agent_name}.md"
                
                task_id = request.task_id or 'ADHOC'
                task_title = request.task_title or f"Message for {self.agent_name}"
                
                prompt_content = f"""# Message từ Agent Server API

**Agent:** {self.agent_name}
**Task ID:** {task_id}
**Task Title:** {task_title}

---

## Message:

{request.message}

---

## Action Required:

1. Đọc message trên
2. Xử lý theo đúng vai trò của bạn ({self.agent_name})
3. Update shared_state.json nếu cần
"""
                
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(prompt_content)
                
                # Trigger auto-submit
                result = self._trigger_auto_submit_file(str(prompt_file.resolve()), worktree_id)
                
                logger.info(f"[{self.agent_name}] Sent message via API")
                
                return {
                    "success": True,
                    "message": "Message sent",
                    "prompt_file": str(prompt_file),
                    "auto_submit": result
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks")
        async def get_tasks(status: Optional[str] = None):
            """List tasks for this agent"""
            try:
                state = self._load_shared_state()
                tasks = state.get('task_board', [])
                
                # Filter by owner
                agent_tasks = [
                    t for t in tasks 
                    if t.get('owner') == self.agent_name
                ]
                
                # Filter by status if provided
                if status:
                    agent_tasks = [
                        t for t in agent_tasks 
                        if t.get('status') == status.upper()
                    ]
                
                return {
                    "agent": self.agent_name,
                    "tasks": agent_tasks,
                    "count": len(agent_tasks)
                }
            except Exception as e:
                logger.error(f"Error getting tasks: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _load_shared_state(self) -> Dict[str, Any]:
        """Load shared_state.json"""
        if not STATE_FILE.exists():
            raise HTTPException(status_code=500, detail="shared_state.json not found")
        
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_shared_state(self, state: Dict[str, Any]):
        """Save shared_state.json"""
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _trigger_auto_submit(self, task: Dict[str, Any]):
        """Trigger auto-submit service for a task"""
        try:
            state = self._load_shared_state()
            agent_info = state.get('agents', {}).get(self.agent_name, {})
            worktree_id = agent_info.get('worktree_id')
            
            if not worktree_id:
                logger.warning(f"No worktree_id for {self.agent_name}, skipping auto-submit")
                return {"success": False, "message": "No worktree_id"}
            
            # Create prompt file
            PENDING_PROMPTS_DIR.mkdir(exist_ok=True)
            prompt_file = PENDING_PROMPTS_DIR / f"{self.agent_name}.md"
            
            prompt_content = f"""# Task Triggered từ Agent Server API

**Agent:** {self.agent_name}
**Task ID:** {task.get('id')}
**Task Title:** {task.get('title', '')}

---

## Task Description:

{task.get('description', 'No description')}

---

## Action Required:

1. Đọc shared_state.json → tìm task {task.get('id')}
2. Bắt đầu làm task ngay
3. Update status: IN_PROGRESS → COMPLETED khi xong
"""
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt_content)
            
            return self._trigger_auto_submit_file(str(prompt_file.resolve()), worktree_id)
        except Exception as e:
            logger.error(f"Error triggering auto-submit: {e}")
            return {"success": False, "message": str(e)}
    
    def _trigger_auto_submit_file(self, prompt_file: str, worktree_id: str) -> Dict[str, Any]:
        """Call auto_submit_service.py"""
        try:
            cmd = [
                'python3',
                str(AUTO_SUBMIT_SCRIPT),
                self.agent_name,
                prompt_file,
                worktree_id
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            logger.error(f"Error calling auto_submit_service: {e}")
            return {"success": False, "message": str(e)}
    
    def run(self, host: str = "0.0.0.0"):
        """Run the FastAPI server"""
        import uvicorn
        logger.info(f"[{self.agent_name}] Starting server on http://{host}:{self.port}")
        uvicorn.run(self.app, host=host, port=self.port, log_level="info")

