export default {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/tests', '<rootDir>/frontend'],
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/*.(test|spec).+(ts|tsx|js)'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        module: 'CommonJS',
        target: 'ES2020'
      }
    }],
  },
  setupFiles: ['<rootDir>/tests/jest.globals.js'],
  collectCoverageFrom: [
    'frontend/**/*.{ts,tsx}',
    'electron/**/*.ts',
    'src/**/*.ts',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/dist/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^@/components/(.*)$': '<rootDir>/frontend/components/$1',
    '^@/hooks/(.*)$': '<rootDir>/frontend/hooks/$1',
    '^@/utils/(.*)$': '<rootDir>/frontend/utils/$1',
    '^@/types/(.*)$': '<rootDir>/src/types/$1',
    '^@/electron/(.*)$': '<rootDir>/electron/$1',
    '^../../electron/python-bridge$': '<rootDir>/tests/mocks/python-bridge.mock.js',
    '^../../electron/main-window$': '<rootDir>/tests/mocks/main-window.mock.js',
    '^../../electron/ipc-handlers$': '<rootDir>/tests/mocks/ipc-handlers.mock.js',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  testTimeout: 10000,
  verbose: true,
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$))'
  ]
};