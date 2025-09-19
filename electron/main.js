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

// Configuration
const CONFIG = {
  primaryPortRange: { start: 8000, end: 8020 },
  fallbackPortRange: { start: 9000, end: 9020 },
  healthCheckTimeout: 30000, // 30 seconds
  healthCheckInterval: 1000,  // 1 second
  maxStartupTime: 60000       // 60 seconds total
};

// Utility: Check if port is available
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    
    server.listen(port, () => {
      server.once('close', () => resolve(true));
      server.close();
    });
    
    server.on('error', () => resolve(false));
  });
}

// Utility: Find available port with fallback strategy
async function findAvailablePort() {
  console.log('🔍 Looking for available port...');
  
  // Strategy 1: Try primary range (8000-8020)
  for (let port = CONFIG.primaryPortRange.start; port <= CONFIG.primaryPortRange.end; port++) {
    if (await isPortAvailable(port)) {
      console.log(`✅ Found available port: ${port} (primary range)`);
      return port;
    }
  }
  
  // Strategy 2: Try fallback range (9000-9020)
  console.log('⚠️ Primary range full, trying fallback range...');
  for (let port = CONFIG.fallbackPortRange.start; port <= CONFIG.fallbackPortRange.end; port++) {
    if (await isPortAvailable(port)) {
      console.log(`✅ Found available port: ${port} (fallback range)`);
      return port;
    }
  }
  
  // Strategy 3: Get random available port from OS
  console.log('⚠️ Fallback range full, requesting OS-assigned port...');
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, () => {
      const port = server.address().port;
      server.close(() => {
        console.log(`✅ OS assigned port: ${port}`);
        resolve(port);
      });
    });
    server.on('error', reject);
  });
}

// Debug function to test different network methods
async function debugHealthCheck(port) {
  const healthUrl = `http://127.0.0.1:${port}/health`;
  console.log(`🔍 Debug: Testing health check to ${healthUrl}`);
  
  // Test 1: Axios (what we normally use)
  try {
    console.log('🔍 Debug: Trying axios...');
    const axiosResponse = await axios.get(healthUrl, { 
      timeout: 5000,
      headers: {
        'User-Agent': 'Electron-Debug'
      }
    });
    console.log(`✅ Debug: Axios success - Status: ${axiosResponse.status}`);
    console.log(`✅ Debug: Axios data: ${JSON.stringify(axiosResponse.data)}`);
    return { method: 'axios', success: true, data: axiosResponse.data };
  } catch (axiosError) {
    console.log(`❌ Debug: Axios failed - Code: ${axiosError.code}, Message: ${axiosError.message}`);
    if (axiosError.response) {
      console.log(`❌ Debug: Axios response status: ${axiosError.response.status}`);
    }
  }
  
  return { method: 'none', success: false };
}

// Utility: Wait for backend health check with comprehensive debugging
async function waitForBackend(port, timeout = CONFIG.healthCheckTimeout) {
  const startTime = Date.now();
  const healthUrl = `http://127.0.0.1:${port}/health`;
  
  console.log(`🏥 Waiting for backend health check at ${healthUrl}...`);
  console.log(`🏥 Timeout configured for ${timeout}ms`);
  
  // First, run comprehensive debug check
  console.log('🔍 Running comprehensive network debug...');
  const debugResult = await debugHealthCheck(port);
  
  if (debugResult.success) {
    console.log(`✅ Debug check passed using ${debugResult.method}! Backend is accessible.`);
    return true;
  }
  
  console.log('❌ Debug check failed. Trying standard health check loop...');
  
  // Continue with original logic but with enhanced logging
  let attemptCount = 0;
  while (Date.now() - startTime < timeout) {
    attemptCount++;
    const elapsed = Date.now() - startTime;
    
    try {
      console.log(`🔍 Health check attempt #${attemptCount} at ${elapsed}ms`);
      console.log(`🔍 Making request to: ${healthUrl}`);
      
      const response = await axios.get(healthUrl, { 
        timeout: 2000,
        headers: {
          'User-Agent': 'Electron-HealthCheck'
        },
        validateStatus: function (status) {
          return status < 500; // Accept anything except server errors
        }
      });
      
      console.log(`📡 Response received - Status: ${response.status}`);
      
      if (response.status === 200) {
        console.log('✅ Backend health check passed!');
        console.log(`✅ Response data: ${JSON.stringify(response.data)}`);
        return true;
      } else {
        console.log(`⚠️ Unexpected status code: ${response.status}`);
      }
    } catch (error) {
      console.log(`❌ Health check attempt #${attemptCount} failed:`);
      console.log(`   Error code: ${error.code || 'unknown'}`);
      console.log(`   Error message: ${error.message}`);
      
      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, CONFIG.healthCheckInterval));
    }
  }
  
  console.error(`❌ Backend health check failed - timeout reached after ${attemptCount} attempts`);
  console.error(`❌ Total time elapsed: ${Date.now() - startTime}ms`);
  return false;
}

