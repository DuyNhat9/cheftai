#!/usr/bin/env python3
"""
Test script for image-based tab detection.
Tests screenshot capture, OCR, and tab switching.
"""
import sys
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

# Import auto_submit_service functions
import importlib.util
spec = importlib.util.spec_from_file_location('auto_submit_service', PROJECT_DIR / '.mcp' / 'auto_submit_service.py')
auto_submit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_submit)

def test_screenshot_capture():
    """Test screenshot capture."""
    print("📸 Test 1: Screenshot Capture")
    print("=" * 60)
    
    screenshot = auto_submit._capture_cursor_window_screenshot()
    if screenshot:
        print(f"✅ Screenshot captured: {screenshot.size}")
        
        # Save for inspection
        test_dir = PROJECT_DIR / ".mcp" / "test_screenshots"
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "test_capture.png"
        screenshot.save(test_file)
        print(f"✅ Saved to: {test_file}")
        return True
    else:
        print("❌ Screenshot capture failed")
        return False

def test_ocr_extraction():
    """Test OCR extraction."""
    print()
    print("🔤 Test 2: OCR Extraction")
    print("=" * 60)
    
    screenshot = auto_submit._capture_cursor_window_screenshot()
    if not screenshot:
        print("❌ Need screenshot first")
        return False
    
    tabs = auto_submit._extract_tab_labels_from_image(screenshot)
    print(f"✅ Extracted {len(tabs)} tab labels:")
    for tab in tabs:
        print(f"   - '{tab['label']}' at {tab['center']} (conf: {tab['confidence']})")
    
    return len(tabs) > 0

def test_tab_detection():
    """Test tab detection for specific model."""
    print()
    print("🎯 Test 3: Tab Detection")
    print("=" * 60)
    
    # Load detected chats
    STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])[:3]  # Test first 3
    
    for chat in detected_chats:
        model = chat.get('model')
        worktree_id = chat.get('worktree_id')
        agent_name = chat.get('agent_name')
        
        if not model:
            continue
        
        print(f"\n📌 Testing: {agent_name} → {model}")
        result = auto_submit._detect_tabs_by_screenshot(model, worktree_id)
        
        if result:
            print(f"   ✅ Found tab: '{result['label']}'")
            print(f"   📍 Coordinates: {result['screen_coords']}")
            print(f"   🎯 Confidence: {result['confidence']}")
        else:
            print(f"   ❌ Tab not found")

def test_full_switch():
    """Test full tab switching flow."""
    print()
    print("🔄 Test 4: Full Tab Switch Flow")
    print("=" * 60)
    
    # Load detected chats
    STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])[:2]  # Test first 2
    
    for chat in detected_chats:
        model = chat.get('model')
        worktree_id = chat.get('worktree_id')
        agent_name = chat.get('agent_name')
        chat_id = chat.get('chat_id')
        
        if not model:
            continue
        
        print(f"\n📌 Testing full switch: {agent_name} → {model}")
        result = auto_submit.switch_to_chat_tab(model, worktree_id, chat_id, max_retries=2)
        print(f"   Result: {result}")
        
        if "switched" in result or "already_on_tab" in result:
            print(f"   ✅ Success!")
        else:
            print(f"   ⚠️  Failed or not found")

def main():
    """Run all tests."""
    print("🧪 Image Detection Test Suite")
    print("=" * 60)
    print()
    
    # Check if image detection is available
    if not auto_submit.IMAGE_DETECTION_AVAILABLE:
        print("❌ Image detection dependencies not available")
        print("   Run: pip install pyautogui pytesseract opencv-python Pillow")
        print("   And: brew install tesseract")
        return 1
    
    print("✅ Image detection available")
    print()
    
    results = []
    
    # Test 1: Screenshot
    results.append(("Screenshot Capture", test_screenshot_capture()))
    
    # Test 2: OCR
    results.append(("OCR Extraction", test_ocr_extraction()))
    
    # Test 3: Tab Detection
    try:
        test_tab_detection()
        results.append(("Tab Detection", True))
    except Exception as e:
        print(f"❌ Tab detection test error: {e}")
        results.append(("Tab Detection", False))
    
    # Test 4: Full Switch (optional, may take time)
    print()
    response = input("Run full tab switch test? (y/n): ").strip().lower()
    if response == 'y':
        try:
            test_full_switch()
            results.append(("Full Switch", True))
        except Exception as e:
            print(f"❌ Full switch test error: {e}")
            results.append(("Full Switch", False))
    else:
        results.append(("Full Switch", "Skipped"))
    
    # Summary
    print()
    print("=" * 60)
    print("📊 Test Summary:")
    for test_name, result in results:
        status = "✅" if result is True else "❌" if result is False else "⏭️"
        print(f"   {status} {test_name}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

