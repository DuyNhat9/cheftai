#!/usr/bin/env python3
"""
API Server để update shared_state.json từ dashboard
Cho phép dashboard trigger agents và update tasks
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import subprocess
import platform
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import cgi
import logging
import fcntl
import shutil
from datetime import datetime
import time

PORT = 8001
BASE_DIR = Path(__file__).parent.parent
STATE_FILE = BASE_DIR / '.mcp' / 'shared_state.json'

# Configure logging
LOG_FILE = Path('/tmp/api_server.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import helper function để mở agent windows (optional, không crash nếu không có)
open_or_focus_agent_window = None
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from open_separate_windows import open_or_focus_agent_window
    logger.info("[api_server] ✅ Loaded open_or_focus_agent_window helper")
except ImportError as e:
    logger.warning(f"[api_server] ⚠️ Could not import open_or_focus_agent_window: {e}")

# Optional import: helper để mở/focus agent window trong Cursor
try:
    from open_separate_windows import open_or_focus_agent_window  # type: ignore
except Exception:
    open_or_focus_agent_window = None

class APIHandler(BaseHTTPRequestHandler):
    def _sync_agent_status_with_tasks(self, state):
        """
        Tự động sync agent status với task_board VÀ chat activity:
        - Nếu agent "Working" nhưng không có task IN_PROGRESS → set "Idle"
        - Nếu agent "Working" nhưng chat không active (>30 phút) → set "Idle"
        - Nếu agent "Idle" nhưng có task IN_PROGRESS VÀ chat active (<30 phút) → set "Working"
        """
        if not state or 'agents' not in state or 'task_board' not in state:
            return state
        
        tasks = state.get('task_board', [])
        agents = state.get('agents', {})
        detected_chats = state.get('detected_chats', [])
        changed = False
        
        # Tạo map: agent_name -> chat activity info
        agent_chat_activity = {}
        for chat in detected_chats:
            agent_name = chat.get('agent_name')
            if agent_name:
                modified_minutes = chat.get('modified_minutes_ago', 999999)
                if agent_name not in agent_chat_activity or modified_minutes < agent_chat_activity[agent_name]:
                    agent_chat_activity[agent_name] = modified_minutes
        
        for agent_name, agent in agents.items():
            # Tìm tasks IN_PROGRESS của agent này
            in_progress_tasks = [
                t for t in tasks 
                if t.get('owner') == agent_name and t.get('status') == 'IN_PROGRESS'
            ]
            
            # Kiểm tra chat activity (nếu có)
            chat_inactive_minutes = agent_chat_activity.get(agent_name, 999999)
            is_chat_active = chat_inactive_minutes < 30  # Chat active nếu < 30 phút
            
            current_status = agent.get('status', 'Idle')
            
            # Nếu agent đang "Working" nhưng không có task IN_PROGRESS → set Idle
            if current_status == 'Working' and len(in_progress_tasks) == 0:
                agent['status'] = 'Idle'
                agent['current_task'] = None
                changed = True
                logger.info(f"[api_server] 🔄 Auto-sync: {agent_name} → Idle (no IN_PROGRESS tasks)")
            
            # Nếu agent đang "Working" nhưng chat không active (>30 phút) → set Idle
            elif current_status == 'Working' and not is_chat_active and chat_inactive_minutes < 999999:
                agent['status'] = 'Idle'
                agent['current_task'] = None
                changed = True
                logger.info(f"[api_server] 🔄 Auto-sync: {agent_name} → Idle (chat inactive for {chat_inactive_minutes:.1f} min)")
            
            # Nếu agent đang "Working" nhưng không có chat activity info → set Idle (không có bằng chứng chat đang active)
            elif current_status == 'Working' and agent_name not in agent_chat_activity:
                agent['status'] = 'Idle'
                agent['current_task'] = None
                changed = True
                logger.info(f"[api_server] 🔄 Auto-sync: {agent_name} → Idle (no chat activity info found)")
            
            # Nếu agent đang "Idle" nhưng có task IN_PROGRESS VÀ chat active → set Working
            elif current_status == 'Idle' and len(in_progress_tasks) > 0 and is_chat_active:
                first_task = in_progress_tasks[0]
                agent['status'] = 'Working'
                agent['current_task'] = f"{first_task.get('id', '')} - {first_task.get('title', '')}"
                changed = True
                logger.info(f"[api_server] 🔄 Auto-sync: {agent_name} → Working (task: {first_task.get('id', '')}, chat active)")
            
            # Nếu agent đang "Idle" nhưng có task IN_PROGRESS NHƯNG chat không active → giữ Idle
            elif current_status == 'Idle' and len(in_progress_tasks) > 0 and not is_chat_active and chat_inactive_minutes < 999999:
                # Có task nhưng chat không active → không set Working
                logger.info(f"[api_server] ⚠️ {agent_name} has IN_PROGRESS task but chat inactive ({chat_inactive_minutes:.1f} min), keeping Idle")
            
            # Nếu agent đang "Idle" nhưng có task IN_PROGRESS NHƯNG không có chat info → giữ Idle
            elif current_status == 'Idle' and len(in_progress_tasks) > 0 and agent_name not in agent_chat_activity:
                # Có task nhưng không có chat info → không set Working
                logger.info(f"[api_server] ⚠️ {agent_name} has IN_PROGRESS task but no chat activity info, keeping Idle")
        
        # Nếu có thay đổi, lưu lại file với file locking và error handling
        if changed and STATE_FILE.exists():
            self._safe_write_state_file(state)
        
        return state
    
    def _safe_read_state_file(self, max_retries=3, retry_delay=0.1):
        """
        Read shared_state.json với file locking và retry logic.
        Returns: dict hoặc None nếu failed
        """
        if not STATE_FILE.exists():
            logger.warning(f"[api_server] ⚠️ State file not found: {STATE_FILE}")
            return None
        
        for attempt in range(max_retries):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    # Acquire shared lock (multiple readers allowed)
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    try:
                        state = json.load(f)
                        logger.debug(f"[api_server] ✅ State file read successfully (attempt {attempt + 1})")
                        return state
                    finally:
                        # Release lock
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        
            except BlockingIOError:
                # File is locked by another process
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"[api_server] ⚠️ File locked, retrying in {wait_time:.2f}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"[api_server] ❌ Failed to acquire lock after {max_retries} attempts")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"[api_server] ❌ JSON decode error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    return None
                    
            except Exception as e:
                logger.error(f"[api_server] ❌ Error reading state file (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    return None
        
        return None
    
    def _safe_write_state_file(self, state, max_retries=3, retry_delay=0.1):
        """
        Write shared_state.json với file locking, backup, và retry logic.
        """
        backup_file = STATE_FILE.with_suffix('.json.backup')
        
        for attempt in range(max_retries):
            try:
                # Tạo backup trước khi write
                if STATE_FILE.exists():
                    shutil.copy2(STATE_FILE, backup_file)
                    logger.debug(f"[api_server] Backup created: {backup_file}")
                
                # Write với file locking
                with open(STATE_FILE, 'w', encoding='utf-8') as f:
                    # Acquire exclusive lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        json.dump(state, f, indent=2, ensure_ascii=False)
                        f.flush()
                        os.fsync(f.fileno())  # Ensure data written to disk
                    finally:
                        # Release lock
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                
                logger.info(f"[api_server] ✅ State file updated successfully (attempt {attempt + 1})")
                return True
                
            except BlockingIOError:
                # File is locked by another process
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"[api_server] ⚠️ File locked, retrying in {wait_time:.2f}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"[api_server] ❌ Failed to acquire lock after {max_retries} attempts")
                    return False
                    
            except Exception as e:
                logger.error(f"[api_server] ❌ Error writing state file (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    # Restore backup nếu write failed
                    if backup_file.exists():
                        try:
                            shutil.copy2(backup_file, STATE_FILE)
                            logger.warning(f"[api_server] ⚠️ Restored from backup due to write failure")
                        except Exception as restore_error:
                            logger.error(f"[api_server] ❌ Failed to restore backup: {restore_error}")
                    return False
        
        return False
    
    def _set_cors_headers(self):
        """Set CORS headers only once per request"""
        if not hasattr(self, '_cors_headers_set'):
            self._cors_headers_set = False
        if not self._cors_headers_set:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self._cors_headers_set = True
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def end_headers(self):
        # Add CORS headers for all responses (only once)
        self._set_cors_headers()
        super().end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/state':
            # Return shared_state.json với auto-sync agent status
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if STATE_FILE.exists():
                state = self._safe_read_state_file()
                if state is None:
                    self.wfile.write(json.dumps({"error": "Failed to read state file"}).encode())
                    return
                
                # Auto-sync agent status với task_board trước khi trả về
                state = self._sync_agent_status_with_tasks(state)
                
                self.wfile.write(json.dumps(state, ensure_ascii=False).encode())
            else:
                self.wfile.write(json.dumps({"error": "File not found"}).encode())
        elif path == '/api/agents':
            # Return only agents block from shared_state.json
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.wfile.write(json.dumps(state.get("agents", {}), ensure_ascii=False).encode())
            else:
                self.wfile.write(json.dumps({"error": "File not found"}).encode())

        elif path == '/api/active-agents':
            # Return danh sách agents có chat đang mở trong session hiện tại
            # Endpoint này để Backend có thể discover tất cả agents active
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                detected_chats = state.get("detected_chats", [])
                agents = state.get("agents", {})
                
                # Tạo danh sách agents có chat active
                active_agents = []
                for chat in detected_chats:
                    agent_name = chat.get('agent_name')
                    if not agent_name:
                        continue
                    
                    # Lấy thông tin agent từ config
                    agent_info = agents.get(agent_name, {})
                    
                    active_agent = {
                        'agent_name': agent_name,
                        'chat_id': chat.get('chat_id'),
                        'worktree_id': chat.get('worktree_id'),
                        'worktree_path': chat.get('worktree_path'),
                        'model': chat.get('model') or agent_info.get('model'),
                        'status': agent_info.get('status', 'Idle'),
                        'current_task': agent_info.get('current_task'),
                        'role': agent_info.get('role'),
                        'last_active': chat.get('last_active'),
                        'modified_minutes_ago': chat.get('modified_minutes_ago', 0),
                        'has_analytics': 'analytics' in chat
                    }
                    
                    # Thêm analytics nếu có
                    if 'analytics' in chat:
                        analytics = chat.get('analytics', {})
                        active_agent['analytics'] = {
                            'has_uncommitted_changes': analytics.get('git_status', {}).get('has_changes', False),
                            'modified_files': analytics.get('file_stats', {}).get('modified_files', 0),
                            'new_files': analytics.get('file_stats', {}).get('new_files', 0),
                            'lines_added': analytics.get('file_stats', {}).get('lines_added', 0),
                            'recent_commits_count': analytics.get('recent_commits', [])
                        }
                    
                    active_agents.append(active_agent)
                
                response = {
                    'success': True,
                    'count': len(active_agents),
                    'active_agents': active_agents,
                    'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
                }
                
                self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode())
            else:
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "File not found",
                    "active_agents": []
                }).encode())

        elif path == '/api/flash-tabs':
            # Flash/highlight tất cả agent tabs đang mở
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                # Import auto_submit_service
                import sys
                import importlib.util
                auto_submit_path = BASE_DIR / '.mcp' / 'auto_submit_service.py'
                spec = importlib.util.spec_from_file_location('auto_submit_service', auto_submit_path)
                auto_submit_service = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(auto_submit_service)
                
                # Flash all tabs
                success = auto_submit_service.flash_all_agent_tabs(delay_between=0.5)
                
                response = {
                    "success": success,
                    "message": "Flashed all agent tabs" if success else "Failed to flash tabs"
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
            except Exception as e:
                logger.error(f"Error flashing tabs: {e}")
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode())

        elif path == '/api/task_board':
            # Return only task_board from shared_state.json
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if STATE_FILE.exists():
                state = self._safe_read_state_file()
                if state:
                    self.wfile.write(json.dumps(state.get("task_board", []), ensure_ascii=False).encode())
                else:
                    self.wfile.write(json.dumps({"error": "Failed to read state file"}).encode())
            else:
                self.wfile.write(json.dumps({"error": "File not found"}).encode())

        elif path == '/api/chat-history/sync':
            # Sync chat history cho tất cả agents
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                import importlib.util
                chat_sync_path = BASE_DIR / '.mcp' / 'chat_history_sync.py'
                if not chat_sync_path.exists():
                    raise FileNotFoundError("chat_history_sync.py not found")
                
                spec = importlib.util.spec_from_file_location('chat_history_sync', chat_sync_path)
                chat_sync = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(chat_sync)
                
                # Sync chat history
                chat_sync.sync_all_agents_chat_history()
                
                # Load updated state để return chat_history
                state = self._safe_read_state_file()
                if state:
                    chat_history = state.get('chat_history', {})
                    response = {
                        "success": True,
                        "message": "Chat history synced",
                        "chat_history": chat_history,
                        "agents_synced": list(chat_history.keys())
                    }
                else:
                    response = {
                        "success": False,
                        "error": "Failed to read state file"
                    }
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
            except Exception as e:
                logger.error(f"Error syncing chat history: {e}")
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode())

        elif path == '/api/chat-history':
            # Get chat history cho một agent hoặc tất cả
            parsed = urlparse(self.path)
            query_params = parse_qs(parsed.query)
            agent_name = query_params.get('agent', [None])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            state = self._safe_read_state_file()
            if state:
                chat_history = state.get('chat_history', {})
                if agent_name:
                    # Return history cho một agent
                    agent_history = chat_history.get(agent_name, {})
                    response = {
                        "success": True,
                        "agent": agent_name,
                        "chat_history": agent_history
                    }
                else:
                    # Return tất cả
                    response = {
                        "success": True,
                        "chat_history": chat_history
                    }
            else:
                response = {
                    "success": False,
                    "error": "Failed to read state file"
                }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        elif path == '/api/get-current-chat':
            # Lấy chat ID từ Cursor window hiện tại (macOS only)
            if platform.system() != 'Darwin':
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "macOS only"}).encode())
                return
            
            try:
                import subprocess
                script_path = BASE_DIR / ".mcp" / "get_current_chat_id.py"
                result = subprocess.run(
                    ["python3", str(script_path), "--json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    chat_info = json.loads(result.stdout)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(chat_info, ensure_ascii=False).encode())
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": result.stderr.strip() or "Failed to get chat ID"
                    }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode())

        elif path == '/api/map-chat':
            # Map chat ID với worktree
            content_length = int(self.headers.get('Content-Length', '0') or '0')
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(post_data.decode('utf-8'))

            chat_id = data.get('chat_id')
            worktree_id = data.get('worktree_id')
            agent_name = data.get('agent_name')
            model = data.get('model')

            if not chat_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "chat_id is required"}).encode())
                return

            try:
                import subprocess
                script_path = BASE_DIR / ".mcp" / "map_chat_to_worktree.py"
                cmd = ["python3", str(script_path), chat_id]
                if worktree_id:
                    cmd.append(worktree_id)
                if agent_name:
                    cmd.append(agent_name)
                if model:
                    cmd.append(model)
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    # Parse output (last line is JSON)
                    output_lines = result.stdout.strip().split('\n')
                    try:
                        result_json = json.loads(output_lines[-1])
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result_json, ensure_ascii=False).encode())
                    except:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "success": True,
                            "message": result.stdout.strip()
                        }).encode())
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": result.stderr.strip() or result.stdout.strip()
                    }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode())

        elif path == '/api/triggers':
            # Return trigger queue
            trigger_file = BASE_DIR / '.mcp' / 'trigger_queue.json'
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if trigger_file.exists():
                with open(trigger_file, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(json.dumps({"triggers": [], "last_trigger_id": 0}).encode())
        elif path.startswith('/api/prompt/'):
            # Return pending prompt markdown for an agent (for debugging / manual copy)
            agent_name = path.split('/')[-1]
            prompt_file = BASE_DIR / '.mcp' / 'pending_prompts' / f"{agent_name}.md"

            self.send_response(200)
            self.send_header('Content-type', 'text/markdown; charset=utf-8')
            self.end_headers()

            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b"# No pending prompt\n\nNo tasks assigned.")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/create-trigger':
            # Create trigger file for agent
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            trigger_data = json.loads(post_data.decode('utf-8'))
            
            trigger_file = BASE_DIR / '.mcp' / 'trigger_queue.json'
            prompts_dir = BASE_DIR / '.mcp' / 'pending_prompts'
            prompts_dir.mkdir(exist_ok=True)
            
            # Load existing triggers
            if trigger_file.exists():
                with open(trigger_file, 'r', encoding='utf-8') as f:
                    triggers = json.load(f)
            else:
                triggers = {"triggers": [], "last_trigger_id": 0}
            
            # Add new trigger
            triggers['triggers'].append(trigger_data)
            triggers['last_trigger_id'] = trigger_data['id']
            
            # Save trigger file
            with open(trigger_file, 'w', encoding='utf-8') as f:
                json.dump(triggers, f, indent=2, ensure_ascii=False)
            
            # Create prompt file for agent (auto-send to chat)
            agent_name = trigger_data.get('agent', '')
            if agent_name:
                prompt_file = prompts_dir / f"{agent_name}.md"
                prompt_content = f"""# 🚀 Task Triggered từ Dashboard

