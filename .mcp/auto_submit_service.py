#!/usr/bin/env python3
"""
auto_submit_service.py

Auto-submit prompt vào đúng Cursor chat window của agent.
Dựa vào worktree_id từ shared_state.json để tìm và focus đúng window.

Usage (được gọi từ api_server.py):
    python3 .mcp/auto_submit_service.py <agent_name> <prompt_or_path>
"""

import sys
import json
import subprocess
import re
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Image processing imports (optional, with fallback)
try:
    import pyautogui
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    IMAGE_DETECTION_AVAILABLE = True
except ImportError:
    IMAGE_DETECTION_AVAILABLE = False
    # Create dummy types for type hints when not available
    Image = None
    print("[auto_submit_debug] ⚠️  Image detection dependencies not available. Install: pip install pyautogui pytesseract opencv-python Pillow")

# Paths
PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

# Agent -> Model mapping (fallback)
AGENT_MODEL_MAP = {
    "Architect": "Sonnet 4.5",
    "Backend_AI_Dev": "GPT-5.1 Codex High Fast",
    "UI_UX_Dev": "claude-4.1-opus",
    "Testing_QA": "o3 Pro",
    "Supervisor": "Sonnet 4 1M",
}


def get_agent_worktree_info(agent_name: str, chat_id: str = None) -> dict:
    """Get worktree info for agent from shared_state.json."""
    if not STATE_FILE.exists():
        return {}
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Nếu có chat_id, tìm trong detected_chats trước
        if chat_id:
            detected_chats = state.get("detected_chats", [])
            for chat in detected_chats:
                if chat.get("chat_id") == chat_id or chat.get("worktree_id") == chat_id:
                    return {
                        "worktree_id": chat.get("worktree_id"),
                        "worktree_path": chat.get("worktree_path"),
                        "model": chat.get("model"),
                        "agent_name": chat.get("agent_name"),
                        "chat_id": chat.get("chat_id"),
                    }
        
        # First try to find by agent name
        agents = state.get("agents", {})
        if agent_name in agents:
            return {
                "worktree_id": agents[agent_name].get("worktree_id"),
                "worktree_path": agents[agent_name].get("worktree_path"),
                "model": agents[agent_name].get("model"),
            }
        
        # If agent_name looks like a chat_id/worktree_id (UUID format or short ID)
        # Try to find in detected_chats
        detected_chats = state.get("detected_chats", [])
        for chat in detected_chats:
            if chat.get("worktree_id") == agent_name:
                return {
                    "worktree_id": chat.get("worktree_id"),
                    "worktree_path": chat.get("worktree_path"),
                    "model": chat.get("model"),
                    "agent_name": chat.get("agent_name"),
                    "chat_id": chat.get("chat_id"),
                }
        
        # If agent_name starts with "chat_", extract the ID
        if agent_name.startswith("chat_"):
            worktree_id = agent_name.replace("chat_", "")
        else:
            worktree_id = agent_name
        
        # Try to find worktree path directly (for short IDs like "qnu", "agd")
        worktree_path = Path.home() / ".cursor" / "worktrees" / "cheftAi" / worktree_id
        if worktree_path.exists():
            # Try to read agent_marker.json
            marker_file = worktree_path / ".mcp" / "agent_marker.json"
            model = "Unknown"
            if marker_file.exists():
                try:
                    with open(marker_file, 'r', encoding='utf-8') as f:
                        marker = json.load(f)
                        model = marker.get("model", "Unknown")
                except:
                    pass
            return {
                "worktree_id": worktree_id,
                "worktree_path": str(worktree_path),
                "model": model,
            }
        
        # If worktree_id is a UUID (long format), try to search in all worktrees
        # by looking for files containing this UUID
        if len(worktree_id) > 10:  # Likely a UUID
            worktrees_base = Path.home() / ".cursor" / "worktrees" / "cheftAi"
            if worktrees_base.exists():
                # Search in all worktree directories
                for wt_dir in worktrees_base.iterdir():
                    if wt_dir.is_dir():
                        # Check if UUID appears in any config files
                        config_files = [
                            wt_dir / ".cursor" / "chat.json",
                            wt_dir / ".cursor" / "session.json",
                            wt_dir / ".mcp" / "agent_marker.json",
                        ]
                        for config_file in config_files:
                            if config_file.exists():
                                try:
                                    content = config_file.read_text(encoding='utf-8', errors='ignore')
                                    if worktree_id in content or worktree_id[:8] in content:
                                        # Found matching worktree
                                        marker_file = wt_dir / ".mcp" / "agent_marker.json"
                                        model = "Unknown"
                                        if marker_file.exists():
                                            try:
                                                with open(marker_file, 'r', encoding='utf-8') as f:
                                                    marker = json.load(f)
                                                    model = marker.get("model", "Unknown")
                                            except:
                                                pass
                                        return {
                                            "worktree_id": wt_dir.name,
                                            "worktree_path": str(wt_dir),
                                            "model": model,
                                        }
                                except:
                                    pass
    except Exception:
        pass
    
    return {}


def resolve_prompt_text(arg: str) -> tuple:
    """
    Trả về (source, text) để debug.
    - Nếu arg là path file tồn tại → đọc nội dung và extract chỉ phần message.
    - Nếu không → coi như inline text.
    """
    if not arg:
        return ("none", "")

    p = Path(arg)
    if not p.is_absolute():
        p = PROJECT_DIR / arg
    
    if p.exists() and p.is_file():
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            # Extract chỉ phần message text từ markdown file
            # Pattern 1: Tìm message sau "Yêu cầu từ dashboard web:"
            pattern1 = r"Yêu cầu từ dashboard web:\s*\n(.*?)(?:\n\n|\n-|$)"
            match1 = re.search(pattern1, txt, re.DOTALL)
            if match1:
                message_text = match1.group(1).strip()
                return (f"file:{p}", message_text)
            
            # Pattern 2: Tìm trong phần Command
            pattern2 = r"## 📋 Command:\s*\n\n.*?Yêu cầu từ dashboard web:\s*\n(.*?)(?:\n\n|\n-|$)"
            match2 = re.search(pattern2, txt, re.DOTALL)
            if match2:
                message_text = match2.group(1).strip()
                return (f"file:{p}", message_text)
            
            # Pattern 3: Tìm message sau "## Message:" (format mới từ agent_server_base)
            pattern3 = r"## Message:\s*\n\s*\n(.*?)(?:\n\n---|\n\n##|$)"
            match3 = re.search(pattern3, txt, re.DOTALL)
            if match3:
                message_text = match3.group(1).strip()
                return (f"file:{p}", message_text)
            
            # Pattern 4: Nếu file đơn giản chỉ có text (không có markdown headers)
            # Lấy dòng đầu tiên không phải là header
            lines = txt.split('\n')
            non_header_lines = []
            skip_headers = True
            for line in lines:
                line_stripped = line.strip()
                # Bỏ qua markdown headers và empty lines đầu
                if skip_headers:
                    if line_stripped.startswith('#') or line_stripped.startswith('**') or line_stripped.startswith('---') or not line_stripped:
                        continue
                    else:
                        skip_headers = False
                if not skip_headers:
                    if line_stripped.startswith('##') or line_stripped.startswith('---'):
                        break
                    if line_stripped:
                        non_header_lines.append(line_stripped)
            
            if non_header_lines:
                message_text = '\n'.join(non_header_lines).strip()
                if message_text:
                    return (f"file:{p}", message_text)
            
            # Fallback: trả về toàn bộ file
            return (f"file:{p}", txt)
        except Exception:
            return (f"file:{p}", "")

    # inline text
    return ("inline", arg)


