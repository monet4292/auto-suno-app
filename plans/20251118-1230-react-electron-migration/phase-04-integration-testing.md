# Phase 4: Integration, Testing & Deployment

## Context
**Parent Plan:** [plan.md](plan.md)
**Dependencies:** [Phase 1](phase-01-python-communication-layer.md), [Phase 2](phase-02-electron-typescript-setup.md), [Phase 3](phase-03-react-frontend-development.md)
**Duration:** 1-2 weeks
**Priority**: High

## Overview

Complete integration testing, performance optimization, error handling refinement, and deployment preparation for the React + Electron Suno Account Manager application.

## Key Insights

- End-to-end testing is crucial due to complex Python-Electron communication
- Performance optimization should focus on IPC communication and React rendering
- User acceptance testing needs to focus on feature parity with CustomTkinter
- Deployment requires careful handling of Python backend integration
- Migration tools need to preserve existing user data and settings

## Requirements

### Functional Requirements
1. **End-to-End Testing:** Complete user workflow testing
2. **Performance Benchmarking:** Compare with CustomTkinter performance
3. **Error Handling:** Robust error recovery and user feedback
4. **Data Migration:** Tools for migrating existing user data
5. **Build Optimization:** Production-ready build pipeline
6. **Deployment Preparation:** Installation and update mechanisms

### Technical Requirements
1. **Integration Tests:** Test React-Electron-Python communication
2. **Unit Tests:** Component and store testing
3. **Performance Monitoring:** Memory usage and response time tracking
4. **Build Pipeline:** Optimized production builds
5. **Distribution:** Cross-platform packaging and installation

## Architecture

### Testing Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Testing Architecture                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  Unit Tests     │  │ Integration   │  │ E2E Tests   │  │
│  │                 │  │    Tests       │  │             │  │
│  │ • Components   │  │ • IPC Bridge   │  │ • Workflows │  │
│  │ • Stores       │  │ • Backend     │  │ • User     │  │
│  │ • Utilities    │  │ • Python       │  │  Scenarios  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  Performance   │  │    Migration   │  │   Build     │  │
│  │     Tests       │  │      Tools     │  │ Pipeline   │  │
│  │                 │  │                 │  │             │  │
│  │ • Benchmarks    │  │ • Data         │  │ • Webpack   │  │
│  │ • Profiling     │  │   Migrator     │  │ • Electron   │  │
│  │ • Memory        │  │ • Backup       │  │ Builder    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Build Pipeline Architecture

```
Development → Testing → Building → Packaging → Distribution
     │              │           │          │
     ▼              ▼           ▼          ▼
Hot Reload    Test Suite  Vite Build  Electron  Installers
             │              │          │          │
             ▼              ▼          ▼          ▼
        Jest/RTL      Vitest    TypeScript Builder    NSIS/DMG
```

## Related Code Files

### Files to Create
- `tests/setup.ts` - Test configuration
- `tests/integration/` - Integration tests
- `tests/e2e/` - End-to-end tests
- `tests/performance/` - Performance benchmarks
- `scripts/` - Build and deployment scripts
- `tools/migration/` - Data migration tools
- `build/` - Build configurations
- `dist/` - Production builds

### Configuration Files
- `jest.config.js` - Testing configuration
- `vitest.config.ts` - Integration testing
- `playwright.config.ts` - E2E testing setup
- `electron-builder.json` - Production build configuration

## Implementation Steps

### Step 1: Testing Infrastructure Setup (Day 1-2)
1. **Setup testing framework**
   ```json
   // package.json additions
   {
     "scripts": {
       "test": "jest",
       "test:watch": "jest --watch",
       "test:integration": "vitest",
       "test:e2e": "playwright test",
       "test:performance": "node tests/performance/benchmark.js"
     },
     "devDependencies": {
       "@testing-library/react": "^13.4.0",
       "@testing-library/jest-dom": "^6.1.5",
       "@testing-library/user-event": "^14.4.3",
       "jest": "^29.7.0",
       "vitest": "^0.34.6",
       "playwright": "^1.40.1",
       "electron-mock-ipc": "^0.4.0"
     }
   }
   ```

