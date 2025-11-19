import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';
import * as path from 'path';
import * as fs from 'fs';
import { BackendCommand, BackendResponse, ProgressEvent } from '../src/types/backend';


export interface PythonBridgeOptions {
  pythonPath?: string;
  scriptPath?: string;
  workingDirectory?: string;
  timeout?: number;
  debug?: boolean;
}

export class PythonBridge extends EventEmitter {
  private pythonProcess: ChildProcess | null = null;
  private pendingCommands: Map<string, {
    resolve: (value: BackendResponse) => void;
    reject: (reason: any) => void;
    timeout: NodeJS.Timeout;
    command: BackendCommand;
  }> = new Map();

  private options: Required<PythonBridgeOptions>;
  private isReady: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 3;

  constructor(options: PythonBridgeOptions = {}) {
    super();

    this.options = {
      pythonPath: options.pythonPath || (process.platform === 'win32' ? 'python' : 'python3'),
      scriptPath: options.scriptPath || path.join(__dirname, '../../backend/main.py'),
      workingDirectory: options.workingDirectory || process.cwd(),
      timeout: options.timeout || 30000,
      debug: options.debug || false
    };
  }

  /**
   * Start the Python backend process
   */
  async start(): Promise<void> {
    if (this.pythonProcess && !this.pythonProcess.killed) {
      throw new Error('Python backend is already running');
    }

    // Validate script exists
    if (!fs.existsSync(this.options.scriptPath)) {
      throw new Error(`Python script not found: ${this.options.scriptPath}`);
    }

    return new Promise((resolve, reject) => {
      try {
        const env = {
          ...process.env,
          PYTHONPATH: path.join(__dirname, '../../src'),
          PYTHONUNBUFFERED: '1'
        };

        this.pythonProcess = spawn(this.options.pythonPath, [this.options.scriptPath], {
          cwd: this.options.workingDirectory,
          stdio: ['pipe', 'pipe', 'pipe'],
          env
        });

        if (!this.pythonProcess) {
          throw new Error('Failed to spawn Python process');
        }

        this.setupProcessHandlers();

        // Wait for backend ready signal
        const readyTimeout = setTimeout(() => {
          reject(new Error('Python backend failed to start within timeout'));
        }, 10000);

        this.once('BACKEND_READY', () => {
          clearTimeout(readyTimeout);
          this.isReady = true;
          this.reconnectAttempts = 0;

          if (this.options.debug) {
            console.log('✅ Python backend is ready');
          }

          resolve();
        });

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Setup process event handlers
   */
  private setupProcessHandlers(): void {
    if (!this.pythonProcess) return;

    // Handle Python stdout (responses and events)
    this.pythonProcess.stdout?.on('data', (data: Buffer) => {
      const messages = data.toString()
        .split('\n')
        .filter(msg => msg.trim());

      messages.forEach(msg => {
        if (msg) {
          try {
            const response = JSON.parse(msg);
            this.handleResponse(response);
          } catch (error) {
            console.error('❌ Invalid JSON from Python:', error, msg);

            this.emit('ERROR_UPDATE', {
              id: 'parsing-error',
              type: 'ERROR_UPDATE',
              payload: {
                message: 'Invalid JSON from Python backend',
                status: 'error'
              },
              timestamp: Date.now()
            } as ProgressEvent);
          }
        }
      });
    });

    // Handle Python stderr (debug output and ready signal)
    this.pythonProcess.stderr?.on('data', (data: Buffer) => {
      const messages = data.toString()
        .split('\n')
        .filter(msg => msg.trim());

      messages.forEach(msg => {
        if (msg) {
          try {
            const parsed = JSON.parse(msg);

            if (parsed.type === 'BACKEND_READY') {
              this.emit('BACKEND_READY', parsed);
            } else {
              console.log('📝 Python log:', parsed);
            }
          } catch {
            // Non-JSON output, just log it
            if (this.options.debug) {
              console.log('📝 Python stderr:', msg);
            }
          }
        }
      });
    });

    // Handle process errors
    this.pythonProcess.on('error', (error: Error) => {
      console.error('❌ Python backend error:', error);

      const errorEvent: ProgressEvent = {
        id: 'python-error',
        type: 'ERROR_UPDATE',
        payload: {
          message: error.message,
          status: 'error'
        },
        timestamp: Date.now()
      };

      this.emit('ERROR_UPDATE', errorEvent);

      // Try to reconnect
      this.attemptReconnect();
    });

    // Handle process exit
    this.pythonProcess.on('close', (code: number, signal: string) => {
      console.log(`🔌 Python backend exited with code ${code}, signal ${signal}`);

      this.isReady = false;
      this.pythonProcess = null;

      if (code !== 0 && code !== null) {
        const errorEvent: ProgressEvent = {
          id: 'python-exit',
          type: 'ERROR_UPDATE',
          payload: {
            message: `Backend exited with code ${code}`,
            status: 'error'
          },
          timestamp: Date.now()
        };

        this.emit('ERROR_UPDATE', errorEvent);

        // Try to reconnect if not intentional shutdown
        this.attemptReconnect();
      }
    });
  }

  /**
   * Handle responses from Python backend
   */
  private handleResponse(response: any): void {
    // Handle progress events (no ID or special ID)
    if (response.id === 'progress-event' || response.type?.endsWith('_PROGRESS') || response.type?.endsWith('_UPDATE')) {
      const progressEvent: ProgressEvent = {
        id: response.id || 'progress-event',
        type: response.type,
        payload: response.payload || response,
        timestamp: response.timestamp || Date.now()
      };

      this.emit(response.type, progressEvent);
      return;
    }

    // Handle command responses
    const pendingCommand = this.pendingCommands.get(response.id);
    if (pendingCommand) {
      clearTimeout(pendingCommand.timeout);
      this.pendingCommands.delete(response.id);

      const backendResponse: BackendResponse = {
        id: response.id,
        type: response.type,
        success: response.success,
        data: response.data,
        error: response.error,
        error_code: response.error_code,
        timestamp: response.timestamp
      };

      if (response.success) {
        pendingCommand.resolve(backendResponse);
      } else {
        pendingCommand.reject(new Error(response.error || 'Unknown backend error'));
      }
    } else {
      // Unhandled response - could be a broadcast event
      console.warn('⚠️ Unhandled response:', response);
      this.emit('BACKEND_RESPONSE', response);
    }
  }

  /**
   * Send command to Python backend
   */
  async sendCommand(command: BackendCommand): Promise<BackendResponse> {
    if (!this.isReady || !this.pythonProcess) {
      throw new Error('Python backend is not ready');
    }

    // Generate unique ID if not provided
    if (!command.id) {
      command.id = `cmd-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    // Set timestamp if not provided
    if (!command.timestamp) {
      command.timestamp = Date.now();
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingCommands.delete(command.id);

        const timeoutMessage = `Command timeout after ${this.options.timeout}ms`;
        reject(new Error(timeoutMessage));
      }, this.options.timeout);

      this.pendingCommands.set(command.id, {
        resolve,
        reject,
        timeout,
        command
      });

      const commandStr = JSON.stringify(command) + '\n';

      if (this.options.debug) {
        console.log('📤 Sending command:', command);
      }

      if (this.pythonProcess?.stdin) {
        this.pythonProcess.stdin.write(commandStr, (error) => {
          if (error) {
            clearTimeout(timeout);
            this.pendingCommands.delete(command.id);

            console.error('❌ Failed to send command:', error);
            reject(error);
          }
        });
      } else {
        clearTimeout(timeout);
        this.pendingCommands.delete(command.id);
        reject(new Error('Python process not available'));
      }
    });
  }

  /**
   * Attempt to reconnect to Python backend
   */
  private async attemptReconnect(): Promise<void> {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;

    console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    // Wait before reconnecting
    await new Promise(resolve => setTimeout(resolve, 2000 * this.reconnectAttempts));

    try {
      await this.start();
    } catch (error) {
      console.error('❌ Reconnection failed:', error);
    }
  }

  /**
   * Stop the Python backend process
   */
  async stop(): Promise<void> {
    this.isReady = false;

    // Clear all pending commands
    for (const [, { timeout, reject }] of this.pendingCommands) {
      clearTimeout(timeout);
      reject(new Error('Backend shutting down'));
    }
    this.pendingCommands.clear();

    if (this.pythonProcess && !this.pythonProcess.killed) {
      return new Promise((resolve) => {
        const cleanup = () => {
          this.pythonProcess = null;
          resolve();
        };

        this.pythonProcess!.once('close', cleanup);
        this.pythonProcess!.kill('SIGTERM');

        // Force kill after 5 seconds
        setTimeout(() => {
          if (this.pythonProcess && !this.pythonProcess.killed) {
            this.pythonProcess.kill('SIGKILL');
            cleanup();
          }
        }, 5000);
      });
    }
  }

  /**
   * Get connection status
   */
  getStatus(): {
    isRunning: boolean;
    isReady: boolean;
    pendingCommands: number;
    reconnectAttempts: number;
  } {
    return {
      isRunning: !!this.pythonProcess && !this.pythonProcess.killed,
      isReady: this.isReady,
      pendingCommands: this.pendingCommands.size,
      reconnectAttempts: this.reconnectAttempts
    };
  }

  /**
   * Force restart the backend
   */
  async restart(): Promise<void> {
    await this.stop();
    await new Promise(resolve => setTimeout(resolve, 1000));
    await this.start();
  }
}