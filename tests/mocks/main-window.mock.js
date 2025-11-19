// Mock for MainWindow to avoid __filename conflicts
class MockMainWindow {
  constructor() {
    this.window = null;
    this.isDestroyed = false;
  }

  async createWindow() {
    this.window = {
      loadURL: jest.fn(),
      maximize: jest.fn(),
      show: jest.fn(),
      on: jest.fn(),
      webContents: {
        on: jest.fn(),
        openDevTools: jest.fn()
      }
    };
    return this.window;
  }

  destroy() {
    this.isDestroyed = true;
    this.window = null;
  }

  show() {}
  hide() {}
  minimize() {}
  maximize() {}
  close() {}
  reload() {}

  getWindow() {
    return this.window;
  }

  isVisible() {
    return true;
  }

  isFocused() {
    return true;
  }
}

module.exports = {
  MainWindow: MockMainWindow
};