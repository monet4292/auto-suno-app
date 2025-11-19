// Jest setup file - must be before other imports
import '@testing-library/jest-dom';

// Setup process.env before React imports
if (!process.env.NODE_ENV) {
  process.env.NODE_ENV = 'test';
}

// Mock global variables for Jest compatibility
(global as any).__filename = '/mock/filename';
(global as any).__dirname = '/mock/dirname';

// Mock Electron API
Object.defineProperty(window, 'electronAPI', {
  value: {
    sendCommand: jest.fn(),
    onBackendResponse: jest.fn(),
    onProgressUpdate: jest.fn(),
    onErrorUpdate: jest.fn(),
    onWarningUpdate: jest.fn(),
    removeListener: jest.fn(),
    removeAllListeners: jest.fn(),
    minimizeWindow: jest.fn(),
    maximizeWindow: jest.fn(),
    closeWindow: jest.fn(),
    getAppVersion: jest.fn(() => '3.0.0'),
    platform: jest.fn(() => 'win32'),
    selectDirectory: jest.fn(),
    selectFile: jest.fn(),
    openExternal: jest.fn(),
    openDevTools: jest.fn(),
    reload: jest.fn()
  },
  writable: true
});

// Mock process type
Object.defineProperty(window, 'process', {
  value: {
    type: 'renderer'
  },
  writable: true
});

// Global test utilities
global.mockBackendResponse = (command: any, response: any) => {
  const mockSendCommand = window.electronAPI.sendCommand as jest.Mock;
  mockSendCommand.mockResolvedValue(response);
};

global.mockBackendError = (command: any, error: string) => {
  const mockSendCommand = window.electronAPI.sendCommand as jest.Mock;
  mockSendCommand.mockRejectedValue(new Error(error));
};

// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
});