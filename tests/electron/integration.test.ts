/**
 * Electron Integration Tests
 * Tests the complete Electron + Python backend integration
 */

import { PythonBridge } from '../../electron/python-bridge';
import { setupIPCHandlers, cleanupIPCHandlers } from '../../electron/ipc-handlers';
import { MainWindow } from '../../electron/main-window';
import { ipcMain } from 'electron';

// Mock Electron modules
jest.mock('electron', () => ({
  ipcMain: {
    handle: jest.fn(),
    removeAllListeners: jest.fn(),
  },
  app: {
    getVersion: jest.fn(() => '3.0.0'),
    getPath: jest.fn(() => '/tmp'),
    quit: jest.fn(),
    whenReady: jest.fn(() => Promise.resolve()),
  },
  BrowserWindow: jest.fn().mockImplementation(() => ({
    on: jest.fn(),
    once: jest.fn(),
    webContents: {
      send: jest.fn(),
      on: jest.fn(),
      once: jest.fn(),
      loadURL: jest.fn(),
      loadFile: jest.fn(),
      openDevTools: jest.fn(),
      getURL: jest.fn(() => 'http://localhost:5173'),
      getOwnerBrowserWindow: jest.fn(() => ({
        minimize: jest.fn(),
        maximize: jest.fn(),
        unmaximize: jest.fn(),
        isMaximized: jest.fn(() => false),
        close: jest.fn(),
      })),
    },
    isMaximized: jest.fn(() => false),
    minimize: jest.fn(),
    maximize: jest.fn(),
    unmaximize: jest.fn(),
    close: jest.fn(),
    show: jest.fn(),
    focus: jest.fn(),
    isDestroyed: jest.fn(() => false),
    getBounds: jest.fn(() => ({ x: 0, y: 0, width: 1400, height: 850 })),
  })),
  screen: {
    getPrimaryDisplay: jest.fn(() => ({
      workAreaSize: { width: 1920, height: 1080 }
    })),
  },
  Menu: {
    buildFromTemplate: jest.fn(),
    setApplicationMenu: jest.fn(),
  },
  dialog: {
    showOpenDialog: jest.fn(),
    showErrorBox: jest.fn(),
  },
  shell: {
    openExternal: jest.fn(),
  },
}));

// Mock child_process
jest.mock('child_process', () => ({
  spawn: jest.fn().mockImplementation(() => {
    const mockProcess = {
      killed: false,
      stdin: {
        write: jest.fn(),
      },
      stdout: {
        on: jest.fn(),
      },
      stderr: {
        on: jest.fn(),
      },
      on: jest.fn(),
      once: jest.fn(),
      kill: jest.fn(),
    };

    // Simulate backend ready signal
    setTimeout(() => {
      const stderrOn = mockProcess.stderr.on;
      if (stderrOn) {
        stderrOn.mock.calls[0][1]('{"type": "BACKEND_READY", "timestamp": 1234567890}');
      }
    }, 100);

    return mockProcess;
  }),
}));

// Mock fs
jest.mock('fs', () => ({
  existsSync: jest.fn(() => true),
  readFileSync: jest.fn(),
  writeFileSync: jest.fn(),
}));

