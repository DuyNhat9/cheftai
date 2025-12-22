#!/usr/bin/env bash
set -euo pipefail

# Dump Accessibility tree around the *focused* element in Cursor (fast).
#
# How to use:
# 1) In Cursor, click exactly where you want to inspect (e.g. Composer input, agent chip).
# 2) Run:
#    scripts/dump_cursor_focus_ax.sh
#    scripts/dump_cursor_focus_ax.sh Backend_AI_Dev   # optional keyword filter
#
# Requires: System Settings → Privacy & Security → Accessibility: Terminal ON

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
  return my safeStr(my getAttr(el, "AXRole"))
end getRole

on getTitle(el)
  return my safeStr(my getAttr(el, "AXTitle"))
end getTitle

on getDesc(el)
  return my safeStr(my getAttr(el, "AXDescription"))
end getDesc

on getId(el)
  return my safeStr(my getAttr(el, "AXIdentifier"))
end getId

on containsCI(hay, needle)
  set h to (my safeStr(hay))
  set n to (my safeStr(needle))
  if n is "" then return true
  try
    set h2 to do shell script "python3 - <<'PY'\nimport sys\nh=sys.argv[1].lower(); n=sys.argv[2].lower()\nprint('1' if n in h else '0')\nPY" & space & quoted form of h & space & quoted form of n
    return h2 is "1"
  on error
    return h contains n
  end try
end containsCI

on printNode(el, depth, keyword)
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
end printNode

on dumpSubtree(el, depth, keyword, maxDepth, maxKids)
  if depth > maxDepth then return
  my printNode(el, depth, keyword)
  try
    tell application "System Events"
      set kids to UI elements of el
    end tell
    set i to 0
    repeat with k in kids
      set i to i + 1
      if i > maxKids then exit repeat
      my dumpSubtree(k, depth + 1, keyword, maxDepth, maxKids)
    end repeat
  end try
end dumpSubtree

on run argv
  set keyword to ""
  if (count of argv) ≥ 1 then set keyword to item 1 of argv

  tell application "System Events"
    if not (exists process "Cursor") then error "Cursor process not found. Open Cursor first."
    set p to process "Cursor"
    set frontmost of p to true
  end tell
  delay 0.2

  tell application "System Events"
    try
      set focusedEl to value of attribute "AXFocusedUIElement" of process "Cursor"
    on error
      set focusedEl to missing value
    end try
  end tell

  if focusedEl is missing value then
    error "No AXFocusedUIElement. Click into Cursor Composer input (or an agent chip) then run again."
  end if

  log "=== Cursor FOCUSED AX dump (filtered by: " & (keyword as text) & ") ==="
  -- Helpful context: window title (if available)
  try
    set w to my getAttr(focusedEl, "AXWindow")
    if w is not missing value then
      set wt to my safeStr(my getAttr(w, "AXTitle"))
      if wt is not "" then log "window=\"" & wt & "\""
    end if
  end try
  log "--- focused element ---"
  my dumpSubtree(focusedEl, 0, keyword, 6, 60)

  -- Friendly hint when user accidentally focuses the integrated terminal.
  try
    set r to my getRole(focusedEl)
    set d to my getDesc(focusedEl)
    if (r is "AXTextField") and (d contains "Terminal") then
      log "HINT: Bạn đang focus vào Terminal panel. Hãy click vào ô input Composer/Chat (chỗ gõ prompt) rồi chạy lại."
    end if
  end try

  -- Try to also dump the immediate parent chain for context.
  log "--- parent chain (up to 10) ---"
  set cur to focusedEl
  repeat with i from 1 to 10
    set parentEl to my getAttr(cur, "AXParent")
    if parentEl is missing value then exit repeat
    my printNode(parentEl, i, keyword)
    set cur to parentEl
  end repeat

  log "=== done ==="
end run
APPLESCRIPT


