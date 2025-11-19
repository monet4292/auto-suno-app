import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useElectron, useBackend } from './providers/ElectronProvider';

import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Accounts from './pages/Accounts';
import SongCreation from './pages/SongCreation';
import Downloads from './pages/Downloads';
import History from './pages/History';
import Settings from './pages/Settings';

function App() {
  const { isElectron, isConnected, backendReady, lastError } = useElectron();

  // Show connection status overlay when not ready
  const showConnectionOverlay = isElectron && (!isConnected || !backendReady);

  return (
    <div className="app">
      {/* Connection Status Overlay */}
      {showConnectionOverlay && (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-90 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md mx-4 text-center">
            <div className="mb-4">
              {!isConnected ? (
                <>
                  <div className="text-red-500 text-4xl mb-2">🔌</div>
                  <h2 className="text-xl font-semibold text-gray-100 mb-2">
                    Connecting to Electron
                  </h2>
                  <p className="text-gray-400">
                    Establishing connection with the desktop application...
                  </p>
                </>
              ) : (
                <>
                  <div className="text-yellow-500 text-4xl mb-2">🐍</div>
                  <h2 className="text-xl font-semibold text-gray-100 mb-2">
                    Starting Backend
                  </h2>
                  <p className="text-gray-400">
                    Initializing Python backend server...
                  </p>
                </>
              )}
            </div>
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {lastError && (
        <div className="fixed top-4 right-4 z-50 max-w-sm">
          <div className="bg-red-500 bg-opacity-10 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
            <div className="flex items-center">
              <div className="text-xl mr-2">⚠️</div>
              <div>
                <div className="font-semibold">Backend Error</div>
                <div className="text-sm">{lastError.message}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Application */}
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/accounts" element={<Accounts />} />
          <Route path="/create" element={<SongCreation />} />
          <Route path="/downloads" element={<Downloads />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </div>
  );
}

export default App;