// src/types/index.ts

// Base API Response
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

// Project Types
export interface Project {
  id: string;
  name: string;
  description: string;
  type: 'creative_writing' | 'business_docs' | 'research' | 'custom';
  created_at: string;
  updated_at: string;
  metadata: ProjectMetadata;
}

export interface ProjectMetadata {
  author?: string;
  genre?: string;
  target_length?: number;
  custom_fields?: Record<string, any>;
}

export interface CreateProjectRequest {
  name: string;
  description: string;
  type: Project['type'];
  metadata?: Partial<ProjectMetadata>;
}

// Bucket Types
export interface Bucket {
  id: string;
  name: string;
  active: boolean;
  doc_count: number;
  ingestion_status: 'idle' | 'processing' | 'complete' | 'error';
  guidance?: string;
  created_at: string;
  updated_at: string;
}

export interface BucketFile {
  id: string;
  bucket_id: string;
  filename: string;
  file_size: number;
  upload_status: 'uploading' | 'complete' | 'error';
  uploaded_at: string;
}

export interface CreateBucketRequest {
  name: string;
  guidance?: string;
}

export interface UploadFileRequest {
  bucket_id: string;
  file: File;
}

// Prompt Types
export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  tone: string;
  style: string;
  task_goal: string;
  easter_egg?: string;
  is_global: boolean;
  project_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreatePromptRequest {
  name: string;
  description: string;
  tone: string;
  style: string;
  task_goal: string;
  easter_egg?: string;
  is_global?: boolean;
  project_id?: string;
}

// Table Types
export interface ProjectTable {
  id: string;
  project_id: string;
  name: string;
  columns: TableColumn[];
  row_count: number;
  created_at: string;
  updated_at: string;
}

export interface TableColumn {
  name: string;
  type: 'text' | 'number' | 'date' | 'boolean';
  required: boolean;
}

export interface TableRow {
  id: string;
  table_id: string;
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Generation Types
export interface BrainstormRequest {
  project_id: string;
  source_table_id: string;
  source_row_id?: string;
  active_buckets: string[];
  prompt_template_id: string;
  easter_egg?: string;
}

export interface WriteRequest {
  project_id: string;
  brainstorm_id?: string;
  source_table_id: string;
  source_row_id?: string;
  prompt_template_id: string;
  custom_context?: string;
}

export interface GenerationOutput {
  id: string;
  project_id: string;
  type: 'brainstorm' | 'write' | 'chat';
  content: string;
  metadata: GenerationMetadata;
  version: number;
  created_at: string;
}

export interface GenerationMetadata {
  prompt_used: string;
  buckets_used: string[];
  source_context: Record<string, any>;
  model_used: string;
  generation_time_ms: number;
}

// User Settings Types
export interface UserSettings {
  openai_api_key?: string;
  default_model: string;
  theme: 'light' | 'dark';
  auto_save: boolean;
  default_prompt_id?: string;
}

// API Error Types
export interface ApiError {
  message: string;
  code: string;
  details?: any;
}

// Upload Progress Types
export interface UploadProgress {
  file_id: string;
  filename: string;
  progress: number; // 0-100
  status: 'uploading' | 'processing' | 'complete' | 'error';
  error_message?: string;
}
