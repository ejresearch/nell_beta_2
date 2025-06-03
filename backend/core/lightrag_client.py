"""
LightRAG Manager - Bucket management for Nell Beta 2
Updated to use official LightRAG OpenAI integration patterns
"""

import os
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import aiofiles
import numpy as np

# Import LightRAG with proper error handling
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import openai_complete_if_cache, openai_embed
    from lightrag.utils import EmbeddingFunc
    LIGHTRAG_AVAILABLE = True
except ImportError as e:
    print(f"LightRAG import error: {e}")
    LIGHTRAG_AVAILABLE = False

# Pydantic Models
class BucketInfo(BaseModel):
    name: str
    project_id: str
    active: bool
    document_count: int
    working_dir: str
    guidance: Optional[str] = ""
    last_updated: Optional[str] = None

class BucketCreate(BaseModel):
    name: str
    guidance: Optional[str] = ""
    active: bool = True

class DocumentInfo(BaseModel):
    filename: str
    size: int
    uploaded_at: str
    status: str  # "pending", "ingested", "error", "saved_only"

class BucketQueryRequest(BaseModel):
    query: str
    active_buckets_only: bool = True
    mode: str = "mix"  # "local", "global", "mix"

class LightRAGManager:
    """
    Manages LightRAG buckets for projects
    Uses official LightRAG OpenAI integration patterns
    """
    
    def __init__(self, projects_base_dir: str = "./projects"):
        self.projects_base_dir = Path(projects_base_dir)
        self._lightrag_instances: Dict[str, Any] = {}
        
        # Check for OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("❌ Warning: OPENAI_API_KEY not found in environment variables")
            print("Set it with: export OPENAI_API_KEY='your-key-here'")
        else:
            print(f"✅ OpenAI API key found (length: {len(self.api_key)})")
        
        if not LIGHTRAG_AVAILABLE:
            print("❌ Warning: LightRAG not available")
        else:
            print("✅ LightRAG available with official OpenAI integration")
        
    def _get_project_lightrag_dir(self, project_id: str) -> Path:
        """Get the base LightRAG directory for a project"""
        return self.projects_base_dir / project_id / "lightrag_data"
    
    def _get_bucket_dir(self, project_id: str, bucket_name: str) -> Path:
        """Get the working directory for a specific bucket"""
        return self._get_project_lightrag_dir(project_id) / bucket_name
    
    def _get_bucket_key(self, project_id: str, bucket_name: str) -> str:
        """Get unique key for bucket instance"""
        return f"{project_id}_{bucket_name}"
    
    async def _create_official_llm_func(self):
        """Create LLM function using official LightRAG OpenAI integration"""
        async def llm_model_func(
            prompt, system_prompt=None, history_messages=[], **kwargs
        ) -> str:
            return await openai_complete_if_cache(
                model="gpt-4o-mini",
                prompt=prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=self.api_key,
                base_url="https://api.openai.com/v1",
                **kwargs
            )
        return llm_model_func
    
    async def _create_official_embedding_func(self):
        """Create embedding function using official LightRAG OpenAI integration"""
        async def embedding_func(texts: list[str]) -> np.ndarray:
            return await openai_embed(
                texts=texts,
                model="text-embedding-3-small",
                api_key=self.api_key,
                base_url="https://api.openai.com/v1",
            )
        return embedding_func
    
    async def _get_embedding_dimension(self):
        """Get the embedding dimension for the model"""
        try:
            embedding_func = await self._create_official_embedding_func()
            test_text = ["This is a test sentence."]
            embedding = await embedding_func(test_text)
            embedding_dim = embedding.shape[1]
            print(f"🔍 Detected embedding dimension: {embedding_dim}")
            return embedding_dim
        except Exception as e:
            print(f"⚠️ Could not detect embedding dimension, using default 1536: {e}")
            return 1536  # Default for text-embedding-3-small
    
    async def _create_lightrag_instance(self, working_dir: str):
        """Create LightRAG instance using official patterns"""
        if not LIGHTRAG_AVAILABLE:
            raise Exception("LightRAG is not available")
        
        if not self.api_key:
            raise Exception("OpenAI API key is required")
        
        try:
            # Ensure working directory exists
            Path(working_dir).mkdir(parents=True, exist_ok=True)
            
            # Create official LightRAG functions
            llm_model_func = await self._create_official_llm_func()
            embedding_func = await self._create_official_embedding_func()
            embedding_dim = await self._get_embedding_dimension()
            
            # Create LightRAG instance with official pattern
            instance = LightRAG(
                working_dir=working_dir,
                llm_model_func=llm_model_func,
                embedding_func=EmbeddingFunc(
                    embedding_dim=embedding_dim,
                    max_token_size=8192,
                    func=embedding_func,
                ),
            )
            
            print(f"✅ LightRAG initialized with official OpenAI integration in {working_dir}")
            return instance
            
        except Exception as e:
            print(f"❌ LightRAG initialization failed: {str(e)}")
            raise Exception(f"Failed to create LightRAG instance: {str(e)}")
    
    async def create_bucket(self, project_id: str, bucket_data: BucketCreate) -> BucketInfo:
        """Create a new LightRAG bucket for a project"""
        bucket_dir = self._get_bucket_dir(project_id, bucket_data.name)
        bucket_key = self._get_bucket_key(project_id, bucket_data.name)
        
        try:
            # Create directory structure
            bucket_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created bucket directory: {bucket_dir}")
            
            # Try to create LightRAG instance
            lightrag_status = "unknown"
            try:
                lightrag_instance = await self._create_lightrag_instance(str(bucket_dir))
                self._lightrag_instances[bucket_key] = lightrag_instance
                lightrag_status = "initialized"
                print(f"✅ LightRAG instance created for bucket: {bucket_data.name}")
            except Exception as e:
                print(f"⚠️ LightRAG initialization failed for bucket {bucket_data.name}: {e}")
                lightrag_status = f"failed: {str(e)}"
            
            # Create bucket metadata
            metadata = {
                "name": bucket_data.name,
                "project_id": project_id,
                "active": bucket_data.active,
                "guidance": bucket_data.guidance,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "document_count": 0,
                "lightrag_status": lightrag_status
            }
            
            metadata_file = bucket_dir / "bucket_metadata.json"
            async with aiofiles.open(metadata_file, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
            
            print(f"✅ Bucket '{bucket_data.name}' created successfully")
            
            return BucketInfo(
                name=bucket_data.name,
                project_id=project_id,
                active=bucket_data.active,
                document_count=0,
                working_dir=str(bucket_dir),
                guidance=bucket_data.guidance,
                last_updated=metadata["last_updated"]
            )
            
        except Exception as e:
            print(f"❌ Failed to create bucket {bucket_data.name}: {str(e)}")
            raise Exception(f"Failed to create bucket: {str(e)}")
    
    async def get_bucket(self, project_id: str, bucket_name: str) -> Optional[BucketInfo]:
        """Get information about a specific bucket"""
        bucket_dir = self._get_bucket_dir(project_id, bucket_name)
        metadata_file = bucket_dir / "bucket_metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            async with aiofiles.open(metadata_file, 'r') as f:
                content = await f.read()
                metadata = json.loads(content)
            
            # Count documents
            doc_count = await self._count_documents(bucket_dir)
            
            return BucketInfo(
                name=metadata["name"],
                project_id=metadata["project_id"],
                active=metadata.get("active", True),
                document_count=doc_count,
                working_dir=str(bucket_dir),
                guidance=metadata.get("guidance", ""),
                last_updated=metadata.get("last_updated")
            )
            
        except Exception as e:
            print(f"❌ Error reading bucket {bucket_name}: {e}")
            return None
    
    async def list_buckets(self, project_id: str) -> List[BucketInfo]:
        """List all buckets for a project"""
        lightrag_dir = self._get_project_lightrag_dir(project_id)
        
        if not lightrag_dir.exists():
            return []
        
        buckets = []
        try:
            for item in lightrag_dir.iterdir():
                if item.is_dir() and (item / "bucket_metadata.json").exists():
                    bucket = await self.get_bucket(project_id, item.name)
                    if bucket:
                        buckets.append(bucket)
        except Exception as e:
            print(f"❌ Error listing buckets: {e}")
            
        return buckets
    
    async def upload_document(self, project_id: str, bucket_name: str, 
                            filename: str, content: str) -> DocumentInfo:
        """Upload and ingest a document into a bucket"""
        bucket_dir = self._get_bucket_dir(project_id, bucket_name)
        
        if not bucket_dir.exists():
            raise ValueError(f"Bucket '{bucket_name}' not found")
        
        timestamp = datetime.now().isoformat()
        
        try:
            # Save the document file
            docs_dir = bucket_dir / "documents"
            docs_dir.mkdir(exist_ok=True)
            
            file_path = docs_dir / filename
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            print(f"📄 Document saved: {filename}")
            
            # Try to ingest into LightRAG
            bucket_key = self._get_bucket_key(project_id, bucket_name)
            
            try:
                # Get or create LightRAG instance
                if bucket_key not in self._lightrag_instances:
                    print(f"🔄 Creating new LightRAG instance for bucket: {bucket_name}")
                    self._lightrag_instances[bucket_key] = await self._create_lightrag_instance(str(bucket_dir))
                
                lightrag_instance = self._lightrag_instances[bucket_key]
                
                # Ingest content into LightRAG
                print(f"🔄 Ingesting document into LightRAG...")
                await asyncio.get_event_loop().run_in_executor(
                    None, lightrag_instance.insert, content
                )
                
                print(f"✅ Document ingested successfully: {filename}")
                status = "ingested"
                
            except Exception as e:
                print(f"⚠️ LightRAG ingestion failed for {filename}: {e}")
                status = "saved_only"
            
            # Update bucket metadata
            await self._update_bucket_metadata(project_id, bucket_name)
            
            return DocumentInfo(
                filename=filename,
                size=len(content.encode('utf-8')),
                uploaded_at=timestamp,
                status=status
            )
            
        except Exception as e:
            print(f"❌ Error uploading document {filename}: {e}")
            return DocumentInfo(
                filename=filename,
                size=len(content.encode('utf-8')) if content else 0,
                uploaded_at=timestamp,
                status="error"
            )
    
    async def query_buckets(self, project_id: str, query_request: BucketQueryRequest) -> Dict[str, Any]:
        """Query multiple buckets and aggregate results"""
        buckets = await self.list_buckets(project_id)
        
        if query_request.active_buckets_only:
            active_buckets = [b for b in buckets if b.active]
        else:
            active_buckets = buckets
        
        print(f"🔍 Querying {len(active_buckets)} active buckets for: '{query_request.query}'")
        
        if not active_buckets:
            return {
                "query": query_request.query,
                "buckets_queried": [],
                "results": {},
                "combined_result": "No active buckets found for this project."
            }
        
        results = {}
        
        for bucket in active_buckets:
            bucket_key = self._get_bucket_key(project_id, bucket.name)
            print(f"🔄 Querying bucket: {bucket.name}")
            
            try:
                # Initialize LightRAG if needed
                if bucket_key not in self._lightrag_instances:
                    print(f"🔄 Creating LightRAG instance for query in bucket: {bucket.name}")
                    self._lightrag_instances[bucket_key] = await self._create_lightrag_instance(bucket.working_dir)
                
                lightrag_instance = self._lightrag_instances[bucket_key]
                
                # Construct query with guidance
                enhanced_query = query_request.query
                if bucket.guidance:
                    enhanced_query = f"{bucket.guidance}\n\n{query_request.query}"
                    print(f"📝 Enhanced query with guidance: {enhanced_query[:100]}...")
                
                # Query LightRAG
                result = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: lightrag_instance.query(
                        enhanced_query, 
                        param=QueryParam(mode=query_request.mode)
                    )
                )
                
                print(f"✅ Query successful for bucket: {bucket.name}")
                results[bucket.name] = {
                    "content": result,
                    "guidance": bucket.guidance,
                    "status": "success"
                }
                
            except Exception as e:
                print(f"❌ Error querying bucket {bucket.name}: {e}")
                results[bucket.name] = {
                    "content": f"Error querying bucket: {str(e)}",
                    "guidance": bucket.guidance,
                    "status": "error"
                }
        
        # Combine successful results
        combined_results = []
        for bucket_name, result in results.items():
            if result["status"] == "success":
                combined_results.append(f"From {bucket_name}:\n{result['content']}")
        
        combined_result = "\n\n---\n\n".join(combined_results) if combined_results else "No successful results from any bucket."
        
        return {
            "query": query_request.query,
            "buckets_queried": [b.name for b in active_buckets],
            "results": results,
            "combined_result": combined_result
        }
    
    async def toggle_bucket(self, project_id: str, bucket_name: str, active: bool) -> BucketInfo:
        """Toggle a bucket's active status"""
        bucket_dir = self._get_bucket_dir(project_id, bucket_name)
        metadata_file = bucket_dir / "bucket_metadata.json"
        
        if not metadata_file.exists():
            raise ValueError(f"Bucket '{bucket_name}' not found")
        
        try:
            async with aiofiles.open(metadata_file, 'r') as f:
                content = await f.read()
                metadata = json.loads(content)
            
            metadata["active"] = active
            metadata["last_updated"] = datetime.now().isoformat()
            
            async with aiofiles.open(metadata_file, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
            
            print(f"✅ Bucket '{bucket_name}' {'activated' if active else 'deactivated'}")
            return await self.get_bucket(project_id, bucket_name)
            
        except Exception as e:
            raise Exception(f"Failed to toggle bucket: {str(e)}")
    
    async def _count_documents(self, bucket_dir: Path) -> int:
        """Count documents in a bucket"""
        docs_dir = bucket_dir / "documents"
        if not docs_dir.exists():
            return 0
        
        count = 0
        try:
            for file_path in docs_dir.iterdir():
                if file_path.is_file():
                    count += 1
        except Exception:
            pass
            
        return count
    
    async def _update_bucket_metadata(self, project_id: str, bucket_name: str):
        """Update bucket metadata after document changes"""
        bucket_dir = self._get_bucket_dir(project_id, bucket_name)
        metadata_file = bucket_dir / "bucket_metadata.json"
        
        if metadata_file.exists():
            try:
                async with aiofiles.open(metadata_file, 'r') as f:
                    content = await f.read()
                    metadata = json.loads(content)
                
                metadata["document_count"] = await self._count_documents(bucket_dir)
                metadata["last_updated"] = datetime.now().isoformat()
                
                async with aiofiles.open(metadata_file, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2))
                    
            except Exception as e:
                print(f"⚠️ Error updating bucket metadata: {e}")

# Global instance
lightrag_manager = LightRAGManager()