**Agent:** {agent_name}
**Task ID:** {trigger_data.get('task_id', 'N/A')}
**Task Title:** {trigger_data.get('task_title', 'N/A')}
**Triggered At:** {trigger_data.get('created_at', 'N/A')}

---

## 📋 Command:

{trigger_data.get('command', 'No command provided')}

---

## ✅ Action Required - LÀM NGAY KHÔNG CHỜ:

🚨 **BẠN PHẢI LÀM VIỆC NGAY, KHÔNG CHỜ THÊM LỆNH!**

1. **ĐỌC NGAY** `.mcp/trigger_queue.json` → tìm trigger có `agent == "{agent_name}"` và `status == "pending"`
2. **ĐỌC NGAY** `.mcp/shared_state.json` → hiểu task {trigger_data.get('task_id', 'N/A')} chi tiết
3. **BẮT ĐẦU NGAY** làm task {trigger_data.get('task_id', 'N/A')} theo đúng vai trò của bạn
4. **CẬP NHẬT NGAY:**
   - trigger_queue.json: status → `processing` (khi bắt đầu) → `completed` (khi xong)
   - shared_state.json: task status → `IN_PROGRESS` → `COMPLETED`

**Hãy trả lời ngay:** "Đã đọc trigger_queue.json và shared_state.json, bắt đầu làm task {trigger_data.get('task_id', 'N/A')} ngay."

