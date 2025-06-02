// src/hooks/useApi.ts

import React, { useState, useCallback } from 'react';
import { useApp } from '../context/AppContext';
import { getErrorMessage } from '../utils/errors';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiOptions {
  showSuccessMessage?: string;
  showErrorMessage?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const { showSuccess, showError } = useApp();

  const execute = useCallback(async (...args: any[]): Promise<T | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await apiFunction(...args);
      
      setState({
        data: result,
        loading: false,
        error: null,
      });

      // Show success message if provided
      if (options.showSuccessMessage) {
        showSuccess(options.showSuccessMessage);
      }

      // Call success callback
      if (options.onSuccess) {
        options.onSuccess(result);
      }

      return result;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      
      setState({
        data: null,
        loading: false,
        error: errorMessage,
      });

      // Show error message (default true)
      if (options.showErrorMessage !== false) {
        showError(errorMessage);
      }

      // Call error callback
      if (options.onError) {
        options.onError(errorMessage);
      }

      return null;
    }
  }, [apiFunction, options, showSuccess, showError]);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    execute,
    reset,
  };
}

// Specialized hook for API calls that should run immediately
export function useApiQuery<T = any>(
  apiFunction: () => Promise<T>,
  dependencies: any[] = [],
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const apiHook = useApi(apiFunction, options);

  // Execute immediately when dependencies change
  React.useEffect(() => {
    apiHook.execute();
  }, dependencies);

  return apiHook;
}

// Hook for mutations (create, update, delete operations)
export function useApiMutation<T = any, P = any>(
  apiFunction: (params: P) => Promise<T>,
  options: UseApiOptions = {}
): Omit<UseApiReturn<T>, 'execute'> & {
  mutate: (params: P) => Promise<T | null>;
  mutateAsync: (params: P) => Promise<T>;
} {
  const apiHook = useApi(apiFunction, options);

  const mutateAsync = useCallback(async (params: P): Promise<T> => {
    const result = await apiHook.execute(params);
    if (result === null) {
      throw new Error(apiHook.error || 'Mutation failed');
    }
    return result;
  }, [apiHook]);

  const mutate = useCallback(async (params: P): Promise<T | null> => {
    return apiHook.execute(params);
  }, [apiHook]);

  return {
    data: apiHook.data,
    loading: apiHook.loading,
    error: apiHook.error,
    reset: apiHook.reset,
    mutate,
    mutateAsync,
  };
}
