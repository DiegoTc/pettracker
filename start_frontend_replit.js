// This script starts the frontend Vite server from Node.js
// It's designed to work with Replit's environment

const { spawn } = require('child_process');
const path = require('path');
const process = require('process');

// Change to the frontend directory
process.chdir(path.join(__dirname, 'frontend'));

console.log('Starting frontend development server...');

// Run the Vite dev server
const viteProcess = spawn('npm', ['run', 'dev', '--', '--host', '0.0.0.0', '--port', '3000'], {
  stdio: 'inherit',
  shell: true
});

viteProcess.on('error', (err) => {
  console.error('Failed to start Vite server:', err);
});

// Handle exit
process.on('SIGINT', () => {
  console.log('Shutting down Vite server...');
  viteProcess.kill();
  process.exit(0);
});