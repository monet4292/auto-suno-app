// Global Jest setup - runs before everything else

// Ensure process exists and set NODE_ENV
if (typeof process === 'undefined') {
  global.process = {};
}

if (!process.env) {
  process.env = {};
}

process.env.NODE_ENV = 'test';

// Mock global variables to avoid conflicts
global.__filename = '/mock/filename';
global.__dirname = '/mock/dirname';

// Fix React JSX runtime issue by mocking process.env before React loads
Object.defineProperty(process, 'env', {
  value: {
    NODE_ENV: 'test',
    ...process.env
  },
  writable: true,
  configurable: true
});