---

**Note:** File này sẽ tự động xóa sau khi bạn đọc và bắt đầu làm task.
"""
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(prompt_content)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "success": True,
                        "trigger_id": trigger_data["id"],
                        "prompt_file": f"{agent_name}.md",
                    }
                ).encode()
            )

        elif path == '/api/auto-submit':
            """
            Auto-submit prompt to the currently focused Cursor chat.

            NOTE: This is a best-effort, hacky solution and is implemented
            in .mcp/auto_submit_service.py. Here we just collect payload
            and delegate to that script.
            """
            content_length = int(self.headers.get("Content-Length", "0") or "0")
            post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
            data = json.loads(post_data.decode("utf-8"))

            agent_name = data.get("agent", "")
            chat_id = data.get("chat_id")  # Nhận chat_id từ request

            # Prefer prompt_path from request, then prompt file, then command
            prompt_text = data.get("prompt_path") or data.get("command") or ""
            if agent_name and not prompt_text:
                prompt_file = BASE_DIR / ".mcp" / "pending_prompts" / f"{agent_name}.md"
                if prompt_file.exists():
                    prompt_text = str(prompt_file.resolve())  # Use absolute path

            # Nếu có agent nhưng chưa có chat_id, tìm worktree_id từ shared_state
            if agent_name and not chat_id:
                if STATE_FILE.exists():
                    try:
                        with open(STATE_FILE, 'r', encoding='utf-8') as f:
                            state = json.load(f)
                        agents = state.get('agents', {})
                        if agent_name in agents:
                            worktree_id = agents[agent_name].get('worktree_id')
                            if worktree_id:
                                chat_id = worktree_id  # Dùng worktree_id làm chat_id
                    except:
                        pass

            try:
                script_path = BASE_DIR / ".mcp" / "auto_submit_service.py"
                if not script_path.exists():
                    raise RuntimeError("auto_submit_service.py not found")

                # Call helper script with agent + prompt (or path) + chat_id
                # Import subprocess here to avoid any potential conflicts
                import subprocess as sp
                # Truyền chat_id vào auto_submit_service nếu có
                cmd = ["python3", str(script_path), agent_name or "unknown", prompt_text]
                if chat_id:
                    cmd.append(chat_id)
                result = sp.run(
                    cmd,
                    check=False,  # Don't raise on error
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                # Check if script succeeded
                if result.returncode == 0:
                    output = result.stdout.strip()
                    success = "sent_to_cursor_ok" in output
    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "success": success,
                                "message": output
                                or f"Prompt auto-submitted for {agent_name or 'active chat'}",
                            }
                        ).encode()
                    )
                else:
                    # Script failed but don't treat as HTTP error
                    error_msg = (
                        result.stderr.strip()
                        or result.stdout.strip()
                        or "auto_submit_service failed"
                    )
                    self.send_response(200)  # Still return 200, but with success=false
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "success": False,
                                "message": error_msg,
                            }
                        ).encode()
                    )
            except Exception as e:
                # Handle all exceptions including timeout
                error_type = type(e).__name__
                if "Timeout" in error_type:
                    error_msg = "Auto-submit timeout (took too long)"
                else:
                    error_msg = f"Auto-submit failed: {str(e)}"
                
                self.send_response(200)  # Return 200 with error info
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "success": False,
                            "message": error_msg,
                        }
                    ).encode()
                )

        elif path == '/api/update-task':
            # Update task status
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Load current state
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            else:
                self.send_response(404)
                self.end_headers()
                return
            
            # Update task
            task_id = data.get('task_id')
            status = data.get('status')
            owner = data.get('owner')
            
            if task_id and status:
                for task in state.get('task_board', []):
                    if task['id'] == task_id:
                        task['status'] = status
                        if owner:
                            task['owner'] = owner
                        break
                
                # Update agent status
                if owner:
                    if owner in state.get('agents', {}):
                        if status == 'IN_PROGRESS':
                            state['agents'][owner]['status'] = 'Working'
                            state['agents'][owner]['current_task'] = f"{task_id} - {data.get('title', '')}"
                        elif status == 'COMPLETED':
                            state['agents'][owner]['status'] = 'Idle'
                            state['agents'][owner]['current_task'] = None
                
                # Save updated state với file locking và error handling
                if not self._safe_write_state_file(state):
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": "Failed to save state file after retries"
                    }).encode())
                    return
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": f"Task {task_id} updated to {status}"}).encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing task_id or status"}).encode())
        elif path == '/api/open-agent-window':
            """
            Mở hoặc focus window chat cho một agent cụ thể trên máy local (Cursor).
            Được gọi từ web dashboard khi user bấm nút "Open Window".
            """
            if open_or_focus_agent_window is None:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "open_separate_windows helper not available"
                }).encode())
                return

            content_length = int(self.headers.get('Content-Length', '0') or '0')
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Invalid JSON in request body"
                }).encode())
                return

            agent_name = data.get('agent')
            chat_index = data.get('chat_index', 1)  # Mặc định là chat đầu tiên
            
            if not agent_name:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "agent is required"
                }).encode())
                return

            # Đọc state và tìm chat tương ứng trong detected_chats
            if not STATE_FILE.exists():
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "shared_state.json not found"
                }).encode())
                return

            state = self._safe_read_state_file()
            if not state:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Failed to read shared_state.json"
                }).encode())
                return

            detected_chats = state.get('detected_chats', [])
            target_chat = None

            # Nếu request có worktree_id thì ưu tiên
            requested_worktree = data.get('worktree_id')
            if requested_worktree:
                for chat in detected_chats:
                    if chat.get('worktree_id') == requested_worktree:
                        target_chat = chat
                        break

            # Nếu chưa tìm thấy, ƯU TIÊN lấy từ agents section (worktree_id chính thức)
            # Vì agents section có worktree_id chính thức của agent
            agents = state.get('agents', {})
            if agent_name in agents:
                agent_info = agents[agent_name]
                agent_worktree_id = agent_info.get('worktree_id')
                
                # Tìm chat trong detected_chats có worktree_id khớp với agent's worktree_id
                if agent_worktree_id:
                    for chat in detected_chats:
                        if chat.get('worktree_id') == agent_worktree_id and chat.get('agent_name') == agent_name:
                            target_chat = chat
                            logger.info(f"[api_server] Found chat matching agent's worktree_id: {agent_worktree_id}")
                            break
                
                # Nếu không tìm thấy trong detected_chats, dùng thông tin từ agents section
                if not target_chat:
                    target_chat = {
                        'agent_name': agent_name,
                        'worktree_id': agent_worktree_id,
                        'worktree_path': agent_info.get('worktree_path'),
                        'model': agent_info.get('model'),
                    }
                    logger.info(f"[api_server] Using agent info from agents section: worktree_id={agent_worktree_id}")
            
            # Fallback: Lấy chat đầu tiên của agent_name nếu vẫn chưa có
            if not target_chat:
                for chat in detected_chats:
                    if chat.get('agent_name') == agent_name:
                        target_chat = chat
                        logger.info(f"[api_server] Using first detected chat for agent: {chat.get('worktree_id')}")
                        break

            if not target_chat:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": f"No active chat window found for agent '{agent_name}'"
                }).encode())
                return

            # Đảm bảo có worktree_path (build từ worktree_id nếu không có)
            worktree_id = target_chat.get('worktree_id')
            worktree_path = target_chat.get('worktree_path')
            
            if not worktree_path and worktree_id:
                # Build worktree_path từ worktree_id
                worktree_path = str(Path.home() / '.cursor' / 'worktrees' / 'cheftAi' / worktree_id)
                logger.info(f"[api_server] Built worktree_path from worktree_id: {worktree_path}")
            
            # Nếu vẫn không có worktree_path, thử lấy từ agents section
            if not worktree_path and agent_name:
                agents = state.get('agents', {})
                if agent_name in agents:
                    worktree_path = agents[agent_name].get('worktree_path')
                    if worktree_path:
                        logger.info(f"[api_server] Got worktree_path from agents section: {worktree_path}")

            # Gọi helper để mở/focus window
            try:
                open_or_focus_agent_window(
                    agent_name=target_chat.get('agent_name') or agent_name,
                    model=target_chat.get('model'),
                    worktree_id=worktree_id,
                    worktree_path=worktree_path,
                    chat_index=chat_index,  # Truyền chat_index vào hàm
                )
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "agent": agent_name,
                    "worktree_id": target_chat.get('worktree_id'),
                    "chat_index": chat_index,
                }).encode())
            except Exception as e:
                logger.error(f"[api_server] Error opening agent window: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": f"Failed to open agent window: {str(e)}"
                }).encode())

        elif path == '/api/open-all-worktrees':
            """
            Mở tất cả worktrees có trong detected_chats hoặc agents section.
            """
            try:
                if open_or_focus_agent_window is None:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": "open_separate_windows helper not available"
                    }).encode())
                    return

                # Đọc state
                if not STATE_FILE.exists():
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": "shared_state.json not found"
                    }).encode())
                    return

                state = self._safe_read_state_file()
                if not state:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": "Failed to read shared_state.json"
                    }).encode())
                    return

                # Lấy tất cả worktrees
                detected_chats = state.get('detected_chats', [])
                agents = state.get('agents', {})
                all_worktrees = []
                
                # Thêm từ detected_chats
                for chat in detected_chats:
                    all_worktrees.append({
                        'agent_name': chat.get('agent_name'),
                        'worktree_id': chat.get('worktree_id'),
                        'worktree_path': chat.get('worktree_path'),
                        'model': chat.get('model'),
                    })
                
                # Thêm từ agents section (nếu chưa có)
                for agent_name, agent_info in agents.items():
                    worktree_id = agent_info.get('worktree_id')
                    if worktree_id:
                        exists = any(wt['worktree_id'] == worktree_id for wt in all_worktrees)
                        if not exists:
                            all_worktrees.append({
                                'agent_name': agent_name,
                                'worktree_id': worktree_id,
                                'worktree_path': agent_info.get('worktree_path'),
                                'model': agent_info.get('model'),
                            })

                # Mở từng worktree
                results = []
                import time
                for i, wt in enumerate(all_worktrees[:6], 1):  # Giới hạn 6 worktrees
                    try:
                        open_or_focus_agent_window(
                            agent_name=wt.get('agent_name'),
                            model=wt.get('model'),
                            worktree_id=wt.get('worktree_id'),
                            worktree_path=wt.get('worktree_path'),
                            chat_index=1
                        )
                        results.append({
                            'worktree_id': wt.get('worktree_id'),
                            'agent_name': wt.get('agent_name'),
                            'success': True
                        })
                        # Đợi giữa các lần mở
                        if i < len(all_worktrees[:6]):
                            time.sleep(1)
                    except Exception as e:
                        logger.error(f"[api_server] Error opening worktree {wt.get('worktree_id')}: {e}")
                        results.append({
                            'worktree_id': wt.get('worktree_id'),
                            'agent_name': wt.get('agent_name'),
                            'success': False,
                            'error': str(e)
                        })

                success_count = sum(1 for r in results if r.get('success'))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "total": len(all_worktrees[:6]),
                    "opened": success_count,
                    "results": results
                }).encode())
                
            except Exception as e:
                logger.error(f"[api_server] Error opening all worktrees: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": f"Failed to open all worktrees: {str(e)}"
                }).encode())

        elif path == '/api/map-worktrees':
            # Map worktrees to agents
            content_length = int(self.headers.get('Content-Length', '0') or '0')
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(post_data.decode('utf-8'))

            mapping = data.get('mapping', {})  # {worktree_id: agent_name}

            if not mapping:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "mapping required"}).encode())
                return

            # Load current state
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            else:
                state = {"detected_chats": [], "agents": {}}

            # Update detected_chats with agent_name
            for chat in state.get('detected_chats', []):
                wt_id = chat.get('worktree_id')
                if wt_id in mapping:
                    agent_name = mapping[wt_id]
                    chat['agent_name'] = agent_name
                    # Also get model from agents
                    if agent_name in state.get('agents', {}):
                        chat['model'] = state['agents'][agent_name].get('model')
                        # Update agent with worktree info
                        state['agents'][agent_name]['worktree_id'] = wt_id
                        state['agents'][agent_name]['worktree_path'] = chat.get('worktree_path')

            # Save updated state với file locking và error handling
            if not self._safe_write_state_file(state):
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Failed to save state file after retries"
                }).encode())
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": f"Mapped {len(mapping)} worktrees to agents",
                "detected_chats": state.get('detected_chats', [])
            }).encode())

        elif path == '/api/scan-worktrees':
            # Scan active worktrees and update shared_state.json
            try:
                import subprocess
                result = subprocess.run(
                    ["python3", str(BASE_DIR / ".mcp" / "detect_active_agents.py"), "scan"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Auto-analyze worktrees after scan
                try:
                    analyze_result = subprocess.run(
                        ["python3", str(BASE_DIR / ".mcp" / "worktree_analytics.py"), "analyze"],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                except:
                    pass  # Analytics is optional, don't fail if it errors
                
                # Reload shared_state to return latest data
                if STATE_FILE.exists():
                    with open(STATE_FILE, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "message": result.stdout.strip(),
                        "detected_chats": state.get("detected_chats", []),
                        "chat_count": state.get("chat_count", 0),
                        "analytics_updated": "analytics" in state.get("worktree_analytics", {})
                    }).encode())
                else:
                    raise Exception("shared_state.json not found")
                    
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode())

        elif path == '/api/analyze-worktrees':
            # Analyze worktrees and return analytics
            try:
                import subprocess
                result = subprocess.run(
                    ["python3", str(BASE_DIR / ".mcp" / "worktree_analytics.py"), "analyze"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if STATE_FILE.exists():
                    with open(STATE_FILE, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "message": result.stdout.strip(),
                        "analytics": state.get("worktree_analytics", {}),
                        "agents_with_analytics": {
                            name: agent.get("analytics", {})
                            for name, agent in state.get("agents", {}).items()
                            if "analytics" in agent
                        }
                    }).encode())
                else:
                    raise Exception("shared_state.json not found")
                    
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode())

        elif path == '/api/update-agents':
            # Update agent models from dashboard Setup tab
            content_length = int(self.headers.get('Content-Length', '0') or '0')
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(post_data.decode('utf-8'))

            agent_models = data.get('agent_models', {})

            if not agent_models:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "agent_models required"}).encode())
                return

            # Load current state
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            else:
                state = {"agents": {}}

            # Update agents with model info
            for agent_name, model_name in agent_models.items():
                if agent_name not in state.get('agents', {}):
                    state['agents'][agent_name] = {"status": "Idle", "current_task": None}
                state['agents'][agent_name]['model'] = model_name

            # Update chat_count
            state['chat_count'] = len(state.get('agents', {}))

            # Save updated state với file locking và error handling
            if not self._safe_write_state_file(state):
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Failed to save state file after retries"
                }).encode())
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": f"Updated {len(agent_models)} agent models",
                "agents": state.get('agents', {})
            }).encode())

        elif path == '/api/notify-change':
            # Force trigger monitor service để check tasks mới (nếu monitor đang chạy)
            # Endpoint này để Architect có thể gọi sau khi update shared_state.json
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Monitor service sẽ tự động detect file change, nhưng endpoint này
            # có thể dùng để trigger ngay lập tức nếu cần
            response_data = {
                "success": True,
                "message": "Monitor service will detect changes automatically. If monitor is not running, start it with: python3 .mcp/monitor_service.py"
            }
            self.wfile.write(json.dumps(response_data).encode())

        elif path == '/api/agent-servers':
            # List all agent servers from config
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            config_file = BASE_DIR / '.mcp' / 'agent_servers_config.json'
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self.wfile.write(json.dumps(config, ensure_ascii=False).encode())
                except Exception as e:
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            else:
                self.wfile.write(json.dumps({"error": "agent_servers_config.json not found"}).encode())

        elif path.startswith('/api/agent/') and '/proxy' in path:
            # Proxy request to agent server
            # Format: /api/agent/{agent_name}/proxy/{endpoint}
            parts = path.split('/')
            if len(parts) >= 5:
                agent_name = parts[3]
                endpoint = '/'.join(parts[5:]) if len(parts) > 5 else ''
                
                # Load config
                config_file = BASE_DIR / '.mcp' / 'agent_servers_config.json'
                if not config_file.exists():
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "agent_servers_config.json not found"}).encode())
                    return
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if agent_name not in config:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"Agent {agent_name} not found"}).encode())
                    return
                
                agent_config = config[agent_name]
                agent_port = agent_config.get('port')
                agent_url = f"http://localhost:{agent_port}"
                
                # Proxy request to agent server
                try:
                    import requests
                    content_length = int(self.headers.get('Content-Length', '0') or '0')
                    post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
                    
                    # Build target URL
                    target_url = f"{agent_url}/{endpoint}" if endpoint else agent_url
                    
                    # Forward request
                    method = self.command
                    headers = {
                        'Content-Type': self.headers.get('Content-Type', 'application/json')
                    }
                    
                    if method == 'GET':
                        response = requests.get(target_url, headers=headers, timeout=10)
                    elif method == 'POST':
                        response = requests.post(target_url, data=post_data, headers=headers, timeout=10)
                    else:
                        self.send_response(405)
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": f"Method {method} not supported"}).encode())
                        return
                    
                    # Forward response
                    self.send_response(response.status_code)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response.content)
                    
                except ImportError:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "requests library not installed"}).encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid proxy path"}).encode())

        elif path == '/api/messages':
            # High-level API: gửi message cho một Agent hoặc Chat ID → tạo trigger tương ứng
            content_length = int(self.headers.get('Content-Length', '0') or '0')
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(post_data.decode('utf-8'))

            agent = data.get('agent')
            chat_id = data.get('chat_id') or data.get('worktree_id')
            message = data.get('message')
            task_id = data.get('task_id') or 'ADHOC'
            task_title = data.get('task_title') or f"Ad-hoc message for {agent or chat_id}"

            # Resolve agent from chat_id if needed, hoặc resolve worktree_id từ agent
            worktree_id_from_chat = None
            # Nếu có agent nhưng chưa có worktree_id, tìm từ shared_state
            if agent and not chat_id:
                if STATE_FILE.exists():
                    try:
                        with open(STATE_FILE, 'r', encoding='utf-8') as f:
                            state = json.load(f)
                        agents = state.get('agents', {})
                        if agent in agents:
                            worktree_id_from_chat = agents[agent].get('worktree_id')
                            if worktree_id_from_chat:
                                chat_id = worktree_id_from_chat  # Set chat_id để auto-submit có thể dùng
                    except:
                        pass
            
            if chat_id and not agent:
                # Try to find agent from detected_chats or worktree
                if STATE_FILE.exists():
                    with open(STATE_FILE, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    detected_chats = state.get('detected_chats', [])
                    for chat in detected_chats:
                        if chat.get('worktree_id') == chat_id:
                            agent = chat.get('agent_name')
                            worktree_id_from_chat = chat_id
                            break
                    # If not found in detected_chats, try to find worktree path
                    if not agent:
                        worktree_path = Path.home() / '.cursor' / 'worktrees' / 'cheftAi' / chat_id
                        if worktree_path.exists():
                            worktree_id_from_chat = chat_id
                            marker_file = worktree_path / '.mcp' / 'agent_marker.json'
                            if marker_file.exists():
                                try:
                                    with open(marker_file, 'r', encoding='utf-8') as f:
                                        marker = json.load(f)
                                        agent = marker.get('agent_name', f'Chat_{chat_id[:8]}')
                                except:
                                    agent = f'Chat_{chat_id[:8]}'
                        else:
                            # If chat_id is a UUID, try to find worktree by searching in files
                            if len(chat_id) > 10:  # Likely a UUID
                                worktrees_base = Path.home() / '.cursor' / 'worktrees' / 'cheftAi'
                                if worktrees_base.exists():
                                    for wt_dir in worktrees_base.iterdir():
                                        if wt_dir.is_dir():
                                            # Check config files for UUID
                                            config_files = [
                                                wt_dir / '.cursor' / 'chat.json',
                                                wt_dir / '.cursor' / 'session.json',
                                                wt_dir / '.mcp' / 'agent_marker.json',
                                            ]
                                            for config_file in config_files:
                                                if config_file.exists():
                                                    try:
                                                        content = config_file.read_text(encoding='utf-8', errors='ignore')
                                                        if chat_id in content or chat_id[:8] in content:
                                                            worktree_id_from_chat = wt_dir.name
                                                            marker_file = wt_dir / '.mcp' / 'agent_marker.json'
                                                            if marker_file.exists():
                                                                try:
                                                                    with open(marker_file, 'r', encoding='utf-8') as f:
                                                                        marker = json.load(f)
                                                                        agent = marker.get('agent_name', f'Chat_{chat_id[:8]}')
                                                                except:
                                                                    agent = f'Chat_{chat_id[:8]}'
                                                            break
                                                    except:
                                                        pass
                                            if worktree_id_from_chat:
                                                break

            if (not agent and not chat_id) or not message:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "agent or chat_id, and message are required"}).encode())
                return

            # Build a simple command that Architect/Agent có thể hiểu
            agent_label = agent or f"Chat {chat_id[:8] if chat_id else 'Unknown'}"
            command = f"""Bạn là Agent {agent_label} cho dự án CheftAi Android + Auto AI Messaging Web.

