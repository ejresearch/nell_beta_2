"""
Nell Beta 2 - API Endpoints
FastAPI routes for all Lizzy workflow modules
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
import json
import uuid
from datetime import datetime

# Import models from core (we'll need to create these imports)
from pydantic import BaseModel, Field
from enum import Enum

# =============================================================================
# SIMPLIFIED MODELS (inline for now)
# =============================================================================

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"

class ProjectCreate(BaseModel):
    """Request model for creating new project"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tables: List[dict] = Field(default=[], description="List of {table_name: [column_names]}")

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
# API ROUTER SETUP
# =============================================================================

# Create API router
api_router = APIRouter(prefix="/api/v1")

# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@api_router.post("/projects", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate):
    """
    Create new project with custom tables
    Port of your new_project.py functionality
    """
    try:
        # Generate project ID
        project_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # For now, return mock response until we connect the real project manager
        return ProjectResponse(
            id=project_id,
            name=project_data.name,
            description=project_data.description,
            status=ProjectStatus.ACTIVE,
            created_at=timestamp,
            updated_at=timestamp,
            db_path=f"./projects/{project_id}/{project_data.name.replace(' ', '_')}.db",
            lightrag_path=f"./projects/{project_id}/lightrag_working_dir",
            tables=[list(table.keys())[0] for table in project_data.tables],
            bucket_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/projects", response_model=ProjectList)
async def list_projects():
    """List all projects"""
    try:
        # Mock response for now
        return ProjectList(projects=[], total=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project by ID"""
    # Mock response for now
    return ProjectResponse(
        id=project_id,
        name="Mock Project",
        description="This is a mock project response",
        status=ProjectStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        db_path=f"./projects/{project_id}/mock.db",
        lightrag_path=f"./projects/{project_id}/lightrag_working_dir",
        tables=["characters", "scenes"],
        bucket_count=0
    )

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete project and all associated data"""
    return {"message": f"Project {project_id} deleted successfully"}

# =============================================================================
# TABLE ENDPOINTS
# =============================================================================

@api_router.get("/projects/{project_id}/tables")
async def list_project_tables(project_id: str):
    """List all tables in project"""
    return {
        "project_id": project_id,
        "tables": ["characters", "scenes", "plot_points"]
    }

@api_router.post("/projects/{project_id}/tables")
async def create_table(project_id: str, table_data: dict):
    """Create new table in project"""
    return {
        "message": "Table created successfully",
        "table_name": table_data.get("table_name"),
        "project_id": project_id
    }

# =============================================================================
# BUCKET ENDPOINTS (LightRAG Management)
# =============================================================================

@api_router.get("/projects/{project_id}/buckets")
async def list_buckets(project_id: str):
    """List all buckets in project"""
    return {
        "project_id": project_id,
        "buckets": []
    }

@api_router.post("/projects/{project_id}/buckets")
async def create_bucket(project_id: str, bucket_data: dict):
    """Create new LightRAG bucket"""
    bucket_id = str(uuid.uuid4())
    return {
        "id": bucket_id,
        "name": bucket_data.get("name"),
        "status": "active",
        "created_at": datetime.now(),
        "project_id": project_id
    }

@api_router.post("/projects/{project_id}/buckets/{bucket_name}/upload")
async def upload_files_to_bucket(
    project_id: str, 
    bucket_name: str,
    files: List[UploadFile] = File(...)
):
    """Upload files to bucket for ingestion"""
    return {
        "message": f"Uploaded {len(files)} files to bucket {bucket_name}",
        "project_id": project_id,
        "bucket_name": bucket_name
    }

# =============================================================================
# BRAINSTORM ENDPOINTS
# =============================================================================

@api_router.post("/projects/{project_id}/brainstorm")
async def generate_brainstorm(project_id: str, request_data: dict):
    """Generate brainstorm content"""
    return {
        "id": f"brainstorm_{uuid.uuid4()}",
        "project_id": project_id,
        "content": "Mock brainstorm content - this will be replaced with real LightRAG generation",
        "created_at": datetime.now()
    }

@api_router.get("/projects/{project_id}/brainstorm/history")
async def get_brainstorm_history(project_id: str):
    """Get brainstorm history for project"""
    return {
        "project_id": project_id,
        "total_sessions": 0,
        "recent_sessions": []
    }

# =============================================================================
# WRITE ENDPOINTS
# =============================================================================

@api_router.post("/projects/{project_id}/write")
async def generate_write(project_id: str, request_data: dict):
    """Generate written content"""
    return {
        "id": f"write_{uuid.uuid4()}",
        "project_id": project_id,
        "content": "Mock written content - this will be replaced with real content generation",
        "word_count": 150,
        "created_at": datetime.now()
    }

@api_router.get("/projects/{project_id}/write/history")
async def get_write_history(project_id: str):
    """Get write history for project"""
    return {
        "project_id": project_id,
        "total_drafts": 0,
        "recent_drafts": []
    }

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@api_router.get("/tone-presets")
async def get_tone_presets():
    """Get available tone presets for brainstorm and write"""
    return {
        "tones": [
            "neutral",
            "cheesy-romcom", 
            "romantic-dramedy",
            "shakespearean-romance",
            "professional",
            "academic",
            "creative"
        ],
        "descriptions": {
            "neutral": "Balanced, clear style",
            "cheesy-romcom": "Lighthearted romantic comedy",
            "romantic-dramedy": "Heartfelt romantic drama",
            "shakespearean-romance": "Elevated poetic style",
            "professional": "Business-appropriate tone",
            "academic": "Scholarly analytical style",
            "creative": "Innovative artistic flair"
        }
    }

@api_router.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "message": "Nell Beta 2 API is running",
        "version": "1.0.0",
        "endpoints": {
            "projects": "Project management",
            "tables": "Dynamic table operations", 
            "buckets": "LightRAG bucket management",
            "brainstorm": "Brainstorm generation",
            "write": "Content writing"
        }
    }