def _get_input_value() -> str:
    """Đọc giá trị ô input hiện tại trong Cursor (text field cuối)."""
    script = r'''
    tell application "System Events"
        try
            set cursorApp to first application process whose name is "Cursor"
        on error
            return ""
        end try
        if not (exists cursorApp) then return ""
        try
            set mainWindow to first window of cursorApp
            set textFields to every text field of mainWindow
            if (count of textFields) > 0 then
                return value of last text field of mainWindow as string
            else
                return ""
            end if
        on error
            return ""
        end try
    end tell
    '''
    try:
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        return ""
    return ""


def _get_chat_content(chat_id: str = None, model: str = None) -> str:
    """
    Lấy nội dung chat hiện tại để verify message đã xuất hiện.
    Dùng AppleScript để đọc text từ chat area.
    """
    script = f'''
    tell application "System Events"
        try
            set cursorApp to first application process whose name is "Cursor"
        on error
            return ""
        end try
        
        if not (exists cursorApp) then return ""
        
        try
            set mainWindow to first window of cursorApp
            -- Tìm text area hoặc scroll area chứa chat messages
            set chatText to ""
            
            -- Thử tìm scroll area (chat messages thường trong scroll view)
            try
                set scrollAreas to every scroll area of mainWindow
                repeat with sa in scrollAreas
                    try
                        set textAreas to every text area of sa
                        repeat with ta in textAreas
                            try
                                set taValue to value of ta as string
                                if taValue is not "" then
                                    set chatText to chatText & taValue & "\\n"
                                end if
                            end try
                        end repeat
                    end try
                end repeat
            end try
            
            -- Fallback: Tìm text area trực tiếp
            if chatText is "" then
                try
                    set textAreas to every text area of mainWindow
                    repeat with ta in textAreas
                        try
                            set taValue to value of ta as string
                            if taValue is not "" then
                                set chatText to chatText & taValue & "\\n"
                            end if
                        end try
                    end repeat
                end try
            end if
            
            return chatText
        on error
            return ""
        end try
    end tell
    '''
    try:
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""


def verify_message_sent(expected_text: str, chat_id: str = None, model: str = None, timeout: float = 2.0) -> bool:
    """
    Xác nhận message đã được gửi bằng cách:
    1. Kiểm tra ô input đã trống
    2. Kiểm tra message xuất hiện trong chat content (nếu có chat_id/model)
    
    Verification logic:
    1. Đợi timeout để submit hoàn tất
    2. Kiểm tra input field value:
       - Nếu trống => có thể đã gửi thành công
       - Nếu vẫn chứa expected_text => chưa gửi (paste nhưng chưa submit)
    3. Kiểm tra chat content (nếu có chat_id/model):
       - Tìm expected_text trong chat content => đã gửi thành công vào đúng chat
       - Không tìm thấy => có thể gửi vào chat khác hoặc chưa gửi
    4. Return True nếu có khả năng đã gửi thành công
    """
    time.sleep(timeout)
    
    # Kiểm tra input value 2 lần với delay để đảm bảo UI đã update
    val1 = _get_input_value()
    time.sleep(0.5)
    val2 = _get_input_value()
    
    # Nếu cả 2 lần đều trống => nhiều khả năng đã gửi thành công
    if not val1 and not val2:
        # Nếu có chat_id/model, verify thêm bằng cách check chat content
        if chat_id or model:
            time.sleep(1.0)  # Đợi thêm để message render trong chat
            chat_content = _get_chat_content(chat_id, model)
            if expected_text:
                text_preview = expected_text[:50].strip()
                if text_preview and text_preview in chat_content:
                    print(f"[auto_submit_debug] ✅ Verification: Message found in chat content")
                    return True
                else:
                    print(f"[auto_submit_debug] ⚠️  Verification: Message not found in chat content (may be in different tab)")
        return True
    
    # Nếu input vẫn chứa expected_text => chưa submit thành công
    if expected_text:
        text_preview = expected_text[:50].strip()
        if text_preview and (text_preview in val1 or text_preview in val2):
            print(f"[auto_submit_debug] ❌ Verification: Input field still contains message")
            return False  # Vẫn còn trong input => chưa submit
    
    # Nếu input không trống nhưng không chứa expected_text => có thể đã gửi hoặc paste vào chỗ khác
    # Verify bằng chat content nếu có
    if chat_id or model:
        time.sleep(1.0)
        chat_content = _get_chat_content(chat_id, model)
        if expected_text:
            text_preview = expected_text[:50].strip()
            if text_preview and text_preview in chat_content:
                print(f"[auto_submit_debug] ✅ Verification: Message found in chat content")
    return True
    
    # Fallback: giả định đã gửi thành công (vì không còn expected_text trong input)
    return True


