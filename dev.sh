#!/bin/bash

# GeoAI - Unified Development Server Starter
# This script launches both the FastAPI backend and Vite frontend.

# Styling
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}========================================${NC}"
echo -e "${BOLD}${BLUE}   GeoAI Development Environment 🚀   ${NC}"
echo -e "${BOLD}${BLUE}========================================${NC}"

# Function to stop background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    # Send SIGTERM to the process group
    kill $(jobs -p) 2>/dev/null
    echo -e "${GREEN}✅ Servers stopped successfully.${NC}"
    exit
}

# Trap Ctrl+C (SIGINT) and SIGTERM (for graceful shutdown)
trap cleanup SIGINT SIGTERM

# Check for Database (PostgreSQL/PostGIS)
echo -e "${YELLOW}🔍 Checking Database Status...${NC}"
if nc -z localhost 5433 2>/dev/null; then
    echo -e "${GREEN}✅ Database is reachable on port 5433.${NC}"
else
    echo -e "${RED}⚠️  Database (PostGIS) not detected on localhost:5433.${NC}"
    echo -e "${YELLOW}💡 Tip: Run 'docker-compose up -d db' to start the database.${NC}"
fi

echo -e "\n"

# 1. Start Backend
echo -e "${GREEN}🐍 Starting Backend (FastAPI)...${NC}"
echo -e "${BOLD}   URL: http://localhost:8000${NC}"
# Use python3 as it is standard on mac and used in the current terminal sessions
python3 backend/src/main.py &
BACKEND_PID=$!

# 2. Start Frontend
echo -e "${BLUE}⚛️  Starting Frontend (Vite)...${NC}"
echo -e "${BOLD}   URL: http://localhost:5173${NC}"
# Run in subshell to avoid changing the script's working directory permanently
(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo -e "\n${YELLOW}💡 Press Ctrl+C to stop both servers whenever you're done.${NC}"
echo -e "${BOLD}${BLUE}----------------------------------------${NC}"

# Wait for processes to keep the script running and the trap active
wait $BACKEND_PID $FRONTEND_PID