2. **Configure Jest for unit testing**
   ```javascript
   // jest.config.js
   module.exports = {
     preset: 'ts-jest',
     testEnvironment: 'jsdom',
     setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
     moduleNameMapping: {
       '^@/(.*)$': '<rootDir>/src/$1',
     },
     transform: {
       '^.+\\.tsx?$': 'ts-jest',
     },
     collectCoverageFrom: [
       'src/**/*.{ts,tsx}',
       '!src/**/*.d.ts',
     ],
     coverageThreshold: {
       global: {
         branches: 70,
         functions: 70,
         lines: 70,
         statements: 70,
       },
     },
   };
   ```

3. **Setup test configuration**
   ```typescript
   // tests/setup.ts
   import '@testing-library/jest-dom';

   // Mock Electron APIs
   const mockElectronAPI = {
     sendCommand: jest.fn(),
     onBackendResponse: jest.fn(),
     onProgressUpdate: jest.fn(),
     onErrorUpdate: jest.fn(),
     removeListener: jest.fn(),
   };

   Object.defineProperty(window, 'electronAPI', {
     value: mockElectronAPI,
     writable: true,
   });
   ```

### Step 2: Unit Testing Implementation (Day 3-4)
1. **Component testing**
   ```typescript
   // tests/components/AccountPanel.test.tsx
   import { render, screen, fireEvent, waitFor } from '@testing-library/react';
   import userEvent from '@testing-library/user-event';
   import { AccountPanel } from '../../src/components/Panels/AccountPanel/AccountPanel';
   import { useAccountStore } from '../../src/stores/accountStore';

   // Mock the store
   jest.mock('../../src/stores/accountStore');

   describe('AccountPanel', () => {
     beforeEach(() => {
       jest.clearAllMocks();
       (useAccountStore as jest.MockedFunction).mockReturnValue({
         accounts: [],
         loading: false,
         error: null,
         loadAccounts: jest.fn(),
         createAccount: jest.fn(),
         updateAccount: jest.fn(),
         deleteAccount: jest.fn(),
       });
     });

     it('renders account panel correctly', () => {
       render(<AccountPanel />);

       expect(screen.getByText('Quản lý tài khoản')).toBeInTheDocument();
       expect(screen.getByRole('button', { name: 'Thêm tài khoản' })).toBeInTheDocument();
     });

     it('loads accounts on mount', () => {
       const mockLoadAccounts = jest.fn();
       (useAccountStore as jest.MockedFunction).mockReturnValue({
         accounts: [],
         loading: false,
         error: null,
         loadAccounts: mockLoadAccounts,
       });

       render(<AccountPanel />);

       expect(mockLoadAccounts).toHaveBeenCalled();
     });

     it('displays accounts when loaded', async () => {
       const mockAccounts = [
         { name: 'test1', email: 'test1@example.com', created_at: '2025-01-01', status: 'active' },
         { name: 'test2', email: 'test2@example.com', created_at: '2025-01-02', status: 'active' },
       ];

       (useAccountStore as jest.MockedFunction).mockReturnValue({
         accounts: mockAccounts,
         loading: false,
         error: null,
         loadAccounts: jest.fn(),
       });

       render(<AccountPanel />);

       await waitFor(() => {
         expect(screen.getByText('test1')).toBeInTheDocument();
         expect(screen.getByText('test2')).toBeInTheDocument();
       });
     });

     it('handles loading state correctly', () => {
       (useAccountStore as jest.MockedFunction).mockReturnValue({
         accounts: [],
         loading: true,
         error: null,
         loadAccounts: jest.fn(),
       });

       render(<AccountPanel />);

       expect(screen.getByText('Đang tải tài khoản...')).toBeInTheDocument();
     });

     it('displays errors when they occur', () => {
       (useAccountStore as jest.MockedFunction).mockReturnValue({
         accounts: [],
         loading: false,
         error: 'Failed to load accounts',
         loadAccounts: jest.fn(),
       });

       render(<AccountPanel />);

       expect(screen.getByText('Failed to load accounts')).toBeInTheDocument();
     });
   });
   ```

