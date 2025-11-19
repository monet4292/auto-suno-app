/**
 * Error handling middleware
 */

import { Request, Response, NextFunction } from 'express';
import { logger, logError } from '../../utils/logger';
import { ApiResponse, ApiError } from '../../types';

export class AppError extends Error {
  public statusCode: number;
  public code: string;
  public isOperational: boolean;
  public details?: Record<string, any>;

  constructor(
    message: string,
    statusCode: number = 500,
    code: string = 'INTERNAL_ERROR',
    details?: Record<string, any>
  ) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;
    this.details = details;

    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 400, 'VALIDATION_ERROR', details);
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication required') {
    super(message, 401, 'AUTHENTICATION_ERROR');
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string = 'Insufficient permissions') {
    super(message, 403, 'AUTHORIZATION_ERROR');
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = 'Resource not found') {
    super(message, 404, 'NOT_FOUND');
  }
}

export class ConflictError extends AppError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 409, 'CONFLICT_ERROR', details);
  }
}

export class RateLimitError extends AppError {
  constructor(message: string = 'Rate limit exceeded') {
    super(message, 429, 'RATE_LIMIT_ERROR');
  }
}

export class ExternalApiError extends AppError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 502, 'EXTERNAL_API_ERROR', details);
  }
}

// Async error handler wrapper
export const asyncHandler = (fn: Function) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Main error handling middleware
export const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  let statusCode = 500;
  let errorCode = 'INTERNAL_ERROR';
  let message = 'Internal server error';
  let details: Record<string, any> | undefined;

  // Handle known application errors
  if (error instanceof AppError) {
    statusCode = error.statusCode;
    errorCode = error.code;
    message = error.message;
    details = error.details;
  } else {
    // Handle unknown errors
    details = {
      stack: error.stack,
      name: error.name
    };
  }

  // Log error details
  logError(error, {
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    body: req.body,
    query: req.query,
    params: req.params
  });

  // Create error response
  const errorResponse: ApiResponse = {
    success: false,
    error: message,
    timestamp: new Date().toISOString()
  };

  // Include details in development
  if (process.env.NODE_ENV === 'development' && details) {
    (errorResponse as any).details = details;
  }

  // Send error response
  res.status(statusCode).json(errorResponse);
};

// 404 handler
export const notFoundHandler = (req: Request, res: Response): void => {
  const errorResponse: ApiResponse = {
    success: false,
    error: `Route ${req.method} ${req.path} not found`,
    timestamp: new Date().toISOString()
  };

  res.status(404).json(errorResponse);
};

// Request validation error helper
export const createValidationError = (field: string, message: string): ValidationError => {
  return new ValidationError(`Validation failed for ${field}`, {
    field,
    message
  });
};

// Multiple validation errors helper
export const createMultipleValidationErrors = (errors: Array<{ field: string; message: string }>): ValidationError => {
  return new ValidationError('Multiple validation errors', {
    errors
  });
};