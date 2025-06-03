"""
Nell Beta 2 - Database Models & Schemas
Based on Lizzy implementation patterns
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"

class BucketStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    INGESTING = "ingesting"
    ERROR = "error"

class OutputType(str, Enum):
    BRAINSTORM = "brainstorm"
    WRITE = "write"
    EDIT = "edit"

# =============================================================================
# PROJECT MODELS
# =============================================================================

class ProjectCreate(BaseModel):
    """Request model for creating new project"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tables: List[Dict[str, List[str]]] = Field(
        default=[], 
        description="List of {table_name: [column_names]} for custom tables"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Romantic Comedy Script",
                "description": "A lighthearted romance set in modern NYC",
                "tables": [
                    {"characters": ["name", "age", "background", "motivation"]},
                    {"scenes": ["scene_number", "location", "description", "emotional_arc"]}
                ]
            }
        }

class ProjectResponse(BaseModel):
    """Response model for project data"""
    id: str
    name: str
    description: Optional[str]
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    db_path: str
    lightrag_path: str
    tables: List[str] = Field(default=[])
    bucket_count: int = Field(default=0)
    
class ProjectList(BaseModel):
    """Response model for listing projects"""
    projects: List[ProjectResponse]
    total: int

# =============================================================================
# TABLE MODELS (Dynamic Schema Support)
# =============================================================================

class TableCreate(BaseModel):
    """Request model for creating custom tables"""
    table_name: str = Field(..., pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$')
    columns: List[str] = Field(..., min_items=1)
    
class TableRow(BaseModel):
    """Generic row data for any table"""
    row_id: Optional[int] = None
    data: Dict[str, Any] = Field(..., description="Column name -> value mapping")
    
class TableSchema(BaseModel):
    """Table structure information"""
    table_name: str
    columns: List[str]
    row_count: int
    
class TableData(BaseModel):
    """Complete table data response"""
    table_schema: TableSchema = Field(..., alias="schema")
    rows: List[TableRow]
    
    class Config:
        allow_population_by_field_name = True

# =============================================================================
# LIGHTRAG BUCKET MODELS
# =============================================================================

class BucketCreate(BaseModel):
    """Request model for creating LightRAG bucket"""
    name: str = Field(..., min_length=1, max_length=50)
    guidance: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = Field(None, max_length=200)

class BucketResponse(BaseModel):
    """Response model for bucket data"""
    id: str
    name: str
    status: BucketStatus
    guidance: Optional[str]
    description: Optional[str]
    doc_count: int = Field(default=0)
    last_updated: datetime
    active: bool = Field(default=True)
    
class BucketUpdate(BaseModel):
    """Request model for updating bucket"""
    guidance: Optional[str] = Field(None, max_length=1000)
    active: Optional[bool] = None

class FileUpload(BaseModel):
    """File upload metadata"""
    filename: str
    content_type: str
    size: int
    
class IngestionStatus(BaseModel):
    """File ingestion status"""
    filename: str
    status: str  # "pending", "processing", "complete", "error"
    progress: float = Field(ge=0, le=100)
    message: Optional[str] = None

# =============================================================================
# BRAINSTORM MODELS
# =============================================================================

class BrainstormRequest(BaseModel):
    """Request model for brainstorm generation"""
    project_id: str
    source_table: str
    selected_rows: List[int] = Field(..., min_items=1)
    selected_buckets: List[str] = Field(..., min_items=1)
    tone: Optional[str] = Field("neutral", max_length=50)
    easter_egg: Optional[str] = Field(None, max_length=200)
    custom_prompt: Optional[str] = Field(None, max_length=1000)

class BrainstormResponse(BaseModel):
    """Response model for brainstorm output"""
    id: str
    project_id: str
    version: int
    source_table: str
    source_rows: List[int]
    buckets_used: List[str]
    tone: str
    easter_egg: Optional[str]
    prompt_used: str
    content: str
    created_at: datetime
    
class BrainstormSummary(BaseModel):
    """Summary of brainstorm sessions"""
    project_id: str
    latest_version: int
    total_sessions: int
    recent_sessions: List[BrainstormResponse]

# =============================================================================
# WRITE MODELS
# =============================================================================

class WriteRequest(BaseModel):
    """Request model for write generation"""
    project_id: str
    brainstorm_version: Optional[int] = Field(None, description="Use latest if not specified")
    source_table: str
    selected_rows: List[int] = Field(..., min_items=1)
    tone: Optional[str] = Field("neutral", max_length=50)
    custom_instructions: Optional[str] = Field(None, max_length=500)

class WriteResponse(BaseModel):
    """Response model for write output"""
    id: str
    project_id: str
    version: int
    brainstorm_version: Optional[int]
    source_table: str
    source_rows: List[int]
    tone: str
    instructions: Optional[str]
    content: str
    word_count: int
    created_at: datetime

class WriteEdit(BaseModel):
    """Request model for editing written content"""
    write_id: str
    edit_instructions: str = Field(..., max_length=500)
    
class WriteSummary(BaseModel):
    """Summary of write outputs"""
    project_id: str
    latest_version: int
    total_drafts: int
    recent_drafts: List[WriteResponse]

# =============================================================================
# OUTPUT TRACKING MODELS
# =============================================================================

class OutputEntry(BaseModel):
    """Generic output tracking entry"""
    id: str
    project_id: str
    output_type: OutputType
    version: int
    table_used: str
    rows_used: List[int]
    buckets_used: List[str]
    metadata: Dict[str, Any] = Field(default={})
    content: str
    created_at: datetime

class OutputHistory(BaseModel):
    """Complete output history for a project"""
    project_id: str
    entries: List[OutputEntry]
    total_brainstorms: int
    total_writes: int
    total_edits: int

# =============================================================================
# API RESPONSE MODELS
# =============================================================================

class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

# =============================================================================
# CONFIGURATION MODELS
# =============================================================================

class ProjectConfig(BaseModel):
    """Project-specific configuration"""
    default_tone: str = "neutral"
    default_buckets: List[str] = Field(default=[])
    auto_backup: bool = True
    max_versions: int = 10
    
class LightRAGConfig(BaseModel):
    """LightRAG configuration settings"""
    working_dir: str = "./lightrag_working_dir"
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    max_tokens: int = 4000