2. **Store testing**
   ```typescript
   // tests/stores/appStore.test.ts
   import { renderHook, act } from '@testing-library/react';
   import { useAppStore } from '../../src/stores/appStore';

   describe('useAppStore', () => {
     it('initializes with default values', () => {
       const { result } = renderHook(() => useAppStore());

       expect(result.current.activePanel).toBe('account');
       expect(result.current.sidebarCollapsed).toBe(false);
       expect(result.current.isBackendConnected).toBe(false);
       expect(result.current.accounts).toEqual([]);
     });

     it('updates active panel correctly', () => {
       const { result } = renderHook(() => useAppStore());

       act(() => {
         result.current.setActivePanel('queue');
       });

       expect(result.current.activePanel).toBe('queue');
     });

     it('toggles sidebar correctly', () => {
       const { result } = renderHook(() => useAppStore());

       expect(result.current.sidebarCollapsed).toBe(false);

       act(() => {
         result.current.toggleSidebar();
       });

       expect(result.current.sidebarCollapsed).toBe(true);
     });
   });
   ```

### Step 3: Integration Testing (Day 5-7)
1. **Setup integration testing framework**
   ```typescript
   // tests/integration/setup.ts
   import { ElectronApplication } from 'spectron';
   import path from 'path';

   export const createApp = async () => {
     const app = new ElectronApplication({
       path: path.join(__dirname, '../../dist/electron/main.js'),
       args: [],
       driverOptions: {
         connectionRetryCount: 3,
         connectionRetryTimeout: 5000,
       },
     });

     await app.start();
     return app;
   };
   ```

2. **Python backend integration tests**
   ```typescript
   // tests/integration/python-bridge.test.ts
   import { PythonBridge } from '../../electron/python-bridge';
   import { spawn, ChildProcess } from 'child_process';

   describe('Python Bridge Integration', () => {
     let bridge: PythonBridge;
     let pythonProcess: ChildProcess;

     beforeEach(async () => {
       // Start mock Python backend
       pythonProcess = spawn('python', ['-m', 'unittest.mock', 'backend.test'], {
         stdio: ['pipe', 'pipe', 'pipe'],
         cwd: __dirname,
       });

       bridge = new PythonBridge();
       bridge.process = pythonProcess;
       bridge.start();
     });

     afterEach(async () => {
       if (bridge) {
         await bridge.stop();
       }
       if (pythonProcess) {
         pythonProcess.kill();
       }
     });

     it('sends commands and receives responses', async () => {
       const command = {
         id: 'test-1',
         type: 'GET_ACCOUNTS',
         payload: {},
       };

       const response = await bridge.sendCommand(command);

       expect(response).toBeDefined();
       expect(response.success).toBe(true);
       expect(response.data).toBeDefined();
     });

     it('handles errors correctly', async () => {
       const command = {
         id: 'test-2',
         type: 'INVALID_COMMAND',
         payload: {},
       };

       await expect(bridge.sendCommand(command)).rejects.toThrow();
     });
   });
   ```

3. **IPC communication tests**
   ```typescript
   // tests/integration/ipc.test.ts
   import { app, BrowserWindow } from 'electron';
   import { ipcMain } from 'electron';
   import { PythonBridge } from '../../electron/python-bridge';

   describe('IPC Communication', () => {
     let window: BrowserWindow;
     let pythonBridge: PythonBridge;

     beforeAll(async () => {
       // Create test window
       window = new BrowserWindow({
         show: false,
         webPreferences: {
           preload: path.join(__dirname, '../preload.js'),
         },
       });

       pythonBridge = new PythonBridge();
       pythonBridge.start();

       // Load test page
       await window.loadFile(path.join(__dirname, 'fixtures/test.html'));
     });

     afterAll(async () => {
       if (window) window.close();
       if (pythonBridge) await pythonBridge.stop();
     });

     it('sends commands from renderer to main process', async () => {
       const command = {
         id: 'test-1',
         type: 'GET_ACCOUNTS',
         payload: {},
       };

       const response = await window.webContents.invoke('SEND_COMMAND', command);

       expect(response).toBeDefined();
       expect(response.success).toBe(true);
     });

     it('receives progress updates in renderer', (done) => {
       window.webContents.once('PROGRESS_UPDATE', (event, progress) => {
         expect(progress).toBeDefined();
         expect(progress.type).toBe('PROGRESS_UPDATE');
         done();
       });

       // Simulate progress update from Python
       pythonBridge.emit('PROGRESS_UPDATE', {
         type: 'PROGRESS_UPDATE',
         payload: {
           operation_id: 'test-op',
           progress: 50,
           message: 'Test progress',
         },
       });
     });
   });
   ```

