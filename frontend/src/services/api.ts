// src/services/api.ts
// Simplified version to avoid import errors

import type { Project, UserSettings, ApiResponse } from '../types';
import { ApiError } from '../utils/errors';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // Generic request method with error handling
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError({
          message: errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          code: response.status.toString(),
          details: errorData,
        });
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError({
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        code: 'NETWORK_ERROR',
      });
    }
  }

  // ===== PROJECT ENDPOINTS =====
  
  async getProjects(): Promise<Project[]> {
    const response = await this.request<ApiResponse<Project[]>>('/api/v1/projects');
    return response.data || [];
  }

  async getProject(id: string): Promise<Project> {
    const response = await this.request<ApiResponse<Project>>(`/api/v1/projects/${id}`);
    return response.data;
  }

  async createProject(projectData: any): Promise<Project> {
    const response = await this.request<ApiResponse<Project>>('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
    return response.data;
  }

  async updateProject(id: string, projectData: any): Promise<Project> {
    const response = await this.request<ApiResponse<Project>>(`/api/v1/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(projectData),
    });
    return response.data;
  }

  async deleteProject(id: string): Promise<void> {
    await this.request(`/api/v1/projects/${id}`, { method: 'DELETE' });
  }

  // ===== BUCKET ENDPOINTS =====

  async getBuckets(projectId: string): Promise<any[]> {
    try {
      const response = await this.request<ApiResponse<any[]>>(`/api/v1/projects/${projectId}/buckets`);
      return response.data || [];
    } catch (error) {
      console.warn('Buckets endpoint not implemented yet:', error);
      return [];
    }
  }

  async createBucket(projectId: string, bucketData: any): Promise<any> {
    const response = await this.request<ApiResponse<any>>(`/api/v1/projects/${projectId}/buckets`, {
      method: 'POST',
      body: JSON.stringify(bucketData),
    });
    return response.data;
  }

  // ===== TABLE ENDPOINTS =====

  async getProjectTables(projectId: string): Promise<string[]> {
    try {
      const response = await this.request<ApiResponse<any>>(`/api/v1/projects/${projectId}/tables`);
      return response.data?.tables || [];
    } catch (error) {
      console.warn('Tables endpoint not implemented yet:', error);
      return [];
    }
  }

  // ===== GENERATION ENDPOINTS =====

  async generateBrainstorm(request: any): Promise<any> {
    try {
      const response = await this.request<ApiResponse<any>>('/api/v1/brainstorm', {
        method: 'POST',
        body: JSON.stringify(request),
      });
      return response.data;
    } catch (error) {
      console.warn('Brainstorm endpoint not implemented yet:', error);
      return { content: 'Mock brainstorm output', id: 'mock' };
    }
  }

  async generateWrite(request: any): Promise<any> {
    try {
      const response = await this.request<ApiResponse<any>>('/api/v1/write', {
        method: 'POST',
        body: JSON.stringify(request),
      });
      return response.data;
    } catch (error) {
      console.warn('Write endpoint not implemented yet:', error);
      return { content: 'Mock write output', id: 'mock', wordCount: 150 };
    }
  }

  async getGenerationOutputs(projectId: string, type?: string): Promise<any[]> {
    try {
      const params = type ? `?type=${type}` : '';
      const response = await this.request<ApiResponse<any[]>>(`/api/v1/projects/${projectId}/outputs${params}`);
      return response.data || [];
    } catch (error) {
      console.warn('Outputs endpoint not implemented yet:', error);
      return [];
    }
  }

  // ===== TONE PRESETS =====

  async getTonePresets(): Promise<any> {
    try {
      const response = await this.request<ApiResponse<any>>('/api/v1/tone-presets');
      return response.data;
    } catch (error) {
      console.warn('Tone presets endpoint not implemented yet:', error);
      return {
        tones: ['neutral', 'cheesy-romcom', 'romantic-dramedy', 'professional'],
        descriptions: {
          'neutral': 'Balanced, clear style',
          'cheesy-romcom': 'Lighthearted romantic comedy',
          'romantic-dramedy': 'Heartfelt romantic drama',
          'professional': 'Business-appropriate tone'
        }
      };
    }
  }

  // ===== SETTINGS ENDPOINTS =====

  async getUserSettings(): Promise<UserSettings> {
    try {
      const response = await this.request<ApiResponse<UserSettings>>('/api/v1/settings');
      return response.data;
    } catch (error) {
      console.warn('Settings endpoint not implemented yet:', error);
      return {
        apiUrl: this.baseURL,
        openaiApiKey: '',
        defaultModel: 'gpt-4o-mini',
        theme: 'light'
      };
    }
  }

  async updateUserSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    try {
      const response = await this.request<ApiResponse<UserSettings>>('/api/v1/settings', {
        method: 'PUT',
        body: JSON.stringify(settings),
      });
      return response.data;
    } catch (error) {
      console.warn('Update settings endpoint not implemented yet:', error);
      return settings as UserSettings;
    }
  }

  // ===== HEALTH CHECK =====

  async healthCheck(): Promise<{ status: string; version: string }> {
    try {
      return await this.request('/health');
    } catch (error) {
      console.warn('Health check failed:', error);
      return { status: 'unknown', version: '1.0.0' };
    }
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export the class for testing or custom instances
export default ApiService;

