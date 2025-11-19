/**
 * Request validation middleware
 */

import { Request, Response, NextFunction } from 'express';
import { ValidationError, createMultipleValidationErrors } from './error';

// Basic validation rules
export const ValidationRules = {
  required: (value: any): boolean => {
    return value !== null && value !== undefined && value !== '';
  },

  optional: (value: any): boolean => {
    return true; // Optional fields are always valid
  },

  string: (value: any): boolean => {
    return typeof value === 'string';
  },

  number: (value: any): boolean => {
    return typeof value === 'number' && !isNaN(value);
  },

  integer: (value: any): boolean => {
    return Number.isInteger(value);
  },

  boolean: (value: any): boolean => {
    return typeof value === 'boolean';
  },

  array: (value: any): boolean => {
    return Array.isArray(value);
  },

  email: (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  },

  url: (value: string): boolean => {
    try {
      new URL(value);
      return true;
    } catch {
      return false;
    }
  },

  username: (value: string): boolean => {
    // Username should start with @ or be alphanumeric
    return /^[a-zA-Z0-9_]+$/.test(value) || /^@[a-zA-Z0-9_]+$/.test(value);
  },

  uuid: (value: string): boolean => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(value);
  },

  minLength: (min: number) => (value: string): boolean => {
    return typeof value === 'string' && value.length >= min;
  },

  maxLength: (max: number) => (value: string): boolean => {
    return typeof value === 'string' && value.length <= max;
  },

  min: (min: number) => (value: number): boolean => {
    return typeof value === 'number' && value >= min;
  },

  max: (max: number) => (value: number): boolean => {
    return typeof value === 'number' && value <= max;
  },

  range: (min: number, max: number) => (value: number): boolean => {
    return typeof value === 'number' && value >= min && value <= max;
  },

  enum: (values: any[]) => (value: any): boolean => {
    return values.includes(value);
  },

  pattern: (regex: RegExp) => (value: string): boolean => {
    return typeof value === 'string' && regex.test(value);
  }
};

// Validation schema interface
export interface ValidationSchema {
  [key: string]: {
    rules: Array<(value: any) => boolean>;
    required?: boolean;
    message?: string;
  };
}

// Validate request body against schema
export const validateBody = (schema: ValidationSchema) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const errors: Array<{ field: string; message: string }> = [];

    for (const [field, fieldSchema] of Object.entries(schema)) {
      const value = req.body[field];
      const isRequired = fieldSchema.required !== false;

      // Check if field is required
      if (isRequired && !ValidationRules.required(value)) {
        errors.push({
          field,
          message: fieldSchema.message || `${field} is required`
        });
        continue;
      }

      // Skip validation if field is optional and not provided
      if (!isRequired && !ValidationRules.required(value)) {
        continue;
      }

      // Run validation rules
      for (const rule of fieldSchema.rules) {
        if (!rule(value)) {
          errors.push({
            field,
            message: fieldSchema.message || `${field} is invalid`
          });
          break; // Stop at first error for this field
        }
      }
    }

    if (errors.length > 0) {
      throw createMultipleValidationErrors(errors);
    }

    next();
  };
};

// Validate query parameters
export const validateQuery = (schema: ValidationSchema) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const errors: Array<{ field: string; message: string }> = [];

    for (const [field, fieldSchema] of Object.entries(schema)) {
      const value = req.query[field];
      const isRequired = fieldSchema.required !== false;

      // Check if field is required
      if (isRequired && !ValidationRules.required(value)) {
        errors.push({
          field,
          message: fieldSchema.message || `${field} query parameter is required`
        });
        continue;
      }

      // Skip validation if field is optional and not provided
      if (!isRequired && !ValidationRules.required(value)) {
        continue;
      }

      // Convert string query params to appropriate types
      let convertedValue = value;
      if (typeof value === 'string') {
        // Try to convert to number if it looks like one
        if (/^\d+$/.test(value)) {
          convertedValue = parseInt(value, 10);
        } else if (/^\d+\.\d+$/.test(value)) {
          convertedValue = parseFloat(value);
        } else if (value === 'true') {
          convertedValue = true;
        } else if (value === 'false') {
          convertedValue = false;
        }
      }

      // Run validation rules
      for (const rule of fieldSchema.rules) {
        if (!rule(convertedValue)) {
          errors.push({
            field,
            message: fieldSchema.message || `${field} query parameter is invalid`
          });
          break;
        }
      }
    }

    if (errors.length > 0) {
      throw createMultipleValidationErrors(errors);
    }

    next();
  };
};

// Validate URL parameters
export const validateParams = (schema: ValidationSchema) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const errors: Array<{ field: string; message: string }> = [];

    for (const [field, fieldSchema] of Object.entries(schema)) {
      const value = req.params[field];
      const isRequired = fieldSchema.required !== false;

      // Check if field is required
      if (isRequired && !ValidationRules.required(value)) {
        errors.push({
          field,
          message: fieldSchema.message || `${field} parameter is required`
        });
        continue;
      }

      // Skip validation if field is optional and not provided
      if (!isRequired && !ValidationRules.required(value)) {
        continue;
      }

      // Run validation rules
      for (const rule of fieldSchema.rules) {
        if (!rule(value)) {
          errors.push({
            field,
            message: fieldSchema.message || `${field} parameter is invalid`
          });
          break;
        }
      }
    }

    if (errors.length > 0) {
      throw createMultipleValidationErrors(errors);
    }

    next();
  };
};

// Common validation schemas
export const CommonSchemas = {
  accountName: {
    required: true,
    rules: [ValidationRules.string, ValidationRules.minLength(1), ValidationRules.maxLength(50)],
    message: 'Account name must be a string between 1 and 50 characters'
  },

  username: {
    required: true,
    rules: [ValidationRules.string, ValidationRules.username],
    message: 'Username must be alphanumeric (with optional @ prefix)'
  },

  email: {
    required: false,
    rules: [ValidationRules.string, ValidationRules.email],
    message: 'Email must be a valid email address'
  },

  uuid: {
    required: true,
    rules: [ValidationRules.string, ValidationRules.uuid],
    message: 'ID must be a valid UUID'
  },

  page: {
    required: false,
    rules: [ValidationRules.integer, ValidationRules.min(0)],
    message: 'Page must be a non-negative integer'
  },

  maxPages: {
    required: false,
    rules: [ValidationRules.integer, ValidationRules.min(1), ValidationRules.max(100)],
    message: 'Max pages must be an integer between 1 and 100'
  },

  limit: {
    required: false,
    rules: [ValidationRules.integer, ValidationRules.min(1), ValidationRules.max(1000)],
    message: 'Limit must be an integer between 1 and 1000'
  },

  sessionToken: {
    required: true,
    rules: [ValidationRules.string, ValidationRules.minLength(10)],
    message: 'Session token must be a string with at least 10 characters'
  }
};