### Step 4: End-to-End Testing (Day 8-10)
1. **Setup Playwright E2E testing**
   ```typescript
   // tests/e2e/playwright.config.ts
   import { defineConfig, devices } from '@playwright/test';

   export default defineConfig({
     testDir: './tests/e2e',
     fullyParallel: true,
     forbidOnly: !!process.env.CI,
     retries: process.env.CI ? 2 : 0,
     workers: process.env.CI ? 1 : undefined,
     reporter: 'html',
     use: {
       baseURL: 'http://localhost:5173',
       trace: 'on-first-retry',
     },
     projects: [
       {
         name: 'chromium',
         use: { ...devices['Desktop Chrome'] },
       },
       {
         name: 'firefox',
         use: { ...devices['Desktop Firefox'] },
       },
       {
         name: 'webkit',
         use: { ...devices['Desktop Safari'] },
       },
     ],
   });
   ```

2. **Complete workflow tests**
   ```typescript
   // tests/e2e/complete-workflow.spec.ts
   import { test, expect } from '@playwright/test';
   import path from 'path';

   test.describe('Complete User Workflow', () => {
     test.beforeEach(async ({ page }) => {
       // Wait for app to load and connect to backend
       await page.waitForSelector('[data-testid="app-loaded"]');
       await page.waitForSelector('[data-testid="backend-connected"]');
     });

     test('account management workflow', async ({ page }) => {
       // Navigate to account panel
       await page.click('[data-testid="nav-account"]');

       // Create new account
       await page.click('[data-testid="add-account-button"]');
       await page.fill('[data-testid="account-name-input"]', 'test-account');
       await page.fill('[data-testid="account-email-input"]', 'test@example.com');
       await page.click('[data-testid="submit-account"]');

       // Verify account created
       await expect(page.locator('text=test-account')).toBeVisible();
       await expect(page.locator('text=test@example.com')).toBeVisible();
     });

     test('queue creation and execution workflow', async ({ page }) => {
       // Navigate to queue panel
       await page.click('[data-testid="nav-queue"]');

       // Upload XML file
       const fileInput = page.locator('[data-testid="xml-file-input"]');
       await fileInput.setInputFiles([
         path.join(__dirname, 'fixtures/prompts.xml')
       ]);

       // Configure queue
       await page.selectOption('[data-testid="account-select"]', 'test-account');
       await page.fill('[data-testid="total-songs-input"]', '10');
       await page.fill('[data-testid="songs-per-batch-input"]', '5');
       await page.click('[data-testid="create-queue"]');

       // Start queue execution
       await page.click('[data-testid="start-queue"]');

       // Monitor progress
       await expect(page.locator('[data-testid="queue-progress"]')).toBeVisible();
       await expect(page.locator('[data-testid="progress-percentage"]')).toContainText('0%');

       // Wait for completion
       await expect(page.locator('[data-testid="queue-status"]')).toContainText('completed');
     });

     test('download workflow', async ({ page }) => {
       // Navigate to download panel
       await page.click('[data-testid="nav-download"]');

       // Configure download
       await page.selectOption('[data-testid="account-select"]', 'test-account');
       await page.fill('[data-testid="download-limit"]', '5');
       await page.click('[data-testid="start-download"]');

       // Monitor download progress
       await expect(page.locator('[data-testid="download-progress"]')).toBeVisible();

       // Wait for completion
       await expect(page.locator('[data-testid="download-status"]')).toContainText('completed');
     });
   });
   ```

