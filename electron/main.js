const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const net = require('net');
const axios = require('axios');

// Keep a global reference of the window object
let mainWindow;
let pythonProcess = null;
let backendPort = null;
let isDev = process.argv.includes('--dev');

// IMPORTANT: Detect if we're running in a packaged app
const isPackaged = app.isPackaged;

console.log(`Running mode: ${isPackaged ? 'PACKAGED' : 'DEVELOPMENT'}`);
console.log(`Development flag: ${isDev}`);

// Configuration
const CONFIG = {
  primaryPortRange: { start: 8000, end: 8020 },
  fallbackPortRange: { start: 9000, end: 9020 },
  healthCheckTimeout: 30000, // 30 seconds
  healthCheckInterval: 1000,  // 1 second
  maxStartupTime: 60000       // 60 seconds total
};

// Get the correct paths based on whether we're packaged or in development
function getPaths() {
  if (isPackaged) {
    // Packaged app - use bundled resources
    const resourcesPath = process.resourcesPath;
    // Add .exe extension on Windows
    const executableName = process.platform === 'win32' ? 'sentopic.exe' : 'sentopic';
    const pythonExecutable = path.join(resourcesPath, 'python-backend', executableName);
    const frontendPath = path.join(__dirname, 'frontend-dist', 'index.html');
    
    console.log('PACKAGED MODE PATHS:');
    console.log(`  Resources path: ${resourcesPath}`);
    console.log(`  Python executable: ${pythonExecutable}`);
    console.log(`  Frontend path: ${frontendPath}`);
    
    return {
      pythonExecutable,
      frontendPath,
      workingDirectory: path.dirname(pythonExecutable)
    };
  } else {
    // Development mode - use existing paths
    const projectRoot = path.dirname(__dirname);
    // Handle different virtual environment structures
    const pythonExecutable = process.platform === 'win32' 
      ? path.join(projectRoot, 'sentopic-env', 'Scripts', 'python.exe')
      : path.join(projectRoot, 'sentopic-env', 'bin', 'python');
    const runApiPath = path.join(projectRoot, 'run_api.py');
    const frontendPath = path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
    
    console.log('DEVELOPMENT MODE PATHS:');
    console.log(`  Project root: ${projectRoot}`);
    console.log(`  Python executable: ${pythonExecutable}`);
    console.log(`  run_api.py: ${runApiPath}`);
    console.log(`  Frontend path: ${frontendPath}`);
    
    return {
      pythonExecutable,
      runApiPath,
      frontendPath,
      workingDirectory: projectRoot
    };
  }
}

// FIXED: More robust port availability checking that detects conflicts properly
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    let resolved = false;
    
    // Set up error handler first
    server.on('error', (err) => {
      if (!resolved) {
        resolved = true;
        console.log(`   Port ${port}: UNAVAILABLE (${err.code})`);
        resolve(false);
      }
    });
    
    // FIXED: Bind to 0.0.0.0 instead of 127.0.0.1 to detect all conflicts
    // This will properly detect conflicts with servers bound to any interface
    server.listen(port, '0.0.0.0', () => {
      if (!resolved) {
        console.log(`   Port ${port}: AVAILABLE`);
        server.close(() => {
          if (!resolved) {
            resolved = true;
            resolve(true);
          }
        });
      }
    });
    
    // Timeout fallback to prevent hanging
    setTimeout(() => {
      if (!resolved) {
        resolved = true;
        console.log(`   Port ${port}: TIMEOUT (assuming unavailable)`);
        try {
          server.destroy();
        } catch (e) {
          // Ignore cleanup errors
        }
        resolve(false);
      }
    }, 2000); // Increased timeout slightly
  });
}

