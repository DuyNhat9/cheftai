#!/bin/bash
# Quick log viewer - Simple aliases cho common log operations

case "$1" in
    all|"")
        # Monitor all logs
        ./scripts/monitor_logs.sh
        ;;
    api)
        # Monitor API server only
        ./scripts/monitor_logs.sh -s api
        ;;
    submit|auto)
        # Monitor auto-submit only
        ./scripts/monitor_logs.sh -s auto_submit
        ;;
    dashboard|dash)
        # Monitor dashboard only
        ./scripts/monitor_logs.sh -s dashboard
        ;;
    error|err)
        # Show only errors
        ./scripts/monitor_logs.sh --error-only
        ;;
    trigger|trig)
        # Show only triggers
        ./scripts/monitor_logs.sh --trigger-only
        ;;
    tail)
        # Quick tail of API log
        tail -f /tmp/api_server.log
        ;;
    *)
        echo "Usage: $0 [all|api|submit|dashboard|error|trigger|tail]"
        echo ""
        echo "Quick commands:"
        echo "  $0          - Monitor all logs"
        echo "  $0 api      - Monitor API server"
        echo "  $0 submit   - Monitor auto-submit"
        echo "  $0 dashboard - Monitor dashboard"
        echo "  $0 error    - Show only errors"
        echo "  $0 trigger - Show only triggers"
        echo "  $0 tail     - Tail API log file"
        exit 1
        ;;
esac

