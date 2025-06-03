"""
Project Manager - Core module for Nell Beta 2
Ports the functionality from new_project.py to FastAPI service
"""

import os
import sqlite3
import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from pathlib import Path

# Pydantic Models
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    project_type: str = "creative_writing"

class ProjectInfo(BaseModel):
    id: str
    name: str
    description: str
    project_type: str
    created_at: str
    db_path: str
    lightrag_dir: str
    tables: List[str] = []

class TableInfo(BaseModel):
    name: str
    columns: List[str]
    row_count: int

class ProjectManager:
    """
    Manages project creation, loading, and database operations
    Ported from Lizzy's new_project.py functionality
    """
    
    def __init__(self, projects_base_dir: str = "./projects"):
        self.projects_base_dir = Path(projects_base_dir)
        self.projects_base_dir.mkdir(exist_ok=True)
        
    def _get_project_dir(self, project_id: str) -> Path:
        """Get the directory path for a project"""
        return self.projects_base_dir / project_id
    
    def _get_db_path(self, project_id: str) -> Path:
        """Get the SQLite database path for a project"""
        return self._get_project_dir(project_id) / f"{project_id}.db"
    
    def _get_lightrag_dir(self, project_id: str) -> Path:
        """Get the LightRAG working directory for a project"""
        return self._get_project_dir(project_id) / "lightrag_data"
    
    async def create_project(self, project_data: ProjectCreate) -> ProjectInfo:
        """
        Create a new project with isolated SQLite database and LightRAG directory
        Similar to new_project.py functionality
        """
        # Generate project ID from name
        project_id = project_data.name.lower().replace(" ", "_").replace("-", "_")
        project_dir = self._get_project_dir(project_id)
        
        # Check if project already exists
        if project_dir.exists():
            raise ValueError(f"Project '{project_id}' already exists")
        
        # Create project directory structure
        project_dir.mkdir(parents=True)
        lightrag_dir = self._get_lightrag_dir(project_id)
        lightrag_dir.mkdir(parents=True)
        
        # Create SQLite database
        db_path = self._get_db_path(project_id)
        
        async with aiosqlite.connect(db_path) as db:
            # Create projects metadata table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS project_metadata (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    project_type TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Insert project metadata
            created_at = datetime.now().isoformat()
            await db.execute("""
                INSERT INTO project_metadata 
                (id, name, description, project_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, project_data.name, project_data.description, 
                  project_data.project_type, created_at, created_at))
            
            # Create default tables based on project type
            await self._create_default_tables(db, project_data.project_type)
            
            await db.commit()
        
        # Return project info
        return ProjectInfo(
            id=project_id,
            name=project_data.name,
            description=project_data.description or "",
            project_type=project_data.project_type,
            created_at=created_at,
            db_path=str(db_path),
            lightrag_dir=str(lightrag_dir),
            tables=await self.get_project_tables(project_id)
        )
    
    async def _create_default_tables(self, db: aiosqlite.Connection, project_type: str):
        """Create default tables based on project type"""
        
        if project_type == "creative_writing":
            # Characters table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    role TEXT,
                    personality TEXT,
                    backstory TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Scenes/Chapters table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS scenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    act_number INTEGER,
                    scene_number INTEGER,
                    setting TEXT,
                    characters TEXT,
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
        elif project_type == "business_writing":
            # Requirements table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT,
                    stakeholder TEXT,
                    acceptance_criteria TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Stakeholders table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS stakeholders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT,
                    department TEXT,
                    contact_info TEXT,
                    influence_level TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
        
        # Always create output tracking tables
        await db.execute("""
            CREATE TABLE IF NOT EXISTS brainstorm_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_table TEXT,
                source_row_id INTEGER,
                prompt_used TEXT,
                buckets_used TEXT,
                easter_egg TEXT,
                output_content TEXT,
                version INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS write_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brainstorm_id INTEGER,
                source_table TEXT,
                source_row_id INTEGER,
                prompt_used TEXT,
                output_content TEXT,
                version INTEGER DEFAULT 1,
                created_at TEXT,
                FOREIGN KEY (brainstorm_id) REFERENCES brainstorm_outputs (id)
            )
        """)
    
    async def get_project(self, project_id: str) -> Optional[ProjectInfo]:
        """Get project information by ID"""
        db_path = self._get_db_path(project_id)
        
        if not db_path.exists():
            return None
        
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("""
                SELECT id, name, description, project_type, created_at 
                FROM project_metadata WHERE id = ?
            """, (project_id,)) as cursor:
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return ProjectInfo(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    project_type=row[3],
                    created_at=row[4],
                    db_path=str(db_path),
                    lightrag_dir=str(self._get_lightrag_dir(project_id)),
                    tables=await self.get_project_tables(project_id)
                )
    
    async def list_projects(self) -> List[ProjectInfo]:
        """List all projects"""
        projects = []
        
        for project_dir in self.projects_base_dir.iterdir():
            if project_dir.is_dir():
                project = await self.get_project(project_dir.name)
                if project:
                    projects.append(project)
        
        return projects
    
    async def get_project_tables(self, project_id: str) -> List[str]:
        """Get list of tables in project database"""
        db_path = self._get_db_path(project_id)
        
        if not db_path.exists():
            return []
        
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def get_table_info(self, project_id: str, table_name: str) -> Optional[TableInfo]:
        """Get information about a specific table"""
        db_path = self._get_db_path(project_id)
        
        if not db_path.exists():
            return None
        
        async with aiosqlite.connect(db_path) as db:
            # Get column info
            async with db.execute(f"PRAGMA table_info({table_name})") as cursor:
                columns_raw = await cursor.fetchall()
                columns = [col[1] for col in columns_raw]  # col[1] is column name
            
            # Get row count
            async with db.execute(f"SELECT COUNT(*) FROM {table_name}") as cursor:
                row_count = (await cursor.fetchone())[0]
            
            return TableInfo(
                name=table_name,
                columns=columns,
                row_count=row_count
            )
    
    async def get_table_data(self, project_id: str, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get data from a table"""
        db_path = self._get_db_path(project_id)
        
        if not db_path.exists():
            return []
        
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row  # Enable dict-like access
            
            async with db.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its data"""
        project_dir = self._get_project_dir(project_id)
        
        if not project_dir.exists():
            return False
        
        import shutil
        shutil.rmtree(project_dir)
        return True

# Global instance
project_manager = ProjectManager()
