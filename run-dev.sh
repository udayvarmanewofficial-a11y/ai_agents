#!/bin/bash

# Run both backend and frontend in local dev mode
# Requires tmux to be installed

if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Install it with: brew install tmux"
    echo ""
    echo "Or run services separately:"
    echo "  Terminal 1: ./run-backend-dev.sh"
    echo "  Terminal 2: ./run-frontend-dev.sh"
    exit 1
fi

# Create a new tmux session
SESSION="planner-dev"

tmux new-session -d -s $SESSION

# Split window
tmux split-window -h -t $SESSION

# Run backend in left pane
tmux send-keys -t $SESSION:0.0 './run-backend-dev.sh' C-m

# Run frontend in right pane
tmux send-keys -t $SESSION:0.1 './run-frontend-dev.sh' C-m

# Attach to session
echo "Starting development servers in tmux session..."
echo "Use Ctrl+B then D to detach, 'tmux attach -t planner-dev' to reattach"
sleep 2
tmux attach -t $SESSION
