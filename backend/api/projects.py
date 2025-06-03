"""
Projects API - FastAPI endpoints for project management
Exposes the ProjectManager functionality as REST API
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
import os

# Add the backend directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.project_manager import (
    project_manager, 
    ProjectCreate, 
    ProjectInfo, 
    TableInfo
)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectInfo)
async def create_project(project_data: ProjectCreate):
    """
    Create a new project with isolated database and LightRAG storage
    """
    try:
        project = await project_manager.create_project(project_data)
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.get("/", response_model=List[ProjectInfo])
async def list_projects():
    """
    Get list of all projects
    """
    try:
        projects = await project_manager.list_projects()
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")

@router.get("/{project_id}", response_model=ProjectInfo)
async def get_project(project_id: str):
    """
    Get detailed information about a specific project
    """
    try:
        project = await project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    Delete a project and all its data
    """
    try:
        success = await project_manager.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        return {"message": f"Project '{project_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

@router.get("/{project_id}/tables", response_model=List[str])
async def get_project_tables(project_id: str):
    """
    Get list of tables in a project database
    """
    try:
        project = await project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        
        tables = await project_manager.get_project_tables(project_id)
        return tables
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")

@router.get("/{project_id}/tables/{table_name}", response_model=TableInfo)
async def get_table_info(project_id: str, table_name: str):
    """
    Get information about a specific table (columns, row count)
    """
    try:
        table_info = await project_manager.get_table_info(project_id, table_name)
        if not table_info:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in project '{project_id}'")
        return table_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table info: {str(e)}")

@router.get("/{project_id}/tables/{table_name}/data")
async def get_table_data(
    project_id: str, 
    table_name: str, 
    limit: int = Query(default=100, ge=1, le=1000)
):
    """
    Get data from a specific table
    """
    try:
        # Verify project exists
        project = await project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        
        data = await project_manager.get_table_data(project_id, table_name, limit)
        return {
            "table_name": table_name,
            "project_id": project_id,
            "data": data,
            "count": len(data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table data: {str(e)}")

@router.get("/{project_id}/status")
async def get_project_status(project_id: str):
    """
    Get comprehensive project status including tables, data counts, and paths
    """
    try:
        project = await project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        
        # Get table information
        table_details = []
        for table_name in project.tables:
            table_info = await project_manager.get_table_info(project_id, table_name)
            if table_info:
                table_details.append({
                    "name": table_info.name,
                    "columns": table_info.columns,
                    "row_count": table_info.row_count
                })
        
        return {
            "project": project,
            "table_details": table_details,
            "total_tables": len(project.tables),
            "paths": {
                "database": project.db_path,
                "lightrag_dir": project.lightrag_dir
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project status: {str(e)}")
