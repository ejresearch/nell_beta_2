// =============================================================================
// TYPES FILE - FIXED TO EXPORT BUCKET AND ALL NEEDED TYPES
// =============================================================================

// USER & SETTINGS
export interface UserSettings {
  apiUrl: string;
  openaiApiKey: string;
  defaultModel: string;
  theme: 'light' | 'dark';
  autoSave?: boolean;
  notifications?: boolean;
}

// PROJECT
export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'archived' | 'draft';
  createdAt: Date;
  updatedAt: Date;
  dbPath: string;
  lightragPath: string;
  tables: string[];
  bucketCount: number;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  tables: Array<Record<string, string[]>>;
}

// BUCKET - THE MISSING EXPORT!
export interface Bucket {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'ingesting' | 'error';
  guidance?: string;
  description?: string;
  docCount: number;
  lastUpdated: Date;
  active: boolean;
}

export interface CreateBucketRequest {
  name: string;
  guidance?: string;
  description?: string;
}

// TABLE
export interface TableSchema {
  tableName: string;
  columns: string[];
  rowCount: number;
}

export interface TableRow {
  rowId?: number;
  data: Record<string, any>;
}

export interface ProjectTable {
  id: string;
  name: string;
  columns: string[];
  rowCount: number;
}

// PROMPTS
export interface PromptTemplate {
  id: string;
  name: string;
  content: string;
  projectId?: string;
  createdAt: Date;
}

export interface CreatePromptRequest {
  name: string;
  content: string;
  projectId?: string;
}

// OUTPUTS
export interface GenerationOutput {
  id: string;
  type: 'brainstorm' | 'write' | 'edit';
  content: string;
  projectId: string;
  createdAt: Date;
}

export interface BrainstormOutput {
  id: string;
  projectId: string;
  version: number;
  sourceTable: string;
  sourceRows: number[];
  bucketsUsed: string[];
  tone: string;
  easterEgg?: string;
  promptUsed: string;
  content: string;
  createdAt: Date;
}

export interface WriteOutput {
  id: string;
  projectId: string;
  version: number;
  brainstormVersion?: number;
  sourceTable: string;
  sourceRows: number[];
  tone: string;
  instructions?: string;
  content: string;
  wordCount: number;
  createdAt: Date;
}

// UPLOAD
export interface UploadProgress {
  file_id: string;
  filename: string;
  progress: number;
  status: 'uploading' | 'complete' | 'error';
}

export interface UploadFileRequest {
  bucketId: string;
  file: File;
}

// NOTIFICATIONS
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

// APP STATE
export interface AppState {
  isOnline: boolean;
  mirandaVisible: boolean;
  sidebarCollapsed: boolean;
  notifications: Notification[];
}

// API
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ApiErrorResponse {
  success: false;
  error: string;
  details?: Record<string, any>;
}

// TONE
export type TonePreset = 
  | 'neutral' 
  | 'cheesy-romcom' 
  | 'romantic-dramedy' 
  | 'shakespearean-romance' 
  | 'professional' 
  | 'academic' 
  | 'creative';

// REQUESTS
export interface BrainstormRequest {
  projectId: string;
  sourceTable: string;
  selectedRows: number[];
  selectedBuckets: string[];
  tone: TonePreset;
  easterEgg?: string;
  customPrompt?: string;
}

export interface WriteRequest {
  projectId: string;
  brainstormVersion?: number;
  sourceTable: string;
  selectedRows: number[];
  tone: TonePreset;
  customInstructions?: string;
}

// UTILITY
export type Status = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  data: T | null;
  status: Status;
  error: string | null;
}
