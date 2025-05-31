"""
Nell Beta 2 - LightRAG Integration Client
Direct port of your LightRAG patterns from ingest.py and bucket handling
"""

import os
import asyncio
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import json
import shutil

from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete, gpt_4o_complete

from .models import (
    BucketCreate, BucketResponse, BucketUpdate, BucketStatus,
    FileUpload, IngestionStatus, LightRAGConfig
)

# =============================================================================
# LIGHTRAG CLIENT CLASS
# =============================================================================

class LightRAGClient:
    """
    Manages LightRAG buckets and document ingestion
    Based on your ingest.py and multi-bucket patterns
    """
    
    def __init__(self, project_id: str, lightrag_base_dir: str = "./projects"):
        self.project_id = project_id
        self.base_dir = Path(lightrag_base_dir) / project_id / "lightrag_working_dir"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Track bucket instances (like your lightrag_instances dict)
        self.bucket_instances: Dict[str, LightRAG] = {}
        self.bucket_metadata: Dict[str, Dict] = {}
        
        # Load existing buckets
        self._load_existing_buckets()
    
    def _load_existing_buckets(self):
        """Load existing bucket configurations"""
        metadata_file = self.base_dir / "buckets_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.bucket_metadata = json.load(f)
        
        # Initialize LightRAG instances for existing buckets
        for bucket_name in self.bucket_metadata.keys():
            bucket_dir = self.base_dir / bucket_name
            if bucket_dir.exists():
                try:
                    self.bucket_instances[bucket_name] = LightRAG(
                        working_dir=str(bucket_dir),
                        llm_model_func=gpt_4o_mini_complete
                    )
                except Exception as e:
                    print(f"Warning: Could not load bucket {bucket_name}: {e}")
    
    def _save_metadata(self):
        """Save bucket metadata to disk"""
        metadata_file = self.base_dir / "buckets_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.bucket_metadata, f, indent=2, default=str)
    
    async def create_bucket(self, bucket_data: BucketCreate) -> BucketResponse:
        """
        Create new LightRAG bucket
        Based on your bucket initialization patterns
        """
        bucket_id = str(uuid.uuid4())
        bucket_name = bucket_data.name.lower().replace(' ', '_')
        bucket_dir = self.base_dir / bucket_name
        
        try:
            # Create bucket directory
            bucket_dir.mkdir(exist_ok=True)
            
            # Initialize LightRAG instance
            lightrag_instance = LightRAG(
                working_dir=str(bucket_dir),
                llm_model_func=gpt_4o_mini_complete
            )
            
            # Store instance and metadata
            self.bucket_instances[bucket_name] = lightrag_instance
            self.bucket_metadata[bucket_name] = {
                "id": bucket_id,
                "name": bucket_data.name,
                "guidance": bucket_data.guidance,
                "description": bucket_data.description,
                "status": BucketStatus.ACTIVE,
                "created_at": datetime.now().isoformat(),
                "doc_count": 0,
                "active": True
            }
            
            self._save_metadata()
            
            return BucketResponse(
                id=bucket_id,
                name=bucket_data.name,
                status=BucketStatus.ACTIVE,
                guidance=bucket_data.guidance,
                description=bucket_data.description,
                doc_count=0,
                last_updated=datetime.now(),
                active=True
            )
            
        except Exception as e:
            # Cleanup on failure
            if bucket_dir.exists():
                shutil.rmtree(bucket_dir)
            raise Exception(f"Failed to create bucket: {str(e)}")
    
    async def list_buckets(self) -> List[BucketResponse]:
        """List all buckets in the project"""
        buckets = []
        
        for bucket_name, metadata in self.bucket_metadata.items():
            doc_count = await self._get_document_count(bucket_name)
            
            buckets.append(BucketResponse(
                id=metadata["id"],
                name=metadata["name"],
                status=BucketStatus(metadata.get("status", "active")),
                guidance=metadata.get("guidance"),
                description=metadata.get("description"),
                doc_count=doc_count,
                last_updated=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                active=metadata.get("active", True)
            ))
        
        return buckets
    
    async def update_bucket(self, bucket_name: str, update_data: BucketUpdate) -> Optional[BucketResponse]:
        """Update bucket configuration"""
        if bucket_name not in self.bucket_metadata:
            return None
        
        metadata = self.bucket_metadata[bucket_name]
        
        if update_data.guidance is not None:
            metadata["guidance"] = update_data.guidance
        
        if update_data.active is not None:
            metadata["active"] = update_data.active
            metadata["status"] = BucketStatus.ACTIVE if update_data.active else BucketStatus.INACTIVE
        
        self._save_metadata()
        
        doc_count = await self._get_document_count(bucket_name)
        
        return BucketResponse(
            id=metadata["id"],
            name=metadata["name"],
            status=BucketStatus(metadata["status"]),
            guidance=metadata.get("guidance"),
            description=metadata.get("description"),
            doc_count=doc_count,
            last_updated=datetime.now(),
            active=metadata["active"]
        )
    
    async def delete_bucket(self, bucket_name: str) -> bool:
        """Delete bucket and all its data"""
        if bucket_name not in self.bucket_metadata:
            return False
        
        try:
            # Remove from instances
            if bucket_name in self.bucket_instances:
                del self.bucket_instances[bucket_name]
            
            # Remove directory
            bucket_dir = self.base_dir / bucket_name
            if bucket_dir.exists():
                shutil.rmtree(bucket_dir)
            
            # Remove from metadata
            del self.bucket_metadata[bucket_name]
            self._save_metadata()
            
            return True
        except Exception:
            return False
    
    async def ingest_document(self, bucket_name: str, content: str, filename: str) -> IngestionStatus:
        """
        Ingest document into bucket
        Based on your file ingestion patterns
        """
        if bucket_name not in self.bucket_instances:
            return IngestionStatus(
                filename=filename,
                status="error",
                progress=0,
                message="Bucket not found"
            )
        
        try:
            # Update bucket status to ingesting
            self.bucket_metadata[bucket_name]["status"] = BucketStatus.INGESTING
            self._save_metadata()
            
            # Ingest document (this is async in LightRAG)
            lightrag_instance = self.bucket_instances[bucket_name]
            await asyncio.to_thread(lightrag_instance.insert, content)
            
            # Update document count
            self.bucket_metadata[bucket_name]["doc_count"] = await self._get_document_count(bucket_name)
            self.bucket_metadata[bucket_name]["status"] = BucketStatus.ACTIVE
            self._save_metadata()
            
            return IngestionStatus(
                filename=filename,
                status="complete",
                progress=100,
                message="Document ingested successfully"
            )
            
        except Exception as e:
            self.bucket_metadata[bucket_name]["status"] = BucketStatus.ERROR
            self._save_metadata()
            
            return IngestionStatus(
                filename=filename,
                status="error",
                progress=0,
                message=f"Ingestion failed: {str(e)}"
            )
    
    async def query_buckets(
        self, 
        selected_buckets: List[str], 
        query: str, 
        mode: str = "mix"
    ) -> Dict[str, str]:
        """
        Query multiple buckets and return results
        Direct port of your multi-bucket querying logic
        """
        results = {}
        
        # Filter to active buckets only (like your selected_buckets pattern)
        active_buckets = [
            bucket for bucket in selected_buckets 
            if (bucket in self.bucket_instances and 
                self.bucket_metadata.get(bucket, {}).get("active", True))
        ]
        
        for bucket_name in active_buckets:
            try:
                lightrag_instance = self.bucket_instances[bucket_name]
                
                # Query with specified mode (like your QueryParam usage)
                result = await asyncio.to_thread(
                    lightrag_instance.query,
                    query,
                    param=QueryParam(mode=mode)
                )
                
                results[bucket_name] = result
                
            except Exception as e:
                results[bucket_name] = f"Error querying bucket: {str(e)}"
        
        return results
    
    async def get_bucket_guidance(self, bucket_name: str) -> Optional[str]:
        """Get bucket-specific guidance text"""
        if bucket_name not in self.bucket_metadata:
            return None
        return self.bucket_metadata[bucket_name].get("guidance")
    
    async def _get_document_count(self, bucket_name: str) -> int:
        """Estimate document count in bucket"""
        bucket_dir = self.base_dir / bucket_name
        if not bucket_dir.exists():
            return 0
        
        # Count files in the bucket directory (rough estimate)
        try:
            file_count = len([f for f in bucket_dir.iterdir() if f.is_file()])
            return max(0, file_count - 2)  # Subtract system files
        except Exception:
            return 0

