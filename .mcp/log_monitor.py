#!/usr/bin/env python3
"""
Log Monitor - Real-time log viewer cho CheftAi Multi-Agent System
Monitor multiple log files với color coding và filtering
"""
import sys
import os
import time
import re
from pathlib import Path
from datetime import datetime
from collections import deque

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Log levels
    ERROR = '\033[91m'  # Red
    WARNING = '\033[93m'  # Yellow
    INFO = '\033[94m'  # Blue
    SUCCESS = '\033[92m'  # Green
    DEBUG = '\033[90m'  # Gray
    
    # Services
    API_SERVER = '\033[96m'  # Cyan
    AUTO_SUBMIT = '\033[95m'  # Magenta
    DASHBOARD = '\033[93m'  # Yellow
    GENERAL = '\033[97m'  # White

# Log file paths
LOG_DIR = Path('/tmp')
LOG_FILES = {
    'api': LOG_DIR / 'api_server.log',
    'dashboard': LOG_DIR / 'dashboard_server.log',
    'auto_submit': LOG_DIR / 'auto_submit.log',
    'general': LOG_DIR / 'cheftai.log',
}

# Pattern matching cho log levels
PATTERNS = {
    'error': re.compile(r'(?i)(error|failed|exception|traceback|❌)'),
    'warning': re.compile(r'(?i)(warning|warn|⚠️|caution)'),
    'success': re.compile(r'(?i)(success|✅|ok|completed|done)'),
    'info': re.compile(r'(?i)(info|ℹ️|note|notice)'),
    'api': re.compile(r'(?i)(api|endpoint|request|response|/api/)'),
    'auto_submit': re.compile(r'(?i)(auto.?submit|cursor|chat|window|agent)'),
    'trigger': re.compile(r'(?i)(trigger|task|agent|shared_state)'),
}

def get_color_for_line(line, service='general'):
    """Determine color for log line based on content"""
    line_lower = line.lower()
    
    # Check for error patterns
    if any(pattern.search(line) for pattern in [PATTERNS['error']]):
        return Colors.ERROR
    
    # Check for warning patterns
    if any(pattern.search(line) for pattern in [PATTERNS['warning']]):
        return Colors.WARNING
    
    # Check for success patterns
    if any(pattern.search(line) for pattern in [PATTERNS['success']]):
        return Colors.SUCCESS
    
    # Service-specific colors
    if service == 'api':
        if PATTERNS['api'].search(line):
            return Colors.API_SERVER
    elif service == 'auto_submit':
        if PATTERNS['auto_submit'].search(line):
            return Colors.AUTO_SUBMIT
    
    # Info/default
    if PATTERNS['info'].search(line):
        return Colors.INFO
    
    return Colors.GENERAL

def format_timestamp():
    """Get formatted timestamp"""
    return datetime.now().strftime('%H:%M:%S')

def format_service_name(service):
    """Format service name with color"""
    colors = {
        'api': Colors.API_SERVER,
        'auto_submit': Colors.AUTO_SUBMIT,
        'dashboard': Colors.DASHBOARD,
        'general': Colors.GENERAL,
    }
    color = colors.get(service, Colors.GENERAL)
    return f"{color}[{service.upper()}]{Colors.RESET}"

def tail_file(file_path, service_name, filter_pattern=None, max_lines=1000):
    """Tail a file and yield new lines"""
    if not file_path.exists():
        print(f"{Colors.WARNING}⚠️  Log file not found: {file_path}{Colors.RESET}")
        return
    
    # Read existing content (last N lines)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            # Get last N lines
            lines = all_lines[-max_lines:] if len(all_lines) > max_lines else all_lines
            # Print last few lines
            for line in lines[-10:]:
                if filter_pattern is None or filter_pattern.search(line):
                    color = get_color_for_line(line, service_name)
                    print(f"{format_timestamp()} {format_service_name(service_name)} {color}{line.rstrip()}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.ERROR}Error reading {file_path}: {e}{Colors.RESET}")
        return
    
    # Monitor for new lines
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Seek to end
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    if filter_pattern is None or filter_pattern.search(line):
                        color = get_color_for_line(line, service_name)
                        print(f"{format_timestamp()} {format_service_name(service_name)} {color}{line.rstrip()}{Colors.RESET}")
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n{Colors.INFO}Stopping monitor for {service_name}...{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.ERROR}Error monitoring {file_path}: {e}{Colors.RESET}")

def monitor_all_logs(filter_pattern=None, services=None):
    """Monitor all log files"""
    import threading
    
    if services is None:
        services = list(LOG_FILES.keys())
    
    threads = []
    for service in services:
        if service not in LOG_FILES:
            print(f"{Colors.WARNING}Unknown service: {service}{Colors.RESET}")
            continue
        
        log_file = LOG_FILES[service]
        if not log_file.exists():
            print(f"{Colors.WARNING}⚠️  Log file not found: {log_file}{Colors.RESET}")
            print(f"   Start service to create log file")
            continue
        
        thread = threading.Thread(
            target=tail_file,
            args=(log_file, service, filter_pattern),
            daemon=True
        )
        thread.start()
        threads.append(thread)
    
    if not threads:
        print(f"{Colors.ERROR}No log files to monitor!{Colors.RESET}")
        print(f"\nAvailable log files:")
        for service, log_file in LOG_FILES.items():
            status = "✅" if log_file.exists() else "❌"
            print(f"  {status} {service}: {log_file}")
        return
    
    print(f"{Colors.SUCCESS}✅ Monitoring {len(threads)} log file(s)...{Colors.RESET}")
    print(f"{Colors.INFO}Press Ctrl+C to stop{Colors.RESET}\n")
    
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print(f"\n{Colors.INFO}Stopping all monitors...{Colors.RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Real-time log monitor cho CheftAi Multi-Agent System'
    )
    parser.add_argument(
        '-s', '--service',
        choices=list(LOG_FILES.keys()) + ['all'],
        default='all',
        help='Service to monitor (default: all)'
    )
    parser.add_argument(
        '-f', '--filter',
        help='Filter pattern (regex)'
    )
    parser.add_argument(
        '--error-only',
        action='store_true',
        help='Show only errors'
    )
    parser.add_argument(
        '--api-only',
        action='store_true',
        help='Show only API-related logs'
    )
    parser.add_argument(
        '--trigger-only',
        action='store_true',
        help='Show only trigger/agent-related logs'
    )
    
    args = parser.parse_args()
    
    # Build filter pattern
    filter_pattern = None
    if args.filter:
        filter_pattern = re.compile(args.filter, re.IGNORECASE)
    elif args.error_only:
        filter_pattern = PATTERNS['error']
    elif args.api_only:
        filter_pattern = PATTERNS['api']
    elif args.trigger_only:
        filter_pattern = PATTERNS['trigger']
    
    # Determine services to monitor
    services = None
    if args.service != 'all':
        services = [args.service]
    
    # Print header
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}🍳 CheftAi Multi-Agent System - Real-time Log Monitor{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"Log directory: {LOG_DIR}")
    print(f"Services: {', '.join(services) if services else 'all'}")
    if filter_pattern:
        print(f"Filter: {filter_pattern.pattern}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    # Start monitoring
    monitor_all_logs(filter_pattern, services)

if __name__ == "__main__":
    main()