// Enhanced port finding with better error handling
async function findAvailablePort() {
  console.log('Looking for available port...');
  
  // Strategy 1: Try primary range (8000-8020)
  console.log(`Checking primary range: ${CONFIG.primaryPortRange.start}-${CONFIG.primaryPortRange.end}`);
  for (let port = CONFIG.primaryPortRange.start; port <= CONFIG.primaryPortRange.end; port++) {
    console.log(`Testing port ${port}...`);
    const available = await isPortAvailable(port);
    if (available) {
      console.log(`Found available port: ${port} (primary range)`);
      return port;
    }
  }
  
  // Strategy 2: Try fallback range (9000-9020)
  console.log('PRIMARY RANGE EXHAUSTED - SWITCHING TO FALLBACK RANGE');
  console.log(`Checking fallback range: ${CONFIG.fallbackPortRange.start}-${CONFIG.fallbackPortRange.end}`);
  for (let port = CONFIG.fallbackPortRange.start; port <= CONFIG.fallbackPortRange.end; port++) {
    console.log(`Testing fallback port ${port}...`);
    const available = await isPortAvailable(port);
    if (available) {
      console.log(`Found available port: ${port} (fallback range)`);
      return port;
    }
  }
  
  // Strategy 3: Get random available port from OS
  console.log('FALLBACK RANGE EXHAUSTED - REQUESTING OS PORT');
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    
    server.listen(0, '0.0.0.0', () => {
      const port = server.address().port;
      server.close(() => {
        console.log(`OS assigned port: ${port}`);
        resolve(port);
      });
    });
    
    server.on('error', (err) => {
      console.error('Failed to get OS-assigned port:', err);
      reject(new Error(`No available ports found. OS port assignment failed: ${err.message}`));
    });
  });
}

// Function to verify Python process is actually responding
async function verifyPythonProcess(port) {
  console.log('Verifying Python process...');
  
  if (!pythonProcess) {
    console.log('Python process is null');
    return false;
  }
  
  if (pythonProcess.killed) {
    console.log('Python process was killed');
    return false;
  }
  
  console.log(`Python process PID: ${pythonProcess.pid}`);
  console.log(`Python process exitCode: ${pythonProcess.exitCode}`);
  console.log(`Python process signalCode: ${pythonProcess.signalCode}`);
  
  // Try a simple TCP connection to the port
  return new Promise((resolve) => {
    const socket = new net.Socket();
    let resolved = false;
    
    socket.setTimeout(3000);
    
    socket.on('connect', () => {
      if (!resolved) {
        resolved = true;
        console.log(`TCP connection to port ${port} successful`);
        socket.destroy();
        resolve(true);
      }
    });
    
    socket.on('error', (err) => {
      if (!resolved) {
        resolved = true;
        console.log(`TCP connection to port ${port} failed: ${err.message}`);
        resolve(false);
      }
    });
    
    socket.on('timeout', () => {
      if (!resolved) {
        resolved = true;
        console.log(`TCP connection to port ${port} timed out`);
        socket.destroy();
        resolve(false);
      }
    });
    
    socket.connect(port, '127.0.0.1');
  });
}

// Health check with better debugging
async function waitForBackend(port, timeout = CONFIG.healthCheckTimeout) {
  const startTime = Date.now();
  const healthUrl = `http://127.0.0.1:${port}/health`;
  
  console.log(`Waiting for backend health check at ${healthUrl}...`);
  console.log(`Timeout configured for ${timeout}ms`);
  
  let attemptCount = 0;
  while (Date.now() - startTime < timeout) {
    attemptCount++;
    const elapsed = Date.now() - startTime;
    
    // Every 10 attempts, do a deeper check
    if (attemptCount % 10 === 0) {
      console.log(`Deep check at attempt ${attemptCount}...`);
      const processOk = await verifyPythonProcess(port);
      if (!processOk) {
        console.error('Python process verification failed - aborting health checks');
        return false;
      }
    }
    
    try {
      if (attemptCount <= 5 || attemptCount % 10 === 0) {
        console.log(`Health check attempt #${attemptCount} at ${elapsed}ms`);
      }
      
      const response = await axios.get(healthUrl, { 
        timeout: 2000,
        headers: {
          'User-Agent': 'Electron-HealthCheck'
        }
      });
      
      if (response.status === 200) {
        console.log('Backend health check passed!');
        console.log(`Response data: ${JSON.stringify(response.data)}`);
        return true;
      } else {
        console.log(`Unexpected status code: ${response.status}`);
      }
    } catch (error) {
      // Only log every 10th error to reduce noise
      if (attemptCount <= 5 || attemptCount % 10 === 0) {
        console.log(`Health check attempt #${attemptCount} failed:`);
        console.log(`   Error code: ${error.code || 'unknown'}`);
        console.log(`   Error message: ${error.message}`);
      }
      
      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, CONFIG.healthCheckInterval));
    }
  }
  
  console.error(`Backend health check failed - timeout reached after ${attemptCount} attempts`);
  console.error(`Total time elapsed: ${Date.now() - startTime}ms`);
  return false;
}

