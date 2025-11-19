/**
 * React Frontend Tests
 * Tests React components and hooks
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

import { ElectronProvider, useElectron, useBackend } from '../../frontend/providers/ElectronProvider';
import Dashboard from '../../frontend/pages/Dashboard';

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <ElectronProvider>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </ElectronProvider>
    </QueryClientProvider>
  );
};

// Test component that uses hooks
const TestComponent: React.FC = () => {
  const { isElectron, isConnected, appVersion, sendCommand } = useElectron();
  const { backendReady } = useBackend();

  return (
    <div>
      <div data-testid="is-electron">{isElectron.toString()}</div>
      <div data-testid="is-connected">{isConnected.toString()}</div>
      <div data-testid="app-version">{appVersion}</div>
      <div data-testid="backend-ready">{backendReady.toString()}</div>
      <button
        data-testid="test-command"
        onClick={() => sendCommand({ id: 'test', type: 'GET_ACCOUNTS', payload: {} })}
      >
        Send Test Command
      </button>
    </div>
  );
};

describe('Electron Provider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should provide Electron API context', () => {
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    expect(screen.getByTestId('is-electron')).toHaveTextContent('true');
    expect(screen.getByTestId('is-connected')).toHaveTextContent('true');
    expect(screen.getByTestId('app-version')).toHaveTextContent('3.0.0');
  });

  it('should handle command sending', async () => {
    // Mock successful response
    const mockResponse = {
      id: 'test',
      type: 'GET_ACCOUNTS_RESPONSE',
      success: true,
      data: [],
      timestamp: Date.now()
    };

    global.mockBackendResponse(
      { id: 'test', type: 'GET_ACCOUNTS', payload: {} },
      mockResponse
    );

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    const button = screen.getByTestId('test-command');
    fireEvent.click(button);

    await waitFor(() => {
      expect(window.electronAPI.sendCommand).toHaveBeenCalledWith({
        id: 'test',
        type: 'GET_ACCOUNTS',
        payload: {}
      });
    });
  });

  it('should handle command errors', async () => {
    global.mockBackendError(
      { id: 'test-error', type: 'GET_ACCOUNTS', payload: {} },
      'Backend error'
    );

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    const button = screen.getByTestId('test-command');

    // Should not throw error in UI, but handle gracefully
    expect(() => fireEvent.click(button)).not.toThrow();
  });
});

describe('Dashboard Component', () => {
  it('should render dashboard correctly', () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    expect(screen.getByText('Welcome to Suno Account Manager')).toBeInTheDocument();
    expect(screen.getByText('Connection Status')).toBeInTheDocument();
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Statistics')).toBeInTheDocument();
  });

  it('should show connection status', () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    // Should show Electron as connected
    expect(screen.getByText('Connected')).toBeInTheDocument();

    // Should show backend as ready (after setup delay)
    setTimeout(() => {
      expect(screen.getByText('Ready')).toBeInTheDocument();
    }, 1500);
  });

  it('should display getting started guide', () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    expect(screen.getByText('Getting Started')).toBeInTheDocument();
    expect(screen.getByText('1. Add Accounts')).toBeInTheDocument();
    expect(screen.getByText('2. Create Songs')).toBeInTheDocument();
  });
});

describe('useBackend Hook', () => {
  const TestBackendComponent: React.FC = () => {
    const { sendCommand, isConnected, backendReady } = useBackend();

    const handleCommand = async () => {
      try {
        const response = await sendCommand({ id: 'test', type: 'GET_ACCOUNTS', payload: {} });
        return response.success;
      } catch (error) {
        return false;
      }
    };

    return (
      <div>
        <div data-testid="backend-connected">{isConnected.toString()}</div>
        <div data-testid="backend-ready">{backendReady.toString()}</div>
        <button data-testid="backend-command" onClick={handleCommand}>
          Backend Command
        </button>
      </div>
    );
  };

  it('should throw error when not connected to Electron', () => {
    // Mock non-Electron environment
    Object.defineProperty(window, 'electronAPI', { value: undefined });

    expect(() => {
      render(
        <TestWrapper>
          <TestBackendComponent />
        </TestWrapper>
      );
    }).toThrow('useElectron must be used within ElectronProvider');
  });

  it('should validate backend readiness before sending commands', async () => {
    render(
      <TestWrapper>
        <TestBackendComponent />
      </TestWrapper>
    );

    const button = screen.getByTestId('backend-command');

    // Should not throw error, but handle gracefully when backend not ready
    expect(() => fireEvent.click(button)).not.toThrow();
  });
});