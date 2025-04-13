#!/bin/bash

# Script to run the frontend in development mode with debug options

echo "Starting frontend development server with debug options..."

# Change to the frontend directory
cd frontend

# Verify .env file exists and has VITE_API_BASE_URL
if [ -f .env ]; then
  echo "Found .env file:"
  grep -v "SECRET\|PASSWORD\|KEY" .env
  
  if ! grep -q "VITE_API_BASE_URL" .env; then
    echo "VITE_API_BASE_URL not found, adding it to .env..."
    echo "VITE_API_BASE_URL=http://localhost:5000" >> .env
  fi
else
  echo "Creating .env file..."
  echo "VITE_API_BASE_URL=http://localhost:5000" > .env
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Run the Vite development server with debug flags
echo "Starting Vite development server..."
export VITE_DEBUG=true

# Use npm run dev with additional flags for debugging
npx vite --host 0.0.0.0 --port 3000 --debug