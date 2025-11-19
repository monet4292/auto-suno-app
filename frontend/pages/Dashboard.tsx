import React from 'react';
import { useBackend } from '../providers/ElectronProvider';

const Dashboard: React.FC = () => {
  const { backendReady, isConnected } = useBackend();

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-100">Welcome to Suno Account Manager</h2>
        </div>
        <div className="card-body">
          <p className="text-gray-300 mb-4">
            Manage your Suno.com accounts, create songs in batches, and download your music library.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Connection Status */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-medium text-gray-100 mb-2">Connection Status</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Electron:</span>
                    <span className={`status ${isConnected ? 'status-active' : 'status-inactive'}`}>
                      {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Backend:</span>
                    <span className={`status ${backendReady ? 'status-active' : 'status-inactive'}`}>
                      {backendReady ? 'Ready' : 'Starting...'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-medium text-gray-100 mb-2">Quick Actions</h3>
                <div className="space-y-2">
                  <button className="btn btn-primary w-full">
                    ➕ Add Account
                  </button>
                  <button className="btn btn-secondary w-full">
                    🎼 Create Songs
                  </button>
                  <button className="btn btn-secondary w-full">
                    📥 Download Music
                  </button>
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-medium text-gray-100 mb-2">Statistics</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Total Accounts:</span>
                    <span className="text-gray-300">0</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Active Queues:</span>
                    <span className="text-gray-300">0</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Songs Created:</span>
                    <span className="text-gray-300">0</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Downloaded:</span>
                    <span className="text-gray-300">0</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-xl font-semibold text-gray-100">Getting Started</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-medium text-gray-100 mb-3">1. Add Accounts</h4>
              <p className="text-gray-300 mb-3">
                Add your Suno.com accounts to start managing them. Each account will have its own Chrome profile and session.
              </p>
              <ol className="list-decimal list-inside text-gray-400 space-y-1 text-sm">
                <li>Navigate to Accounts page</li>
                <li>Click "Add Account" button</li>
                <li>Enter account name and email</li>
                <li>Chrome will open for login</li>
                <li>Complete login on Suno.com</li>
              </ol>
            </div>

            <div>
              <h4 className="text-lg font-medium text-gray-100 mb-3">2. Create Songs</h4>
              <p className="text-gray-300 mb-3">
                Create multiple songs at once using our queue system with XML prompts.
              </p>
              <ol className="list-decimal list-inside text-gray-400 space-y-1 text-sm">
                <li>Prepare XML file with song prompts</li>
                <li>Navigate to Create Songs page</li>
                <li>Upload XML file</li>
                <li>Configure batch settings</li>
                <li>Start queue execution</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;