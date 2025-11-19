/**
 * Main Express server
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { config } from './utils/config';
import { logger, logApiRequest, logApiResponse, RequestTimer } from './utils/logger';
import { errorHandler, notFoundHandler } from './api/middleware/error';
import { extractSessionToken, validateBridgeAccess } from './api/middleware/auth';

// Import routes
import routes from './api/routes';

const app = express();
const PORT = config.port;

// Trust proxy for rate limiting and IP detection
app.set('trust proxy', 1);

// Security middleware
if (config.security.enableHelmet) {
  app.use(helmet({
    contentSecurityPolicy: false, // Disable CSP for API
    crossOriginEmbedderPolicy: false
  }));
}

// Compression middleware
app.use(compression());

// CORS configuration
app.use(cors({
  origin: config.cors.origins,
  credentials: config.cors.credentials,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

// Rate limiting
if (config.security.rateLimitEnabled) {
  const limiter = rateLimit({
    windowMs: config.security.rateLimitWindow,
    max: config.security.rateLimitMax,
    message: {
      success: false,
      error: 'Too many requests from this IP, please try again later',
      timestamp: new Date().toISOString()
    },
    standardHeaders: true,
    legacyHeaders: false,
  });
  app.use(limiter);
}

// Body parsing middleware
app.use(express.json({
  limit: '10mb',
  verify: (req, res, buf) => {
    // Store raw body for signature verification if needed
    (req as any).rawBody = buf;
  }
}));
app.use(express.urlencoded({
  extended: true,
  limit: '10mb'
}));

// Request logging and timing
app.use((req, res, next) => {
  const timer = new RequestTimer();

  // Log request
  logApiRequest(req.method, req.path, req.ip, req.get('User-Agent'));

  // Override res.end to log response timing
  const originalEnd = res.end;
  res.end = function(chunk?: any, encoding?: any) {
    const duration = timer.log(`${req.method} ${req.path}`, {
      statusCode: res.statusCode,
      ip: req.ip
    });
    logApiResponse(req.method, req.path, res.statusCode, duration);

    originalEnd.call(this, chunk, encoding);
  };

  next();
});

// Authentication middleware (extract session token)
app.use(extractSessionToken);

// Health check endpoint (no auth required)
app.get('/health', (req, res) => {
  const memory = process.memoryUsage();

  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.npm_package_version || '1.0.0',
    environment: config.nodeEnv,
    memory: {
      rss: `${Math.round(memory.rss / 1024 / 1024)}MB`,
      heapUsed: `${Math.round(memory.heapUsed / 1024 / 1024)}MB`,
      heapTotal: `${Math.round(memory.heapTotal / 1024 / 1024)}MB`,
      external: `${Math.round(memory.external / 1024 / 1024)}MB`
    }
  });
});

// API root endpoint
app.get('/api', (req, res) => {
  res.json({
    success: true,
    message: 'Suno Manager API Server',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      accounts: '/api/accounts',
      clips: '/api/clips',
      download: '/api/download',
      bridge: '/api/bridge'
    },
    documentation: '/api/docs',
    timestamp: new Date().toISOString()
  });
});

// API routes
app.use('/api', routes);

// Bridge routes with special validation
// app.use('/api/bridge', validateBridgeAccess, bridgeRoutes);

// Static file serving for documentation (if needed)
// app.use('/api/docs', express.static(path.join(__dirname, '../docs')));

// 404 handler for API routes
app.use('/api/*', notFoundHandler);

// Global error handler
app.use(errorHandler);

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', {
    promise,
    reason,
    timestamp: new Date().toISOString()
  });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', {
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString()
  });

  // Graceful shutdown
  process.exit(1);
});

// Graceful shutdown handler
const gracefulShutdown = (signal: string) => {
  logger.info(`Received ${signal}. Starting graceful shutdown...`);

  // Close server and database connections here
  process.exit(0);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Start server
const server = app.listen(PORT, () => {
  logger.info(`🚀 Node.js API server running on port ${PORT}`, {
    environment: config.nodeEnv,
    port: PORT,
    corsOrigins: config.cors.origins,
    rateLimit: config.security.rateLimitEnabled,
    helmet: config.security.enableHelmet
  });

  logger.info(`📍 Health check available at: http://localhost:${PORT}/health`);
  logger.info(`🔗 API documentation available at: http://localhost:${PORT}/api`);
});

// Export server for testing
export default server;