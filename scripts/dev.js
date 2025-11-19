#!/usr/bin/env node

/**
 * Development script for Suno React App
 * Starts both Python backend and Electron frontend
 */

const { spawn } = require('child_process');
const { existsSync } = require('fs');
const path = require('path');

// ANSI color codes for better output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

function log(message, color = 'white') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkRequirements() {
  log('🔍 Checking development requirements...', 'cyan');

  // Check if Python backend exists
  const backendPath = path.join(__dirname, '../backend/main.py');
  if (!existsSync(backendPath)) {
    log('❌ Python backend not found at ' + backendPath, 'red');
    process.exit(1);
  }
  log('✅ Python backend found', 'green');

  // Check if package.json exists
  const packagePath = path.join(__dirname, '../package.json');
  if (!existsSync(packagePath)) {
    log('❌ package.json not found', 'red');
    process.exit(1);
  }
  log('✅ package.json found', 'green');

  // Check if node_modules exists
  const nodeModulesPath = path.join(__dirname, '../node_modules');
  if (!existsSync(nodeModulesPath)) {
    log('⚠️  node_modules not found. Running npm install...', 'yellow');
    const npmInstall = spawn('npm', ['install'], {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });

    npmInstall.on('close', (code) => {
      if (code !== 0) {
        log('❌ npm install failed', 'red');
        process.exit(1);
      }
      log('✅ Dependencies installed', 'green');
      startDevelopment();
    });
  } else {
    startDevelopment();
  }
}

function startDevelopment() {
  log('🚀 Starting development environment...', 'cyan');
  log('', 'white');

  // Start Python backend
  log('🐍 Starting Python backend...', 'blue');
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  const backendProcess = spawn(pythonCmd, ['main.py'], {
    stdio: ['pipe', 'pipe', 'inherit'],
    cwd: path.join(__dirname, '../backend'),
    env: {
      ...process.env,
      PYTHONPATH: path.join(__dirname, '../src'),
      PYTHONUNBUFFERED: '1'
    }
  });

  // Handle Python backend output
  backendProcess.stdout.on('data', (data) => {
    const lines = data.toString().split('\n').filter(line => line.trim());
    lines.forEach(line => {
      try {
        const parsed = JSON.parse(line);
        if (parsed.type === 'BACKEND_READY') {
          log('✅ Python backend is ready', 'green');
        } else {
          log('📝 Python: ' + JSON.stringify(parsed), 'magenta');
        }
      } catch {
        log('📝 Python: ' + line, 'magenta');
      }
    });
  });

  backendProcess.on('error', (error) => {
    log('❌ Python backend error: ' + error.message, 'red');
  });

  backendProcess.on('close', (code) => {
    if (code !== 0) {
      log('❌ Python backend exited with code ' + code, 'red');
    } else {
      log('🔌 Python backend stopped', 'yellow');
    }
  });

  // Wait a bit for backend to start, then start Electron
  setTimeout(() => {
    log('⚡ Starting Electron + React...', 'blue');

    const electronProcess = spawn('npm', ['run', 'dev'], {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });

    electronProcess.on('error', (error) => {
      log('❌ Electron process error: ' + error.message, 'red');
    });

    electronProcess.on('close', (code) => {
      if (code !== 0) {
        log('❌ Electron process exited with code ' + code, 'red');
      } else {
        log('👋 Development environment stopped', 'yellow');
      }

      // Stop Python backend when Electron exits
      backendProcess.kill('SIGTERM');
      process.exit(code);
    });

    // Handle process termination
    process.on('SIGINT', () => {
      log('\n🛑 Shutting down development environment...', 'yellow');
      electronProcess.kill('SIGTERM');
      backendProcess.kill('SIGTERM');
    });

    process.on('SIGTERM', () => {
      log('\n🛑 Shutting down development environment...', 'yellow');
      electronProcess.kill('SIGTERM');
      backendProcess.kill('SIGTERM');
    });

  }, 2000);
}

// Start the development process
if (require.main === module) {
  checkRequirements();
}

module.exports = { checkRequirements, startDevelopment };