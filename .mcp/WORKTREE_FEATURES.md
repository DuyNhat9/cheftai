# Worktree Features - Tận Dụng Tối Đa Worktree

## 📋 Tổng Quan

Hệ thống đã được mở rộng để tận dụng tối đa thông tin từ Git worktrees (mỗi Cursor chat session sử dụng một worktree riêng).

## 🎯 Các Tính Năng Hiện Có

### 1. **Auto-Detect Active Agents** ✅
- **Script**: `detect_active_agents.py`
- **Chức năng**: 
  - Detect các worktrees đang active (modified trong 120 phút hoặc top 5 mới nhất)
  - Đọc agent marker files để lấy model realtime
  - Tự động tạo marker files cho worktrees đã được map
  - Preserve mappings khi rescan

**Usage:**
```bash
python3 .mcp/detect_active_agents.py scan
python3 .mcp/detect_active_agents.py mark "Architect" "Sonnet 4.5"
```

### 2. **Worktree Analytics** ✅ (MỚI)
- **Script**: `worktree_analytics.py`
- **Chức năng**:
  - Track file changes per agent (files đang edit)
  - Git status tracking (uncommitted changes, commits)
  - Activity stats (số file edit, số dòng code thay đổi)
  - Activity heatmap (commits per day trong 7 ngày)
  - Recent commits tracking (commits trong 24h)

**Usage:**
```bash
python3 .mcp/worktree_analytics.py analyze
```

**Thông tin được track:**
- `git_status`: Uncommitted changes, modified/new/deleted files
- `file_stats`: Total files, lines added/deleted
- `recent_commits`: Commits trong 24h với hash, author, date, message
- `activity_heatmap`: Số commits per day trong 7 ngày

### 3. **Dashboard Integration** ✅
- **API Endpoints**:
  - `POST /api/scan-worktrees`: Scan + auto-analyze worktrees
  - `POST /api/analyze-worktrees`: Analyze worktrees riêng
  
- **Dashboard UI**:
  - Tab "Monitor": Hiển thị worktrees với analytics (file changes, commits, etc.)
  - Tab "Setup Agents": Nút "Scan" và "Analyze" riêng
  - Real-time updates sau khi scan/analyze

## 🚀 Các Tính Năng Có Thể Mở Rộng Thêm

### 1. **Task Completion Detection** 🔄
- Detect khi agent hoàn thành task dựa trên file changes
- Pattern matching: Map task_id → file patterns
- Auto-update task status trong shared_state.json

**Ví dụ:**
```python
task_patterns = {
    "T100": ["api_server.py", "*.py"],
    "T101": ["dashboard*.html", "*.md"]
}
completions = detect_task_completion(analytics, task_patterns)
```

### 2. **Cross-Worktree File Sync** 💡
- Sync file changes giữa worktrees
- Detect conflicts khi nhiều agents edit cùng file
- Auto-merge hoặc notify conflicts

### 3. **Activity Heatmap Visualization** 💡
- Visualize activity theo thời gian (ngày/giờ)
- Show activity peaks để optimize agent scheduling
- Track productivity metrics

### 4. **Resource Usage Tracking** 💡
- Track CPU/memory usage per worktree (nếu có thể)
- Track file count, lines of code per agent
- Generate productivity reports

### 5. **Chat History Tracking** 💡
- Lưu chat history của mỗi agent trong worktree
- Search chat history để tìm context
- Share chat context giữa agents

### 6. **Auto-Switch Worktree** 💡
- Khi trigger agent, tự động focus vào worktree của agent đó trong Cursor
- Auto-open files liên quan đến task
- Context-aware navigation

### 7. **Git Commit Auto-Tracking** 💡
- Auto-detect commits từ mỗi worktree
- Link commits với tasks trong shared_state.json
- Generate commit history per agent/task

## 📊 Data Structure

### `shared_state.json` Structure:

```json
{
  "detected_chats": [
    {
      "worktree_id": "qnu",
      "worktree_path": "/Users/.../qnu",
      "agent_name": "Architect",
      "model": "Sonnet 4.5",
      "analytics": {
        "git_status": {
          "has_changes": true,
          "modified_files": ["file1.py", "file2.py"],
          "new_files": ["file3.py"],
          "total_changes": 3
        },
        "file_stats": {
          "modified_files": 2,
          "new_files": 1,
          "lines_added": 345,
          "lines_deleted": 0
        },
        "recent_commits": [...],
        "activity_heatmap": {"2025-12-18": 4, ...}
      }
    }
  ],
  "agents": {
    "Architect": {
      "analytics": {
        "has_uncommitted_changes": true,
        "modified_files": 2,
        "lines_added": 345,
        "recent_commits_count": 4
      }
    }
  },
  "worktree_analytics": {
    "last_updated": "2025-12-18T23:43:49",
    "analytics": {...}
  }
}
```

## 🔧 Integration Flow

1. **Scan Worktrees**:
   ```
   Dashboard → POST /api/scan-worktrees
   → detect_active_agents.py scan
   → worktree_analytics.py analyze (auto)
   → Update shared_state.json
   → Reload dashboard
   ```

2. **Analyze Worktrees**:
   ```
   Dashboard → POST /api/analyze-worktrees
   → worktree_analytics.py analyze
   → Update shared_state.json
   → Display analytics in dashboard
   ```

## 📝 Notes

- Analytics được update tự động khi scan worktrees
- Có thể analyze riêng bằng nút "Analyze Worktrees"
- Analytics data được cache trong shared_state.json
- Git commands timeout sau 5-15 giây để tránh hang

## 🎯 Best Practices

1. **Scan thường xuyên**: Scan worktrees mỗi khi cần check agent status
2. **Analyze khi cần**: Analyze khi cần detailed stats về file changes
3. **Monitor analytics**: Check analytics trong Monitor tab để track progress
4. **Auto-mark agents**: Agents tự động được mark khi scan (nếu đã map trước đó)

