/**
 * Authentication and authorization middleware
 */

import { Request, Response, NextFunction } from 'express';
import { AuthenticationError, AuthorizationError } from './error';
import { RequestWithAuth } from '../../types';

// Session token extraction middleware
export const extractSessionToken = (
  req: RequestWithAuth,
  res: Response,
  next: NextFunction
): void => {
  try {
    // Try to get token from Authorization header
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      req.sessionToken = authHeader.substring(7);
      next();
      return;
    }

    // Try to get token from query parameter (for bridge requests)
    const tokenFromQuery = req.query.session_token as string;
    if (tokenFromQuery) {
      req.sessionToken = tokenFromQuery;
      next();
      return;
    }

    // Try to get token from request body (for bridge requests)
    const tokenFromBody = req.body?.session_token;
    if (tokenFromBody) {
      req.sessionToken = tokenFromBody;
      next();
      return;
    }

    // No token found - this is acceptable for some endpoints
    next();
  } catch (error) {
    next(new AuthenticationError('Failed to extract session token'));
  }
};

// Require authentication middleware
export const requireAuth = (
  req: RequestWithAuth,
  res: Response,
  next: NextFunction
): void => {
  if (!req.sessionToken) {
    throw new AuthenticationError('Session token is required for this endpoint');
  }

  // Basic token validation (JWT validation would be added here)
  if (req.sessionToken.length < 10) {
    throw new AuthenticationError('Invalid session token format');
  }

  next();
};

// Optional authentication middleware
export const optionalAuth = (
  req: RequestWithAuth,
  res: Response,
  next: NextFunction
): void => {
  // Token extraction is already handled by extractSessionToken
  // This middleware just marks that authentication was attempted
  (req as any).authAttempted = true;
  next();
};

// API key validation for bridge endpoints
export const validateBridgeAccess = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  // For now, allow all local requests
  const clientIP = req.ip || req.connection.remoteAddress;

  const allowedIPs = [
    '127.0.0.1',
    '::1',
    'localhost',
    '::ffff:127.0.0.1' // IPv6-mapped IPv4
  ];

  const isAllowed = allowedIPs.includes(clientIP as string) ||
                   clientIP?.startsWith('192.168.') || // Private networks
                   clientIP?.startsWith('10.') ||
                   clientIP?.startsWith('172.');

  if (!isAllowed && process.env.NODE_ENV === 'production') {
    throw new AuthorizationError('Bridge access denied from this IP address');
  }

  next();
};

// User agent validation for suspicious requests
export const validateUserAgent = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const userAgent = req.get('User-Agent');

  // Block requests without user agent (likely bots)
  if (!userAgent && process.env.NODE_ENV === 'production') {
    throw new AuthorizationError('User-Agent header is required');
  }

  // Check for known bot patterns
  const botPatterns = [
    /bot/i,
    /crawler/i,
    /spider/i,
    /scraper/i
  ];

  if (userAgent && botPatterns.some(pattern => pattern.test(userAgent))) {
    if (process.env.NODE_ENV === 'production') {
      throw new AuthorizationError('Bot access not allowed');
    } else {
      // Log in development but allow
      console.warn(`Bot user agent detected: ${userAgent}`);
    }
  }

  next();
};

// Rate limiting per user/session
export const createRateLimitMiddleware = (maxRequests: number, windowMs: number) => {
  const requests = new Map<string, { count: number; resetTime: number }>();

  return (req: Request, res: Response, next: NextFunction): void => {
    const key = req.sessionToken || req.ip || 'unknown';
    const now = Date.now();

    // Clean up expired entries
    for (const [k, v] of requests.entries()) {
      if (now > v.resetTime) {
        requests.delete(k);
      }
    }

    // Get or create entry for this key
    let entry = requests.get(key);
    if (!entry) {
      entry = {
        count: 0,
        resetTime: now + windowMs
      };
      requests.set(key, entry);
    }

    // Check rate limit
    if (entry.count >= maxRequests) {
      const resetIn = Math.ceil((entry.resetTime - now) / 1000);
      res.set('Retry-After', resetIn.toString());
      throw new AuthorizationError(`Rate limit exceeded. Try again in ${resetIn} seconds.`);
    }

    // Increment counter
    entry.count++;

    // Set rate limit headers
    res.set({
      'X-RateLimit-Limit': maxRequests.toString(),
      'X-RateLimit-Remaining': Math.max(0, maxRequests - entry.count).toString(),
      'X-RateLimit-Reset': new Date(entry.resetTime).toISOString()
    });

    next();
  };
};