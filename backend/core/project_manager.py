"""
Nell Beta 2 - Project Management System
Direct port of new_project.py patterns to FastAPI
"""

import os
import sqlite3
import aiosqlite
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import shutil
import json

from .models import (
    ProjectCreate, ProjectResponse, ProjectList, ProjectStatus,
    TableCreate, TableRow, TableSchema, TableData,
    ProjectConfig, ErrorResponse
)

# =============================================================================
# PROJECT MANAGER CLASS
# =============================================================================

class ProjectManager:
    """
    Manages project creation, loading, and database operations
    Based on your new_project.py implementation
    """
    
    def __init__(self, projects_dir: str = "./projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)
        
        # Create projects index database
        self.index_db = self.projects_dir / "projects_index.db"
        self._init_index_database()
    
    def _init_index_database(self):
        """Initialize the projects index database"""
        with sqlite3.connect(self.index_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    db_path TEXT NOT NULL,
                    lightrag_path TEXT NOT NULL,
                    config TEXT DEFAULT '{}'
                )
            """)
            conn.commit()
    
    async def create_project(self, project_data: ProjectCreate) -> ProjectResponse:
        """
        Create new project with isolated database and LightRAG directory
        Port of your new_project.py logic
        """
        project_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Create project directory structure
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Database and LightRAG paths
        db_path = project_dir / f"{project_data.name.replace(' ', '_')}.db"
        lightrag_path = project_dir / "lightrag_working_dir"
        lightrag_path.mkdir(exist_ok=True)
        
        try:
            # Create project database with custom tables
            async with aiosqlite.connect(db_path) as conn:
                # Create standard metadata table
                await conn.execute("""
                    CREATE TABLE project_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert project info
                await conn.execute(
                    "INSERT INTO project_metadata (key, value) VALUES (?, ?)",
                    ("project_name", project_data.name)
                )
                await conn.execute(
                    "INSERT INTO project_metadata (key, value) VALUES (?, ?)",
                    ("description", project_data.description or "")
                )
                
                # Create custom tables (like your dynamic table creation)
                table_names = []
                for table_def in project_data.tables:
                    for table_name, columns in table_def.items():
                        await self._create_custom_table(conn, table_name, columns)
                        table_names.append(table_name)
                
                # Create standard output tracking tables
                await self._create_output_tables(conn)
                await conn.commit()
            
            # Register project in index database
            with sqlite3.connect(self.index_db) as index_conn:
                index_conn.execute("""
                    INSERT INTO projects 
                    (id, name, description, status, created_at, updated_at, db_path, lightrag_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id, project_data.name, project_data.description,
                    ProjectStatus.ACTIVE, timestamp, timestamp,
                    str(db_path), str(lightrag_path)
                ))
                index_conn.commit()
            
            return ProjectResponse(
                id=project_id,
                name=project_data.name,
                description=project_data.description,
                status=ProjectStatus.ACTIVE,
                created_at=timestamp,
                updated_at=timestamp,
                db_path=str(db_path),
                lightrag_path=str(lightrag_path),
                tables=table_names,
                bucket_count=0
            )
            
        except Exception as e:
            # Cleanup on failure
            if project_dir.exists():
                shutil.rmtree(project_dir)
            raise Exception(f"Failed to create project: {str(e)}")
    
    async def _create_custom_table(self, conn: aiosqlite.Connection, table_name: str, columns: List[str]):
        """
        Create custom table with user-defined columns
        Direct port of your create_custom_table function
        """
        # Add id column automatically
        all_columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + [f"{col} TEXT" for col in columns]
        column_definitions = ", ".join(all_columns)
        
        await conn.execute(f"CREATE TABLE {table_name} ({column_definitions})")
    
    async def _create_output_tables(self, conn: aiosqlite.Connection):
        """Create standard output tracking tables"""
        # Brainstorm outputs (versioned like your brainstorm_log_v2, etc.)
        await conn.execute("""
            CREATE TABLE brainstorm_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                source_table TEXT NOT NULL,
                source_rows TEXT NOT NULL,  -- JSON array of row IDs
                buckets_used TEXT NOT NULL, -- JSON array of bucket names
                tone TEXT,
                easter_egg TEXT,
                prompt_used TEXT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Write outputs (versioned like your finalized_draft_v2, etc.)
        await conn.execute("""
            CREATE TABLE write_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                brainstorm_version INTEGER,
                source_table TEXT NOT NULL,
                source_rows TEXT NOT NULL,  -- JSON array of row IDs
                tone TEXT,
                instructions TEXT,
                content TEXT NOT NULL,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Edit history
        await conn.execute("""
            CREATE TABLE edit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                write_id INTEGER,
                edit_instructions TEXT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (write_id) REFERENCES write_outputs (id)
            )
        """)
    
    async def get_project(self, project_id: str) -> Optional[ProjectResponse]:
        """Get project by ID"""
        with sqlite3.connect(self.index_db) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            
            if not row:
                return None
            
            # Get table count
            table_count = await self._get_table_count(row['db_path'])
            bucket_count = await self._get_bucket_count(row['lightrag_path'])
            
            return ProjectResponse(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                status=ProjectStatus(row['status']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                db_path=row['db_path'],
                lightrag_path=row['lightrag_path'],
                tables=await self._get_table_names(row['db_path']),
                bucket_count=bucket_count
            )
    
    async def list_projects(self) -> ProjectList:
        """List all projects"""
        with sqlite3.connect(self.index_db) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC"
            ).fetchall()
            
            projects = []
            for row in rows:
                table_names = await self._get_table_names(row['db_path'])
                bucket_count = await self._get_bucket_count(row['lightrag_path'])
                
                projects.append(ProjectResponse(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    status=ProjectStatus(row['status']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    db_path=row['db_path'],
                    lightrag_path=row['lightrag_path'],
                    tables=table_names,
                    bucket_count=bucket_count
                ))
            
            return ProjectList(projects=projects, total=len(projects))
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete project and all associated data"""
        project = await self.get_project(project_id)
        if not project:
            return False
        
        try:
            # Remove project directory
            project_dir = Path(project.db_path).parent
            if project_dir.exists():
                shutil.rmtree(project_dir)
            
            # Remove from index
            with sqlite3.connect(self.index_db) as conn:
                conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                conn.commit()
            
            return True
        except Exception:
            return False
    
    async def _get_table_names(self, db_path: str) -> List[str]:
        """Get list of user-created tables (excluding system tables)"""
        if not os.path.exists(db_path):
            return []
        
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT IN ('project_metadata', 'brainstorm_outputs', 'write_outputs', 'edit_history')"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def _get_table_count(self, db_path: str) -> int:
        """Get count of user-created tables"""
        tables = await self._get_table_names(db_path)
        return len(tables)
    
    async def _get_bucket_count(self, lightrag_path: str) -> int:
        """Get count of LightRAG buckets"""
        lightrag_dir = Path(lightrag_path)
        if not lightrag_dir.exists():
            return 0
        return len([d for d in lightrag_dir.iterdir() if d.is_dir()])

# =============================================================================
# TABLE OPERATIONS
# =============================================================================

class TableManager:
    """
    Manages table operations within projects
    Based on your dynamic table handling patterns
    """
    
    def __init__(self, project_manager: ProjectManager):
        self.project_manager = project_manager
    
    async def create_table(self, project_id: str, table_data: TableCreate) -> TableSchema:
        """Create new table in project database"""
        project = await self.project_manager.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
        
        async with aiosqlite.connect(project.db_path) as conn:
            await self.project_manager._create_custom_table(
                conn, table_data.table_name, table_data.columns
            )
            await conn.commit()
        
        return TableSchema(
            table_name=table_data.table_name,
            columns=table_data.columns,
            row_count=0
        )
    
    async def get_table_data(self, project_id: str, table_name: str) -> Optional[TableData]:
        """Get complete table data"""
        project = await self.project_manager.get_project(project_id)
        if not project:
            return None
        
        async with aiosqlite.connect(project.db_path) as conn:
            # Get table schema
            cursor = await conn.execute(f"PRAGMA table_info({table_name})")
            schema_rows = await cursor.fetchall()
            columns = [row[1] for row in schema_rows if row[1] != 'id']  # Exclude auto-generated id
            
            # Get table data
            cursor = await conn.execute(f"SELECT * FROM {table_name}")
            data_rows = await cursor.fetchall()
            
            rows = []
            for row in data_rows:
                row_dict = dict(zip([col[0] for col in cursor.description], row))
                row_id = row_dict.pop('id')
                rows.append(TableRow(row_id=row_id, data=row_dict))
            
            return TableData(
                schema=TableSchema(
                    table_name=table_name,
                    columns=columns,
                    row_count=len(rows)
                ),
                rows=rows
            )
    
    async def add_row(self, project_id: str, table_name: str, row_data: TableRow) -> int:
        """Add new row to table"""
        project = await self.project_manager.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
        
        async with aiosqlite.connect(project.db_path) as conn:
            columns = list(row_data.data.keys())
            values = list(row_data.data.values())
            placeholders = ", ".join(["?" for _ in values])
            
            cursor = await conn.execute(
                f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                values
            )
            await conn.commit()
            return cursor.lastrowid
    
    async def update_row(self, project_id: str, table_name: str, row_data: TableRow) -> bool:
        """Update existing row"""
        if not row_data.row_id:
            return False
        
        project = await self.project_manager.get_project(project_id)
        if not project:
            return False
        
        async with aiosqlite.connect(project.db_path) as conn:
            set_clauses = [f"{col} = ?" for col in row_data.data.keys()]
            values = list(row_data.data.values()) + [row_data.row_id]
            
            await conn.execute(
                f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = ?",
                values
            )
            await conn.commit()
            return True
    
    async def delete_row(self, project_id: str, table_name: str, row_id: int) -> bool:
        """Delete row from table"""
        project = await self.project_manager.get_project(project_id)
        if not project:
            return False
        
        async with aiosqlite.connect(project.db_path) as conn:
            await conn.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
            await conn.commit()
            return True

# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

# Global instances for dependency injection
project_manager = ProjectManager()
table_manager = TableManager(project_manager)