### Step 5: Performance Testing and Optimization (Day 11-12)
1. **Performance benchmarking**
   ```javascript
   // tests/performance/benchmark.js
   const { spawn } = require('child_process');
   const { performance } = require('perf_hooks');

   class PerformanceBenchmark {
     async measureStartup() {
       return new Promise((resolve) => {
         const startTime = performance.now();

         const child = spawn('electron', ['dist/electron/main.js'], {
           stdio: 'pipe',
         });

         let output = '';
         child.stdout.on('data', (data) => {
           output += data.toString();

           // Detect when app is ready
           if (output.includes('Backend ready')) {
             const endTime = performance.now();
             resolve(endTime - startTime);
           }
         });
       });
     }

     async measureResponseTime(operation) {
       const times = [];
       const iterations = 10;

       for (let i = 0; i < iterations; i++) {
         const startTime = performance.now();
         await operation();
         const endTime = performance.now();
         times.push(endTime - startTime);
       }

       return {
         average: times.reduce((a, b) => a + b, 0) / times.length,
         min: Math.min(...times),
         max: Math.max(...times),
         median: times.sort((a, b) => a - b)[Math.floor(times.length / 2)],
       };
     }

     async measureMemoryUsage() {
       return process.memoryUsage();
     }
   }

   module.exports = PerformanceBenchmark;
   ```

2. **Memory usage monitoring**
   ```typescript
   // tests/performance/memory.test.ts
   import { test, expect } from '@playwright/test';
   import { MemoryUsageBenchmark } from './memory-usage';

   test.describe('Memory Usage', () => {
     test('measures baseline memory usage', async ({ page }) => {
       const baseline = await new MemoryUsageBenchmark().measureBaseline();
       console.log('Baseline memory usage:', baseline);

       expect(baseline.heapUsed).toBeLessThan(200 * 1024 * 1024); // 200MB
       expect(baseline.external).toBeLessThan(100 * 1024 * 1024); // 100MB
     });

     test('measures memory usage during queue operation', async ({ page }) => {
       // Start queue operation
       await page.click('[data-testid="nav-queue"]');
       await page.click('[data-testid="start-queue"]');

       // Measure memory during operation
       const peakMemory = await new MemoryUsageBenchmark().measureDuringOperation(
         () => page.waitForSelector('[data-testid="queue-status"]', { timeout: 60000 })
       );

       console.log('Peak memory during queue:', peakMemory);

       expect(peakMemory.heapUsed - baseline.heapUsed).toBeLessThan(100 * 1024 * 1024); // 100MB increase
     });
   });
   ```

