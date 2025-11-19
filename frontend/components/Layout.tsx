import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useElectron } from '../providers/ElectronProvider';

interface LayoutProps {
  children: React.ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: '🏠' },
  { name: 'Accounts', href: '/accounts', icon: '👤' },
  { name: 'Create Songs', href: '/create', icon: '🎼' },
  { name: 'Downloads', href: '/downloads', icon: '📥' },
  { name: 'History', href: '/history', icon: '📜' },
  { name: 'Settings', href: '/settings', icon: '⚙️' },
];

function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const { appVersion, platform, isConnected } = useElectron();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-gray-800 border-r border-gray-700 transition-all duration-300 flex flex-col`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className={`flex items-center ${sidebarOpen ? '' : 'justify-center'}`}>
              <div className="text-2xl mr-2">🎵</div>
              {sidebarOpen && (
                <span className="text-xl font-semibold text-gray-100">Suno Manager</span>
              )}
            </div>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-400 hover:text-gray-200 p-1 rounded"
            >
              {sidebarOpen ? '◀' : '▶'}
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`flex items-center ${sidebarOpen ? '' : 'justify-center'} px-3 py-2 rounded-lg transition-colors duration-200 ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }`}
                  >
                    <span className="text-lg mr-3">{item.icon}</span>
                    {sidebarOpen && <span>{item.name}</span>}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Sidebar Footer */}
        {sidebarOpen && (
          <div className="p-4 border-t border-gray-700">
            <div className="text-xs text-gray-400">
              <div>v{appVersion}</div>
              <div>{platform}</div>
              <div className={`flex items-center mt-1 ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full mr-1 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                {isConnected ? 'Connected' : 'Offline'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-100">
              {navigation.find(item => item.href === location.pathname)?.name || 'Dashboard'}
            </h1>

            <div className="flex items-center space-x-4">
              {/* Window Controls */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => window.electronAPI?.minimizeWindow?.()}
                  className="text-gray-400 hover:text-gray-200 p-2 rounded hover:bg-gray-700"
                  title="Minimize"
                >
                  &#8212;
                </button>
                <button
                  onClick={() => window.electronAPI?.maximizeWindow?.()}
                  className="text-gray-400 hover:text-gray-200 p-2 rounded hover:bg-gray-700"
                  title="Maximize"
                >
                  &#9633;
                </button>
                <button
                  onClick={() => window.electronAPI?.closeWindow?.()}
                  className="text-gray-400 hover:text-red-400 p-2 rounded hover:bg-gray-700"
                  title="Close"
                >
                  &#10005;
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto bg-gray-900">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

export default Layout;