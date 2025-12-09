#!/bin/bash
# Control script for parallel import workers

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PID_FILE="/tmp/breachvault_import.pid"
LOG_FILE="/tmp/breachvault_import.log"

show_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            WORKER_COUNT=$(pgrep -P "$PID" | wc -l)
            echo -e "${GREEN}✓ Import running${NC}"
            echo -e "  PID: $PID"
            echo -e "  Workers: $WORKER_COUNT"
            echo -e "  Log: $LOG_FILE"
            
            # Show current database count
            DB_COUNT=$(sudo docker compose exec -T postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes;" 2>/dev/null | xargs || echo "0")
            echo -e "  Database: $(printf "%'d" $DB_COUNT) passwords"
        else
            echo -e "${YELLOW}⚠ Import stopped (stale PID file)${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${BLUE}○ No import running${NC}"
    fi
}

start_import() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠ Import already running (PID: $PID)${NC}"
            echo "Use 'stop' to stop it first"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    echo -e "${CYAN}🚀 Starting parallel import...${NC}"
    
    # Run import in background and save PID
    nohup ./parallel-import.sh > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Import started${NC}"
        echo -e "  PID: $(cat $PID_FILE)"
        echo -e "  Log: $LOG_FILE"
        echo ""
        echo -e "${CYAN}Monitor with:${NC} ./monitor-import.sh"
        echo -e "${CYAN}View logs:${NC} tail -f $LOG_FILE"
    else
        echo -e "${RED}✗ Failed to start import${NC}"
        cat "$LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop_import() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}⚠ No import running${NC}"
        exit 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Import not running (cleaning up)${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    
    echo -e "${YELLOW}⏸  Stopping import (PID: $PID)...${NC}"
    
    # Kill process group (parent + all workers)
    pkill -P "$PID" 2>/dev/null || true
    kill "$PID" 2>/dev/null || true
    
    sleep 2
    
    # Force kill if still running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${RED}Force killing...${NC}"
        pkill -9 -P "$PID" 2>/dev/null || true
        kill -9 "$PID" 2>/dev/null || true
    fi
    
    rm -f "$PID_FILE"
    echo -e "${GREEN}✓ Import stopped${NC}"
}

restart_import() {
    echo -e "${CYAN}🔄 Restarting import...${NC}"
    stop_import 2>/dev/null || true
    sleep 1
    start_import
}

view_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${YELLOW}⚠ No log file found${NC}"
        exit 1
    fi
}

case "${1:-status}" in
    start)
        start_import
        ;;
    stop)
        stop_import
        ;;
    restart)
        restart_import
        ;;
    status)
        show_status
        ;;
    logs)
        view_logs
        ;;
    *)
        echo "BreachVault Import Control"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start parallel import in background"
        echo "  stop     - Stop all import workers"
        echo "  restart  - Restart import"
        echo "  status   - Show current status"
        echo "  logs     - View live logs"
        echo ""
        echo "Current status:"
        show_status
        exit 1
        ;;
esac
