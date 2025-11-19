import React from 'react';

const Accounts: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-100">Account Management</h2>
        </div>
        <div className="card-body">
          <p className="text-gray-300">
            Account management interface will be implemented in Phase 3.
          </p>
          <div className="mt-4 p-4 bg-gray-750 rounded-lg">
            <p className="text-sm text-gray-400">
              📋 Planned features:
            </p>
            <ul className="mt-2 text-sm text-gray-400 list-disc list-inside">
              <li>Add/remove Suno accounts</li>
              <li>Chrome profile management</li>
              <li>Session status monitoring</li>
              <li>Account settings</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Accounts;