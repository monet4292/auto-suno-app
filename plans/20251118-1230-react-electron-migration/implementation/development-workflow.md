# Development Workflow Guide

## Overview

This guide outlines the development workflow for migrating Suno Account Manager from CustomTkinter to React + Electron + TypeScript, ensuring consistent development practices and smooth collaboration.

## Prerequisites

### Required Tools
- **Node.js** 18+ (LTS)
- **Python** 3.10+
- **Git** for version control
- **VS Code** recommended IDE
- **Chrome** for debugging and testing

### VS Code Extensions (Recommended)
```json
{
  "recommendations": [
    "ms-python.python",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode.vscode-json",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "ms-vscode.vscode-jest",
    "ms-playwright.playwright"
  ]
}
```

## Repository Structure Setup

### Initial Repository Setup
```bash
# Clone existing repository
git clone <repository-url>
cd auto-suno-app

# Create new branches for migration
git checkout -b feature/react-electron-migration
git checkout -b develop/frontend
git checkout -b develop/backend

# Create new frontend directory structure
mkdir -p frontend
mkdir -p frontend/src/{main,renderer,shared}
mkdir -p frontend/src/renderer/{components,hooks,stores,services,styles,utils}
mkdir -p frontend/public
mkdir -p tests
mkdir -p docs/migration
```

## Development Environment Setup

### 1. Frontend Environment

```bash
# Navigate to frontend directory
cd frontend

# Initialize package.json
npm init -y

# Install dependencies
npm install react@18.2.0 react-dom@18.2.0
npm install react-router-dom@6.8.0 zustand@4.3.6
npm install @tanstack/react-query@4.24.6 axios@1.3.4
npm install clsx@1.2.1 tailwind-merge@1.10.0

# Install development dependencies
npm install -D @types/react@18.0.28 @types/react-dom@18.0.11
npm install -D @types/node@18.14.6 @vitejs/plugin-react@3.1.0
npm install -D typescript@4.9.4 vite@4.1.4
npm install -D electron@23.1.0 electron-builder@23.6.0
npm install -D concurrently@7.6.0 tailwindcss@3.2.7 autoprefixer@10.4.14
npm install -D @headlessui/react@1.7.13 @heroicons/react@2.0.16
npm install -D react-hook-form@7.43.5 react-hot-toast@2.4.0

# Install testing dependencies
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test eslint @typescript-eslint/parser
```

### 2. Backend Environment (Communication Layer)

```bash
# Create backend communication module
mkdir -p backend/src
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (reuse existing ones)
pip install -r ../requirements.txt
```

## Configuration Files

### 1. TypeScript Configuration

#### `frontend/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "allowJs": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/main/*": ["src/main/*"],
      "@/renderer/*": ["src/renderer/*"],
      "@/shared/*": ["src/shared/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "build"]
}
```

#### `frontend/tsconfig.main.json`
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "dist/main",
    "module": "CommonJS",
    "target": "ES2020",
    "noEmit": false,
    "skipLibCheck": true
  },
  "include": ["src/main/**/*"]
}
```

### 2. Vite Configuration

#### `frontend/vite.config.ts`
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist/renderer',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/main': resolve(__dirname, 'src/main'),
      '@/renderer': resolve(__dirname, 'src/renderer'),
      '@/shared': resolve(__dirname, 'src/shared')
    }
  },
  server: {
    port: 5173,
    strictPort: true
  }
});
```

### 3. Tailwind CSS Configuration

#### `frontend/tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        gray: {
          800: '#1f2937',
          900: '#111827',
        }
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### 4. ESLint Configuration

#### `frontend/.eslintrc.json`
```json
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaFeatures": {
      "jsx": true
    },
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "plugins": [
    "react",
    "@typescript-eslint"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "warn",
    "prefer-const": "error",
    "no-var": "error"
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
```

### 5. Playwright Testing Configuration

