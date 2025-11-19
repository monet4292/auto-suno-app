import pkg from 'electron';
const { app, BrowserWindow } = pkg;
import * as os from 'os';

import { PythonBridge } from './python-bridge.js';
import { MainWindow } from './main-window.js';
import { setupIPCHandlers, cleanupIPCHandlers } from './ipc-handlers.js';

class ElectronApp {
  private mainWindow: MainWindow;
  private pythonBridge: PythonBridge;
  private isShuttingDown: boolean = false;
  private isQuitting: boolean = false;

  constructor() {
    this.mainWindow = new MainWindow();
    this.pythonBridge = new PythonBridge({
      debug: process.env.NODE_ENV === 'development'
    });
  }

  /**
   * Initialize the Electron application
   */
  async initialize(): Promise<void> {
    console.log('🚀 Initializing Suno Account Manager...');

    try {
      // Ensure app is ready
      await app.whenReady();

      // Setup global error handlers
      this.setupErrorHandlers();

      // Initialize Python backend
      console.log('🐍 Starting Python backend...');
      await this.setupPythonBackend();

      // Create main window
      console.log('🪟 Creating main window...');
      this.createMainWindow();

      // Setup IPC handlers
      console.log('📡 Setting up IPC handlers...');
      setupIPCHandlers(this.pythonBridge, this.mainWindow);

      // Setup application event handlers
      this.setupAppEventHandlers();

      console.log('✅ Application initialized successfully');

    } catch (error) {
      console.error('❌ Failed to initialize application:', error);
      await this.handleError(error instanceof Error ? error : new Error(String(error)));
    }
  }

  /**
   * Setup Python backend integration
   */
  private async setupPythonBackend(): Promise<void> {
    // Handle Python backend events
    this.pythonBridge.on('BACKEND_READY', () => {
      console.log('✅ Python backend is ready');
      this.mainWindow.send('PYTHON_BACKEND_READY');
    });

    this.pythonBridge.on('ERROR_UPDATE', (error) => {
      console.error('❌ Python backend error:', error.payload.message);
      this.mainWindow.send('PYTHON_BACKEND_ERROR', error);
    });

    // Start Python backend
    await this.pythonBridge.start();
  }

  /**
   * Create and setup main window
   */
  private createMainWindow(): void {
    this.mainWindow.create();

    const window = this.mainWindow.getInstance();
    if (!window) {
      throw new Error('Failed to create main window');
    }

    // Setup window-specific event handlers
    window.on('close', async (event) => {
      if (!this.isShuttingDown) {
        event.preventDefault();
        await this.shutdown();
      }
    });

    window.on('closed', () => {
      // Window closed, but app will handle shutdown
    });
  }

  /**
   * Setup application-level event handlers
   */
  private setupAppEventHandlers(): void {
    // Handle all windows closed
    app.on('window-all-closed', () => {
      // On Windows/Linux, quit when all windows are closed
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    // Handle app activation (macOS)
    app.on('activate', async () => {
      // On macOS, recreate window when app is activated
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createMainWindow();
      } else {
        this.mainWindow.focus();
      }
    });

    // Handle app before quit
    app.on('before-quit', async (event) => {
      if (!this.isShuttingDown) {
        event.preventDefault();
        await this.shutdown();
      }
    });

    // Handle app will quit
    app.on('will-quit', async (event) => {
      if (!this.isShuttingDown) {
        event.preventDefault();
        await this.shutdown();
      }
    });
  }

  /**
   * Setup global error handlers
   */
  private setupErrorHandlers(): void {
    // Handle uncaught exceptions
    process.on('uncaughtException', async (error) => {
      console.error('💥 Uncaught Exception:', error);
      await this.handleError(error);
    });

    // Handle unhandled promise rejections
    process.on('unhandledRejection', async (reason, promise) => {
      console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
      await this.handleError(new Error(String(reason)));
    });

    // Handle SIGTERM
    process.on('SIGTERM', async () => {
      console.log('📡 SIGTERM received');
      await this.shutdown();
    });

    // Handle SIGINT (Ctrl+C)
    process.on('SIGINT', async () => {
      console.log('📡 SIGINT received');
      await this.shutdown();
    });
  }

  /**
   * Handle application errors
   */
  private async handleError(error: Error): Promise<void> {
    try {
      // Show error dialog in development
      if (process.env.NODE_ENV === 'development') {
        const electron = await import('electron');
        await electron.dialog.showErrorBox('Application Error', error.message);
      } else {
        // In production, log error and attempt graceful shutdown
        console.error('Application error:', error);
        await this.shutdown();
      }
    } catch (handlerError) {
      console.error('Error in error handler:', handlerError);
      process.exit(1);
    }
  }

  /**
   * Graceful shutdown
   */
  async shutdown(): Promise<void> {
    if (this.isShuttingDown) {
      console.log('⏳ Shutdown already in progress...');
      return;
    }

    this.isShuttingDown = true;
    console.log('🛑 Shutting down application...');

    try {
      // Cleanup IPC handlers
      cleanupIPCHandlers();

      // Stop Python backend
      console.log('🐍 Stopping Python backend...');
      await this.pythonBridge.stop();

      // Close main window
      const window = this.mainWindow.getInstance();
      if (window && !window.isDestroyed()) {
        console.log('🪟 Closing main window...');
        window.close();
      }

      console.log('✅ Application shutdown complete');

    } catch (error) {
      console.error('❌ Error during shutdown:', error);
    } finally {
      // Force quit if not already quitting
      if (!this.isQuitting) {
        this.isQuitting = true;
        app.quit();
      }
    }
  }

  /**
   * Get application information
   */
  getAppInfo(): {
    name: string;
    version: string;
    platform: string;
    arch: string;
    electronVersion: string;
    nodeVersion: string;
    chromeVersion: string;
  } {
    return {
      name: app.getName(),
      version: app.getVersion(),
      platform: process.platform,
      arch: process.arch,
      electronVersion: process.versions.electron,
      nodeVersion: process.versions.node,
      chromeVersion: process.versions.chrome
    };
  }

  /**
   * Get system information
   */
  getSystemInfo(): {
    platform: string;
    arch: string;
    totalMemory: number;
    freeMemory: number;
    cpus: string[];
    uptime: number;
  } {
    return {
      platform: os.platform(),
      arch: os.arch(),
      totalMemory: os.totalmem(),
      freeMemory: os.freemem(),
      cpus: os.cpus().map(cpu => cpu.model),
      uptime: os.uptime()
    };
  }
}

// Application entry point
async function main(): Promise<void> {
  try {
    console.log('🎵 Suno Account Manager v3.0');
    console.log('🖥️  Platform:', process.platform, process.arch);
    console.log('🔧 Environment:', process.env.NODE_ENV || 'production');
    console.log('📦 Node:', process.versions.node);
    console.log('⚡ Electron:', process.versions.electron);
    console.log('');

    const electronApp = new ElectronApp();
    await electronApp.initialize();

    // Store app instance globally for access in other modules
    (global as any).electronApp = electronApp;

  } catch (error) {
    console.error('💥 Failed to start application:', error);
    process.exit(1);
  }
}

// Start the application
main().catch((error) => {
  console.error('💥 Fatal error:', error);
  process.exit(1);
});