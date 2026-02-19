import React from 'react';
import ModernStockDashboard from './components/ModernStockDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './index.css';

function App() {
  return (
    <ErrorBoundary>
      <ModernStockDashboard />
    </ErrorBoundary>
  );
}

export default App;