Yêu cầu từ dashboard web:
{message}

- Đọc .mcp/shared_state.json để hiểu context và task_board.
- Nếu phù hợp với một task cụ thể thì làm task đó và cập nhật shared_state.json.
- Nếu là yêu cầu mới, hãy đề xuất/cập nhật task_board cho phù hợp.
"""

            trigger_id = int(data.get('id') or data.get('trigger_id') or 0) or int(__import__("time").time() * 1000)

            trigger_payload = {
                "id": trigger_id,
                "agent": agent or f"Chat_{chat_id[:8] if chat_id else 'Unknown'}",
                "chat_id": chat_id,
                "worktree_id": worktree_id_from_chat or chat_id,
                "task_id": task_id,
                "task_title": task_title,
                "command": command,
                "created_at": data.get("created_at") or __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "status": "pending",
            }

            # Reuse create-trigger logic by faking a request
            trigger_file = BASE_DIR / '.mcp' / 'trigger_queue.json'
            prompts_dir = BASE_DIR / '.mcp' / 'pending_prompts'
            prompts_dir.mkdir(exist_ok=True)

            if trigger_file.exists():
                with open(trigger_file, 'r', encoding='utf-8') as f:
                    triggers = json.load(f)
            else:
                triggers = {"triggers": [], "last_trigger_id": 0}

            triggers['triggers'].append(trigger_payload)
            triggers['last_trigger_id'] = trigger_payload['id']

            with open(trigger_file, 'w', encoding='utf-8') as f:
                json.dump(triggers, f, indent=2, ensure_ascii=False)

            # Use chat_id as filename if no agent, otherwise use agent name
            prompt_filename = f"{agent}.md" if agent else f"chat_{chat_id[:8] if chat_id else 'unknown'}.md"
            prompt_file = prompts_dir / prompt_filename
            prompt_content = f"""# 🚀 Message từ Web Dashboard

