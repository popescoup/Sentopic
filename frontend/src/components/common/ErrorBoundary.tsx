/**
 * Error Boundary Component
 * Professional error handling with graceful fallbacks
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

interface Props {
  children: ReactNode;
  /** Custom fallback component */
  fallback?: ReactNode;
  /** Whether to show technical error details */
  showDetails?: boolean;
  /** Custom error message */
  message?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details
    console.error('Error Boundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Report to error tracking service in production
    if (import.meta.env.PROD) {
      // TODO: Send to error tracking service (Sentry, LogRocket, etc.)
      // reportError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <Card className="max-w-lg w-full">
            <div className="text-center">
              {/* Error icon */}
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <svg
                  className="h-6 w-6 text-danger"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
              </div>

              {/* Error message */}
              <h2 className="font-section-header text-text-primary mb-2">
                Something went wrong
              </h2>
              
              <p className="font-body text-text-secondary mb-6">
                {this.props.message || 
                 'An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.'}
              </p>

              {/* Action buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  variant="primary"
                  onClick={this.handleReset}
                >
                  Try Again
                </Button>
                
                <Button
                  variant="secondary"
                  onClick={this.handleReload}
                >
                  Refresh Page
                </Button>
              </div>

              {/* Technical details (development only) */}
              {(this.props.showDetails || import.meta.env.DEV) && this.state.error && (
                <details className="mt-6 text-left">
                  <summary className="cursor-pointer font-small text-text-tertiary hover:text-text-secondary">
                    Technical Details
                  </summary>
                  <div className="mt-3 p-4 bg-panel rounded-input border border-border-primary">
                    <div className="font-technical text-xs text-text-secondary">
                      <div className="mb-2">
                        <strong>Error:</strong> {this.state.error.message}
                      </div>
                      <div className="mb-2">
                        <strong>Stack:</strong>
                        <pre className="mt-1 whitespace-pre-wrap break-words">
                          {this.state.error.stack}
                        </pre>
                      </div>
                      {this.state.errorInfo && (
                        <div>
                          <strong>Component Stack:</strong>
                          <pre className="mt-1 whitespace-pre-wrap break-words">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                </details>
              )}
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook-based error boundary for functional components
export const useErrorHandler = () => {
  const [error, setError] = React.useState<Error | null>(null);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  const captureError = React.useCallback((error: Error) => {
    console.error('Error captured:', error);
    setError(error);
  }, []);

  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return { captureError, resetError };
};

// Simple error fallback component
export const ErrorFallback: React.FC<{
  error?: Error;
  resetError?: () => void;
  message?: string;
}> = ({ 
  error, 
  resetError,
  message = 'Something went wrong'
}) => {
  return (
    <Card className="text-center py-8">
      <div className="text-danger mb-4">
        <svg
          className="h-8 w-8 mx-auto"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      
      <h3 className="font-subsection text-text-primary mb-2">
        {message}
      </h3>
      
      {error && (
        <p className="font-small text-text-secondary mb-4">
          {error.message}
        </p>
      )}
      
      {resetError && (
        <Button variant="outline" size="sm" onClick={resetError}>
          Try Again
        </Button>
      )}
    </Card>
  );
};

export default ErrorBoundary;