#### `frontend/playwright.config.ts`
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './src/tests',
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
  webServer: {
    command: 'npm run dev',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Development Scripts

### Package.json Scripts

#### `frontend/package.json` (scripts section)
```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:renderer\" \"npm run dev:main\"",
    "dev:renderer": "vite",
    "dev:main": "tsc -p tsconfig.main.json && electron dist/main/main.js",
    "build": "npm run build:renderer && npm run build:main",
    "build:renderer": "vite build",
    "build:main": "tsc -p tsconfig.main.json",
    "build:all": "npm run build && npm run build:backend && electron-builder",
    "preview": "vite preview",
    "electron": "electron dist/main/main.js",
    "test": "npm run test:unit && npm run test:e2e",
    "test:unit": "vitest",
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
    "clean": "rimraf dist build release",
    "start": "npm run dev"
  }
}
```

### Python Development Scripts

#### `backend/requirements.txt` (add communication dependencies)
```txt
# Existing dependencies
customtkinter>=5.2.0
selenium>=4.15.0
webdriver-manager>=4.0.1
mutagen>=1.47.0
requests>=2.31.0
colorama>=0.4.6

# Additional for communication
psutil>=5.9.0
```

## Git Workflow

### Branch Strategy
```
main                    # Production ready code
├── develop            # Integration branch
├── feature/backend    # Backend communication layer
├── feature/frontend   # React frontend development
├── feature/integration# Integration and testing
└── hotfix/*           # Critical fixes
```

### Commit Convention
```
feat: Add account creation component
fix: Resolve memory leak in progress tracking
docs: Update API documentation
refactor: Optimize queue state management
test: Add e2e tests for download workflow
chore: Update dependencies and configurations
```

### Development Workflow Steps

#### 1. Start New Feature
```bash
# Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/component-name

# Setup development environment
cd frontend
npm install
npm run dev

# In another terminal
cd backend
source venv/bin/activate
python communication_server.py
```

#### 2. Development Process
```bash
# Regular commits
git add .
git commit -m "feat: Implement account panel UI"

# Push to remote for collaboration
git push origin feature/component-name

# Create pull request when ready
gh pr create --title "Implement Account Panel" --body "Feature description..."
```

#### 3. Testing Before Merge
```bash
# Run all tests
npm run test

# Type checking
npm run type-check

# Linting
npm run lint

# Build validation
npm run build
```

#### 4. Merge Process
```bash
# Update develop branch
git checkout develop
git pull origin develop

# Merge feature
git merge feature/component-name

# Push changes
git push origin develop
```

## Development Best Practices

### 1. Code Organization
- Use absolute imports with path aliases (`@/components/Button`)
- Co-locate related files (components, hooks, types)
- Keep components small and focused
- Use composition over inheritance

### 2. TypeScript Usage
- Enable strict mode
- Avoid `any` types
- Use proper interfaces for all data structures
- Leverage type inference where appropriate

### 3. React Patterns
- Use functional components with hooks
- Implement proper error boundaries
- Use useCallback and useMemo for optimization
- Follow React best practices for state management

### 4. Testing Strategy
- Write tests for all components
- Mock external dependencies
- Use Storybook for component development
- Perform E2E testing for critical workflows

### 5. Performance Considerations
- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Optimize bundle size with code splitting
- Monitor memory usage in long-running operations

## Debugging Setup

### 1. VS Code Debug Configuration

#### `.vscode/launch.json`
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Renderer Process",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/frontend/src",
      "sourceMaps": true
    },
    {
      "name": "Debug Main Process",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/frontend/dist/main/main.js",
      "cwd": "${workspaceFolder}/frontend",
      "env": {
        "NODE_ENV": "development"
      },
      "console": "integratedTerminal",
      "outputCapture": "std"
    }
  ]
}
```

### 2. Browser DevTools Setup
- Enable React Developer Tools extension
- Use Redux DevTools for state debugging
- Leverage Performance tab for optimization
- Use Network tab for API debugging

### 3. Python Debugging
```python
# Add debugging to communication server
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def _handle_command(self, command: Dict) -> Response:
    logger.debug(f"Received command: {command}")
    # ... rest of implementation
