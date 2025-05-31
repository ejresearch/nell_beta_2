// src/services/api.ts

import {
  Project,
  CreateProjectRequest,
  Bucket,
  CreateBucketRequest,
  UploadFileRequest,
  PromptTemplate,
  CreatePromptRequest,
  ProjectTable,
  TableRow,
  BrainstormRequest,
  WriteRequest,
  GenerationOutput,
  UserSettings,
  ApiResponse,
  ApiError,
  UploadProgress,
} from '../types';

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

  // File upload with progress tracking
  private async uploadFile(
    endpoint: string,
    file: File,
    additionalData: Record<string, string> = {},
    onProgress?: (progress: UploadProgress) => void
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      
      formData.append('file', file);
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = Math.round((event.loaded / event.total) * 100);
          onProgress({
            file_id: `temp_${Date.now()}`,
            filename: file.name,
            progress,
            status: 'uploading',
          });
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch {
            resolve(xhr.responseText);
          }
        } else {
          reject(new ApiError({
            message: `Upload failed: ${xhr.statusText}`,
            code: xhr.status.toString(),
          }));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new ApiError({
          message: 'Upload failed: Network error',
          code: 'UPLOAD_ERROR',
        }));
      });

      xhr.open('POST', `${this.baseURL}${endpoint}`);
      xhr.send(formData);
    });
  }

  // ===== PROJECT ENDPOINTS =====
  
  async getProjects(): Promise<Project[]> {
    const response = await this.request<ApiResponse<Project[]>>('/projects');
    return response.data;
  }

  async getProject(id: string): Promise<Project> {
    const response = await this.request<ApiResponse<Project>>(`/projects/${id}`);
    return response.data;
  }

  async createProject(projectData: CreateProjectRequest): Promise<Project> {
    const response = await this.request<ApiResponse<Project>>('/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
    return response.data;
  }

  async updateProject(id: string, projectData: Partial<CreateProjectRequest>): Promise<Project> {
    const response = await this.request<ApiResponse<Project>>(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(projectData),
    });
    return response.data;
  }

  async deleteProject(id: string): Promise<void> {
    await this.request(`/projects/${id}`, { method: 'DELETE' });
  }

  // ===== BUCKET ENDPOINTS =====

  async getBuckets(projectId: string): Promise<Bucket[]> {
    const response = await this.request<ApiResponse<Bucket[]>>(`/projects/${projectId}/buckets`);
    return response.data;
  }

  async createBucket(projectId: string, bucketData: CreateBucketRequest): Promise<Bucket> {
    const response = await this.request<ApiResponse<Bucket>>(`/projects/${projectId}/buckets`, {
      method: 'POST',
      body: JSON.stringify(bucketData),
    });
    return response.data;
  }

  async toggleBucket(bucketId: string, active: boolean): Promise<Bucket> {
    const response = await this.request<ApiResponse<Bucket>>(`/buckets/${bucketId}/toggle`, {
      method: 'POST',
      body: JSON.stringify({ active }),
    });
    return response.data;
  }

  async uploadFileToBucket(
    bucketId: string,
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<any> {
    return this.uploadFile(`/buckets/${bucketId}/upload`, file, {}, onProgress);
  }

  async updateBucketGuidance(bucketId: string, guidance: string): Promise<Bucket> {
    const response = await this.request<ApiResponse<Bucket>>(`/buckets/${bucketId}/guidance`, {
      method: 'PUT',
      body: JSON.stringify({ guidance }),
    });
    return response.data;
  }

  // ===== PROMPT ENDPOINTS =====

  async getPrompts(projectId?: string): Promise<PromptTemplate[]> {
    const endpoint = projectId ? `/projects/${projectId}/prompts` : '/prompts';
    const response = await this.request<ApiResponse<PromptTemplate[]>>(endpoint);
    return response.data;
  }

  async createPrompt(promptData: CreatePromptRequest): Promise<PromptTemplate> {
    const response = await this.request<ApiResponse<PromptTemplate>>('/prompts', {
      method: 'POST',
      body: JSON.stringify(promptData),
    });
    return response.data;
  }

  async updatePrompt(id: string, promptData: Partial<CreatePromptRequest>): Promise<PromptTemplate> {
    const response = await this.request<ApiResponse<PromptTemplate>>(`/prompts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(promptData),
    });
    return response.data;
  }

  async deletePrompt(id: string): Promise<void> {
    await this.request(`/prompts/${id}`, { method: 'DELETE' });
  }

  // ===== TABLE ENDPOINTS =====

  async getProjectTables(projectId: string): Promise<ProjectTable[]> {
    const response = await this.request<ApiResponse<ProjectTable[]>>(`/projects/${projectId}/tables`);
    return response.data;
  }

  async getTableRows(tableId: string): Promise<TableRow[]> {
    const response = await this.request<ApiResponse<TableRow[]>>(`/tables/${tableId}/rows`);
    return response.data;
  }

  async createTableRow(tableId: string, data: Record<string, any>): Promise<TableRow> {
    const response = await this.request<ApiResponse<TableRow>>(`/tables/${tableId}/rows`, {
      method: 'POST',
      body: JSON.stringify({ data }),
    });
    return response.data;
  }

  async updateTableRow(rowId: string, data: Record<string, any>): Promise<TableRow> {
    const response = await this.request<ApiResponse<TableRow>>(`/table-rows/${rowId}`, {
      method: 'PUT',
      body: JSON.stringify({ data }),
    });
    return response.data;
  }

  async deleteTableRow(rowId: string): Promise<void> {
    await this.request(`/table-rows/${rowId}`, { method: 'DELETE' });
  }

  // ===== GENERATION ENDPOINTS =====

  async generateBrainstorm(request: BrainstormRequest): Promise<GenerationOutput> {
    const response = await this.request<ApiResponse<GenerationOutput>>('/generate/brainstorm', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.data;
  }

  async generateWrite(request: WriteRequest): Promise<GenerationOutput> {
    const response = await this.request<ApiResponse<GenerationOutput>>('/generate/write', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.data;
  }

  async getGenerationOutputs(projectId: string, type?: 'brainstorm' | 'write' | 'chat'): Promise<GenerationOutput[]> {
    const params = type ? `?type=${type}` : '';
    const response = await this.request<ApiResponse<GenerationOutput[]>>(`/projects/${projectId}/outputs${params}`);
    return response.data;
  }

  // ===== SETTINGS ENDPOINTS =====

  async getUserSettings(): Promise<UserSettings> {
    const response = await this.request<ApiResponse<UserSettings>>('/settings');
    return response.data;
  }

  async updateUserSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await this.request<ApiResponse<UserSettings>>('/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
    return response.data;
  }

  // ===== HEALTH CHECK =====

  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export the class for testing or custom instances
export default ApiService;
