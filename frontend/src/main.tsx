/**
 * Application Entry Point
 * React 18 setup with StrictMode and global styles
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Import global styles
import '@/styles/globals.css';

// Ensure we have a root element
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Failed to find the root element');
}

// Create React root with React 18 API
const root = ReactDOM.createRoot(rootElement);

// Render app with StrictMode for better development experience
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);