**Agent:** {agent_label}
**Chat ID:** {chat_id or 'N/A'}
**Task ID:** {task_id}
**Task Title:** {task_title}
**Triggered At:** {trigger_payload['created_at']}

---

## 📋 Command:

{command}

---

## ✅ Action Required:

1. Đọc shared_state.json để hiểu context.
2. Xử lý yêu cầu trên (làm task tương ứng hoặc cập nhật task_board).
3. Update trigger_queue.json (status) và shared_state.json khi hoàn thành.
"""
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt_content)

            # Auto-map chat_id to worktree if not found
            if chat_id and not worktree_id_from_chat and platform.system() == 'Darwin':
                try:
                    import subprocess as sp
                    map_script = BASE_DIR / ".mcp" / "map_chat_to_worktree.py"
                    if map_script.exists():
                        # Try to map chat_id to worktree
                        map_result = sp.run(
                            ["python3", str(map_script), chat_id],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if map_result.returncode == 0:
                            # Re-read shared_state to get updated worktree info
                            if STATE_FILE.exists():
                                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                                    state = json.load(f)
                                detected_chats = state.get('detected_chats', [])
                                for chat in detected_chats:
                                    if chat.get('chat_id') == chat_id or chat.get('worktree_id') == chat_id:
                                        worktree_id_from_chat = chat.get('worktree_id')
                                        if not agent:
                                            agent = chat.get('agent_name')
                                        break
                except Exception:
                    pass  # Ignore mapping errors, continue with auto-submit

            # Auto-submit if chat_id is provided OR if agent is provided (có worktree_id)
            auto_submit_result = None
            # Nếu có chat_id hoặc có agent với worktree_id thì auto-submit
            should_auto_submit = (chat_id or (agent and worktree_id_from_chat)) and platform.system() == 'Darwin'
            if should_auto_submit:
                try:
                    script_path = BASE_DIR / ".mcp" / "auto_submit_service.py"
                    if script_path.exists():
                        import subprocess as sp
                        # Use worktree_id if found, otherwise use chat_id
                        submit_target = worktree_id_from_chat or chat_id
                        agent_name_for_submit = agent or f"chat_{submit_target[:8] if len(submit_target) > 8 else submit_target}"
                        # Truyền chat_id vào auto_submit_service để tìm đúng window
                        result = sp.run(
                            ["python3", str(script_path), agent_name_for_submit, str(prompt_file.resolve()), chat_id],
                            check=False,
                            capture_output=True,
                            text=True,
                            timeout=15
                        )
                        auto_submit_result = {
                            "success": result.returncode == 0 and "sent_to_cursor_ok" in result.stdout,
                            "message": result.stdout.strip() or result.stderr.strip()
                        }
                except Exception as e:
                    auto_submit_result = {"success": False, "message": str(e)}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_data = {
                        "success": True,
                        "trigger_id": trigger_payload["id"],
                "prompt_file": prompt_filename,
                "chat_id": chat_id or worktree_id_from_chat,
            }
            # Luôn trả về auto_submit result (có thể là None nếu không thực hiện)
            # Để frontend biết đã thử auto-submit chưa
            if auto_submit_result is not None:
                response_data["auto_submit"] = auto_submit_result
            else:
                # Nếu không có auto_submit_result, có nghĩa là không thực hiện auto-submit
                # (không phải macOS, không có chat_id, hoặc không có agent)
                response_data["auto_submit"] = {
                    "success": False,
                    "message": "auto_submit_skipped",
                    "skipped": True
                    }
            self.wfile.write(json.dumps(response_data).encode())

        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    
    server = HTTPServer(("", PORT), APIHandler)
    logger.info(f"[api_server] API Server running on http://localhost:{PORT}")
    logger.info(f"[api_server] Endpoints:")
    logger.info(f"   GET  /api/state - Get shared_state.json (with auto-sync)")
    logger.info(f"   GET  /api/triggers      - Get trigger_queue.json")
    logger.info(f"   GET  /api/prompt/<agent> - Get pending prompt markdown")
    logger.info(f"   GET  /api/agents        - Get agents block only")
    logger.info(f"   GET  /api/task_board    - Get task_board only")
    logger.info(f"   POST /api/create-trigger - Create new trigger + prompt file")
    logger.info(f"   POST /api/messages      - High-level endpoint: send message to an Agent (wraps create-trigger)")
    logger.info(f"   POST /api/auto-submit   - Auto-submit prompt to Cursor chat (macOS only)")
    logger.info(f"   POST /api/update-task   - Update task status")
    logger.info(f"   POST /api/execute-command - Execute terminal commands/scripts from web (whitelist only)")
    print(f"\n🚀 API Server running on http://localhost:{PORT}")
    print(f"📝 Logs: {LOG_FILE}")
    print(f"Press Ctrl+C to stop...\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n✅ Server stopped")
        print("\n✅ Server stopped")
        server.shutdown()