// Show error dialog to user
function showErrorDialog(title, message) {
  dialog.showErrorBox(title, `${message}\n\nPlease check the console for more details.`);
}

// Python backend startup with comprehensive debugging and mode detection
async function startPythonBackend() {
  try {
    console.log('STARTING PYTHON BACKEND PROCESS...');
    console.log('='.repeat(60));
    
    // Find available port FIRST
    console.log('Step 1: Finding available port...');
    backendPort = await findAvailablePort();
    console.log(`SELECTED PORT: ${backendPort}`);
    console.log('='.repeat(60));
    
    // Get correct paths based on mode
    console.log('Step 2: Determining file paths...');
    const paths = getPaths();
    
    // Verify files exist
    if (!fs.existsSync(paths.pythonExecutable)) {
      throw new Error(`Python executable not found at: ${paths.pythonExecutable}`);
    }
    console.log('Python executable found');
    
    if (!isPackaged && !fs.existsSync(paths.runApiPath)) {
      throw new Error(`run_api.py not found at: ${paths.runApiPath}`);
    }
    
    console.log('='.repeat(60));
    
    // Start Python process with mode-specific arguments
    console.log('Step 3: Starting Python process...');
    
    let spawnArgs, command;
    
    if (isPackaged) {
      // Packaged mode - execute the bundled standalone executable directly
      command = paths.pythonExecutable;
      spawnArgs = []; // No additional arguments needed for standalone executable
      console.log(`PACKAGED MODE - Command: ${command}`);
    } else {
      // Development mode - use Python interpreter with script
      command = paths.pythonExecutable;
      spawnArgs = [paths.runApiPath];
      console.log(`DEVELOPMENT MODE - Command: ${command} ${spawnArgs.join(' ')}`);
    }
    
    console.log(`Working directory: ${paths.workingDirectory}`);
    console.log(`Environment PORT: ${backendPort}`);
    
    // Prepare environment variables
    const spawnEnv = {
      ...process.env,
      PORT: backendPort.toString(),
      PYTHONPATH: isPackaged ? paths.workingDirectory : path.dirname(__dirname)
    };
    
    // In packaged mode, tell Python where to find bundled resources (like config.example.json)
    if (isPackaged && process.resourcesPath) {
      spawnEnv.SENTOPIC_BUNDLE_DIR = path.join(process.resourcesPath, 'python-backend');
      console.log(`Environment SENTOPIC_BUNDLE_DIR: ${spawnEnv.SENTOPIC_BUNDLE_DIR}`);
    }
    
    pythonProcess = spawn(command, spawnArgs, {
      cwd: paths.workingDirectory,
      env: spawnEnv,
      stdio: ['pipe', 'pipe', 'pipe'] // Always capture output for debugging
    });
    
    console.log(`Python process started with PID: ${pythonProcess.pid}`);
    
    // Capture and log all output from Python process
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        console.log(`PYTHON STDOUT: ${output}`);
      }
    });
    
    pythonProcess.stderr.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        console.log(`PYTHON STDERR: ${output}`);
      }
    });
    
    // Handle process events
    pythonProcess.on('error', (error) => {
      console.error('Python process spawn error:', error);
      showErrorDialog('Backend Startup Error', `Failed to start Python backend: ${error.message}`);
    });
    
    pythonProcess.on('exit', (code, signal) => {
      console.log(`Python process exited - Code: ${code}, Signal: ${signal}`);
      if (code !== 0 && code !== null) {
        console.error(`Python process exited with code ${code}`);
      }
      pythonProcess = null;
    });
    
    console.log('='.repeat(60));
    console.log('Step 4: Waiting for process initialization...');
    await new Promise(resolve => setTimeout(resolve, 3000)); // Give it more time
    
    // Verify process is still running
    if (!pythonProcess || pythonProcess.killed || pythonProcess.exitCode !== null) {
      throw new Error('Python process died during startup');
    }
    console.log('Python process still running after initialization period');
    
    console.log('='.repeat(60));
    console.log('Step 5: Starting health checks...');
    const isHealthy = await waitForBackend(backendPort);
    
    if (!isHealthy) {
      throw new Error('Backend failed to start within timeout period');
    }
    
    console.log('PYTHON BACKEND STARTED SUCCESSFULLY!');
    console.log('='.repeat(60));
    return true;
    
  } catch (error) {
    console.error('FAILED TO START PYTHON BACKEND:', error);
    console.log('='.repeat(60));
    showErrorDialog('Backend Startup Failed', error.message);
    return false;
  }
}

