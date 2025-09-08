/**
 * Main App Component
 * Root application component with routing and providers
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ErrorBoundary from '@/components/common/ErrorBoundary';
import MainLayout from '@/components/layout/MainLayout';
import ProjectsDashboard from '@/pages/ProjectsDashboard';
import ProjectWorkspace from '@/pages/ProjectWorkspace';
import CollectionManager from '@/pages/CollectionManager';
import ProjectSetupWizard from '@/pages/ProjectSetupWizard';
import AnalysisProgress from '@/pages/AnalysisProgress';
import CollectionSetupWizard from '@/pages/CollectionSetupWizard';

// Create QueryClient for TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// 404 Not Found page
const NotFoundPage: React.FC = () => (
  <MainLayout title="Page Not Found">
    <div className="text-center py-12">
      <div className="mb-6">
        <h1 className="font-page-title text-text-primary mb-3">
          404 - Page Not Found
        </h1>
        <p className="font-body text-text-secondary max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved.
        </p>
      </div>
      
      <div className="flex justify-center">
        <a
          href="/"
          className="inline-flex items-center px-4 py-2 bg-accent text-white rounded-default hover:bg-blue-700 transition-colors duration-150"
        >
          ← Return to Dashboard
        </a>
      </div>
    </div>
  </MainLayout>
);

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="App">
          <Routes>
            {/* Main dashboard route */}
            <Route path="/" element={<ProjectsDashboard />} />
  
            {/* Project setup wizard route */}
            <Route path="/projects/new" element={<ProjectSetupWizard />} />
  
            {/* Analysis progress route */}
            <Route path="/analysis/:projectId" element={<AnalysisProgress />} />
  
            {/* Project workspace route */}
            <Route path="/project/:projectId" element={<ProjectWorkspace />} />
  
            {/* Collection manager route */}
            <Route path="/collections" element={<CollectionManager />} />

            {/* Collection setup wizard route */}
            <Route path="/collections/new" element={<CollectionSetupWizard />} />
  
            {/* Redirect old paths */}
            <Route path="/dashboard" element={<Navigate to="/" replace />} />
            <Route path="/projects" element={<Navigate to="/" replace />} />
  
            {/* 404 page */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
          </div>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;