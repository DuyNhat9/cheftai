#!/usr/bin/env python3
"""Click trực tiếp vào model cards để switch"""
import subprocess
import time
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def get_window_bounds():
    """Lấy bounds của Cursor window"""
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.2
        set cursorApp to first application process whose name is "Cursor"
        set mainWindow to first window of cursorApp
        set windowBounds to bounds of mainWindow
        return windowBounds as string
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
            bounds = [int(x.strip()) for x in result.stdout.strip().split(",")]
            return bounds  # [x, y, width, height]
    except:
        pass
    return None

def click_at_position(x: int, y: int):
    """Click tại vị trí x, y trên màn hình"""
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.2
        click at {{{x}, {y}}}
        delay 0.3
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def find_and_click_model_card(model_name: str):
    """Tìm và click vào model card bằng cách tìm text trong UI"""
    print(f"   🔍 Tìm model card: {model_name}")
    
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        set cursorApp to first application process whose name is "Cursor"
        set mainWindow to first window of cursorApp
        
        -- Tìm tất cả static texts
        set allTexts to static texts of mainWindow
        set targetText to null
        
        repeat with txt in allTexts
            try
                set txtValue to value of txt as string
                if txtValue contains "{model_name}" then
                    set targetText to txt
                    exit repeat
                end if
            end try
        end repeat
        
        if targetText is not null then
            -- Click vào text hoặc parent element
            try
                click targetText
                delay 0.5
                return "clicked"
            on error
                -- Thử click vào parent
                try
                    set parentGroup to parent of targetText
                    click parentGroup
                    delay 0.5
                    return "clicked_parent"
                end try
            end try
        end if
        
        return "not_found"
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
            if "clicked" in output:
                print(f"   ✅ Đã click vào model card")
                return True
            else:
                print(f"   ⚠️  {output}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def switch_to_model_by_clicking(model_name: str, agent_name: str):
    """Switch đến model bằng cách click vào card"""
    print(f"\n🎯 Click vào model card: {agent_name} ({model_name})")
    
    # Strategy 1: Tìm và click vào text
    success = find_and_click_model_card(model_name)
    
    if not success:
        # Strategy 2: Thử click vào partial match
        model_parts = model_name.split()
        if len(model_parts) > 0:
            first_part = model_parts[0]
            print(f"   🔄 Thử với partial match: {first_part}")
            success = find_and_click_model_card(first_part)
    
    if success:
        time.sleep(0.5)
        print(f"   ✅ Switch thành công!")
        return True
    else:
        print(f"   ❌ Không tìm thấy model card")
        return False

def main():
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    # Tìm Sonnet 4 1M và claude-4.1-opus
    target_agents = []
    for i, chat in enumerate(detected_chats):
        model = chat.get('model', '')
        agent_name = chat.get('agent_name', '')
        
        if 'Sonnet 4 1M' in model:
            target_agents.append({
                'name': 'Sonnet 4 1M',
                'model': model,
                'agent_name': agent_name
            })
        elif 'claude-4.1-opus' in model.lower():
            target_agents.append({
                'name': 'claude-4.1-opus',
                'model': model,
                'agent_name': agent_name
            })
    
    if not target_agents:
        print("⚠️  Không tìm thấy targets")
        return
    
    print("=" * 60)
    print(f"🎯 Tìm thấy {len(target_agents)} agents để switch")
    print("=" * 60)
    
    # Switch đến từng agent
    for i, agent in enumerate(target_agents):
        switch_to_model_by_clicking(agent['model'], agent['agent_name'])
        
        if i < len(target_agents) - 1:
            print(f"   ⏳ Đợi 2s...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Hoàn tất!")
    print("💡 Kiểm tra viền xanh trên cards để verify")

if __name__ == "__main__":
    main()

