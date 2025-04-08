// This is a script to start the Vite development server
// that's compatible with Replit's environment
const { spawn } = require('child_process');
const path = require('path');

// Get the Vite binary from node_modules
const viteBin = path.join(__dirname, 'node_modules', '.bin', 'vite');

// Start Vite with the appropriate parameters
const viteProcess = spawn(viteBin, ['--host', '0.0.0.0'], {
  stdio: 'inherit',
  shell: true
});

// Handle exit
viteProcess.on('close', (code) => {
  console.log(`Vite process exited with code ${code}`);
});
