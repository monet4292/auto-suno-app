// React mock to fix NODE_ENV issue
const React = require('react');

// Mock JSX runtime with proper NODE_ENV
const originalJSXRuntime = require('react/jsx-runtime');

// Ensure process.env.NODE_ENV exists
if (!process.env.NODE_ENV) {
  process.env.NODE_ENV = 'test';
}

module.exports = React;
module.exports.jsx = originalJSXRuntime.jsx;
module.exports.jsxs = originalJSXRuntime.jsxs;
module.exports.Fragment = React.Fragment;