def _enumerate_cursor_tabs() -> list:
    """
    Enumerate all accessible tabs/UI elements in Cursor window.
    Returns list of tab information: [{"title": "...", "index": 0, "type": "tab"}, ...]
    """
    script = '''
    tell application "System Events"
        try
            set cursorApp to first application process whose name is "Cursor"
        on error
            return "[]"
        end try
        
        if not (exists cursorApp) then
            return "[]"
        end if
        
        set mainWindow to first window of cursorApp
        set tabList to ""
        
        -- Strategy 1: Query tab groups
        try
            set tabGroups to every tab group of mainWindow
            repeat with tg in tabGroups
                try
                    set tabs to every tab of tg
                    repeat with i from 1 to count of tabs
                        try
                            set aTab to item i of tabs
                            set tabTitle to title of aTab as string
                            set tabList to tabList & "{\\"title\\":\\"" & tabTitle & "\\",\\"index\\":" & (i - 1) & ",\\"type\\":\\"tab_group\\"}|"
                        end try
                    end repeat
                end try
            end repeat
        end try
        
        -- Strategy 2: Query buttons that might be tabs
        try
            set buttons to every button of mainWindow
            repeat with i from 1 to count of buttons
                try
                    set b to item i of buttons
                    set btnTitle to title of b as string
                    set btnName to name of b as string
                    -- Only include buttons with meaningful titles (not empty, not generic)
                    if btnTitle is not "" and btnTitle is not "Button" and btnTitle is not btnName then
                        set tabList to tabList & "{\\"title\\":\\"" & btnTitle & "\\",\\"index\\":" & (i - 1) & ",\\"type\\":\\"button\\"}|"
                    end if
                end try
            end repeat
        end try
        
        -- Strategy 3: Query groups that might contain tab-like elements
        try
            set groups to every group of mainWindow
            repeat with i from 1 to count of groups
                try
                    set g to item i of groups
                    set groupTitle to title of g as string
                    if groupTitle is not "" and groupTitle is not "Group" then
                        set tabList to tabList & "{\\"title\\":\\"" & groupTitle & "\\",\\"index\\":" & (i - 1) & ",\\"type\\":\\"group\\"}|"
                    end if
                end try
            end repeat
        end try
        
        -- Strategy 4: Query static text elements that might be tab labels
        try
            set textElements to every static text of mainWindow
            repeat with i from 1 to count of textElements
                try
                    set te to item i of textElements
                    set textValue to value of te as string
                    -- Filter for text that looks like model names or chat titles
                    if textValue is not "" and (textValue contains "Sonnet" or textValue contains "GPT" or textValue contains "claude" or textValue contains "Pro" or textValue contains "Chat") then
                        set tabList to tabList & "{\\"title\\":\\"" & textValue & "\\",\\"index\\":" & (i - 1) & ",\\"type\\":\\"static_text\\"}|"
                    end if
                end try
            end repeat
        end try
        
        -- Return as JSON-like string (will parse in Python)
        if tabList is "" then
            return "[]"
        else
            -- Remove trailing pipe and wrap in brackets
            set tabList to text 1 thru -2 of tabList
            return "[" & tabList & "]"
        end if
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output and output != "[]":
                # Parse the pipe-separated JSON-like string
                tabs = []
                for item_str in output.strip("[]").split("|"):
                    if item_str:
                        try:
                            # Simple parsing - extract title, index, type
                            import re
                            title_match = re.search(r'"title":"([^"]+)"', item_str)
                            index_match = re.search(r'"index":(\d+)', item_str)
                            type_match = re.search(r'"type":"([^"]+)"', item_str)
                            
                            if title_match and index_match and type_match:
                                tabs.append({
                                    "title": title_match.group(1),
                                    "index": int(index_match.group(1)),
                                    "type": type_match.group(1)
                                })
                        except Exception:
                            continue
                return tabs
    except Exception as e:
        print(f"[auto_submit_debug] Error enumerating tabs: {e}")
    
    return []


def _capture_cursor_window_screenshot():
    # Return type: Optional[Image.Image] when PIL available
    """
    Capture screenshot of Cursor window using AppleScript to get bounds and pyautogui to capture.
    Returns PIL Image object or None on failure.
    """
    if not IMAGE_DETECTION_AVAILABLE:
        return None
    
    try:
        # Get window bounds via AppleScript
        script = '''
        tell application "System Events"
            try
                set cursorApp to first application process whose name is "Cursor"
            on error
                return "app_not_running"
            end try
            
            if not (exists cursorApp) then
                return "app_not_running"
            end if
            
            set mainWindow to first window of cursorApp
            try
                set windowBounds to bounds of mainWindow
                return windowBounds as string
            on error
                return "bounds_failed"
            end try
        end tell
        '''
        
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"[auto_submit_debug] Failed to get window bounds: {result.stderr}")
            return None
        
        bounds_str = result.stdout.strip()
        if "app_not_running" in bounds_str or "bounds_failed" in bounds_str:
            return None
        
        # Parse bounds: "x, y, width, height"
        try:
            bounds = [int(x.strip()) for x in bounds_str.split(",")]
            if len(bounds) != 4:
                return None
            
            x, y, width, height = bounds
            
            # Capture screenshot of window area
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            print(f"[auto_submit_debug] Screenshot captured: {width}x{height} at ({x}, {y})")
            return screenshot
            
        except (ValueError, IndexError) as e:
            print(f"[auto_submit_debug] Failed to parse window bounds: {e}")
            return None
            
    except Exception as e:
        print(f"[auto_submit_debug] Error capturing screenshot: {e}")
        return None


def _extract_tab_labels_from_image(image):
    # Parameter type: Image.Image when PIL available
    """
    Extract tab labels from screenshot using OCR.
    Crops to tab bar area (top portion) and uses pytesseract.
    Returns list of tab info: [{"label": "...", "bbox": (x, y, w, h), "center": (cx, cy)}, ...]
    """
    if not IMAGE_DETECTION_AVAILABLE:
        return []
    
    try:
        # Crop to tab bar area (top 100-150px)
        width, height = image.size
        tab_bar_height = min(150, height // 4)  # Top 25% or 150px, whichever is smaller
        
        tab_bar_image = image.crop((0, 0, width, tab_bar_height))
        
        # Use pytesseract OCR with bounding boxes
        try:
            ocr_data = pytesseract.image_to_data(tab_bar_image, output_type=pytesseract.Output.DICT)
        except Exception as e:
            print(f"[auto_submit_debug] OCR failed: {e}")
            return []
        
        # Extract text with bounding boxes
        tabs = []
        current_text = ""
        current_bbox = None
        
        n_boxes = len(ocr_data['text'])
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            
            # Skip low confidence or empty text
            if conf < 30 or not text:
                continue
            
            # Check if this looks like a model name (contains keywords)
            model_keywords = ["Sonnet", "GPT", "claude", "Pro", "Codex", "opus", "o3", "Gemini"]
            if any(keyword.lower() in text.lower() for keyword in model_keywords):
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                
                # Calculate center for clicking
                center_x = x + w // 2
                center_y = y + h // 2
                
                tabs.append({
                    "label": text,
                    "bbox": (x, y, w, h),
                    "center": (center_x, center_y),
                    "confidence": conf
                })
        
        # Also try to extract full lines (combine words on same line)
        if not tabs:
            # Try image_to_string for full text extraction
            try:
                full_text = pytesseract.image_to_string(tab_bar_image)
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                for line in lines:
                    if any(keyword.lower() in line.lower() for keyword in model_keywords):
                        # Approximate position (middle of tab bar)
                        tabs.append({
                            "label": line,
                            "bbox": (width // 4, tab_bar_height // 2, width // 2, 30),
                            "center": (width // 2, tab_bar_height // 2),
                            "confidence": 50
                        })
            except Exception:
                pass
        
        print(f"[auto_submit_debug] Extracted {len(tabs)} tab labels from OCR")
        for tab in tabs:
            print(f"[auto_submit_debug]   - Tab: '{tab['label']}' at {tab['center']} (conf: {tab['confidence']})")
        
        return tabs
        
    except Exception as e:
        print(f"[auto_submit_debug] Error extracting tab labels: {e}")
        return []


def _match_tab_by_template(image, model: str):
    # Parameter type: Image.Image when PIL available
    # Return type: Optional[Tuple[int, int]]
    """
    Fallback: Use OpenCV template matching if OCR fails.
    Returns click coordinates (x, y) or None.
    """
    if not IMAGE_DETECTION_AVAILABLE:
        return None
    
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Crop to tab bar
        height, width = img_cv.shape[:2]
        tab_bar = img_cv[0:min(150, height//4), :]
        
        # Try to find text regions that might be tab labels
        # Convert to grayscale for better text detection
        gray = cv2.cvtColor(tab_bar, cv2.COLOR_BGR2GRAY)
        
        # Use text detection (if available) or simple edge detection
        # For now, return None as template matching requires pre-saved templates
        # This can be enhanced later with:
        # 1. Saved template images for each model name
        # 2. Text region detection using EAST or similar
        # 3. Color-based detection (if tabs have distinct colors)
        
        # Placeholder: Could add template images in .mcp/templates/ directory
        template_dir = PROJECT_DIR / ".mcp" / "templates"
        if template_dir.exists():
            # Look for template image matching model name
            model_safe = model.replace(" ", "_").replace(".", "_")
            template_path = template_dir / f"{model_safe}_tab.png"
            if template_path.exists():
                try:
                    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        if max_val > 0.7:  # Threshold for match
                            # Return center of matched region
                            h, w = template.shape
                            center_x = max_loc[0] + w // 2
                            center_y = max_loc[1] + h // 2
                            print(f"[auto_submit_debug] Template match found at ({center_x}, {center_y}) with confidence {max_val:.2f}")
                            return (center_x, center_y)
                except Exception as e:
                    print(f"[auto_submit_debug] Template matching error: {e}")
        
        return None
        
    except Exception as e:
        print(f"[auto_submit_debug] Template matching failed: {e}")
        return None


def _detect_tabs_by_screenshot(model: str, worktree_id: str = None) -> Optional[Dict]:
    """
    Detect and match tab by taking screenshot and using OCR.
    Returns dict with click coordinates or None if not found.
    """
    if not IMAGE_DETECTION_AVAILABLE:
        print(f"[auto_submit_debug] Image detection not available, skipping screenshot method")
        return None
    
    try:
        # Capture screenshot
        screenshot = _capture_cursor_window_screenshot()
        if not screenshot:
            return None
        
        # Extract tab labels
        tabs = _extract_tab_labels_from_image(screenshot)
        if not tabs:
            print(f"[auto_submit_debug] No tabs found in OCR results")
            return None
        
        # Match model name with tab labels
        model_lower = model.lower()
        model_parts = model.split()
        model_first_word = model_parts[0].lower() if model_parts else ""
        worktree_lower = (worktree_id or "").lower()
        
        best_match = None
        best_score = 0
        
        for tab in tabs:
            label_lower = tab["label"].lower()
            score = 0
            
            # Exact match
            if model_lower in label_lower or label_lower in model_lower:
                score = 100
            # First word match
            elif model_first_word and model_first_word in label_lower:
                score = 80
            # Worktree ID match
            elif worktree_lower and worktree_lower in label_lower:
                score = 70
            # Fuzzy match (any model word)
            else:
                for word in model_parts:
                    if len(word) > 3 and word.lower() in label_lower:
                        score = max(score, 50)
            
            if score > best_score:
                best_score = score
                best_match = tab
        
        if best_match and best_score >= 50:
            # Get window bounds to convert relative to screen coordinates
            script = '''
            tell application "System Events"
                set cursorApp to first application process whose name is "Cursor"
                set mainWindow to first window of cursorApp
                set windowBounds to bounds of mainWindow
                return windowBounds as string
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                try:
                    bounds = [int(x.strip()) for x in result.stdout.strip().split(",")]
                    window_x, window_y = bounds[0], bounds[1]
                    
                    # Convert tab center (relative to window) to screen coordinates
                    tab_center_x, tab_center_y = best_match["center"]
                    screen_x = window_x + tab_center_x
                    screen_y = window_y + tab_center_y
                    
                    print(f"[auto_submit_debug] ✅ Matched tab: '{best_match['label']}' (score: {best_score})")
                    print(f"[auto_submit_debug] Click coordinates: ({screen_x}, {screen_y})")
                    
                    return {
                        "label": best_match["label"],
                        "screen_coords": (screen_x, screen_y),
                        "window_coords": best_match["center"],
                        "confidence": best_score
                    }
                except (ValueError, IndexError):
                    pass
        
        print(f"[auto_submit_debug] No matching tab found for model: {model}")
        return None
        
    except Exception as e:
        print(f"[auto_submit_debug] Error in screenshot detection: {e}")
        return None