### Step 6: Data Migration Tools (Day 13-14)
1. **Create migration script**
   ```python
   # tools/migration/migrate_user_data.py
   """
   Migrate user data from CustomTkinter JSON files to new format
   """

   import json
   import shutil
   from pathlib import Path
   from datetime import datetime

   class DataMigrator:
       def __init__(self, source_dir: Path, target_dir: Path):
           self.source_dir = source_dir
           self.target_dir = target_dir
           self.backup_dir = target_dir / 'backup'

       def create_backup(self):
           """Create backup of existing data"""
           self.backup_dir.mkdir(parents=True, exist_ok=True)

           backup_file = self.backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"

           import tarfile
           with tarfile.open(backup_file, 'w:gz') as tar:
               tar.add(self.source_dir / 'data', arcname='data')

           print(f"Backup created: {backup_file}")
           return backup_file

       def migrate_accounts(self):
           """Migrate accounts from old format"""
           source_file = self.source_dir / 'data' / 'suno_accounts.json'
           target_file = self.target_dir / 'data' / 'accounts.json'

           if not source_file.exists():
               print("No existing accounts file found")
               return

           with open(source_file, 'r') as f:
               old_data = json.load(f)

           # Transform to new format
           new_data = {
               'version': '3.0.0',
               'migrated_at': datetime.now().isoformat(),
               'accounts': []
           }

           for account_name, account_data in old_data.items():
               new_account = {
                   'id': account_name,
                   'name': account_name,
                   'email': account_data.get('email', ''),
                   'created_at': account_data.get('created_at', ''),
                   'last_used': account_data.get('last_used'),
                   'status': account_data.get('status', 'active')
               }
               new_data['accounts'].append(new_account)

           # Save new format
           target_file.parent.mkdir(parents=True, exist_ok=True)
           with open(target_file, 'w') as f:
               json.dump(new_data, f, indent=2)

           print(f"Migrated {len(new_data['accounts'])} accounts")

       def migrate_queue_state(self):
           """Migrate queue state from old format"""
           source_file = self.source_dir / 'data' / 'queue_state.json'
           target_file = self.target_dir / 'data' / 'queue_state.json'

           if source_file.exists():
               shutil.copy2(source_file, target_file)
               print("Queue state migrated (no transformation needed)")
           else:
               print("No existing queue state found")

       def run_migration(self):
           """Run complete migration process"""
           print("Starting data migration...")

           try:
               # Create backup
               backup_file = self.create_backup()

               # Migrate different data types
               self.migrate_accounts()
               self.migrate_queue_state()

               # Copy other data files
               data_source = self.source_dir / 'data'
               data_target = self.target_dir / 'data'

               if data_source.exists():
                   for file_path in data_source.glob('*.json'):
                       if file_path.name not in ['suno_accounts.json', 'queue_state.json']:
                           target_path = data_target / file_path.name
                           target_path.parent.mkdir(parents=True, exist_ok=True)
                           shutil.copy2(file_path, target_path)

               print("Migration completed successfully!")
               print(f"Backup saved to: {backup_file}")

           except Exception as e:
               print(f"Migration failed: {e}")
               raise

   if __name__ == '__main__':
       migrator = DataMigrator(
           source_dir=Path('..'),  # CustomTkinter app directory
           target_dir=Path('..')  # React app directory
       )
       migrator.run_migration()
   ```

2. **Create validation script**
   ```typescript
   // tools/migration/validate-migration.ts
   import fs from 'fs/promises';
   import path from 'path';

   interface ValidationResult {
     success: boolean;
     issues: string[];
     summary: {
       accountsMigrated: number;
       queuesMigrated: number;
       filesMigrated: number;
     };
   }

   export class MigrationValidator {
     constructor(private dataDir: string) {}

     async validate(): Promise<ValidationResult> {
       const issues: string[] = [];
       const summary = {
         accountsMigrated: 0,
         queuesMigrated: 0,
         filesMigrated: 0,
       };

       try {
         // Validate accounts file
         const accountsPath = path.join(this.dataDir, 'accounts.json');
         if (await this.fileExists(accountsPath)) {
           const accountsData = JSON.parse(await fs.readFile(accountsPath, 'utf-8'));

           if (accountsData.version !== '3.0.0') {
             issues.push('Accounts file has incorrect version');
           }

           summary.accountsMigrated = accountsData.accounts?.length || 0;
         } else {
           issues.push('Accounts file not found');
         }

         // Validate queue state file
         const queuePath = path.join(this.dataDir, 'queue_state.json');
         if (await this.fileExists(queuePath)) {
           const queueData = JSON.parse(await fs.readFile(queuePath, 'utf-8'));
           summary.queuesMigrated = queueData.queues?.length || 0;
         } else {
           issues.push('Queue state file not found');
         }

         // Count total files
         const dataFiles = await fs.readdir(this.dataDir);
         summary.filesMigrated = dataFiles.filter(f => f.endsWith('.json')).length;

       } catch (error) {
         issues.push(`Validation error: ${error.message}`);
       }

       return {
         success: issues.length === 0,
         issues,
         summary,
       };
     }

     private async fileExists(filePath: string): Promise<boolean> {
       try {
         await fs.access(filePath);
         return true;
       } catch {
         return false;
       }
     }
   }

   // Run validation
   const validator = new MigrationValidator('./data');
   validator.validate().then(result => {
     console.log('Migration validation result:');
     console.log(JSON.stringify(result, null, 2));
   });
   ```

