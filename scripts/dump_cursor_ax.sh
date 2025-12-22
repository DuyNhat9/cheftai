#!/usr/bin/env bash
set -euo pipefail

# Dump Cursor Accessibility (AX) UI tree and optionally filter by keyword.
#
# Usage:
#   scripts/dump_cursor_ax.sh                # dump top-level summary
#   scripts/dump_cursor_ax.sh Backend_AI_Dev # filter nodes containing keyword
#
# Notes:
# - Requires: System Settings → Privacy & Security → Accessibility: Terminal ON
# - Cursor must be running.

KEYWORD="${1:-}"

osascript - <<'APPLESCRIPT' "$KEYWORD"
on safeStr(v)
  try
    if v is missing value then return ""
    return v as text
  on error
    return ""
  end try
end safeStr

on getAttr(el, attrName)
  try
    tell application "System Events"
      return value of attribute attrName of el
    end tell
  on error
    return missing value
  end try
end getAttr

on getRole(el)
  set r to my getAttr(el, "AXRole")
  return my safeStr(r)
end getRole

on getTitle(el)
  set t to my getAttr(el, "AXTitle")
  return my safeStr(t)
end getTitle

on getDesc(el)
  set d to my getAttr(el, "AXDescription")
  return my safeStr(d)
end getDesc

on getId(el)
  set i to my getAttr(el, "AXIdentifier")
  return my safeStr(i)
end getId

on containsCI(hay, needle)
  set h to (my safeStr(hay))
  set n to (my safeStr(needle))
  if n is "" then return true
  try
    set h2 to do shell script "python3 - <<'PY'\nimport sys\nh=sys.argv[1].lower(); n=sys.argv[2].lower()\nprint('1' if n in h else '0')\nPY" & space & quoted form of h & space & quoted form of n
    return h2 is "1"
  on error
    -- fallback
    return h contains n
  end try
end containsCI

on dumpNode(el, depth, keyword)
  -- Cursor/Electron UIs can be deeply nested; allow deeper traversal.
  if depth > 30 then return

  set role to my getRole(el)
  set title to my getTitle(el)
  set desc to my getDesc(el)
  set ident to my getId(el)

  set hit to false
  if my containsCI(role, keyword) then set hit to true
  if my containsCI(title, keyword) then set hit to true
  if my containsCI(desc, keyword) then set hit to true
  if my containsCI(ident, keyword) then set hit to true

  if hit then
    set indent to ""
    repeat depth times
      set indent to indent & "  "
    end repeat
    set lineOut to indent & "- role=" & role
    if title is not "" then set lineOut to lineOut & " title=\"" & title & "\""
    if desc is not "" then set lineOut to lineOut & " desc=\"" & desc & "\""
    if ident is not "" then set lineOut to lineOut & " id=\"" & ident & "\""
    log lineOut
  end if

  try
    tell application "System Events"
      set kids to UI elements of el
    end tell
    repeat with k in kids
      my dumpNode(k, depth + 1, keyword)
    end repeat
  end try
end dumpNode

on run argv
  set keyword to ""
  if (count of argv) ≥ 1 then set keyword to item 1 of argv

  tell application "System Events"
    if not (exists process "Cursor") then error "Cursor process not found. Open Cursor first."
    set p to process "Cursor"
    set frontmost of p to true
  end tell
  delay 0.5

  log "=== Cursor AX dump (filtered by: " & (keyword as text) & ") ==="
  tell application "System Events"
    set root to process "Cursor"
    set wins to windows of root
  end tell
  log "windows=" & (count of wins)
  if (count of wins) > 0 then
    repeat with w in wins
      my dumpNode(w, 0, keyword)
    end repeat
  else
    -- Some Cursor builds don't expose AXWindows; traverse from the process root.
    my dumpNode(root, 0, keyword)
  end if
  log "=== done ==="
end run
APPLESCRIPT


