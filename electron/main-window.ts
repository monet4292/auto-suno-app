import pkg from 'electron';
const { BrowserWindow, screen, Menu, app, shell } = pkg;
import type { BrowserWindow as BrowserWindowType } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import { WindowState } from '../src/types/electron';


export class MainWindow {
  private window: BrowserWindowType | null = null;
  private isDev: boolean;
  private statePath: string;
  private windowState: Partial<WindowState> = {};

  constructor(isDev: boolean = process.env.NODE_ENV === 'development') {
    this.isDev = isDev;
    this.statePath = path.join(app.getPath('userData'), 'window-state.json');
    this.loadWindowState();
  }

  /**
   * Create and show the main window
   */
  create(): void {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;

    // Default window configuration
    const defaultConfig = {
      width: Math.min(1400, width - 100),
      height: Math.min(850, height - 100),
      minWidth: 1200,
      minHeight: 700,
      x: Math.floor((width - 1400) / 2),
      y: Math.floor((height - 850) / 2)
    };

    // Use saved state if available
    const windowConfig = {
      ...defaultConfig,
      ...this.windowState.bounds
    };

    this.window = new BrowserWindow({
      width: windowConfig.width,
      height: windowConfig.height,
      minWidth: 1200,
      minHeight: 700,
      x: windowConfig.x,
      y: windowConfig.y,
      webPreferences: {
        preload: path.join(__dirname, 'preload.cjs'),
        contextIsolation: true,
        nodeIntegration: false,
        nodeIntegrationInWorker: false,
        sandbox: false, // Required for some Electron APIs
        webSecurity: !this.isDev,
        allowRunningInsecureContent: this.isDev
      },
      icon: this.getAppIcon(),
      show: false,
      titleBarStyle: 'default',
      title: 'Suno Account Manager',
      backgroundColor: '#1f2937',
      darkTheme: true
    });

    // Restore maximized state
    if (this.windowState.isMaximized) {
      this.window.maximize();
    }

    this.setupEventHandlers();
    this.loadContent();
    this.setupMenu();

    // Show window when ready
    this.window.once('ready-to-show', () => {
      this.window!.show();

      if (this.isDev) {
        this.window!.webContents.openDevTools();
      }
    });

    // Handle window closed
    this.window.on('closed', () => {
      this.window = null;
    });
  }

