/**
 * Application configuration
 */

import path from 'path';
import { logger } from './logger';

export interface AppConfig {
  port: number;
  nodeEnv: string;
  dataDir: string;
  profilesDir: string;
  downloadsDir: string;
  sunoApi: {
    baseUrl: string;
    timeout: number;
    rateLimitDelay: number;
    maxRetries: number;
  };
  cors: {
    origins: string[];
    credentials: boolean;
  };
  logging: {
    level: string;
    file: string;
  };
  security: {
    enableHelmet: boolean;
    rateLimitEnabled: boolean;
    rateLimitWindow: number;
    rateLimitMax: number;
  };
}

// Default configuration
const defaultConfig: AppConfig = {
  port: parseInt(process.env.PORT || '3000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  dataDir: process.env.DATA_DIR || path.join(__dirname, '../../data'),
  profilesDir: process.env.PROFILES_DIR || path.join(__dirname, '../../profiles'),
  downloadsDir: process.env.DOWNLOADS_DIR || path.join(__dirname, '../../downloads'),
  sunoApi: {
    baseUrl: process.env.SUNO_API_BASE_URL || 'https://studio-api.prod.suno.com/api',
    timeout: parseInt(process.env.REQUEST_TIMEOUT || '30000', 10),
    rateLimitDelay: parseInt(process.env.RATE_LIMIT_DELAY || '2000', 10),
    maxRetries: parseInt(process.env.MAX_RETRIES || '3', 10)
  },
  cors: {
    origins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:8080', 'http://127.0.0.1:8080'],
    credentials: true
  },
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || path.join(__dirname, '../../logs/app.log')
  },
  security: {
    enableHelmet: process.env.ENABLE_HELMET !== 'false',
    rateLimitEnabled: process.env.ENABLE_RATE_LIMIT !== 'false',
    rateLimitWindow: parseInt(process.env.RATE_LIMIT_WINDOW || '900000', 10), // 15 minutes
    rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX || '100', 10)
  }
};

// Validate and create directories
function validateAndCreateDirectories(config: AppConfig): void {
  const dirs = [config.dataDir, config.profilesDir, config.downloadsDir];

  dirs.forEach(dir => {
    try {
      const fs = require('fs');
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        logger.info(`Created directory: ${dir}`);
      }
    } catch (error) {
      logger.error(`Failed to create directory ${dir}:`, error);
    }
  });
}

// Load configuration with validation
export function loadConfig(): AppConfig {
  const config = { ...defaultConfig };

  // Override with environment variables
  if (process.env.PORT) {
    config.port = parseInt(process.env.PORT, 10);
  }

  if (process.env.NODE_ENV) {
    config.nodeEnv = process.env.NODE_ENV;
  }

  // Validate required configuration
  if (!config.sunoApi.baseUrl) {
    throw new Error('SUNO_API_BASE_URL is required');
  }

  if (!config.dataDir) {
    throw new Error('DATA_DIR is required');
  }

  // Validate port range
  if (config.port < 1 || config.port > 65535) {
    throw new Error('PORT must be between 1 and 65535');
  }

  // Validate timeout
  if (config.sunoApi.timeout < 1000) {
    throw new Error('REQUEST_TIMEOUT must be at least 1000ms');
  }

  // Create necessary directories
  validateAndCreateDirectories(config);

  // Log configuration (without sensitive data)
  logger.info('Configuration loaded', {
    port: config.port,
    nodeEnv: config.nodeEnv,
    dataDir: config.dataDir,
    sunoApi: {
      baseUrl: config.sunoApi.baseUrl,
      timeout: config.sunoApi.timeout
    },
    cors: {
      origins: config.cors.origins.length
    },
    security: {
      helmet: config.security.enableHelmet,
      rateLimit: config.security.rateLimitEnabled
    }
  });

  return config;
}

// Export singleton config instance
export const config = loadConfig();

export default config;