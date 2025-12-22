#!/usr/bin/env bash
set -euo pipefail

cd /Users/davidtran/Documents/cheftAi

echo "==> Testing macOS UI automation (System Events keystroke) via TextEdit..."
osascript <<'APPLESCRIPT'
set marker to "ACCESSIBILITY_TEST_456"
try
  tell application "System Events"
    set frontAppBefore to name of first application process whose frontmost is true
  end tell
  set report to "Frontmost(before): " & frontAppBefore & linefeed

  tell application "TextEdit"
    activate
    if (count of documents) = 0 then make new document
  end tell
  delay 1.2
  tell application "System Events"
    tell process "TextEdit" to set frontmost to true
    delay 0.5
    -- Try to focus the editor area (best effort; varies by macOS versions)
    try
      click (text area 1 of scroll area 1 of window 1 of process "TextEdit")
    end try
    delay 0.2
    tell process "TextEdit"
      keystroke "a" using {command down}
      keystroke marker
    end tell
  end tell
  delay 0.3
  tell application "TextEdit" to set docText to text of front document
  -- Fallback validation: select all + copy, then check clipboard
  tell application "System Events"
    tell process "TextEdit"
      keystroke "a" using {command down}
      delay 0.1
      keystroke "c" using {command down}
      delay 0.1
    end tell
  end tell
  set clipText to (the clipboard as text)

  if docText contains marker or clipText contains marker then
    set report to report & "OK: keystroke delivered" & linefeed
  else
    set report to report & "FAIL: keystroke not delivered - check Accessibility and Automation permissions" & linefeed
  end if

  tell application "System Events"
    set frontAppAfter to name of first application process whose frontmost is true
  end tell
  set report to report & "Frontmost(after): " & frontAppAfter & linefeed
  return report
on error errMsg number errNum
  return "ERROR:" & errNum & ":" & errMsg
end try
APPLESCRIPT

echo "==> Done."