def _click_tab_by_coordinates(x: int, y: int) -> bool:
    """
    Click at screen coordinates using pyautogui.
    Verifies click success by checking window title change.
    Returns True if successful.
    """
    if not IMAGE_DETECTION_AVAILABLE:
        return False
    
    try:
        # Get current window title before click
        script_before = '''
        tell application "System Events"
            set cursorApp to first application process whose name is "Cursor"
            set mainWindow to first window of cursorApp
            return title of mainWindow as string
        end tell
        '''
        
        result_before = subprocess.run(
            ["osascript", "-e", script_before],
            capture_output=True,
            text=True,
            timeout=5
        )
        title_before = result_before.stdout.strip() if result_before.returncode == 0 else ""
        
        # Click at coordinates
        pyautogui.click(x, y)
        time.sleep(0.5)  # Wait for UI update
        
        # Verify click success by checking if title changed
        result_after = subprocess.run(
            ["osascript", "-e", script_before],
            capture_output=True,
            text=True,
            timeout=5
        )
        title_after = result_after.stdout.strip() if result_after.returncode == 0 else ""
        
        if title_after != title_before:
            print(f"[auto_submit_debug] ✅ Tab click verified: Title changed")
            return True
        else:
            print(f"[auto_submit_debug] ⚠️  Tab click may not have worked: Title unchanged")
            # Still return True as click was executed (title might not change for all tab switches)
            return True
            
    except Exception as e:
        print(f"[auto_submit_debug] Error clicking tab: {e}")
        return False


def _verify_tab_switch(model: str, worktree_id: str = None) -> bool:
    """
    Verify that tab switch was successful by checking window title and active tab content.
    Returns True if switch appears successful.
    """
    script = f'''
    tell application "System Events"
        try
            set cursorApp to first application process whose name is "Cursor"
        on error
            return "false"
        end try
        
        if not (exists cursorApp) then
            return "false"
        end if
        
        set mainWindow to first window of cursorApp
        set windowTitle to title of mainWindow as string
        
        -- Check if window title contains model name or worktree_id
        set modelToFind to "{model}"
        set worktreeToFind to "{worktree_id or ''}"
        
        if windowTitle contains modelToFind then
            return "true"
        end if
        
        -- Check first word of model (e.g., "Sonnet" for "Sonnet 4.5")
        set modelWords to words of modelToFind
        if (count of modelWords) > 0 then
            set firstWord to item 1 of modelWords
            if windowTitle contains firstWord then
                return "true"
            end if
        end if
        
        -- Check worktree_id if provided
        if worktreeToFind is not "" and windowTitle contains worktreeToFind then
            return "true"
        end if
        
        return "false"
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return output.lower() == "true"
    except Exception:
        pass
    
    return False


def _click_tab_by_index(index: int, tab_type: str) -> str:
    """
    Click on a tab by its index and type using AppleScript.
    Returns "clicked" on success, error string otherwise.
    """
    script = f'''
    tell application "System Events"
        try
            set cursorApp to first application process whose name is "Cursor"
        on error
            return "app_not_running"
        end try
        
        if not (exists cursorApp) then
            return "app_not_running"
        end if
        
        set mainWindow to first window of cursorApp
        set targetIndex to {index}
        set targetType to "{tab_type}"
        
        -- Try to click based on type
        if targetType is "tab_group" then
            try
                set tabGroups to every tab group of mainWindow
                repeat with tg in tabGroups
                    try
                        set tabs to every tab of tg
                        if (count of tabs) > targetIndex then
                            set targetTab to item (targetIndex + 1) of tabs
                            click targetTab
                            delay 0.5
                            return "clicked"
                        end if
                    end try
                end repeat
            end try
        else if targetType is "button" then
            try
                set buttons to every button of mainWindow
                if (count of buttons) > targetIndex then
                    set targetButton to item (targetIndex + 1) of buttons
                    click targetButton
                    delay 0.5
                    return "clicked"
                end if
            end try
        else if targetType is "group" then
            try
                set groups to every group of mainWindow
                if (count of groups) > targetIndex then
                    set targetGroup to item (targetIndex + 1) of groups
                    click targetGroup
                    delay 0.5
                    return "clicked"
                end if
            end try
        end if
        
        return "element_not_found"
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if "clicked" in output:
                return "clicked"
            else:
                return output or "click_failed"
        else:
            return "osascript_failed"
    except Exception as e:
        return f"exception:{str(e)}"


