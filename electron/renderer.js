/**
 * Renderer process helper for frontend integration
 * This file provides utilities for the React frontend to communicate with the Electron backend
 */

// Check if backend is available and show connection status
async function checkBackendConnection() {
    try {
      const backendStatus = await window.electronAPI.getBackendStatus();
      console.log('🔍 Backend status:', backendStatus);
      
      if (backendStatus.isRunning && backendStatus.url) {
        // Test the health endpoint
        const response = await fetch(`${backendStatus.url}/health`);
        if (response.ok) {
          console.log('✅ Backend connection verified');
          return backendStatus.url;
        }
      }
    } catch (error) {
      console.error('❌ Backend connection check failed:', error);
    }
    
    return null;
  }
  
  // Show connection status to user
  function displayConnectionStatus(isConnected, backendUrl = null) {
    // Remove any existing status messages
    const existingStatus = document.getElementById('electron-connection-status');
    if (existingStatus) {
      existingStatus.remove();
    }
    
    // Create status message
    const statusDiv = document.createElement('div');
    statusDiv.id = 'electron-connection-status';
    statusDiv.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      padding: 10px 15px;
      border-radius: 5px;
      color: white;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 14px;
      z-index: 10000;
      ${isConnected ? 
        'background-color: #10b981; border: 1px solid #059669;' : 
        'background-color: #ef4444; border: 1px solid #dc2626;'
      }
    `;
    
    statusDiv.innerHTML = isConnected ? 
      `🟢 Backend Connected${backendUrl ? ` (${backendUrl})` : ''}` : 
      '🔴 Backend Disconnected';
    
    document.body.appendChild(statusDiv);
    
    // Auto-remove success message after 3 seconds
    if (isConnected) {
      setTimeout(() => {
        if (statusDiv && statusDiv.parentNode) {
          statusDiv.remove();
        }
      }, 3000);
    }
  }
  
  // Initialize connection checking when DOM loads
  document.addEventListener('DOMContentLoaded', async () => {
    console.log('📄 DOM loaded, checking backend connection...');
    
    // Check if we're in Electron
    if (window.electronAPI) {
      // Wait a moment for backend to stabilize
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const backendUrl = await checkBackendConnection();
      displayConnectionStatus(!!backendUrl, backendUrl);
      
      // Periodic connection check (every 30 seconds)
      setInterval(async () => {
        const backendUrl = await checkBackendConnection();
        if (!backendUrl) {
          displayConnectionStatus(false);
        }
      }, 30000);
    }
  });
  
  // Export utilities for use by the main application
  window.SentopicElectron = {
    checkBackendConnection,
    displayConnectionStatus
  };