### Step 7: Build Pipeline Setup (Day 15)
1. **Configure production build**
   ```json
   // electron-builder.json (production)
   {
     "appId": "com.suno.app.manager",
     "productName": "Suno Account Manager",
     "version": "3.0.0",
     "directories": {
       "output": "release",
       "buildResources": "assets"
     },
     "files": [
       "dist-electron/**/*",
       "backend/**/*",
       "data/**/*",
       "!node_modules/**/*"
     ],
     "extraResources": [
       {
         "from": "assets",
         "to": "assets"
       }
     ],
     "win": {
       "target": [
         {
           "target": "nsis",
           "arch": ["x64"],
           "artifactName": "suno-account-manager-${version}-setup.exe"
         }
       ],
       "requestedExecutionLevel": "asInvoker"
     },
     "mac": {
       "target": [
         {
           "target": "dmg",
           "arch": ["x64", "arm64"],
           "artifactName": "Suno-Account-Manager-${version}.dmg"
         }
       ]
     },
     "linux": {
       "target": [
         {
           "target": "AppImage",
           "arch": ["x64"],
           "artifactName": "suno-account-manager-${version}.AppImage"
         }
       ]
     },
     "nsis": {
       "oneClick": false,
       "allowToChangeInstallationDirectory": true,
       "perMachine": false,
       "createDesktopShortcut": true,
       "createStartMenuShortcut": true
     },
     "publish": {
       "provider": "github",
       "owner": "your-username",
       "repo": "suno-account-manager"
     }
   }
   ```

2. **Create build scripts**
   ```bash
   # scripts/build.sh
   #!/bin/bash

   echo "Building Suno Account Manager v3.0..."

   # Clean previous builds
   rm -rf dist release

   # Build React app
   echo "Building React app..."
   npm run build:renderer

   # Build Electron main process
   echo "Building Electron main process..."
   npm run build:main

   # Package with Electron Builder
   echo "Packaging application..."
   npm run pack

   echo "Build completed!"
   ls -la release/
   ```

## Todo List

- [ ] Setup testing infrastructure (Jest, Playwright, Vitest)
- [ ] Implement unit tests for components and stores
- [ ] Create integration tests for IPC and Python bridge
- [ ] Implement end-to-end tests for user workflows
- [ ] Set up performance monitoring and benchmarking
- [ ] Create data migration tools
-   [ ] Backup creation script
   - [ ] Account migration script
   - [ ] Queue state migration
   - [ ] Validation script
- [ ] Optimize build pipeline for production
- [ ] Configure Electron Builder for distribution
- [ ] Test installation and update mechanisms
- [ ] Create documentation for migration process

## Success Criteria

- ✅ All unit tests passing with >70% coverage
- ✅ Integration tests covering IPC communication
- ✅ End-to-end tests covering all user workflows
- ✅ Performance benchmarks meeting or exceeding CustomTkinter
- ✅ Memory usage within acceptable limits
- ✅ Data migration tools working correctly
- ✅ Production build pipeline optimized
- ✅ Installation and update mechanisms working
- ✅ Error handling and recovery tested thoroughly

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Migration data loss** | Low | Critical | Comprehensive backup and validation |
| **Performance regression** | Medium | High | Benchmarking and optimization |
| **Testing coverage gaps** | Low | Medium | Comprehensive test suite |
| **Build pipeline issues** | Medium | Medium | Multiple build environments |
| **Platform compatibility** | Medium | Medium | Cross-platform testing |

## Security Considerations

1. **Data Encryption:** Encrypt sensitive user data during migration
2. **Code Signing:** Sign applications for distribution security
3. **Input Validation:** Validate all user inputs and API responses
4. **Secure IPC:** Maintain context isolation and API restrictions
5. **Update Security:** Implement secure update mechanisms

## Next Steps

1. **Production Deployment:** Release first version of React + Electron app
2. **User Documentation:** Create migration guides and user manuals
3. **Beta Testing:** Limited release for user feedback
4. **Performance Monitoring:** Track real-world performance metrics
5. **Maintenance:** Ongoing support and updates

---

*This phase ensures the React + Electron application is production-ready with comprehensive testing, performance optimization, and a smooth migration path for existing users.*