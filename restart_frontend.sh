#!/bin/bash

# Stop any running npm processes
echo "Stopping any running frontend processes..."
pkill -f "npm run dev" || true
pkill -f "node" || true

# Wait a moment
sleep 2

# Navigate to frontend directory
cd frontend

# Clear any cache if needed
echo "Clearing Vite cache..."
rm -rf node_modules/.vite || true

# Start the frontend in the background
echo "Starting frontend server on port 3000..."
npm run dev -- --host 0.0.0.0 &

# Wait for it to start
sleep 5

echo "Frontend server should now be running at http://localhost:3000"
echo "You may need to restart your browser or clear cache to see changes"