#!/bin/bash

cd frontend

# Run Vite development server with host parameter to make it accessible
# from outside the container
npm run dev -- --host 0.0.0.0