  /**
   * Setup window event handlers
   */
  private setupEventHandlers(): void {
    if (!this.window) return;

    // Track window state changes
    this.window.on('resize', () => this.saveWindowState());
    this.window.on('move', () => this.saveWindowState());
    this.window.on('maximize', () => {
      this.windowState.isMaximized = true;
      this.saveWindowState();
    });
    this.window.on('unmaximize', () => {
      this.windowState.isMaximized = false;
      this.saveWindowState();
    });

    // Handle external links
    this.window.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });

    // Handle navigation
    this.window.webContents.on('will-navigate', (event, url) => {
      if (url !== this.window!.webContents.getURL()) {
        event.preventDefault();
        shell.openExternal(url);
      }
    });

    // Prevent new window creation
    this.window.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
  }

  /**
   * Load application content
   */
  private loadContent(): void {
    if (!this.window) return;

    if (this.isDev) {
      // Load development server
      this.window.loadURL('http://localhost:5173');

      // Handle dev server connection errors
      this.window.webContents.on('did-fail-load', () => {
        console.log('Dev server not available, showing fallback...');
        this.showFallbackContent();
      });
    } else {
      // Load built application
      const indexPath = path.join(__dirname, '../renderer/index.html');

      if (fs.existsSync(indexPath)) {
        this.window.loadFile(indexPath);
      } else {
        console.error('Built application not found');
        this.showFallbackContent();
      }
    }
  }

  /**
   * Show fallback content if main content fails to load
   */
  private showFallbackContent(): void {
    if (!this.window) return;

    const fallbackHtml = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Suno Account Manager</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1f2937;
            color: #f3f4f6;
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
          }
          .container {
            max-width: 500px;
            text-align: center;
          }
          .icon {
            font-size: 4rem;
            margin-bottom: 1rem;
          }
          h1 { margin: 1rem 0; color: #60a5fa; }
          p { color: #9ca3af; line-height: 1.6; }
          .status {
            background: #374151;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 2rem 0;
          }
          .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #4b5563;
            border-radius: 50%;
            border-top-color: #60a5fa;
            animation: spin 1s ease-in-out infinite;
            margin-right: 0.5rem;
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="icon">🎵</div>
          <h1>Suno Account Manager</h1>
          <div class="status">
            <span class="loading"></span>
            ${this.isDev ? 'Waiting for development server...' : 'Loading application...'}
          </div>
          <p>
            ${this.isDev
              ? 'Please make sure the development server is running on <code>http://localhost:5173</code>'
              : 'The application is starting up. Please wait...'}
          </p>
          <button onclick="location.reload()" style="
            background: #60a5fa;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.375rem;
            cursor: pointer;
            margin-top: 1rem;
            font-size: 1rem;
          ">
            Retry
          </button>
        </div>
      </body>
      </html>
    `;

    this.window.loadURL(`data:text/html;charset=UTF-8,${encodeURIComponent(fallbackHtml)}`);
  }

  /**
   * Setup application menu
   */
  private setupMenu(): void {
    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: 'File',
        submenu: [
          {
            label: 'New Account',
            accelerator: 'CmdOrCtrl+N',
            click: () => {
              this.window?.webContents.send('MENU_ACTION', 'NEW_ACCOUNT');
            }
          },
          { type: 'separator' as const },
          {
            label: 'Preferences',
            accelerator: process.platform === 'darwin' ? 'Cmd+,' : 'Ctrl+,',
            click: () => {
              this.window?.webContents.send('MENU_ACTION', 'PREFERENCES');
            }
          },
          { type: 'separator' as const },
          {
            label: 'Exit',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => {
              app.quit();
            }
          }
        ]
      },
      {
        label: 'View',
        submenu: [
          { role: 'reload' },
          { role: 'forceReload' },
          { type: 'separator' as const },
          { role: 'resetZoom' },
          { role: 'zoomIn' },
          { role: 'zoomOut' },
          { type: 'separator' as const },
          { role: 'togglefullscreen' },
          ...(this.isDev ? [
            { type: 'separator' as const },
              { role: 'toggleDevTools' as const }
          ] : [])
        ]
      },
      {
        label: 'Window',
        submenu: [
          { role: 'minimize' },
          { role: 'close' }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'About',
            click: () => {
              this.window?.webContents.send('MENU_ACTION', 'ABOUT');
            }
          },
          {
            label: 'Learn More',
            click: () => {
              shell.openExternal('https://github.com/yourusername/Auto-Suno-App');
            }
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  /**
   * Get application icon path
   */
  private getAppIcon(): string | undefined {
    const iconPaths = [
      path.join(__dirname, '../../assets/icon.png'),
      path.join(__dirname, '../../assets/icon.ico'),
      path.join(__dirname, '../../assets/icon.icns')
    ];

    for (const iconPath of iconPaths) {
      if (fs.existsSync(iconPath)) {
        return iconPath;
      }
    }

    return undefined;
  }

  /**
   * Load window state from file
   */
  private loadWindowState(): void {
    try {
      if (fs.existsSync(this.statePath)) {
        const data = fs.readFileSync(this.statePath, 'utf8');
        this.windowState = JSON.parse(data);
      }
    } catch (error) {
      console.warn('Failed to load window state:', error);
    }
  }

  /**
   * Save window state to file
   */
  private saveWindowState(): void {
    if (!this.window) return;

    try {
      const bounds = this.window.getBounds();
      this.windowState = {
        ...this.windowState,
        bounds: {
          x: bounds.x,
          y: bounds.y,
          width: bounds.width,
          height: bounds.height
        },
        isMaximized: this.window.isMaximized()
      };

      fs.writeFileSync(this.statePath, JSON.stringify(this.windowState, null, 2));
    } catch (error) {
      console.warn('Failed to save window state:', error);
    }
  }

  /**
   * Get window instance
   */
  getInstance(): BrowserWindowType | null {
    return this.window;
  }

  /**
   * Get current window state
   */
  getWindowState(): WindowState {
    if (!this.window) {
      throw new Error('Window not created');
    }

    const bounds = this.window.getBounds();

    return {
      isMaximized: this.window.isMaximized(),
      isMinimized: this.window.isMinimized(),
      isFocused: this.window.isFocused(),
      bounds: {
        x: bounds.x,
        y: bounds.y,
        width: bounds.width,
        height: bounds.height
      }
    };
  }

  /**
   * Focus window
   */
  focus(): void {
    if (this.window) {
      if (this.window.isMinimized()) {
        this.window.restore();
      }
      this.window.focus();
    }
  }

  /**
   * Close window
   */
  close(): void {
    if (this.window) {
      this.window.close();
    }
  }

  /**
   * Send message to renderer process
   */
  send(channel: string, ...args: any[]): void {
    if (this.window && !this.window.isDestroyed()) {
      this.window.webContents.send(channel, ...args);
    }
  }
}