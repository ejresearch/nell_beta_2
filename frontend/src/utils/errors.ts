// src/utils/errors.ts

// Define ApiError here; no import from '../types'
export class ApiError extends Error {
  public code: string;
  public details?: any;

  constructor({ message, code, details }: { message: string; code: string; details?: any }) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
  }
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  return 'An unexpected error occurred';
}

export function isNetworkError(error: unknown): boolean {
  return error instanceof ApiError && error.code === 'NETWORK_ERROR';
}

export function isValidationError(error: unknown): boolean {
  return error instanceof ApiError && error.code.startsWith('4');
}

export function isServerError(error: unknown): boolean {
  return error instanceof ApiError && error.code.startsWith('5');
}

// Error toast helper (to be used with a toast library later)
export function handleApiError(error: unknown, context: string = ''): void {
  const message = getErrorMessage(error);
  const contextMessage = context ? `${context}: ${message}` : message;

  console.error('API Error:', error);

  // TODO: Integrate with toast notification system
  // toast.error(contextMessage);

  // For now, just log to console
  console.error(contextMessage);
}