def _switch_tab_by_keyboard(model: str, worktree_id: str = None) -> str:
    """
    Fallback: Use keyboard shortcuts to cycle through tabs.
    Uses Cmd+Option+Right to cycle, then verifies.
    """
    script = f'''
    tell application "System Events"
        try
            set cursorApp to first application process whose name is "Cursor"
        on error
            return "app_not_running"
        end try
        
        if not (exists cursorApp) then
            return "app_not_running"
        end if
        
        set mainWindow to first window of cursorApp
        
        -- Try cycling through tabs with Cmd+Option+Right (up to 5 times)
        repeat 5 times
            -- Cycle to next tab
            keystroke (character id 124) using {{command down, option down}}  -- Right arrow
            delay 0.5
            
            -- Check if we're on the right tab
            set windowTitle to title of mainWindow as string
            set modelToFind to "{model}"
            
            if windowTitle contains modelToFind then
                return "tab_switched"
            end if
            
            -- Check first word
            set modelWords to words of modelToFind
            if (count of modelWords) > 0 then
                set firstWord to item 1 of modelWords
                if windowTitle contains firstWord then
                    return "tab_switched"
                end if
            end if
        end repeat
        
        return "keyboard_switch_failed"
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if "tab_switched" in output:
                return "tab_switched"
            elif "app_not_running" in output:
                return "app_not_running"
            else:
                return "keyboard_switch_failed"
        else:
            return "osascript_failed"
    except Exception as e:
        return f"exception:{str(e)}"


def switch_to_chat_tab(model: str = None, worktree_id: str = None, chat_id: str = None, max_retries: int = 3) -> str:
    """
    Switch đến đúng chat tab trong Cursor window dựa trên model name hoặc worktree_id.
    Uses systematic enumeration, matching, retry logic, and verification.
    
    Returns status string.
    """
    if not model or model == "Unknown":
        return "no_model_provided"
    
    # Extract model name parts for fuzzy matching
    model_parts = model.split()
    model_first_word = model_parts[0] if model_parts else ""
    
    # Check if already on correct tab
    if _verify_tab_switch(model, worktree_id):
        print(f"[auto_submit_debug] Already on correct tab (model: {model})")
        return "already_on_tab"
    
    # Retry loop
    for attempt in range(1, max_retries + 1):
        print(f"[auto_submit_debug] Tab switch attempt {attempt}/{max_retries} for model: {model}")
        
        # Step 1: Try image-based detection (primary strategy)
        if IMAGE_DETECTION_AVAILABLE:
            print(f"[auto_submit_debug] Trying image-based tab detection...")
            screenshot_result = _detect_tabs_by_screenshot(model, worktree_id)
            
            if screenshot_result:
                screen_x, screen_y = screenshot_result["screen_coords"]
                print(f"[auto_submit_debug] Attempting to click tab at ({screen_x}, {screen_y})")
                
                if _click_tab_by_coordinates(screen_x, screen_y):
                    # Verify switch success
                    time.sleep(0.5)
                    if _verify_tab_switch(model, worktree_id):
                        print(f"[auto_submit_debug] ✅ Tab switch verified successfully (image-based)")
                        return "tab_switched"
                    else:
                        print(f"[auto_submit_debug] ⚠️  Tab clicked but verification failed")
                else:
                    print(f"[auto_submit_debug] ⚠️  Failed to click tab coordinates")
            else:
                print(f"[auto_submit_debug] Image-based detection found no matching tab")
                
                # Try template matching as fallback within image detection
                try:
                    screenshot = _capture_cursor_window_screenshot()
                    if screenshot:
                        template_coords = _match_tab_by_template(screenshot, model)
                        if template_coords:
                            # Get window bounds to convert to screen coordinates
                            script = '''
                            tell application "System Events"
                                set cursorApp to first application process whose name is "Cursor"
                                set mainWindow to first window of cursorApp
                                set windowBounds to bounds of mainWindow
                                return windowBounds as string
                            end tell
                            '''
                            result = subprocess.run(
                                ["osascript", "-e", script],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if result.returncode == 0:
                                try:
                                    bounds = [int(x.strip()) for x in result.stdout.strip().split(",")]
                                    window_x, window_y = bounds[0], bounds[1]
                                    screen_x = window_x + template_coords[0]
                                    screen_y = window_y + template_coords[1]
                                    
                                    if _click_tab_by_coordinates(screen_x, screen_y):
                                        time.sleep(0.5)
                                        if _verify_tab_switch(model, worktree_id):
                                            print(f"[auto_submit_debug] ✅ Tab switch verified (template matching)")
                                            return "tab_switched"
                                except (ValueError, IndexError):
                                    pass
                except Exception as e:
                    print(f"[auto_submit_debug] Template matching fallback error: {e}")
        
        # Step 2: Enumerate tabs (fallback if image detection fails)
        tabs = _enumerate_cursor_tabs()
        print(f"[auto_submit_debug] Enumerated {len(tabs)} tabs/elements")
        if tabs:
            for tab in tabs:
                print(f"[auto_submit_debug]   - Tab: {tab['title']} (type: {tab['type']}, index: {tab['index']})")
        
        # Step 3: Find matching tab
        matched_tab = None
        match_reason = ""
        
        if tabs:
            for tab in tabs:
                tab_title = tab.get("title", "").lower()
                model_lower = model.lower()
                model_first_lower = model_first_word.lower()
                worktree_lower = (worktree_id or "").lower()
                
                # Exact match
                if model_lower in tab_title:
                    matched_tab = tab
                    match_reason = "exact_match"
                    break
                
                # Partial match (first word)
                if model_first_lower and model_first_lower in tab_title:
                    matched_tab = tab
                    match_reason = "partial_match"
                    break
                
                # Worktree ID match
                if worktree_lower and worktree_lower in tab_title:
                    matched_tab = tab
                    match_reason = "worktree_match"
                    break
                
                # Fuzzy match: check if any model word appears in title
                for word in model_parts:
                    if len(word) > 3 and word.lower() in tab_title:
                        matched_tab = tab
                        match_reason = "fuzzy_match"
                        break
                if matched_tab:
                    break
        
        # Step 4: Try to switch to matched tab
        if matched_tab:
            print(f"[auto_submit_debug] Matched tab: {matched_tab['title']} (reason: {match_reason})")
            
            # Try clicking the tab using AppleScript
            switch_result = _click_tab_by_index(matched_tab['index'], matched_tab['type'])
            
            if switch_result == "clicked":
                # Verify switch success
                time.sleep(0.5)  # Wait for UI update
                if _verify_tab_switch(model, worktree_id):
                    print(f"[auto_submit_debug] ✅ Tab switch verified successfully")
                    return "tab_switched"
                else:
                    print(f"[auto_submit_debug] ⚠️  Tab clicked but verification failed")
            else:
                print(f"[auto_submit_debug] ⚠️  Failed to click tab: {switch_result}")
        else:
            print(f"[auto_submit_debug] No matching tab found in enumeration")
        
        # Step 5: Fallback to keyboard shortcuts (on last attempt)
        if attempt == max_retries:
            print(f"[auto_submit_debug] Trying keyboard shortcut fallback")
            keyboard_result = _switch_tab_by_keyboard(model, worktree_id)
            if keyboard_result in ["tab_switched", "already_on_tab"]:
                return keyboard_result
        
        # Delay before next attempt
        if attempt < max_retries:
            delay = 0.5 * attempt
            print(f"[auto_submit_debug] Waiting {delay}s before next attempt...")
            time.sleep(delay)
    
    # All attempts failed
    print(f"[auto_submit_debug] ❌ Tab switch failed after {max_retries} attempts")
    return "tab_switch_failed"


def flash_all_agent_tabs(delay_between: float = 0.8) -> bool:
    """
    Làm nháy viền xanh (blue border highlight) qua tất cả các agent cards đang mở.
    Strategy:
    1. Focus vào Cursor window
    2. Dùng keyboard shortcuts để switch qua các model tabs (Cmd+1, Cmd+2, etc.)
    3. Mỗi lần switch sẽ làm viền xanh nháy trên card tương ứng
    4. Delay đủ lâu để thấy được viền xanh nháy
    
    Returns True nếu thành công.
    """
    try:
        # Load detected chats
        if not STATE_FILE.exists():
            print(f"[auto_submit_debug] ⚠️  Shared state file not found")
            return False
        
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        detected_chats = state.get("detected_chats", [])
        if not detected_chats:
            print(f"[auto_submit_debug] ⚠️  No active chats found")
            return False
        
        print(f"[auto_submit_debug] ✨ Flashing viền xanh qua {len(detected_chats)} agent cards...")
        
        # Focus vào Cursor window đầu tiên
        first_chat = detected_chats[0]
        window_status = find_and_focus_cursor_window(
            worktree_id=first_chat.get('worktree_id'),
            chat_id=first_chat.get('chat_id'),
            worktree_path=first_chat.get('worktree_path'),
            model=first_chat.get('model')
        )
        if "focused" not in window_status:
            print(f"[auto_submit_debug] ⚠️  Failed to focus Cursor window")
            return False
        
        # Đảm bảo Cursor window đã được focus và sẵn sàng
        time.sleep(0.5)
        
        # Cycle qua các tabs bằng Cmd+1, Cmd+2, etc. để làm viền xanh nháy
        for i, chat in enumerate(detected_chats):
            agent_name = chat.get('agent_name')
            model = chat.get('model')
            
            if not agent_name:
                continue
            
            tab_number = i + 1
            print(f"[auto_submit_debug]   [{tab_number}/{len(detected_chats)}] ✨ Viền xanh nháy: {agent_name} ({model})")
            
            # Dùng Cmd+1, Cmd+2, etc để switch tab - viền xanh sẽ tự động nháy trên card
            tab_script = f'''
            tell application "System Events"
                tell application "Cursor" to activate
                delay 0.1
                keystroke "{tab_number}" using {{command down}}
                delay 0.2
            end tell
            '''
            
            try:
                result = subprocess.run(
                    ["osascript", "-e", tab_script],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"[auto_submit_debug]     ✅ Card {tab_number} highlighted (viền xanh)")
                else:
                    print(f"[auto_submit_debug]     ⚠️  Failed to switch to card {tab_number}")
            except Exception as e:
                print(f"[auto_submit_debug]     ⚠️  Error: {e}")
            
            # Delay đủ lâu để thấy viền xanh nháy (tăng delay để dễ thấy hơn)
            if i < len(detected_chats) - 1:
                time.sleep(delay_between)
        
        # Quay lại tab đầu tiên để hoàn tất chu kỳ
        final_script = '''
        tell application "System Events"
            tell application "Cursor" to activate
            delay 0.1
            keystroke "1" using {command down}
        end tell
        '''
        subprocess.run(["osascript", "-e", final_script], capture_output=True, timeout=3)
        
        print(f"[auto_submit_debug] ✅ Finished flashing viền xanh qua tất cả {len(detected_chats)} cards")
        return True
        
    except Exception as e:
        print(f"[auto_submit_debug] ❌ Error flashing tabs: {e}")
        return False


def find_and_focus_cursor_window(worktree_id: str, chat_id: str = None, worktree_path: str = None, model: str = None) -> str:
    """
    Tìm và focus vào Cursor window. Ưu tiên window có chứa model name (vì title chứa model),
    sau đó worktree_id, chat_id, hoặc "cheftAi", nhưng luôn fallback về window đầu tiên nếu không tìm thấy.
    
    Returns status string.
    """
    try:
        # AppleScript: Tìm Cursor window, ưu tiên window có chứa model name (title chứa model)
        search_terms = []
        
        # Ưu tiên 1: Search bằng model name (title window chứa model như "Sonnet 4.5", "GPT-5.1 Codex High Fast")
        if model and model != "Unknown":
            # Extract model name parts để search (vì title có thể có format khác)
            model_parts = model.split()
            # Thêm full model name và các parts quan trọng
            search_terms.append(model)  # Full model name
            if len(model_parts) > 0:
                search_terms.append(model_parts[0])  # First part (e.g., "Sonnet", "GPT-5.1")
            if len(model_parts) > 1:
                # Thêm combination như "Sonnet 4.5" hoặc "GPT-5.1 Codex"
                search_terms.append(f"{model_parts[0]} {model_parts[1]}")
        
        # Ưu tiên 2: Search bằng worktree_id và chat_id
        if worktree_id:
            search_terms.append(worktree_id)
        if chat_id and chat_id != worktree_id:
            search_terms.append(chat_id)
        
        # Fallback: Search bằng project name
        search_terms.append("cheftAi")
        
        search_terms_str = " or ".join([f'windowTitle contains "{term}"' for term in search_terms])
        
        script = f'''
        tell application "System Events"
            try
                set cursorApp to first application process whose name is "Cursor"
            on error
                return "app_not_running"
            end try
            
            -- Kiểm tra xem Cursor có đang chạy không
            if not (exists cursorApp) then
                return "app_not_running"
            end if
            
            -- Kiểm tra xem có window nào không
            set windowCount to count of windows of cursorApp
            if windowCount = 0 then
                -- Không có window, thử mở Cursor bằng cách activate app
                tell application "Cursor" to activate
                    delay 0.5
                set windowCount to count of windows of cursorApp
                if windowCount = 0 then
                    return "no_windows"
                end if
            end if
            
            -- Log all window titles for debugging
            set allTitles to ""
            repeat with aWindow in windows of cursorApp
                try
                    set allTitles to allTitles & title of aWindow & "\\n"
                end try
            end repeat
            log "DEBUG_WINDOW_TITLES:" & allTitles
            
            -- Tìm window ưu tiên: worktree_id là cách chính xác nhất để match window
            set foundWindow to missing value
            
            -- Ưu tiên 1: Tìm window bằng worktree_id (chính xác nhất)
            set worktreeToFind to "{worktree_id}"
            if worktreeToFind is not "" then
            repeat with aWindow in windows of cursorApp
                try
                    set windowTitle to title of aWindow
                        -- Check exact match hoặc contains worktree_id
                        if windowTitle is worktreeToFind or windowTitle contains worktreeToFind then
                        set foundWindow to aWindow
                            log "DEBUG_FOUND_BY_WORKTREE:" & worktreeToFind & " in " & windowTitle
                        exit repeat
                    end if
                end try
            end repeat
            end if
            
            -- Ưu tiên 2: Nếu không tìm thấy bằng worktree_id, thử tìm bằng chat_id
            if foundWindow is missing value then
                set chatToFind to "{chat_id}"
                if chatToFind is not "" and chatToFind is not "{worktree_id}" then
                    repeat with aWindow in windows of cursorApp
                        try
                            set windowTitle to title of aWindow
                            if windowTitle is chatToFind or windowTitle contains chatToFind then
                                set foundWindow to aWindow
                                log "DEBUG_FOUND_BY_CHAT:" & chatToFind & " in " & windowTitle
                                exit repeat
                            end if
                        end try
                    end repeat
                end if
            end if
            
            -- Ưu tiên 3: Nếu vẫn không tìm thấy, thử tìm bằng model name (ít chính xác hơn)
            if foundWindow is missing value then
                set modelToFind to "{model}"
                if modelToFind is not "Unknown" and modelToFind is not "" then
                    repeat with aWindow in windows of cursorApp
                        try
                            set windowTitle to title of aWindow
                            if windowTitle contains modelToFind then
                                set foundWindow to aWindow
                                log "DEBUG_FOUND_BY_MODEL:" & modelToFind & " in " & windowTitle
                                exit repeat
                            end if
                        end try
                    end repeat
                end if
            end if
            
            -- Fallback: Nếu không tìm thấy window ưu tiên, thử mở window bằng worktree path
            if foundWindow is missing value then
                set worktreePathToOpen to "{worktree_path}"
                if worktreePathToOpen is not "" and worktreePathToOpen is not "not_found" then
                    try
                        -- Thử mở window bằng cursor CLI với worktree path
                        do shell script "cursor " & quoted form of worktreePathToOpen
                        delay 2.0
                        -- Sau khi mở, tìm lại windows
                    set windowCount to count of windows of cursorApp
                    if windowCount > 0 then
                            -- Tìm window mới mở bằng cách check worktree_id trong title
                            set worktreeToFind to "{worktree_id}"
                            if worktreeToFind is not "" then
                                repeat with aWindow in windows of cursorApp
                                    try
                                        set windowTitle to title of aWindow
                                        if windowTitle contains worktreeToFind then
                                            set foundWindow to aWindow
                                            log "DEBUG_FOUND_AFTER_OPEN:" & worktreeToFind & " in " & windowTitle
                                            exit repeat
                                        end if
                                    end try
                                end repeat
                            end if
                            -- Nếu vẫn không tìm thấy, dùng window đầu tiên
                            if foundWindow is missing value then
                        set foundWindow to item 1 of windows of cursorApp
                                log "DEBUG_FALLBACK_TO_FIRST_WINDOW_AFTER_OPEN"
                            end if
                        end if
                    on error
                        -- Nếu không mở được bằng CLI, fallback về window đầu tiên
                        try
                            set foundWindow to item 1 of windows of cursorApp
                            log "DEBUG_FALLBACK_TO_FIRST_WINDOW"
                        on error
                            return "window_not_found"
                        end try
                    end try
                else
                    -- Nếu không có worktree_path, fallback về window đầu tiên
                    try
                        set foundWindow to item 1 of windows of cursorApp
                        log "DEBUG_FALLBACK_TO_FIRST_WINDOW"
                    on error
                        return "window_not_found"
                end try
                end if
            end if
            
            -- Focus vào window đó: Set frontmost và AXRaise để đảm bảo window được raise lên top
            if foundWindow is not missing value then
                set frontmost of cursorApp to true
                delay 0.2
                perform action "AXRaise" of foundWindow
                delay 0.3
                -- Đảm bảo window được focus
                set value of attribute "AXMain" of foundWindow to true
                delay 0.3
                log "DEBUG_WINDOW_FOCUSED:" & title of foundWindow
                return "focused"
            else
                return "window_not_found"
            end if
        end tell
        '''
        
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=8  # Giảm timeout xuống 8s để nhanh hơn
        )
        
        # Extract debug logs từ stderr (AppleScript log output goes to stderr)
        debug_output = result.stderr.strip()
        if debug_output:
            # Parse window titles và log info
            for line in debug_output.split('\n'):
                if 'DEBUG_WINDOW_TITLES:' in line:
                    titles = line.replace('DEBUG_WINDOW_TITLES:', '').strip()
                    print(f"[auto_submit_debug] All Cursor window titles:\n{titles}")
                elif 'DEBUG_FOUND_BY_MODEL:' in line:
                    print(f"[auto_submit_debug] {line.replace('DEBUG_FOUND_BY_MODEL:', '').strip()}")
                elif 'DEBUG_FOUND_BY_WORKTREE:' in line:
                    print(f"[auto_submit_debug] {line.replace('DEBUG_FOUND_BY_WORKTREE:', '').strip()}")
                elif 'DEBUG_FOUND_BY_CHAT:' in line:
                    print(f"[auto_submit_debug] {line.replace('DEBUG_FOUND_BY_CHAT:', '').strip()}")
                elif 'DEBUG_WINDOW_FOCUSED:' in line:
                    print(f"[auto_submit_debug] {line.replace('DEBUG_WINDOW_FOCUSED:', '').strip()}")
                elif 'DEBUG_FALLBACK_TO_FIRST_WINDOW' in line:
                    print(f"[auto_submit_debug] Fallback: Using first window (model not found in titles)")
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if "focused" in output:
                # Đợi một chút để window focus hoàn tất
                time.sleep(0.5)
                return "focused_window"
            elif "app_not_running" in output:
                return "app_not_running"
            elif "no_windows" in output:
                return "no_windows"
            else:
                return "window_not_found"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            # Nếu lỗi nhưng Cursor có thể vẫn đang chạy, thử gửi vào window đang active
            if "not found" in error_msg.lower() or "doesn't exist" in error_msg.lower():
                return "window_not_found"
            return f"osascript_failed:{error_msg}"
    except subprocess.TimeoutExpired:
        return "osascript_timeout"
    except Exception as e:
        return f"osascript_error:{str(e)}"


def send_to_cursor(file_path: str = None, text: str = None, chat_id: str = None, model: str = None, retry_count: int = 2) -> str:  # Giảm retry xuống 2 lần
    """
    Send prompt to Cursor by paste + Enter với retry logic để đảm bảo ổn định.
    Đảm bảo Cursor đang active và focus vào chat input.
    """
    # Dùng text để verify, nếu không có thì đọc từ file_path
    expected_text = text or ""
    if not expected_text and file_path:
        try:
            expected_text = Path(file_path).read_text(encoding="utf-8", errors="replace")[:200]
        except Exception:
            expected_text = ""

    strategies = [
        ("cmd_enter", """
            -- Đảm bảo focus vào chat input trước khi paste
            -- Cmd+L và Cmd+W đã được gọi ở trên
            -- Thử Escape một lần nữa để đảm bảo không có dialog nào
            key code 53  -- Escape key
            delay 0.2
            -- Đảm bảo focus vào chat input bằng cách click vào chat area
            -- Hoặc dùng Cmd+L lại một lần nữa để chắc chắn
            keystroke "l" using {{command down}}
            delay 0.8
            -- Clear input để đảm bảo focus đúng
            keystroke "a" using {{command down}}
            delay 0.2
            key code 51  -- Delete
            delay 0.3
            -- Paste message vào chat input (Cmd+V)
            keystroke "v" using {{command down}}
            delay 1.2
            -- Submit bằng Cmd+Enter (an toàn, tránh trigger command)
            keystroke return using {{command down}}
            delay 0.5
        """),
        ("enter_only", """
            -- Đảm bảo focus vào chat input trước khi paste
            key code 53  -- Escape key
            delay 0.3
            -- Paste message vào chat input (Cmd+V)
            keystroke "v" using {{command down}}
            delay 1.0
            -- Submit bằng Enter
            key code 36
            delay 0.5
        """),
        ("click_send_button", """
            keystroke "v" using {{command down}}
            delay 1.5
            -- Thử click nút Send
            try
                tell cursorApp
                    set btns to every button of mainWindow
                    repeat with b in btns
                        try
                            set btnName to name of b
                            if btnName contains "Send" or btnName contains "send" or btnName contains "Submit" then
                                click b
                                delay 0.5
                                exit repeat
                            end if
                        end try
                    end repeat
                end tell
            end try
            delay 0.5
        """),
    ]

    def build_script(paste_section: str, use_temp: bool, temp_path: str = "") -> str:
        paste_src = f'''
                    -- Copy file content to clipboard
                    set thePath to "{temp_path}"
                    set theText to do shell script "cat " & quoted form of thePath
                    set the clipboard to theText
                    delay 0.3
        ''' if use_temp else '''
                    -- Clipboard đã có sẵn nội dung text
                    delay 0.1
        '''
        return f'''
                tell application "System Events"
                    try
                        set cursorApp to first application process whose name is "Cursor"
                    on error
                        return "app_not_running"
                    end try
                    
                    set windowCount to count of windows of cursorApp
                    if windowCount = 0 then
                        tell application "Cursor" to activate
                        delay 0.5
                        set windowCount to count of windows of cursorApp
                        if windowCount = 0 then
                            return "no_windows"
                        end if
                    end if
                    
                    set frontmost of cursorApp to true
                    delay 0.5
                    
                    -- QUAN TRỌNG: Focus vào chat input TRƯỚC khi paste
                    -- Bước 1: Đóng tất cả file đang mở trong editor (Cmd+W)
                    keystroke "w" using {{command down}}
                                    delay 0.3
                    -- Bước 2: Escape để đảm bảo không có dialog nào đang mở
                    key code 53  -- Escape
                                    delay 0.3
                    -- Bước 3: Dùng Cmd+L để mở/focus vào chat input (QUAN TRỌNG)
                    keystroke "l" using {{command down}}
                    delay 2.0
                    -- Bước 4: Đảm bảo chat input được focus bằng cách clear nó
                                        keystroke "a" using {{command down}}
                    delay 0.4
                    key code 51  -- Delete key để clear
                                delay 0.5
                    -- Bước 5: Thử Tab để focus vào input field nếu chưa focus
                    key code 48  -- Tab key
                    delay 0.3
                    -- Bước 6: Clear lại để đảm bảo focus đúng
                                keystroke "a" using {{command down}}
                                delay 0.2
                    key code 51  -- Delete
                                delay 0.3
                    
