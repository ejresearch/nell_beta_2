"""
Brainstorm API - Exposes BrainstormModule endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
import sys
import os

# Ensure backend modules can be imported when running as package or script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import BrainstormRequest, BrainstormResponse, BrainstormSummary
from core.project_manager import project_manager
from core.lightrag_manager import lightrag_manager
from core.brainstorm import BrainstormModule, get_brainstorm_module

router = APIRouter(prefix="/projects/{project_id}/brainstorm", tags=["brainstorm"])


def _get_module() -> BrainstormModule:
    """Instantiate or retrieve the BrainstormModule"""
    return get_brainstorm_module(project_manager, lightrag_manager)


@router.post("/", response_model=BrainstormResponse)
async def generate_brainstorm(
    project_id: str,
    request: BrainstormRequest,
    module: BrainstormModule = Depends(_get_module),
):
    """Generate brainstorm content for a project"""
    try:
        request.project_id = project_id
        return await module.generate_brainstorm(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=BrainstormSummary)
async def brainstorm_history(
    project_id: str,
    module: BrainstormModule = Depends(_get_module),
):
    """Get brainstorm history for a project"""
    try:
        return await module.get_brainstorm_history(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