```

## Continuous Integration

### GitHub Actions Workflow

#### `.github/workflows/ci.yml`
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test-frontend:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Type check
        working-directory: ./frontend
        run: npm run type-check

      - name: Lint
        working-directory: ./frontend
        run: npm run lint

      - name: Unit tests
        working-directory: ./frontend
        run: npm run test:unit

      - name: Build
        working-directory: ./frontend
        run: npm run build

  test-backend:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        working-directory: ./backend
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt

      - name: Run tests
        working-directory: ./backend
        run: |
          source venv/bin/activate
          python -m pytest

  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Install Playwright
        working-directory: ./frontend
        run: npx playwright install --with-deps

      - name: Build application
        working-directory: ./frontend
        run: npm run build

      - name: Run E2E tests
        working-directory: ./frontend
        run: npm run test:e2e

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Documentation Standards

### 1. Code Documentation
```typescript
/**
 * Account management panel component
 *
 * Provides UI for managing Suno.com accounts including:
 * - Creating new accounts with Chrome profiles
 * - Activating existing accounts for use
 * - Renaming and deleting accounts
 * - Viewing account status and session information
 *
 * @example
 * ```tsx
 * <AccountPanel />
 * ```
 */
export function AccountPanel(): JSX.Element {
  // Component implementation
}
```

### 2. API Documentation
```typescript
/**
 * Creates a new Suno account
 *
 * @param accountName - Unique name for the account
 * @param email - Optional email address for the account
 * @returns Promise resolving to creation result
 * @throws {Error} When account name already exists or creation fails
 *
 * @example
 * ```typescript
 * const result = await window.electronAPI.account.create('main_account', 'user@example.com');
 * if (result.account_created) {
 *   console.log('Account created successfully');
 * }
 * ```
 */
create: (accountName: string, email?: string) => Promise<AccountCreateResponse>;
```

### 3. Component Storybook Stories
```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Click me',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Cancel',
  },
};
```

## Performance Monitoring

### 1. React Performance Profiling
```typescript
// Add performance monitoring
import { Profiler } from 'react';

function App() {
  const onRender = (id, phase, actualDuration) => {
    console.log('Component render:', { id, phase, actualDuration });
  };

  return (
    <Profiler id="App" onRender={onRender}>
      <Router>
        <Routes>
          {/* Routes */}
        </Routes>
      </Router>
    </Profiler>
  );
}
```

### 2. Memory Usage Monitoring
```typescript
// Memory usage tracking
const useMemoryMonitor = () => {
  useEffect(() => {
    const interval = setInterval(() => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        console.log('Memory usage:', {
          used: Math.round(memory.usedJSHeapSize / 1024 / 1024) + 'MB',
          total: Math.round(memory.totalJSHeapSize / 1024 / 1024) + 'MB'
        });
      }
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, []);
};
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Electron Doesn't Start
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Check TypeScript compilation
npx tsc --noEmit
```

#### 2. IPC Communication Errors
```bash
# Check Python backend is running
python backend/communication_server.py

# Test communication manually
echo '{"id":"test","type":"ping"}' | python backend/communication_server.py
```

#### 3. React Component Errors
```bash
# Check TypeScript types
npm run type-check

# Clear React dev tools cache
localStorage.clear()
sessionStorage.clear()
```

#### 4. Build Failures
```bash
# Clean build artifacts
npm run clean

# Check for missing dependencies
npm audit fix

# Update build tools
npm update vite @vitejs/plugin-react
```

This development workflow ensures consistent, high-quality development practices throughout the migration process, enabling smooth collaboration and reliable code delivery.