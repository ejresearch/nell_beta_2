"""
Write API - Exposes WriteModule endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import WriteRequest, WriteResponse, WriteSummary
from core.project_manager import project_manager
from core.lightrag_manager import lightrag_manager
from core.brainstorm import get_brainstorm_module
from core.write import WriteModule, get_write_module

router = APIRouter(prefix="/projects/{project_id}/write", tags=["write"])


def _get_module() -> WriteModule:
    brainstorm = get_brainstorm_module(project_manager, lightrag_manager)
    return get_write_module(project_manager, lightrag_manager, brainstorm)


@router.post("/", response_model=WriteResponse)
async def generate_write(
    project_id: str,
    request: WriteRequest,
    module: WriteModule = Depends(_get_module),
):
    """Generate written content for a project"""
    try:
        request.project_id = project_id
        return await module.generate_write(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=WriteSummary)
async def write_history(
    project_id: str,
    module: WriteModule = Depends(_get_module),
):
    """Get write history for a project"""
    try:
        return await module.get_write_history(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
