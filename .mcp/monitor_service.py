#!/usr/bin/env python3
"""
monitor_service.py

Service để monitor shared_state.json và tự động trigger worker agents
khi có task mới (PENDING) được thêm vào.

Flow:
1. Watch shared_state.json cho thay đổi
2. Khi có task PENDING mới → tạo prompt file
3. Auto-submit prompt vào chat Cursor của agent tương ứng
4. Update task status → IN_PROGRESS

Chạy: python3 .mcp/monitor_service.py
Hoặc background: nohup python3 .mcp/monitor_service.py > /tmp/monitor_service.log 2>&1 &
"""

import json
import time
import os
import subprocess
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Try import cloud agent client (optional)
try:
    from cloud_agent_client import CloudAgentClient, load_config
    CLOUD_API_AVAILABLE = True
except ImportError:
    CLOUD_API_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("[monitor_service] Cloud API client not available, using local method only")

# Configure logging
LOG_FILE = Path('/tmp/monitor_service.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_DIR = Path(__file__).parent.parent
SHARED_STATE_PATH = PROJECT_DIR / '.mcp' / 'shared_state.json'
PENDING_PROMPTS_DIR = PROJECT_DIR / '.mcp' / 'pending_prompts'
AUTO_SUBMIT_SCRIPT = PROJECT_DIR / '.mcp' / 'auto_submit_service.py'

# Track processed tasks để tránh trigger nhiều lần
processed_tasks = set()


class SharedStateHandler(FileSystemEventHandler):
    """Handler để monitor thay đổi shared_state.json"""
    
    def __init__(self):
        self.last_modified = 0
        self.debounce_seconds = 2  # Debounce để tránh trigger nhiều lần
        
        # Load config và init cloud client nếu available
        self.cloud_client = None
        self.use_cloud_api = False
        
        if CLOUD_API_AVAILABLE:
            try:
                config = load_config()
                cloud_config = config.get('cursor_cloud_api', {})
                if cloud_config.get('enabled') and cloud_config.get('api_key'):
                    self.cloud_client = CloudAgentClient(
                        api_key=cloud_config.get('api_key'),
                        api_base=cloud_config.get('api_base', 'https://api.cursor.com/v0')
                    )
                    self.use_cloud_api = self.cloud_client.enabled
                    logger.info(f"[monitor_service] Cloud API enabled: {self.use_cloud_api}")
                else:
                    logger.info(f"[monitor_service] Cloud API disabled in config, using local method")
            except Exception as e:
                logger.warning(f"[monitor_service] Failed to init cloud client: {e}, using local method")
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Chỉ xử lý shared_state.json
        if event.src_path != str(SHARED_STATE_PATH):
            return
        
        # Debounce: chỉ xử lý nếu file thực sự thay đổi (không phải metadata)
        current_time = time.time()
        if current_time - self.last_modified < self.debounce_seconds:
            return
        
        try:
            # Kiểm tra file có thực sự thay đổi không
            mtime = os.path.getmtime(event.src_path)
            if mtime == self.last_modified:
                return
            self.last_modified = mtime
        except:
            pass
        
        logger.info(f"[monitor_service] Detected change in shared_state.json")
        time.sleep(0.5)  # Đợi file write hoàn tất
        self.process_new_tasks()
    
    def process_new_tasks(self):
        """Xử lý tasks mới (PENDING) và trigger agents"""
        if not SHARED_STATE_PATH.exists():
            logger.warning(f"[monitor_service] shared_state.json not found")
            return
        
        try:
            with open(SHARED_STATE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"[monitor_service] Failed to read shared_state.json: {e}")
            return
        
        agents = data.get('agents', {})
        tasks = data.get('task_board', [])
        
        # Tìm tasks PENDING mới (chưa được xử lý)
        pending_tasks = [
            t for t in tasks 
            if t.get('status') == 'PENDING' and t.get('id') not in processed_tasks
        ]
        
        if not pending_tasks:
            return
        
        logger.info(f"[monitor_service] Found {len(pending_tasks)} new PENDING task(s)")
        
        changed = False
        for task in pending_tasks:
            task_id = task.get('id')
            agent_name = task.get('owner')
            task_title = task.get('title', '')
            task_desc = task.get('description', '')
            
            if not agent_name:
                logger.warning(f"[monitor_service] Task {task_id} has no owner, skipping")
                continue
            
            if agent_name not in agents:
                logger.warning(f"[monitor_service] Agent {agent_name} not found in agents, skipping")
                continue
            
            # Lấy thông tin agent
            agent = agents[agent_name]
            worktree_id = agent.get('worktree_id')
            model = agent.get('model', 'Unknown')
            
            if not worktree_id:
                logger.warning(f"[monitor_service] Agent {agent_name} has no worktree_id, skipping")
                continue
            
            # Tạo prompt file
            PENDING_PROMPTS_DIR.mkdir(exist_ok=True)
            prompt_file = PENDING_PROMPTS_DIR / f"{agent_name}.md"
            
            prompt_content = f"""# 🚀 Task Triggered Tự Động

**Agent:** {agent_name}
**Task ID:** {task_id}
**Task Title:** {task_title}
**Triggered At:** {datetime.now().isoformat()}

---

## 📋 Task Description:

{task_desc if task_desc else 'No description provided'}

---

## ✅ Action Required - LÀM NGAY:

1. **ĐỌC NGAY** `.mcp/shared_state.json` → tìm task `{task_id}` trong `task_board`
2. **BẮT ĐẦU NGAY** làm task `{task_id}` theo đúng vai trò của bạn ({agent_name})
3. **CẬP NHẬT NGAY:**
   - shared_state.json: task status → `IN_PROGRESS` (khi bắt đầu) → `COMPLETED` (khi xong)
   - Nếu cần, commit code và update docs

**Hãy trả lời ngay:** "Đã đọc shared_state.json, bắt đầu làm task {task_id} ngay."

---

**Note:** Task này được trigger tự động từ monitor_service.py khi Architect tạo plan.
"""
            
            try:
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(prompt_content)
                logger.info(f"[monitor_service] Created prompt file: {prompt_file}")
            except Exception as e:
                logger.error(f"[monitor_service] Failed to create prompt file: {e}")
                continue
            
            # Trigger agent: Try Cloud API first, fallback to local method
            logger.info(f"[monitor_service] Triggering {agent_name} (worktree: {worktree_id}) for task {task_id}")
            
            success = False
            
            # Try Cloud API if enabled
            if self.use_cloud_api and self.cloud_client:
                try:
                    # Check if agent already has cloud_id
                    cloud_id = agent.get('cloud_id')
                    
                    if not cloud_id:
                        # Launch new cloud agent
                        cloud_id = self.cloud_client.launch_agent(
                            agent_name=agent_name,
                            model=model,
                            prompt=prompt_content
                        )
                        
                        if cloud_id:
                            # Save cloud_id to agent config
                            agent['cloud_id'] = cloud_id
                            changed = True
                    
                    if cloud_id:
                        # Send followup if needed
                        self.cloud_client.send_followup(
                            cloud_id=cloud_id,
                            instruction=f"Tiếp tục task {task_id} và báo khi hoàn thành."
                        )
                        
                        # Poll conversation (non-blocking, update status later)
                        logger.info(f"[monitor_service] ✅ Cloud agent triggered for {agent_name} (cloud_id: {cloud_id})")
                        processed_tasks.add(task_id)
                        task['status'] = 'IN_PROGRESS'
                        changed = True
                        success = True
                        
                        # Note: Conversation polling có thể chạy async hoặc trong background
                        # Ở đây chỉ mark IN_PROGRESS, polling sẽ được handle riêng nếu cần
                        
                except Exception as e:
                    logger.warning(f"[monitor_service] ⚠️ Cloud API failed for {agent_name}: {e}, falling back to local")
            
            # Fallback to local method if Cloud API not used or failed
            if not success:
                try:
                    # Gọi auto_submit_service.py (local method)
                    cmd = [
                        'python3',
                        str(AUTO_SUBMIT_SCRIPT),
                        agent_name,
                        str(prompt_file.resolve()),
                        worktree_id,  # Pass worktree_id as chat_id
                        model        # Pass model name để auto_submit tìm đúng window
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"[monitor_service] ✅ Auto-submit successful for {agent_name} (model: {model})")
                        processed_tasks.add(task_id)
                        task['status'] = 'IN_PROGRESS'
                        changed = True
                        success = True
                        
                        # Delay giữa triggers để Cursor ổn định và focus đúng window
                        logger.info(f"[monitor_service] Waiting 5s before next trigger to allow window switch...")
                        time.sleep(5)
                    else:
                        logger.warning(f"[monitor_service] ⚠️ Auto-submit failed for {agent_name}: {result.stderr}")
                        processed_tasks.add(task_id)
                        time.sleep(3)
                        
                except subprocess.TimeoutExpired:
                    logger.error(f"[monitor_service] ❌ Auto-submit timeout for {agent_name}")
                    processed_tasks.add(task_id)
                except Exception as e:
                    logger.error(f"[monitor_service] ❌ Auto-submit error for {agent_name}: {e}")
                    processed_tasks.add(task_id)
        
        # Lưu lại shared_state nếu có thay đổi
        if changed:
            try:
                with open(SHARED_STATE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"[monitor_service] ✅ Updated shared_state.json with IN_PROGRESS tasks")
            except Exception as e:
                logger.error(f"[monitor_service] ❌ Failed to save shared_state.json: {e}")


def main():
    """Main function để start monitor service"""
    logger.info(f"[monitor_service] Starting monitor service...")
    logger.info(f"[monitor_service] Watching: {SHARED_STATE_PATH}")
    logger.info(f"[monitor_service] Logs: {LOG_FILE}")
    
    # Đảm bảo directories tồn tại
    PENDING_PROMPTS_DIR.mkdir(exist_ok=True)
    
    # Tạo event handler
    event_handler = SharedStateHandler()
    observer = Observer()
    
    # Watch directory chứa shared_state.json
    watch_dir = SHARED_STATE_PATH.parent
    observer.schedule(event_handler, path=str(watch_dir), recursive=False)
    
    observer.start()
    logger.info(f"[monitor_service] ✅ Monitor service started. Waiting for changes...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info(f"[monitor_service] Stopping monitor service...")
        observer.stop()
    
    observer.join()
    logger.info(f"[monitor_service] ✅ Monitor service stopped")


if __name__ == "__main__":
    main()

