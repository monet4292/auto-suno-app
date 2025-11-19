/**
 * API routes index
 */

import { Router } from 'express';
import { asyncHandler } from '../middleware/error';

// Import route modules (will be created next)
// import accountsRouter from './accounts';
// import clipsRouter from './clips';
// import downloadRouter from './download';
// import bridgeRouter from './bridge';

const router = Router();

// API info endpoint
router.get('/', asyncHandler(async (req, res) => {
  res.json({
    success: true,
    message: 'Suno Manager API v1.0',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    endpoints: {
      accounts: {
        base: '/accounts',
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        description: 'Account management operations'
      },
      clips: {
        base: '/clips',
        methods: ['GET'],
        description: 'Clip fetching and management'
      },
      download: {
        base: '/download',
        methods: ['POST', 'GET'],
        description: 'Download operations'
      },
      bridge: {
        base: '/bridge',
        methods: ['POST'],
        description: 'Python-Node.js compatibility bridge'
      }
    }
  });
}));

// Health check
router.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// Mount route modules (uncomment as they're created)
// router.use('/accounts', accountsRouter);
// router.use('/clips', clipsRouter);
// router.use('/download', downloadRouter);
// router.use('/bridge', bridgeRouter);

export default router;