# =============================================================================
# BUCKET MANAGER CLASS
# =============================================================================

class BucketManager:
    """
    High-level bucket management operations
    Combines project management with LightRAG operations
    """
    
    def __init__(self):
        self.clients: Dict[str, LightRAGClient] = {}
    
    def get_client(self, project_id: str) -> LightRAGClient:
        """Get or create LightRAG client for project"""
        if project_id not in self.clients:
            self.clients[project_id] = LightRAGClient(project_id)
        return self.clients[project_id]
    
    async def upload_files(
        self, 
        project_id: str, 
        bucket_name: str, 
        files: List[tuple]  # (filename, content) pairs
    ) -> List[IngestionStatus]:
        """
        Upload multiple files to bucket
        Based on your batch file processing patterns
        """
        client = self.get_client(project_id)
        results = []
        
        for filename, content in files:
            # Filter for .txt files (like your original pattern)
            if not filename.lower().endswith('.txt'):
                results.append(IngestionStatus(
                    filename=filename,
                    status="error",
                    progress=0,
                    message="Only .txt files are supported"
                ))
                continue
            
            result = await client.ingest_document(bucket_name, content, filename)
            results.append(result)
        
        return results
    
    async def get_active_buckets(self, project_id: str) -> List[str]:
        """Get list of active bucket names for querying"""
        client = self.get_client(project_id)
        buckets = await client.list_buckets()
        return [bucket.name for bucket in buckets if bucket.active]
    
    async def query_with_context(
        self,
        project_id: str,
        buckets: List[str],
        base_query: str,
        context_data: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Query buckets with additional context
        Used by brainstorm and write modules
        """
        client = self.get_client(project_id)
        
        # Enhance query with context (like your prompt building)
        enhanced_query = base_query
        if context_data:
            context_str = "\n".join([f"{k}: {v}" for k, v in context_data.items()])
            enhanced_query = f"{context_str}\n\n{base_query}"
        
        return await client.query_buckets(buckets, enhanced_query)

# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# Global bucket manager for dependency injection
bucket_manager = BucketManager()
