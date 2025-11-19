// Mock for PythonBridge to avoid __filename conflicts
const EventEmitter = require('events');

class MockPythonBridge extends EventEmitter {
  constructor(options = {}) {
    super();
    this.options = options;
    this.pythonProcess = null;
    this.pendingCommands = new Map();
    this.isReady = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
  }

  async start() {
    // Mock implementation
    setTimeout(() => {
      this.isReady = true;
      this.emit('BACKEND_READY');
    }, 100);
  }

  async sendCommand(command) {
    return {
      id: command.id || 'mock-id',
      type: command.type || 'MOCK_RESPONSE',
      success: true,
      data: { mock: true },
      timestamp: Date.now()
    };
  }

  async stop() {
    this.isReady = false;
    this.pendingCommands.clear();
  }

  getStatus() {
    return {
      isRunning: false,
      isReady: this.isReady,
      pendingCommands: this.pendingCommands.size,
      reconnectAttempts: this.reconnectAttempts
    };
  }

  async restart() {
    await this.stop();
    await this.start();
  }
}

module.exports = {
  PythonBridge: MockPythonBridge
};