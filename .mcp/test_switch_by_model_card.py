#!/usr/bin/env python3
"""
Test switch model bằng cách click vào model cards ở sidebar
Dựa trên screenshot, có các model cards ở bên trái
"""
import subprocess
import time
import json
from pathlib import Path

def switch_to_model_by_card(model_name: str):
    """
    Switch đến model bằng cách click vào model card ở sidebar
    """
    # Extract model name parts để tìm trong UI
    model_parts = model_name.split()
    search_terms = [model_name]
    if len(model_parts) > 0:
        search_terms.append(model_parts[0])
    if len(model_parts) > 1:
        search_terms.append(f"{model_parts[0]} {model_parts[1]}")
    
    script = f'''
    tell application "System Events"
        set cursorApp to first application process whose name is "Cursor"
        set mainWindow to first window of cursorApp
        
        -- Tìm tất cả UI elements có thể là model cards
        set foundElement to missing value
        
        -- Strategy 1: Tìm trong static text (model cards có thể là text elements)
        try
            set textElements to every static text of mainWindow
            repeat with te in textElements
                try
                    set textValue to value of te as string
                    if textValue contains "{model_name}" or textValue contains "{model_parts[0] if model_parts else ''}" then
                        -- Tìm parent element (có thể là button hoặc group)
                        try
                            set parentElem to parent of te
                            set parentClass to class of parentElem as string
                            if parentClass is "button" or parentClass is "group" then
                                set foundElement to parentElem
                                log "DEBUG_FOUND_MODEL_CARD:" & textValue & " in " & parentClass
                                exit repeat
                            end if
                        end try
                    end if
                end try
            end repeat
        end try
        
        -- Strategy 2: Tìm trong buttons (model cards có thể là buttons)
        if foundElement is missing value then
            try
                set buttons to every button of mainWindow
                repeat with b in buttons
                    try
                        set btnName to name of b as string
                        set btnTitle to title of b as string
                        if btnName contains "{model_name}" or btnTitle contains "{model_name}" or btnName contains "{model_parts[0] if model_parts else ''}" or btnTitle contains "{model_parts[0] if model_parts else ''}" then
                            set foundElement to b
                            log "DEBUG_FOUND_MODEL_BUTTON:" & btnName & " / " & btnTitle
                            exit repeat
                        end if
                    end try
                end repeat
            end try
        end if
        
        -- Strategy 3: Tìm trong groups (model cards có thể là groups)
        if foundElement is missing value then
            try
                set groups to every group of mainWindow
                repeat with g in groups
                    try
                        set groupTitle to title of g as string
                        if groupTitle contains "{model_name}" or groupTitle contains "{model_parts[0] if model_parts else ''}" then
                            set foundElement to g
                            log "DEBUG_FOUND_MODEL_GROUP:" & groupTitle
                            exit repeat
                        end if
                    end try
                end repeat
            end try
        end if
        
        -- Click vào element nếu tìm thấy
        if foundElement is not missing value then
            try
                click foundElement
                delay 1.0
                -- Check window title sau khi click
                set newTitle to title of mainWindow as string
                log "DEBUG_AFTER_CLICK:" & newTitle
                return "clicked:" & newTitle
            on error
                return "click_failed"
            end try
        else
            return "element_not_found"
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
        
        # Extract debug logs
        debug_output = result.stderr.strip()
        if debug_output:
            for line in debug_output.split('\n'):
                if 'DEBUG' in line:
                    print(f"   {line}")
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return output
        else:
            return f"error:{result.stderr.strip()}"
            
    except Exception as e:
        return f"exception:{str(e)}"

def test_switch_by_cards():
    """Test switch model bằng cách click vào model cards"""
    
    print("🧪 Testing Model Switching by Clicking Cards")
    print("=" * 60)
    
    # Load detected chats
    STATE_FILE = Path(__file__).parent.parent / ".mcp" / "shared_state.json"
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    print(f"📊 Testing với {len(detected_chats)} models:")
    print()
    
    # Get current window title
    script = '''
    tell application "System Events"
        set cursorApp to first application process whose name is "Cursor"
        set mainWindow to first window of cursorApp
        return title of mainWindow as string
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
    initial_title = result.stdout.strip()
    print(f"📍 Initial window title: {initial_title}")
    print()
    
    # Test switch đến từng model
    for chat in detected_chats[:4]:  # Test 4 đầu tiên
        model = chat.get('model')
        agent_name = chat.get('agent_name')
        
        if not model:
            continue
        
        print(f"🔄 Switching to: {agent_name} → {model}")
        
        result = switch_to_model_by_card(model)
        print(f"   Result: {result}")
        
        # Check window title sau khi switch
        result2 = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
        new_title = result2.stdout.strip()
        print(f"   New title: {new_title}")
        
        if model in new_title or (model.split()[0] if model.split() else '') in new_title:
            print(f"   ✅ Success! Model found in title")
        else:
            print(f"   ⚠️  Model not found in title")
        
        print()
        time.sleep(2)

if __name__ == "__main__":
    test_switch_by_cards()