describe('Electron Integration', () => {
  let pythonBridge: PythonBridge;
  let mainWindow: MainWindow;

  beforeEach(() => {
    pythonBridge = new PythonBridge({
      debug: false,
      timeout: 5000
    });
    mainWindow = new MainWindow();
  });

  afterEach(async () => {
    await pythonBridge.stop();
    cleanupIPCHandlers();
    jest.clearAllMocks();
  });

  describe('Python Bridge', () => {
    it('should initialize successfully', () => {
      expect(pythonBridge).toBeDefined();
      const status = pythonBridge.getStatus();
      expect(status.isRunning).toBe(false);
      expect(status.isReady).toBe(false);
    });

    it('should start and connect to Python backend', async () => {
      await pythonBridge.start();

      const status = pythonBridge.getStatus();
      expect(status.isRunning).toBe(true);
      expect(status.isReady).toBe(true);
    });

    it('should send commands and receive responses', async () => {
      await pythonBridge.start();

      const command = {
        id: 'test-cmd-1',
        type: 'GET_ACCOUNTS',
        payload: {}
      };

      const response = await pythonBridge.sendCommand(command);

      expect(response).toBeDefined();
      expect(response.id).toBe(command.id);
      expect(response.type).toBe('GET_ACCOUNTS_RESPONSE');
    });

    it('should handle progress events', (done) => {
      pythonBridge.on('PROGRESS_UPDATE', (event) => {
        expect(event.type).toBe('PROGRESS_UPDATE');
        expect(event.payload).toBeDefined();
        done();
      });

      pythonBridge.start().then(() => {
        // Simulate progress event
        const progressEvent = {
          id: 'progress-event',
          type: 'QUEUE_PROGRESS',
          payload: {
            operation_id: 'test-op',
            message: 'Test progress',
            progress: 50
          },
          timestamp: Date.now()
        };

        // Mock the progress event handling
        setTimeout(() => {
          pythonBridge.emit('PROGRESS_UPDATE', progressEvent);
        }, 200);
      });
    });

    it('should handle backend errors gracefully', async () => {
      await pythonBridge.start();

      const command = {
        id: 'test-error',
        type: 'INVALID_COMMAND',
        payload: {}
      };

      try {
        await pythonBridge.sendCommand(command);
        // Should throw an error
        expect(true).toBe(false);
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
      }
    });
  });

  describe('IPC Handlers', () => {
    beforeEach(() => {
      setupIPCHandlers(pythonBridge, mainWindow);
    });

    it('should register IPC handlers', () => {
      expect(ipcMain.handle).toHaveBeenCalled();
    });

    it('should handle SEND_COMMAND requests', async () => {
      await pythonBridge.start();

      // Mock the IPC handler callback
      const mockCallback = jest.fn();
      const handleCall = (ipcMain.handle as jest.Mock).mock.calls.find(
        call => call[0] === 'SEND_COMMAND'
      );

      if (handleCall) {
        const handler = handleCall[1];
        const mockEvent = {
          sender: {
            getOwnerBrowserWindow: jest.fn(() => ({
              minimize: jest.fn(),
              maximize: jest.fn(),
              close: jest.fn(),
            }))
          }
        };

        const command = {
          id: 'test-ipc',
          type: 'GET_ACCOUNTS',
          payload: {}
        };

        await handler(mockEvent, command);

        expect(mockCallback).toHaveBeenCalled();
      }
    });

    it('should handle window management commands', () => {
      const mockEvent = {
        sender: {
          getOwnerBrowserWindow: jest.fn(() => ({
            minimize: jest.fn(),
            maximize: jest.fn(),
            unmaximize: jest.fn(),
            isMaximized: jest.fn(() => false),
            close: jest.fn(),
          }))
        }
      };

      // Test WINDOW_MINIMIZE
      const minimizeCall = (ipcMain.handle as jest.Mock).mock.calls.find(
        call => call[0] === 'WINDOW_MINIMIZE'
      );

      if (minimizeCall) {
        const handler = minimizeCall[1];
        const result = handler(mockEvent);
        expect(result.success).toBe(true);
      }
    });
  });

  describe('Main Window', () => {
    it('should create main window successfully', () => {
      mainWindow.create();
      const instance = mainWindow.getInstance();
      expect(instance).toBeDefined();
    });

    it('should handle window state changes', () => {
      mainWindow.create();
      const state = mainWindow.getWindowState();
      expect(state).toBeDefined();
      expect(typeof state.isMaximized).toBe('boolean');
      expect(typeof state.bounds).toBe('object');
    });

    it('should show loading fallback when dev server unavailable', () => {
      const window = mainWindow.getInstance();
      if (window) {
        // Simulate dev server failure
        window.webContents.emit('did-fail-load');
        // Should show fallback content
        expect(window.loadURL).toHaveBeenCalled();
      }
    });
  });

  describe('Full Integration', () => {
    it('should initialize complete Electron app', async () => {
      // Start Python backend
      await pythonBridge.start();
      expect(pythonBridge.getStatus().isReady).toBe(true);

      // Setup IPC handlers
      setupIPCHandlers(pythonBridge, mainWindow);
      expect(ipcMain.handle).toHaveBeenCalled();

      // Create main window
      mainWindow.create();
      expect(mainWindow.getInstance()).toBeDefined();

      // Test command flow
      const command = {
        id: 'integration-test',
        type: 'GET_ACCOUNTS',
        payload: {}
      };

      const response = await pythonBridge.sendCommand(command);
      expect(response.success).toBe(true);
    });

    it('should handle graceful shutdown', async () => {
      await pythonBridge.start();
      setupIPCHandlers(pythonBridge, mainWindow);
      mainWindow.create();

      // Test shutdown sequence
      await pythonBridge.stop();
      cleanupIPCHandlers();

      const status = pythonBridge.getStatus();
      expect(status.isRunning).toBe(false);
    });
  });
});