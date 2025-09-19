const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Get the backend URL for API calls
  getBackendURL: () => ipcRenderer.invoke('get-backend-url'),
  
  // Get backend status information
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  
  // Check if we're running in Electron
  isElectron: true,
  
  // Platform information
  platform: process.platform,
  
  // Version information
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron
  }
});

// Log that preload script has loaded
console.log('🔌 Electron preload script loaded');

// Expose backend URL globally when DOM is ready
window.addEventListener('DOMContentLoaded', async () => {
  try {
    const backendURL = await ipcRenderer.invoke('get-backend-url');
    if (backendURL) {
      console.log(`🔗 Backend URL available: ${backendURL}`);
      // Store it globally for the API client
      window.__ELECTRON_BACKEND_URL__ = backendURL;
    } else {
      console.warn('⚠️ Backend URL not yet available');
    }
  } catch (error) {
    console.error('❌ Failed to get backend URL:', error);
  }
});