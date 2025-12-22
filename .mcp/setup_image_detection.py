#!/usr/bin/env python3
"""
Setup and calibration script for image-based tab detection.
Verifies dependencies, tests screenshot capture, and calibrates tab bar region.
"""
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    print("=" * 60)
    
    missing = []
    
    try:
        import pyautogui
        print("✅ pyautogui installed")
    except ImportError:
        print("❌ pyautogui not installed")
        missing.append("pyautogui")
    
    try:
        import pytesseract
        print("✅ pytesseract installed")
    except ImportError:
        print("❌ pytesseract not installed")
        missing.append("pytesseract")
    
    try:
        import cv2
        print("✅ opencv-python installed")
    except ImportError:
        print("❌ opencv-python not installed")
        missing.append("opencv-python")
    
    try:
        from PIL import Image
        print("✅ Pillow installed")
    except ImportError:
        print("❌ Pillow not installed")
        missing.append("Pillow")
    
    # Check Tesseract OCR
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR installed")
    except Exception as e:
        print(f"❌ Tesseract OCR not found: {e}")
        print("   Install: brew install tesseract (macOS)")
        missing.append("tesseract")
    
    print()
    if missing:
        print("❌ Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print()
        print("💡 Install with:")
        print(f"   pip install {' '.join(missing)}")
        if "tesseract" in missing:
            print("   brew install tesseract")
        return False
    else:
        print("✅ All dependencies installed!")
        return True

def test_screenshot():
    """Test screenshot capture of Cursor window."""
    print()
    print("📸 Testing screenshot capture...")
    print("=" * 60)
    
    try:
        import pyautogui
        import subprocess
        
        # Check if Cursor is running
        script = '''
        tell application "System Events"
            try
                set cursorApp to first application process whose name is "Cursor"
                return "running"
            on error
                return "not_running"
            end try
        end tell
        '''
        
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "not_running" in result.stdout.strip():
            print("⚠️  Cursor is not running")
            print("   Please open Cursor and try again")
            return False
        
        # Get window bounds
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
        
        if result.returncode != 0:
            print("❌ Failed to get window bounds")
            return False
        
        bounds = [int(x.strip()) for x in result.stdout.strip().split(",")]
        x, y, width, height = bounds
        
        print(f"✅ Window bounds: {width}x{height} at ({x}, {y})")
        
        # Capture screenshot
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        print(f"✅ Screenshot captured: {screenshot.size}")
        
        # Save for inspection
        test_dir = PROJECT_DIR / ".mcp" / "test_screenshots"
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "cursor_window_test.png"
        screenshot.save(test_file)
        print(f"✅ Screenshot saved to: {test_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Screenshot test failed: {e}")
        return False

def test_ocr():
    """Test OCR on Cursor window."""
    print()
    print("🔤 Testing OCR extraction...")
    print("=" * 60)
    
    try:
        import pyautogui
        import pytesseract
        from PIL import Image
        import subprocess
        
        # Capture screenshot
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
        
        bounds = [int(x.strip()) for x in result.stdout.strip().split(",")]
        x, y, width, height = bounds
        
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Crop to tab bar (top 150px)
        tab_bar = screenshot.crop((0, 0, width, min(150, height // 4)))
        
        # Extract text
        text = pytesseract.image_to_string(tab_bar)
        print("📋 Extracted text from tab bar:")
        print("-" * 60)
        print(text)
        print("-" * 60)
        
        # Check for model keywords
        keywords = ["Sonnet", "GPT", "claude", "Pro", "Codex", "opus", "o3", "Gemini"]
        found = [kw for kw in keywords if kw.lower() in text.lower()]
        
        if found:
            print(f"✅ Found model keywords: {', '.join(found)}")
        else:
            print("⚠️  No model keywords found in OCR")
            print("   This is normal if tabs are not visible or OCR needs calibration")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def calibrate_tab_bar():
    """Calibrate tab bar region (user may need to adjust)."""
    print()
    print("⚙️  Tab Bar Calibration")
    print("=" * 60)
    print("Default tab bar region: Top 150px or 25% of window height")
    print("If tabs are not detected, you may need to adjust this value.")
    print()
    print("To calibrate:")
    print("1. Open Cursor with multiple chat tabs")
    print("2. Note the pixel height of the tab bar")
    print("3. Update TAB_BAR_HEIGHT in auto_submit_service.py if needed")
    print()
    
    # Save config
    config = {
        "tab_bar_height": 150,
        "tab_bar_percent": 25,
        "ocr_confidence_threshold": 30
    }
    
    config_file = PROJECT_DIR / ".mcp" / "image_detection_config.json"
    import json
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Default config saved to: {config_file}")
    return True

def main():
    """Run all setup checks."""
    print("🔧 Image Detection Setup for Cursor Tab Switching")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check dependencies
    if not check_dependencies():
        all_ok = False
        print()
        print("❌ Please install missing dependencies first")
        return 1
    
    # Test screenshot
    if not test_screenshot():
        all_ok = False
    
    # Test OCR
    if not test_ocr():
        all_ok = False
    
    # Calibrate
    calibrate_tab_bar()
    
    print()
    print("=" * 60)
    if all_ok:
        print("✅ Setup complete! Image detection is ready to use.")
    else:
        print("⚠️  Setup completed with warnings. Check output above.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

