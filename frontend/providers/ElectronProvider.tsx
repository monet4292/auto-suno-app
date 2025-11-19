import React, { createContext, useContext, useEffect, useState } from 'react';
import { ElectronAPI, AppError, ProgressEvent } from '../../src/types/electron';
import { BackendCommand, BackendResponse } from '../../src/types/backend';

interface ElectronContextType {
  electronAPI: ElectronAPI | null;
  isElectron: boolean;
  appVersion: string;
  platform: string;
  isConnected: boolean;
  backendReady: boolean;
  lastError: AppError | null;

  // Send command to backend
  sendCommand: (command: BackendCommand) => Promise<BackendResponse>;

  // Utility functions
  selectDirectory: () => Promise<string | null>;
  selectFile: (filters?: Electron.FileFilter[]) => Promise<string | null>;
  openExternal: (url: string) => Promise<boolean>;
}

const ElectronContext = createContext<ElectronContextType | null>(null);

export function ElectronProvider({ children }: { children: React.ReactNode }) {
  const [electronAPI, setElectronAPI] = useState<ElectronAPI | null>(null);
  const [isElectron, setIsElectron] = useState(false);
  const [appVersion, setAppVersion] = useState('3.0.0');
  const [platform, setPlatform] = useState('unknown');
  const [isConnected, setIsConnected] = useState(false);
  const [backendReady, setBackendReady] = useState(false);
  const [lastError, setLastError] = useState<AppError | null>(null);

  // Check if running in Electron
  useEffect(() => {
    const checkElectron = async () => {
      const isElectronEnv = window && window.process && window.process.type;
      setIsElectron(!!isElectronEnv);

      if (isElectronEnv && window.electronAPI) {
        setElectronAPI(window.electronAPI);

        try {
          // Get app info
          const version = await window.electronAPI.getAppVersion();
          const plat = await window.electronAPI.platform();

          setAppVersion(version);
          setPlatform(plat);
          setIsConnected(true);

          console.log('🟢 Electron environment detected');
          console.log(`📱 Platform: ${plat}`);
          console.log(`🔢 Version: ${version}`);

        } catch (error) {
          console.error('❌ Failed to get Electron info:', error);
          setIsConnected(false);
        }
      } else {
        console.log('🌐 Running in browser environment');
      }
    };

    checkElectron();
  }, []);

  // Setup event listeners when Electron API is available
  useEffect(() => {
    if (!electronAPI || !isElectron) return;

    let mounted = true;

    // Listen for backend ready signal
    const handleBackendReady = () => {
      if (mounted) {
        console.log('🟢 Python backend is ready');
        setBackendReady(true);
        setLastError(null);
      }
    };

    // Listen for backend errors
    const handleBackendError = (error: any) => {
      if (mounted) {
        console.error('❌ Backend error:', error);
        setBackendReady(false);
        setLastError({
          type: 'PYTHON_ERROR',
          message: error.payload?.message || 'Unknown backend error',
          details: error,
          timestamp: Date.now()
        });
      }
    };

    // Listen for progress updates
    const handleProgressUpdate = (progress: ProgressEvent) => {
      if (mounted) {
        // Clear any previous errors when progress is made
        if (lastError) {
          setLastError(null);
        }
      }
    };

    // Setup listeners
    electronAPI.onBackendResponse?.(handleBackendReady);
    electronAPI.onErrorUpdate?.(handleBackendError);
    electronAPI.onProgressUpdate?.(handleProgressUpdate);

    // Check if backend is already ready
    const checkBackendStatus = async () => {
      try {
        // Try to get accounts to check if backend is ready
        await electronAPI.sendCommand({
          id: 'backend-check',
          type: 'GET_ACCOUNTS',
          payload: {}
        });

        if (mounted) {
          handleBackendReady();
        }
      } catch (error) {
        // Backend not ready yet
        console.log('⏳ Waiting for backend...');
      }
    };

    // Wait a bit then check backend status
    setTimeout(checkBackendStatus, 1000);

    // Cleanup
    return () => {
      mounted = false;
      electronAPI.removeListener?.('BACKEND_RESPONSE', handleBackendReady);
      electronAPI.removeListener?.('ERROR_UPDATE', handleBackendError);
      electronAPI.removeListener?.('PROGRESS_UPDATE', handleProgressUpdate);
    };
  }, [electronAPI, isElectron, lastError]);

  // Send command wrapper
  const sendCommand = async (command: BackendCommand): Promise<BackendResponse> => {
    if (!electronAPI) {
      throw new Error('Electron API not available');
    }

    try {
      setLastError(null);
      const response = await electronAPI.sendCommand(command);
      return response;
    } catch (error) {
      const appError: AppError = {
        type: 'IPC_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
        details: error,
        timestamp: Date.now()
      };

      setLastError(appError);
      throw error;
    }
  };

  // Utility functions
  const selectDirectory = async (): Promise<string | null> => {
    if (!electronAPI) return null;
    try {
      return await electronAPI.selectDirectory();
    } catch (error) {
      console.error('Failed to select directory:', error);
      return null;
    }
  };

  const selectFile = async (filters?: Electron.FileFilter[]): Promise<string | null> => {
    if (!electronAPI) return null;
    try {
      return await electronAPI.selectFile(filters);
    } catch (error) {
      console.error('Failed to select file:', error);
      return null;
    }
  };

  const openExternal = async (url: string): Promise<boolean> => {
    if (!electronAPI) return false;
    try {
      const result = await electronAPI.openExternal(url);
      return result.success;
    } catch (error) {
      console.error('Failed to open external URL:', error);
      return false;
    }
  };

  const contextValue: ElectronContextType = {
    electronAPI,
    isElectron,
    appVersion,
    platform,
    isConnected,
    backendReady,
    lastError,
    sendCommand,
    selectDirectory,
    selectFile,
    openExternal,
  };

  return (
    <ElectronContext.Provider value={contextValue}>
      {children}
    </ElectronContext.Provider>
  );
}

export function useElectron(): ElectronContextType {
  const context = useContext(ElectronContext);
  if (!context) {
    throw new Error('useElectron must be used within ElectronProvider');
  }
  return context;
}

// Hook for backend operations
export function useBackend() {
  const { sendCommand, backendReady, isConnected } = useElectron();

  const sendCommandWithCheck = async (command: BackendCommand): Promise<BackendResponse> => {
    if (!isConnected) {
      throw new Error('Not connected to Electron');
    }

    if (!backendReady) {
      throw new Error('Python backend not ready');
    }

    return await sendCommand(command);
  };

  return {
    sendCommand: sendCommandWithCheck,
    isConnected,
    backendReady,
  };
}