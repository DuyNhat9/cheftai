#!/usr/bin/env python3
"""
Debug script để xem cấu trúc UI của Cursor window
Giúp tìm cách access tabs hoặc chat panes
"""
import subprocess

def debug_cursor_ui():
    """Debug Cursor UI structure"""
    
    print("🔍 Debugging Cursor UI Structure")
    print("=" * 60)
    
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
        set windowTitle to title of mainWindow as string
        
        set output to "Window Title: " & windowTitle & "\\n\\n"
        
        -- List all UI elements
        set output to output & "=== UI Elements ===\\n"
        try
            set uiElements to every UI element of mainWindow
            repeat with elem in uiElements
                try
                    set elemClass to class of elem as string
                    set elemTitle to ""
                    try
                        set elemTitle to title of elem as string
                    end try
                    set output to output & "  - " & elemClass & ": " & elemTitle & "\\n"
                end try
            end repeat
        end try
        
        -- Check for tab groups
        set output to output & "\\n=== Tab Groups ===\\n"
        try
            set tabGroups to every tab group of mainWindow
            repeat with tg in tabGroups
                try
                    set tgTitle to title of tg as string
                    set output to output & "  Tab Group: " & tgTitle & "\\n"
                    try
                        set tabs to every tab of tg
                        repeat with aTab in tabs
                            try
                                set tabTitle to title of aTab as string
                                set output to output & "    - Tab: " & tabTitle & "\\n"
                            end try
                        end repeat
                    end try
                end try
            end repeat
        end try
        
        -- Check for buttons (có thể là tab buttons)
        set output to output & "\\n=== Buttons ===\\n"
        try
            set buttons to every button of mainWindow
            repeat with b in buttons
                try
                    set btnName to name of b as string
                    set btnTitle to ""
                    try
                        set btnTitle to title of b as string
                    end try
                    if btnName is not "" or btnTitle is not "" then
                        set output to output & "  - Button: " & btnName & " (" & btnTitle & ")\\n"
                    end if
                end try
            end repeat
        end try
        
        -- Check for menu items (có thể có View menu với tabs)
        set output to output & "\\n=== Menu Bar ===\\n"
        try
            set menuBar to menu bar 1 of cursorApp
            set menus to every menu of menuBar
            repeat with m in menus
                try
                    set menuName to name of m as string
                    set output to output & "  Menu: " & menuName & "\\n"
                    if menuName is "View" then
                        set menuItems to every menu item of m
                        repeat with mi in menuItems
                            try
                                set itemName to name of mi as string
                                set output to output & "    - " & itemName & "\\n"
                            end try
                        end repeat
                    end if
                end try
            end repeat
        end try
        
        return output
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
            print(result.stdout)
            if result.stderr:
                print("\nStderr:")
                print(result.stderr)
        else:
            print(f"❌ Error: {result.returncode}")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_cursor_ui()

