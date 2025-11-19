/**
 * Winston logger configuration
 */

import winston from 'winston';
import path from 'path';
import fs from 'fs';

// Ensure logs directory exists
const logsDir = path.join(__dirname, '../../logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Custom log format
const logFormat = winston.format.combine(
  winston.format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss'
  }),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.prettyPrint()
);

// Console format for development
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({
    format: 'HH:mm:ss'
  }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let msg = `${timestamp} [${level}]: ${message}`;

    if (Object.keys(meta).length > 0) {
      msg += ' ' + JSON.stringify(meta, null, 2);
    }

    return msg;
  })
);

// Create logger instance
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: { service: 'suno-manager-api' },
  transports: [
    // Write all logs to combined file
    new winston.transports.File({
      filename: path.join(logsDir, 'app.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 10,
      tailable: true
    }),

    // Write error logs to error file
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true
    }),

    // Write API logs to separate file
    new winston.transports.File({
      filename: path.join(logsDir, 'api.log'),
      level: 'http',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true
    })
  ],

  // Handle uncaught exceptions and rejections
  exceptionHandlers: [
    new winston.transports.File({
      filename: path.join(logsDir, 'exceptions.log')
    })
  ],

  rejectionHandlers: [
    new winston.transports.File({
      filename: path.join(logsDir, 'rejections.log')
    })
  ]
});

// Add console transport for development
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: consoleFormat
  }));
}

// Helper methods for structured logging
export const logApiRequest = (method: string, path: string, ip?: string, userAgent?: string) => {
  logger.http('API Request', {
    method,
    path,
    ip,
    userAgent,
    timestamp: new Date().toISOString()
  });
};

export const logApiResponse = (method: string, path: string, statusCode: number, duration: number) => {
  logger.http('API Response', {
    method,
    path,
    statusCode,
    duration: `${duration}ms`,
    timestamp: new Date().toISOString()
  });
};

export const logError = (error: Error, context?: Record<string, any>) => {
  logger.error('Application Error', {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString()
  });
};

export const logPerformance = (operation: string, duration: number, details?: Record<string, any>) => {
  logger.info('Performance Metric', {
    operation,
    duration: `${duration}ms`,
    ...details,
    timestamp: new Date().toISOString()
  });
};

// Request duration tracker
export class RequestTimer {
  private startTime: number;

  constructor() {
    this.startTime = Date.now();
  }

  getDuration(): number {
    return Date.now() - this.startTime;
  }

  log(operation: string, details?: Record<string, any>) {
    const duration = this.getDuration();
    logPerformance(operation, duration, details);
    return duration;
  }
}

// Export default logger
export default logger;