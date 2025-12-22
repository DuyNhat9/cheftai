#!/usr/bin/env python3
"""Click trực tiếp vào model cards để switch"""
import sys
import json
import time
from pathlib import Path

try:
    import pyautogui
    from PIL import Image
    import pytesseract
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False
    print("⚠️  Cần cài: pip install pyautogui pytesseract Pillow")

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def capture_screenshot():
    """Capture screenshot của Cursor window"""
    if not IMAGE_AVAILABLE:
        return None
    
    try:
        import subprocess
        
        # Lấy bounds của Cursor window
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
        
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            bounds = [int(x.strip()) for x in result.stdout.strip().split(",")]
            x, y, width, height = bounds
            
            # Capture screenshot của top portion (nơi có model cards)
            screenshot = pyautogui.screenshot(region=(x, y, width, min(300, height)))
            return screenshot, (x, y)
    except Exception as e:
        print(f"   ⚠️  Error capturing screenshot: {e}")
    
    return None, None

def find_model_card_in_image(image, model_name):
    """Tìm model card trong screenshot bằng OCR"""
    if not IMAGE_AVAILABLE:
        return None
    
    try:
        # Crop top portion (model cards thường ở trên)
        width, height = image.size
        top_portion = image.crop((0, 0, width, min(200, height)))
        
        # OCR để tìm model name
        text = pytesseract.image_to_string(top_portion)
        
        # Tìm vị trí của model name trong text
        if model_name.lower() in text.lower():
            # Thử tìm bounding box
            data = pytesseract.image_to_data(top_portion, output_type=pytesseract.Output.DICT)
            
            for i, txt in enumerate(data['text']):
                if model_name.lower() in txt.lower():
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # Return center của bounding box
                    center_x = x + w // 2
                    center_y = y + h // 2
                    return (center_x, center_y)
    except Exception as e:
        print(f"   ⚠️  OCR error: {e}")
    
    return None

def click_at_screen_position(x, y):
    """Click tại vị trí trên màn hình"""
    if not IMAGE_AVAILABLE:
        return False
    
    try:
        pyautogui.click(x, y)
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"   ⚠️  Click error: {e}")
        return False

def switch_to_model_by_clicking(model_name: str, agent_name: str):
    """Switch đến model bằng cách click vào card"""
    print(f"\n🎯 Click vào model card: {agent_name} ({model_name})")
    
    if not IMAGE_AVAILABLE:
        print("   ❌ Image detection không available")
        return False
    
    # Capture screenshot
    print("   📸 Đang capture screenshot...")
    screenshot, window_pos = capture_screenshot()
    
    if not screenshot:
        print("   ❌ Không capture được screenshot")
        return False
    
    # Tìm model card trong image
    print(f"   🔍 Đang tìm model card '{model_name}'...")
    card_pos = find_model_card_in_image(screenshot, model_name)
    
    if not card_pos:
        # Thử với partial match
        model_parts = model_name.split()
        if len(model_parts) > 0:
            print(f"   🔄 Thử với partial match: {model_parts[0]}")
            card_pos = find_model_card_in_image(screenshot, model_parts[0])
    
    if card_pos:
        # Convert relative position to screen coordinates
        screen_x = window_pos[0] + card_pos[0]
        screen_y = window_pos[1] + card_pos[1]
        
        print(f"   📍 Tìm thấy tại: ({screen_x}, {screen_y})")
        print(f"   🖱️  Đang click...")
        
        success = click_at_screen_position(screen_x, screen_y)
        
        if success:
            print(f"   ✅ Đã click vào model card")
            return True
        else:
            print(f"   ❌ Click failed")
    else:
        print(f"   ❌ Không tìm thấy model card trong screenshot")
    
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
    for chat in detected_chats:
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

