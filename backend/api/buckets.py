"""
Buckets API - FastAPI endpoints for LightRAG bucket management
Exposes bucket functionality as REST API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import sys
import os

# Add the backend directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.lightrag_manager import (
    lightrag_manager,
    BucketInfo,
    BucketCreate,
    DocumentInfo,
    BucketQueryRequest
)

router = APIRouter(prefix="/projects/{project_id}/buckets", tags=["buckets"])

@router.post("/", response_model=BucketInfo)
async def create_bucket(project_id: str, bucket_data: BucketCreate):
    """
    Create a new LightRAG bucket for a project
    """
    try:
        bucket = await lightrag_manager.create_bucket(project_id, bucket_data)
        return bucket
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bucket: {str(e)}")

@router.get("/", response_model=List[BucketInfo])
async def list_buckets(project_id: str):
    """
    Get list of all buckets for a project
    """
    try:
        buckets = await lightrag_manager.list_buckets(project_id)
        return buckets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list buckets: {str(e)}")

@router.get("/{bucket_name}", response_model=BucketInfo)
async def get_bucket(project_id: str, bucket_name: str):
    """
    Get detailed information about a specific bucket
    """
    try:
        bucket = await lightrag_manager.get_bucket(project_id, bucket_name)
        if not bucket:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found")
        return bucket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bucket: {str(e)}")

@router.post("/{bucket_name}/upload", response_model=DocumentInfo)
async def upload_document(
    project_id: str,
    bucket_name: str,
    file: UploadFile = File(...),
    filename: Optional[str] = Form(None)
):
    """
    Upload a document to a bucket for ingestion
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('text/'):
            if not file.filename or not file.filename.endswith('.txt'):
                raise HTTPException(
                    status_code=400, 
                    detail="Only text files (.txt) are supported"
                )
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Use provided filename or original filename
        final_filename = filename or file.filename or "uploaded_document.txt"
        
        # Upload and ingest
        document_info = await lightrag_manager.upload_document(
            project_id, bucket_name, final_filename, content_str
        )
        
        return document_info
        
    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.post("/{bucket_name}/upload-text", response_model=DocumentInfo)
async def upload_text_content(
    project_id: str,
    bucket_name: str,
    filename: str = Form(...),
    content: str = Form(...)
):
    """
    Upload text content directly to a bucket
    """
    try:
        document_info = await lightrag_manager.upload_document(
            project_id, bucket_name, filename, content
        )
        return document_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload text: {str(e)}")

@router.post("/{bucket_name}/toggle")
async def toggle_bucket(project_id: str, bucket_name: str, active: bool = Form(...)):
    """
    Toggle a bucket's active status
    """
    try:
        bucket = await lightrag_manager.toggle_bucket(project_id, bucket_name, active)
        return {
            "message": f"Bucket '{bucket_name}' {'activated' if active else 'deactivated'}",
            "bucket": bucket
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle bucket: {str(e)}")

@router.post("/query")
async def query_buckets(project_id: str, query_request: BucketQueryRequest):
    """
    Query multiple buckets and get aggregated results
    Similar to brainstorm.py multi-bucket querying
    """
    try:
        results = await lightrag_manager.query_buckets(project_id, query_request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query buckets: {str(e)}")

@router.get("/{bucket_name}/status")
async def get_bucket_status(project_id: str, bucket_name: str):
    """
    Get comprehensive bucket status
    """
    try:
        bucket = await lightrag_manager.get_bucket(project_id, bucket_name)
        if not bucket:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found")
        
        return {
            "bucket": bucket,
            "status": "active" if bucket.active else "inactive",
            "ready_for_queries": bucket.document_count > 0,
            "paths": {
                "working_dir": bucket.working_dir,
                "documents_dir": f"{bucket.working_dir}/documents"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bucket status: {str(e)}")
