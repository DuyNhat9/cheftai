# Flow Đồng Bộ Giữa Các Agents

## 📋 Tổng Quan

Các agents hoạt động trong **separate windows** nhưng **đồng bộ với nhau** qua file `shared_state.json` và API server.

---

## 🔄 Flow Đồng Bộ Chính

### 1. **Shared State File (`shared_state.json`)**

File này là **single source of truth** cho tất cả agents:

```json
{
  "agents": {
    "Architect": {
      "status": "Working",
      "current_task": "A200 - ...",
      "worktree_id": "qnu"
    },
    "UI_UX_Dev": {
      "status": "Working", 
      "current_task": "U200 - ...",
      "worktree_id": "cqd"
    }
  },
  "task_board": [
    {
      "id": "U200",
      "owner": "UI_UX_Dev",
      "status": "IN_PROGRESS"
    }
  ],
  "detected_chats": [
    {
      "worktree_id": "cqd",
      "agent_name": "UI_UX_Dev",
      "modified_minutes_ago": 5.2
    }
  ]
}
```

### 2. **API Server (`api_server.py`)**

API server đóng vai trò **coordinator**:
- Serve `shared_state.json` cho dashboard và agents
- Auto-sync agent status với tasks
- Handle triggers và messages

---

## 🔗 Flow Chi Tiết

### **Flow 1: Dashboard → Agent (Trigger Task)**

```
1. User click "Start" trên dashboard
   ↓
2. Dashboard gọi POST /api/triggers
   ↓
3. API Server:
   - Tạo trigger entry trong trigger_queue.json
   - Tạo prompt file trong .mcp/pending_prompts/{agent_name}.md
   ↓
4. API Server gọi POST /api/auto-submit
   ↓
5. auto_submit_service.py:
   - Tìm window của agent (worktree_id)
   - Focus vào window đó
   - Paste prompt vào chat input
   - Submit message
   ↓
6. Agent nhận được prompt trong chat window riêng của mình
   ↓
7. Agent đọc shared_state.json để hiểu context
   ↓
8. Agent làm task và update shared_state.json:
   - Update task status: IN_PROGRESS → COMPLETED
   - Update agent status: Idle → Working → Idle
```

### **Flow 2: Agent → Agent (Collaboration)**

```
1. Agent A hoàn thành task T001
   ↓
2. Agent A update shared_state.json:
   - task_board: T001.status = "COMPLETED"
   - agents: AgentA.status = "Idle"
   ↓
3. Agent B đọc shared_state.json
   ↓
4. Agent B thấy T001 đã COMPLETED
   ↓
5. Agent B bắt đầu task T002 (dependency của T001)
   ↓
6. Agent B update shared_state.json:
   - task_board: T002.status = "IN_PROGRESS"
   - agents: AgentB.status = "Working"
```

### **Flow 3: Auto-Sync Agent Status**

API Server tự động sync agent status mỗi khi có request:

```python
def _sync_agent_status_with_tasks(state):
    # Nếu agent "Working" nhưng không có task IN_PROGRESS → set "Idle"
    if agent.status == "Working" and no_in_progress_tasks:
        agent.status = "Idle"
    
    # Nếu agent "Working" nhưng chat không active (>30 phút) → set "Idle"
    if agent.status == "Working" and chat_inactive:
        agent.status = "Idle"
    
    # Nếu agent "Idle" nhưng có task IN_PROGRESS VÀ chat active → set "Working"
    if agent.status == "Idle" and has_in_progress_task and chat_active:
        agent.status = "Working"
```

---

## ✅ Đồng Bộ Hoạt Động Như Thế Nào?

### **1. File-Based Synchronization**

- Tất cả agents đọc từ cùng một file: `shared_state.json`
- Khi agent update, file được ghi lại
- Agents khác đọc lại file để có thông tin mới nhất

### **2. API Server Coordination**

- API server serve `shared_state.json` qua HTTP
- Dashboard và agents đều gọi API để đọc/update
- API server auto-sync status mỗi request

### **3. Real-time Updates**

- Dashboard poll API mỗi vài giây để refresh
- Agents đọc `shared_state.json` trước khi làm task
- `detected_chats` được update khi scan worktrees

---

## 🔍 Các Điểm Đồng Bộ

### **1. Task Board**
- Tất cả agents đọc `task_board` để biết tasks
- Khi agent complete task → update `task_board`
- Agents khác thấy task đã COMPLETED → có thể làm task tiếp theo

### **2. Agent Status**
- `agents.{agent_name}.status`: "Idle" hoặc "Working"
- `agents.{agent_name}.current_task`: Task đang làm
- Auto-sync với `task_board` và `detected_chats`

### **3. Detected Chats**
- Track chat activity của mỗi agent
- `modified_minutes_ago`: Thời gian chat cuối cùng
- Dùng để verify agent đang active

---

## ⚠️ Limitations Hiện Tại

### **1. Không có Real-time Push**
- Agents phải **poll** `shared_state.json` để biết updates
- Không có notification khi có thay đổi

### **2. File Conflicts**
- Nếu 2 agents update cùng lúc → có thể conflict
- Cần file locking hoặc atomic writes

### **3. Chat Messages Không Đồng Bộ**
- Mỗi window có chat history riêng
- Không tự động load messages từ agents khác
- Cần manually scroll hoặc trigger load

---

## 💡 Cách Cải Thiện Đồng Bộ

### **1. WebSocket cho Real-time Updates**
```python
# API Server broadcast updates qua WebSocket
# Dashboard và agents subscribe để nhận updates
```

### **2. File Locking**
```python
# Dùng file lock khi write shared_state.json
# Tránh conflicts khi nhiều agents update cùng lúc
```

### **3. Chat History Sync**
```python
# Lưu chat history vào shared_state.json
# Agents có thể đọc messages từ agents khác
```

---

## 📊 Summary

**✅ CÓ ĐỒNG BỘ:**
- Task status được sync qua `task_board`
- Agent status được sync qua `agents` section
- API server auto-sync status với tasks và chat activity

**❌ KHÔNG ĐỒNG BỘ:**
- Chat messages không tự động load giữa các windows
- Không có real-time push notifications
- File conflicts có thể xảy ra nếu nhiều agents update cùng lúc

**💡 KẾT LUẬN:**
Các windows riêng **CÓ hoạt động đồng bộ** qua `shared_state.json`, nhưng **không có real-time chat sync**. Agents có thể collaborate qua task board và shared state, nhưng chat messages chỉ hiển thị trong window riêng của mỗi agent.