// Show error dialog to user
function showErrorDialog(title, message) {
  dialog.showErrorBox(title, `${message}\n\nPlease check the console for more details.`);
}

// Start Python backend subprocess
async function startPythonBackend() {
  try {
    console.log('🐍 Starting Python backend...');
    
    // Find available port
    backendPort = await findAvailablePort();
    console.log(`🔌 Backend will use port: ${backendPort}`);
    
    // Determine project root (parent of electron directory)
    const projectRoot = path.dirname(__dirname);
    const venvPath = path.join(projectRoot, 'sentopic-env', 'bin', 'python');
    const runApiPath = path.join(projectRoot, 'run_api.py');
    
    console.log(`📁 Project root: ${projectRoot}`);
    console.log(`🐍 Virtual env python: ${venvPath}`);
    console.log(`🚀 Starting backend on port ${backendPort}`);
    
    // Check if venv python exists
    if (!fs.existsSync(venvPath)) {
      throw new Error(`Virtual environment not found at: ${venvPath}`);
    }
    
    if (!fs.existsSync(runApiPath)) {
      throw new Error(`run_api.py not found at: ${runApiPath}`);
    }
    
    // Start Python process
    console.log('🚀 Spawning Python process...');
    pythonProcess = spawn(venvPath, [runApiPath], {
      cwd: projectRoot,
      env: {
        ...process.env,
        PORT: backendPort.toString(),
        PYTHONPATH: projectRoot
      },
      stdio: isDev ? 'inherit' : 'pipe'
    });
    
    console.log(`✅ Python process started with PID: ${pythonProcess.pid}`);
    
    // Handle process events
    pythonProcess.on('error', (error) => {
      console.error('❌ Python process error:', error);
      showErrorDialog('Backend Startup Error', `Failed to start Python backend: ${error.message}`);
    });
    
    pythonProcess.on('exit', (code, signal) => {
      console.log(`🔄 Python process exited - Code: ${code}, Signal: ${signal}`);
      if (code !== 0 && code !== null) {
        console.error(`❌ Python process exited with code ${code}`);
      }
      pythonProcess = null;
    });
    
    // Give the process a moment to start
    console.log('⏳ Waiting 2 seconds for process initialization...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Wait for backend to be ready
    console.log('🏥 Starting health check process...');
    const isHealthy = await waitForBackend(backendPort);
    
    if (!isHealthy) {
      throw new Error('Backend failed to start within timeout period');
    }
    
    console.log('🎉 Python backend started successfully!');
    return true;
    
  } catch (error) {
    console.error('❌ Failed to start Python backend:', error);
    showErrorDialog('Backend Startup Failed', error.message);
    return false;
  }
}

// Create the main application window
function createWindow() {
  console.log('🪟 Creating main window...');
  
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
  
  // Load the built frontend
  const frontendPath = path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
  
  if (fs.existsSync(frontendPath)) {
    mainWindow.loadFile(frontendPath);
    console.log(`✅ Loaded frontend from: ${frontendPath}`);
  } else {
    console.error(`❌ Frontend not found at: ${frontendPath}`);
    showErrorDialog('Frontend Not Found', 'Please run "npm run build" in the frontend directory first.');
    return;
  }
  
  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    console.log('✅ Window ready to show');
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
  console.log(`🔗 IPC: Providing backend URL: ${backendUrl}`);
  return backendUrl;
});

ipcMain.handle('get-backend-status', () => {
  const status = {
    port: backendPort,
    isRunning: pythonProcess !== null,
    url: backendPort ? `http://127.0.0.1:${backendPort}` : null
  };
  console.log(`📊 IPC: Backend status requested:`, status);
  return status;
});

// App event handlers
app.whenReady().then(async () => {
  console.log('🚀 Sentopic Desktop App starting...');
  console.log(`📍 Development mode: ${isDev}`);
  console.log(`📍 Node version: ${process.version}`);
  console.log(`📍 Electron version: ${process.versions.electron}`);
  console.log(`📍 Platform: ${process.platform}`);
  
  // Start backend first
  const backendStarted = await startPythonBackend();
  
  if (backendStarted) {
    // Create window after backend is ready
    createWindow();
  } else {
    // Exit if backend failed to start
    console.log('❌ Exiting due to backend startup failure');
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
app.on('before-quit', (event) => {
  console.log('🛑 App shutting down...');
  
  if (pythonProcess) {
    console.log('⏳ Terminating Python backend...');
    pythonProcess.kill('SIGTERM');
    
    // Give it a moment to shut down gracefully
    setTimeout(() => {
      if (pythonProcess) {
        console.log('🔨 Force killing Python backend...');
        pythonProcess.kill('SIGKILL');
      }
    }, 3000);
  }
});