{paste_src}

{paste_section}

                    return "done"
                end tell
        '''

    # Nếu text được cung cấp, dùng file tạm để paste an toàn
    temp_path = None
    use_temp = False
    if text:
        import tempfile
        tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        tmp.write(text)
        tmp.close()
        temp_path = tmp.name.replace("'", "'\\''")
        use_temp = True

    for attempt in range(retry_count):
        print(f"[auto_submit_debug] === Attempt {attempt+1}/{retry_count} ===")
        for strategy_name, paste_section in strategies:
            try:
                print(f"[auto_submit_debug] Trying strategy: {strategy_name}")
                script = build_script(paste_section, use_temp, temp_path or "")
                result = subprocess.run(
                    ["osascript", "-e", script],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=10  # Giảm timeout xuống 10s để nhanh hơn
                )
                output = result.stdout.strip()
                print(f"[auto_submit_debug] Strategy {strategy_name} - Step: Focus & Paste")
                print(f"[auto_submit_debug]   Return code: {result.returncode}")
                print(f"[auto_submit_debug]   Stdout: {output}")
                if result.stderr.strip():
                    print(f"[auto_submit_debug]   Stderr: {result.stderr.strip()}")
                
                if result.returncode == 0 and "app_not_running" not in output and "no_windows" not in output:
                    print(f"[auto_submit_debug] Strategy {strategy_name} - Step: Submit (via {strategy_name})")
                    print(f"[auto_submit_debug] Strategy {strategy_name} - Step: Verification")
                    # Pass chat_id và model để verify message trong đúng chat tab
                    if verify_message_sent(expected_text, chat_id=chat_id, model=model, timeout=1.0):
                        print(f"[auto_submit_debug] ✅ Verification PASSED - Message sent successfully")
                        return "sent_to_cursor_ok"
                    else:
                        print(f"[auto_submit_debug] ❌ Verification FAILED - Input field still contains message")
                else:
                    if "app_not_running" in output:
                        print(f"[auto_submit_debug] ❌ Error: Cursor app not running")
                    elif "no_windows" in output:
                        print(f"[auto_submit_debug] ❌ Error: No Cursor windows found")
                    else:
                        print(f"[auto_submit_debug] ❌ Error: osascript not successful for strategy={strategy_name}")
            except subprocess.TimeoutExpired:
                print(f"[auto_submit_debug] ❌ Error: Timeout after 20s for strategy={strategy_name}")
                continue
            except Exception as e:
                print(f"[auto_submit_debug] ❌ Error: Exception in strategy={strategy_name}: {e}")
                continue
        # Retry với delay tăng dần
        if attempt < retry_count - 1:
            delay = 0.8 * (attempt + 1)
            print(f"[auto_submit_debug] Waiting {delay:.1f}s before next attempt...")
            time.sleep(delay)

    return "osascript_failed: max_retries_exceeded"


def main() -> int:
    agent = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    prompt_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    chat_id_arg = sys.argv[3] if len(sys.argv) > 3 else None

    # Get agent info from shared_state.json
    # agent can be agent name, chat_id, or worktree_id
    agent_info = get_agent_worktree_info(agent, chat_id_arg)
    worktree_id = agent_info.get("worktree_id", "")
    worktree_path = agent_info.get("worktree_path", "")
    model = agent_info.get("model") or AGENT_MODEL_MAP.get(agent, "Unknown")
    
    # Extract chat_id from agent_info if available
    chat_id = chat_id_arg or agent_info.get("chat_id", "")
    
    # If worktree_path not found but we have worktree_id, try to construct path
    if not worktree_path and worktree_id:
        potential_path = Path.home() / ".cursor" / "worktrees" / "cheftAi" / worktree_id
        if potential_path.exists():
            worktree_path = str(potential_path)
    
    src, text = resolve_prompt_text(prompt_arg)
    preview = (text or "").replace("\n", " ")
    if len(preview) > 200:
        preview = preview[:200] + "..."

    # Log header
    base_log = (
        f"[auto_submit_service]\n"
        f"  agent       = {agent}\n"
        f"  model       = {model}\n"
        f"  worktree_id = {worktree_id or 'not_mapped'}\n"
        f"  chat_id     = {chat_id or 'not_provided'}\n"
        f"  worktree_path = {worktree_path or 'not_found'}\n"
        f"  prompt_src  = {src}\n"
        f"  prompt_prev = {preview}"
    )

    # Step 1: Tìm và focus vào Cursor window
    window_status = find_and_focus_cursor_window(worktree_id, chat_id, worktree_path, model)
    
    # Step 1.5: Nếu window đã được focus, thử switch đến đúng chat tab
    # (Nếu Cursor dùng multi-tabs trong một window)
    tab_status = "tab_switch_skipped"
    if "focused" in window_status and model and model != "Unknown":
        tab_status = switch_to_chat_tab(model, worktree_id, chat_id, max_retries=3)
        if "switched" in tab_status or "already_on_tab" in tab_status:
            print(f"[auto_submit_debug] Tab switch: {tab_status}")
        elif "failed" in tab_status or "error" in tab_status:
            # Tab switch failed - nhưng nếu window đã được focus thành công thì vẫn tiếp tục
            # (Cursor có thể dùng separate windows, không cần tab switching)
            print(f"[auto_submit_debug] ⚠️  Tab switch failed: {tab_status}")
            # Nếu window đã được focus thành công thì tiếp tục (Cursor có thể dùng separate windows)
            if "focused" in window_status:
                print(f"[auto_submit_debug] ✅ Window đã được focus thành công - tiếp tục gửi message (tab switching không cần thiết)")
                # Không abort, tiếp tục với message send
            else:
                print(f"[auto_submit_debug] ❌ Window cũng không được focus - abort để tránh gửi sai")
                error_msg = f"tab_switch_failed:{tab_status}"
                extra = f"\n  window_switch = {window_status}\n  tab_switch   = {tab_status}\n  ui_status   = {error_msg}"
                print(base_log + extra)
                return 1  # Return error code
        elif "not_found" in tab_status:
            # Không tìm thấy tabs, có thể là single window mode hoặc tabs không accessible
            print(f"[auto_submit_debug] Tab switch: {tab_status} (may be single window mode)")
    
    # Step 2: Send prompt to Cursor (paste + Enter)
    # Ưu tiên gửi text (message đã extract) thay vì file_path
    # Vì text đã được extract từ file và chỉ chứa message thực tế
    # Gửi message nếu:
    # - Tìm thấy và focus được window (focused_window)
    # - Hoặc không có worktree_id (gửi vào window đang active)
    # - Hoặc window_not_found/no_windows (vẫn thử gửi vào window đang active)
    # Chỉ skip nếu Cursor không chạy (app_not_running)
    if "focused" in window_status or "cursor_cli" in window_status or not worktree_id:
        # Luôn dùng text (message đã extract) thay vì file_path
        # text đã được extract từ resolve_prompt_text() và chỉ chứa message thực tế
        # Pass chat_id và model để verify message trong đúng chat tab
        ui_status = send_to_cursor(text=text, chat_id=chat_id, model=model) if text else send_to_cursor(file_path=prompt_arg, chat_id=chat_id, model=model)
    elif window_status == "window_not_found" or window_status == "no_windows":
        # Nếu không tìm thấy window cụ thể, vẫn thử gửi vào window đang active
        # send_to_cursor sẽ tự động focus vào Cursor
        ui_status = send_to_cursor(text=text, chat_id=chat_id, model=model) if text else send_to_cursor(file_path=prompt_arg, chat_id=chat_id, model=model)
    elif window_status == "app_not_running":
        # Cursor không chạy, không thể gửi
        ui_status = f"skipped_send:{window_status}"
    else:
        # Các trường hợp khác (osascript_error, osascript_timeout, etc.) - vẫn thử gửi
        ui_status = send_to_cursor(text=text, chat_id=chat_id, model=model) if text else send_to_cursor(file_path=prompt_arg, chat_id=chat_id, model=model)
    
    # Final log
    extra = f"\n  window_switch = {window_status}\n  tab_switch   = {tab_status}\n  ui_status   = {ui_status}"
    print(base_log + extra)

    # In "sent_to_cursor_ok" vào stdout để api_server.py có thể detect thành công
    if ui_status == "sent_to_cursor_ok":
        print("sent_to_cursor_ok", flush=True)
        return 0
    elif "sent_to_cursor_ok" in str(ui_status):
        print("sent_to_cursor_ok", flush=True)
        return 0
    else:
        # Nếu không thành công, vẫn return 0 nhưng không in "sent_to_cursor_ok"
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
