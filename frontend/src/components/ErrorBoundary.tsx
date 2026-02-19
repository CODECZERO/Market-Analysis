/**
 * Error Boundary Component
 * 
 * Catches React errors in child components and displays a friendly error UI.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): Partial<State> {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('[ErrorBoundary] Caught error:', error);
        console.error('[ErrorBoundary] Error info:', errorInfo);

        this.setState({ errorInfo });

        // Report to analytics/monitoring service
        // You could integrate with Sentry, LogRocket, etc. here
        if (typeof window !== 'undefined') {
            // Log to console in development
            if (import.meta.env.DEV) {
                console.group('Error Boundary Caught Error');
                console.error('Error:', error);
                console.error('Component Stack:', errorInfo.componentStack);
                console.groupEnd();
            }
        }
    }

    private handleRetry = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    private handleGoHome = () => {
        window.location.href = '/brands';
    };

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-[400px] flex items-center justify-center p-6">
                    <div className="max-w-md w-full text-center">
                        {/* Icon */}
                        <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-6">
                            <AlertTriangle className="w-8 h-8 text-red-500" />
                        </div>

                        {/* Title */}
                        <h2 className="text-2xl font-semibold text-white mb-2">
                            Something went wrong
                        </h2>
                        <p className="text-zinc-400 mb-6">
                            We encountered an unexpected error. Don't worry, your data is safe.
                        </p>

                        {/* Error details (dev only) */}
                        {import.meta.env.DEV && this.state.error && (
                            <div className="mb-6 p-4 rounded-lg bg-zinc-900/50 border border-zinc-800 text-left overflow-auto max-h-32">
                                <p className="text-xs font-mono text-red-400">
                                    {this.state.error.message}
                                </p>
                            </div>
                        )}

                        {/* Actions */}
                        <div className="flex gap-3 justify-center">
                            <Button
                                onClick={this.handleRetry}
                                variant="outline"
                                className="gap-2 border-zinc-700 hover:bg-zinc-800"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Try Again
                            </Button>
                            <Button
                                onClick={this.handleGoHome}
                                className="gap-2 bg-blue-600 hover:bg-blue-500"
                            >
                                <Home className="w-4 h-4" />
                                Go to Dashboard
                            </Button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
