#!/bin/bash
# Start the frontend development server

# Change to the frontend directory
cd frontend || { echo "Error: No frontend directory found"; exit 1; }

# Make sure node_modules exists
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Start the frontend development server
echo "Starting frontend on port 3000..."
npm run dev -- --host 0.0.0.0 --port 3000