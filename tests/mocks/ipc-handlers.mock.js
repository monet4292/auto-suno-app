// Mock for IPC handlers
const IPC_CHANNELS = {
  BACKEND_COMMAND: 'backend:command',
  BACKEND_RESPONSE: 'backend:response',
  PROGRESS_UPDATE: 'progress:update',
  ERROR_UPDATE: 'error:update',
  WARNING_UPDATE: 'warning:update'
};

const setupIPCHandlers = jest.fn();
const cleanupIPCHandlers = jest.fn();

module.exports = {
  IPC_CHANNELS,
  setupIPCHandlers,
  cleanupIPCHandlers
};