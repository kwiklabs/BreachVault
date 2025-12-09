#!/bin/bash
# Quick Docker control script for BreachVault
# Learn what each command does in DOCKER.md

case "$1" in
  start)
    docker compose up -d
    ;;
  stop)
    docker compose down
    ;;
  restart)
    docker compose restart
    ;;
  rebuild)
    docker compose build && docker compose up -d
    ;;
  logs)
    docker compose logs -f "${2:-}"
    ;;
  status)
    docker compose ps
    ;;
  *)
    echo "Usage: ./docker.sh {start|stop|restart|rebuild|logs [service]|status}"
    echo ""
    echo "Examples:"
    echo "  ./docker.sh start           # Start all services"
    echo "  ./docker.sh stop            # Stop all services"
    echo "  ./docker.sh restart         # Restart all services"
    echo "  ./docker.sh rebuild         # Rebuild and restart"
    echo "  ./docker.sh logs            # Follow all logs"
    echo "  ./docker.sh logs backend    # Follow backend logs only"
    echo "  ./docker.sh status          # Show running containers"
    echo ""
    echo "See DOCKER.md to learn what these commands actually do!"
    exit 1
    ;;
esac