// Create the main application window
function createWindow() {
  console.log('Creating main window...');
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false // Don't show until ready
  });
  
  // Load the frontend based on mode
  const paths = getPaths();
  
  if (fs.existsSync(paths.frontendPath)) {
    mainWindow.loadFile(paths.frontendPath);
    console.log(`Loaded frontend from: ${paths.frontendPath}`);
  } else {
    console.error(`Frontend not found at: ${paths.frontendPath}`);
    showErrorDialog('Frontend Not Found', 'Please run "npm run build" in the frontend directory first.');
    return;
  }
  
  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    console.log('Window ready to show');
    mainWindow.show();
    
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });
  
  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// IPC handlers
ipcMain.handle('get-backend-url', () => {
  const backendUrl = backendPort ? `http://127.0.0.1:${backendPort}` : null;
  console.log(`IPC: Providing backend URL: ${backendUrl}`);
  return backendUrl;
});

ipcMain.handle('get-backend-status', () => {
  const status = {
    port: backendPort,
    isRunning: pythonProcess !== null,
    url: backendPort ? `http://127.0.0.1:${backendPort}` : null,
    mode: isPackaged ? 'packaged' : 'development'
  };
  console.log(`IPC: Backend status requested:`, status);
  return status;
});

// App event handlers
app.whenReady().then(async () => {
  console.log('Sentopic Desktop App starting...');
  console.log(`Development mode: ${isDev}`);
  console.log(`Packaged mode: ${isPackaged}`);
  console.log(`Node version: ${process.version}`);
  console.log(`Electron version: ${process.versions.electron}`);
  console.log(`Platform: ${process.platform}`);
  console.log('='.repeat(60));
  
  // Start backend first
  const backendStarted = await startPythonBackend();
  
  if (backendStarted) {
    // Create window after backend is ready
    createWindow();
  } else {
    // Exit if backend failed to start
    console.log('Exiting due to backend startup failure');
    app.quit();
  }
});

app.on('window-all-closed', () => {
  // On macOS, keep app running even when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On macOS, re-create window when dock icon is clicked
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Graceful shutdown
app.on('before-quit', async (event) => {
  if (pythonProcess && !pythonProcess.killed) {
    event.preventDefault(); // Prevent immediate quit
    
    console.log('App shutting down - terminating Python backend...');
    
    try {
      // Try graceful shutdown first
      pythonProcess.kill('SIGTERM');
      
      // Wait for process to exit (with timeout)
      const shutdownPromise = new Promise((resolve) => {
        const timeout = setTimeout(() => {
          console.log('Graceful shutdown timeout - force killing...');
          if (pythonProcess && !pythonProcess.killed) {
            pythonProcess.kill('SIGKILL');
          }
          resolve();
        }, 3000);
        
        if (pythonProcess) {
          pythonProcess.once('exit', () => {
            clearTimeout(timeout);
            console.log('Python process terminated successfully');
            resolve();
          });
        } else {
          clearTimeout(timeout);
          resolve();
        }
      });
      
      await shutdownPromise;
      pythonProcess = null;
      
    } catch (error) {
      console.error('Error during Python process shutdown:', error);
    } finally {
      // Now actually quit
      app.quit();
    }
  }
});