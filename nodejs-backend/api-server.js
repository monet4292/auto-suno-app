/**
 * Node.js API Server for Suno Account Manager
 * Proof of Concept for Python to Node.js Migration
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Import Node.js modules (to be implemented)
const SunoApiClient = require('./src/api/suno-api-client');
const DownloadManager = require('./src/core/download-manager');

// Initialize managers
const apiClient = new SunoApiClient();
const downloadManager = new DownloadManager();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: '1.0.0-nodejs-poc'
  });
});

// API Routes - Mirror Python functionality

/**
 * Fetch clips from profile
 * GET /api/clips/profile/:username?page=0
 */
app.get('/api/clips/profile/:username', async (req, res) => {
  try {
    const { username } = req.params;
    const page = parseInt(req.query.page) || 0;

    console.log(`Fetching clips for profile: ${username}, page: ${page}`);

    // This would implement the same logic as Python's fetch_profile_clips
    const clips = await apiClient.fetchProfileClips(username, page);

    res.json({
      success: true,
      data: clips,
      page: page,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching profile clips:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Fetch current user's clips (/me)
 * GET /api/clips/me
 */
app.get('/api/clips/me', async (req, res) => {
  try {
    const sessionToken = req.headers.authorization?.replace('Bearer ', '');

    if (!sessionToken) {
      return res.status(401).json({
        success: false,
        error: 'Session token required'
      });
    }

    // Update API client with session token
    apiClient.updateSessionToken(sessionToken);

    const clips = await apiClient.fetchMyClips();

    res.json({
      success: true,
      data: clips,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching user clips:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Get current user information
 * GET /api/user/info
 */
app.get('/api/user/info', async (req, res) => {
  try {
    const sessionToken = req.headers.authorization?.replace('Bearer ', '');

    if (!sessionToken) {
      return res.status(401).json({
        success: false,
        error: 'Session token required'
      });
    }

    apiClient.updateSessionToken(sessionToken);
    const userInfo = await apiClient.getCurrentUserInfo();

    res.json({
      success: true,
      data: userInfo,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching user info:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Queue management endpoints
 * These would mirror the Python QueueManager functionality
 */

/**
 * Get queue status
 * GET /api/queue/status
 */
app.get('/api/queue/status', async (req, res) => {
  try {
    // This would integrate with queue management
    // For now, return mock status
    res.json({
      success: true,
      data: {
        active_queues: 0,
        pending_songs: 0,
        completed_today: 0,
        status: 'idle'
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Compatibility endpoint for Python integration
 * POST /api/compatibility/python-bridge
 */
app.post('/api/compatibility/python-bridge', async (req, res) => {
  try {
    const { action, data } = req.body;

    console.log(`Python bridge request: ${action}`);

    switch (action) {
      case 'test_connection':
        res.json({ success: true, message: 'Node.js API ready' });
        break;

      case 'fetch_clips':
        // Proxy to appropriate endpoint
        if (data.profile) {
          const clips = await apiClient.fetchProfileClips(data.profile, data.page || 0);
          res.json({ success: true, data: clips });
        } else {
          res.json({ success: false, error: 'Profile required' });
        }
        break;

      default:
        res.json({ success: false, error: 'Unknown action' });
    }

  } catch (error) {
    console.error('Python bridge error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    path: req.path,
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`
🚀 Suno Account Manager Node.js API Server
📍 Server running on http://localhost:${PORT}
🔍 Health check: http://localhost:${PORT}/health
📚 API Documentation:
   • GET /api/clips/profile/:username
   • GET /api/clips/me
   • GET /api/user/info
   • GET /api/queue/status
   • POST /api/compatibility/python-bridge

🔗 Python Integration Ready!
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});

module.exports = app;