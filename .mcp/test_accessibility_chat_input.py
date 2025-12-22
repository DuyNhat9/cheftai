#!/usr/bin/env python3
"""
Test script để kiểm tra Accessibility API có thể tìm chat input trong Cursor không
"""
import subprocess
import time

def test_find_chat_input():
    """Test tìm chat input element bằng Accessibility API"""
    script = '''
    tell application "System Events"
        try
            set cursorApp to first application process whose name is "Cursor"
        on error
            return "app_not_running"
        end try
        
        set windowCount to count of windows of cursorApp
        if windowCount = 0 then
            return "no_windows"
        end if
        
        set frontmost of cursorApp to true
        delay 0.5
        
        -- Mở chat panel
        keystroke "l" using {command down}
        delay 2.0
        
        -- Tìm tất cả UI elements trong window
        tell process "Cursor"
            set mainWindow to window 1
            set allElements to every UI element of mainWindow
            
            -- Tìm text fields
            try
                set textFields to (text fields of mainWindow)
                log "DEBUG_FOUND_TEXT_FIELDS: " & (count of textFields)
                
                repeat with tf in textFields
                    try
                        set tfRole to role description of tf
                        set tfName to name of tf
                        log "DEBUG_TEXT_FIELD: role=" & tfRole & ", name=" & tfName
                    end try
                end repeat
            end try
            
            -- Tìm text areas
            try
                set textAreas to (text areas of mainWindow)
                log "DEBUG_FOUND_TEXT_AREAS: " & (count of textAreas)
                
                repeat with ta in textAreas
                    try
                        set taRole to role description of ta
                        set taName to name of ta
                        log "DEBUG_TEXT_AREA: role=" & taRole & ", name=" & taName
                    end try
                end repeat
            end try
            
            -- Tìm scroll areas (chat panel thường có scroll)
            try
                set scrollAreas to (scroll areas of mainWindow)
                log "DEBUG_FOUND_SCROLL_AREAS: " & (count of scrollAreas)
            end try
            
            -- Tìm groups (chat panel có thể là group)
            try
                set groups to (groups of mainWindow)
                log "DEBUG_FOUND_GROUPS: " & (count of groups)
                
                repeat with g in groups
                    try
                        set gName to name of g
                        if gName is not "" then
                            log "DEBUG_GROUP: name=" & gName
                        end if
                    end try
                end repeat
            end try
            
        end tell
        
        return "done"
    end tell
    '''
    
    print("🔍 Testing Accessibility API để tìm chat input...")
    print("📋 Đảm bảo Cursor đang mở và chat panel đã được mở (Cmd+L)")
    print("")
    
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print("=== STDOUT ===")
    print(result.stdout)
    print("")
    print("=== STDERR (Debug logs) ===")
    for line in result.stderr.strip().split('\n'):
        if 'DEBUG_' in line:
            print(line)
    print("")
    
    if result.returncode == 0:
        print("✅ Script chạy thành công")
    else:
        print(f"❌ Script failed với return code: {result.returncode}")

if __name__ == "__main__":
    test_find_chat_input()

