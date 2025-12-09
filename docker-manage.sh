#!/bin/bash

# BreachVault Docker Management Script
# Easy commands to manage your Docker deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓ ${NC}$1"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${NC}$1"
}

print_error() {
    echo -e "${RED}✗ ${NC}$1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to show usage
show_usage() {
    cat << EOF
${GREEN}BreachVault Docker Management${NC}

Usage: ./docker-manage.sh [command]

${BLUE}Commands:${NC}
  start         Start all services
  stop          Stop all services
  restart       Restart all services
  rebuild       Rebuild and restart (updates code changes)
  logs          View logs (all services)
  logs-backend  View backend logs
  logs-frontend View frontend logs
  status        Show service status
  clean         Stop and remove containers (keeps data)
  reset         Clean everything including data (DANGEROUS!)
  shell         Open shell in backend container
  db            Open PostgreSQL shell
  update        Pull latest code and rebuild

${YELLOW}Examples:${NC}
  ./docker-manage.sh start
  ./docker-manage.sh rebuild
  ./docker-manage.sh logs-backend

EOF
}

# Function to start services
cmd_start() {
    print_info "Starting BreachVault services..."
    docker compose up -d
    print_success "Services started!"
    print_info "Frontend: http://localhost:3000"
    print_info "Backend API: http://localhost:8000"
    print_info "API Docs: http://localhost:8000/docs"
}

# Function to stop services
cmd_stop() {
    print_info "Stopping BreachVault services..."
    docker compose down
    print_success "Services stopped!"
}

# Function to restart services
cmd_restart() {
    print_info "Restarting BreachVault services..."
    docker compose restart
    print_success "Services restarted!"
}

# Function to rebuild and restart (for code updates)
cmd_rebuild() {
    print_warning "Rebuilding containers (this will apply code changes)..."
    print_info "Stopping services..."
    docker compose down
    
    print_info "Building images..."
    docker compose build --no-cache
    
    print_info "Starting services..."
    docker compose up -d
    
    print_success "Rebuild complete! Services are running."
    print_info "Frontend: http://localhost:3000"
    print_info "Backend API: http://localhost:8000"
}

# Function to view logs
cmd_logs() {
    print_info "Showing logs (Ctrl+C to exit)..."
    docker compose logs -f
}

# Function to view backend logs
cmd_logs_backend() {
    print_info "Showing backend logs (Ctrl+C to exit)..."
    docker compose logs -f backend
}

# Function to view frontend logs
cmd_logs_frontend() {
    print_info "Showing frontend logs (Ctrl+C to exit)..."
    docker compose logs -f frontend
}

# Function to show status
cmd_status() {
    print_info "Service status:"
    docker compose ps
    echo ""
    print_info "Resource usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Function to clean (remove containers, keep data)
cmd_clean() {
    print_warning "This will stop and remove containers (database data will be kept)"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning containers..."
        docker compose down
        print_success "Containers removed. Data volumes preserved."
    else
        print_info "Cancelled."
    fi
}

# Function to reset (DANGEROUS - removes everything)
cmd_reset() {
    print_error "⚠️  DANGER: This will delete ALL data including the database!"
    print_warning "This cannot be undone!"
    read -p "Are you ABSOLUTELY sure? Type 'DELETE' to confirm: " -r
    echo
    if [[ $REPLY == "DELETE" ]]; then
        print_info "Stopping and removing everything..."
        docker compose down -v --remove-orphans
        print_success "Everything removed. Fresh start ready."
    else
        print_info "Cancelled (wise choice!)."
    fi
}

# Function to open shell in backend
cmd_shell() {
    print_info "Opening shell in backend container..."
    docker compose exec backend /bin/bash
}

# Function to open database shell
cmd_db() {
    print_info "Opening PostgreSQL shell..."
    docker compose exec postgres psql -U breachvault -d breachvault
}

# Function to pull updates and rebuild
cmd_update() {
    print_info "Pulling latest code from git..."
    git pull
    
    print_info "Rebuilding containers..."
    cmd_rebuild
    
    print_success "Update complete!"
}

# Main command handler
case "$1" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    rebuild)
        cmd_rebuild
        ;;
    logs)
        cmd_logs
        ;;
    logs-backend)
        cmd_logs_backend
        ;;
    logs-frontend)
        cmd_logs_frontend
        ;;
    status)
        cmd_status
        ;;
    clean)
        cmd_clean
        ;;
    reset)
        cmd_reset
        ;;
    shell)
        cmd_shell
        ;;
    db)
        cmd_db
        ;;
    update)
        cmd_update
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
