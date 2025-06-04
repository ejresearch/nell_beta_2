"""
Nell Beta 2 - Brainstorm Module
Direct port of your brainstorm.py logic to FastAPI
"""

import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiosqlite

from .models import (
    BrainstormRequest, BrainstormResponse, BrainstormSummary
)
from .project_manager import ProjectManager
from .lightrag_manager import BucketManager

# =============================================================================
# BRAINSTORM MODULE CLASS
# =============================================================================

class BrainstormModule:
    """
    Handles brainstorming generation using LightRAG buckets and project context
    Direct port of your brainstorm.py workflow
    """
    
    def __init__(self, project_manager: ProjectManager, bucket_manager: BucketManager):
        self.project_manager = project_manager
        self.bucket_manager = bucket_manager
        
        # Tone presets (from your original brainstorm.py)
        self.tone_presets = {
            "neutral": "Generate creative and balanced ideas",
            "cheesy-romcom": "Generate lighthearted, romantic comedy ideas with playful banter and meet-cute scenarios",
            "romantic-dramedy": "Generate heartfelt romantic drama ideas with emotional depth and character growth", 
            "shakespearean-romance": "Generate romantic ideas inspired by Shakespearean themes, wit, and dramatic tension",
            "professional": "Generate professional, business-focused ideas with clear structure and objectives",
            "academic": "Generate scholarly, research-oriented ideas with analytical depth",
            "creative": "Generate innovative, out-of-the-box creative concepts"
        }
    
    async def generate_brainstorm(self, request: BrainstormRequest) -> BrainstormResponse:
        """
        Generate brainstorm content using selected rows and buckets
        Direct port of your brainstorm.py main logic
        """
        # Validate project exists
        project = await self.project_manager.get_project(request.project_id)
        if not project:
            raise ValueError("Project not found")
        
        # Get source table data (like your row selection logic)
        source_context = await self._get_source_context(
            project.db_path, 
            request.source_table, 
            request.selected_rows
        )
        
        # Get next version number
        next_version = await self._get_next_brainstorm_version(project.db_path)
        
        # Build brainstorm prompt (like your prompt construction)
        brainstorm_prompt = await self._build_brainstorm_prompt(
            request, 
            source_context,
            request.selected_buckets
        )
        
        # Query LightRAG buckets (your multi-bucket querying pattern)
        bucket_results = await self.bucket_manager.query_with_context(
            request.project_id,
            request.selected_buckets,
            brainstorm_prompt,
            source_context
        )
        
        # Generate final brainstorm content
        final_content = await self._synthesize_brainstorm_results(
            bucket_results,
            request,
            source_context
        )
        
        # Save to database (like your brainstorm_log_v2 tables)
        brainstorm_id = await self._save_brainstorm_output(
            project.db_path,
            {
                "version": next_version,
                "source_table": request.source_table,
                "source_rows": request.selected_rows,
                "buckets_used": request.selected_buckets,
                "tone": request.tone or "neutral",
                "easter_egg": request.easter_egg,
                "prompt_used": brainstorm_prompt,
                "content": final_content
            }
        )
        
        return BrainstormResponse(
            id=brainstorm_id,
            project_id=request.project_id,
            version=next_version,
            source_table=request.source_table,
            source_rows=request.selected_rows,
            buckets_used=request.selected_buckets,
            tone=request.tone or "neutral",
            easter_egg=request.easter_egg,
            prompt_used=brainstorm_prompt,
            content=final_content,
            created_at=datetime.now()
        )
    
    async def _get_source_context(
        self, 
        db_path: str, 
        table_name: str, 
        row_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Get context data from selected table rows
        Like your source table processing in brainstorm.py
        """
        context = {
            "table_name": table_name,
            "rows": []
        }
        
        async with aiosqlite.connect(db_path) as conn:
            for row_id in row_ids:
                cursor = await conn.execute(
                    f"SELECT * FROM {table_name} WHERE id = ?", 
                    (row_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    # Get column names
                    cursor = await conn.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in await cursor.fetchall()]
                    
                    # Create row dict
                    row_dict = dict(zip(columns, row))
                    context["rows"].append(row_dict)
        
        return context
    
    async def _build_brainstorm_prompt(
        self, 
        request: BrainstormRequest,
        source_context: Dict[str, Any],
        selected_buckets: List[str]
    ) -> str:
        """
        Build comprehensive brainstorm prompt
        Based on your prompt construction patterns
        """
        # Get tone preset
        tone_instruction = self.tone_presets.get(request.tone, self.tone_presets["neutral"])
        
        # Get bucket guidance
        bucket_guidance = []
        for bucket_name in selected_buckets:
            guidance = await self.bucket_manager.get_client(request.project_id).get_bucket_guidance(bucket_name)
            if guidance:
                bucket_guidance.append(f"{bucket_name}: {guidance}")
        
        # Build context from source rows
        context_text = self._format_source_context(source_context)
        
        # Construct prompt (like your brainstorm prompt template)
        prompt_parts = [
            f"BRAINSTORMING TASK:",
            f"Tone/Style: {tone_instruction}",
            "",
            f"SOURCE CONTEXT from {source_context['table_name']}:",
            context_text,
            ""
        ]
        
        if bucket_guidance:
            prompt_parts.extend([
                "BUCKET GUIDANCE:",
                "\n".join(bucket_guidance),
                ""
            ])
        
        prompt_parts.extend([
            "TASK:",
            "Generate creative brainstorming ideas based on the source context above.",
            "Use the knowledge from the selected buckets to inform your suggestions.",
            "Provide specific, actionable ideas that build on the given context."
        ])
        
        # Add easter egg if provided (like your easter egg injection)
        if request.easter_egg:
            prompt_parts.extend([
                "",
                f"SPECIAL INSTRUCTION: {request.easter_egg}"
            ])
        
        # Add custom prompt if provided
        if request.custom_prompt:
            prompt_parts.extend([
                "",
                f"ADDITIONAL INSTRUCTIONS: {request.custom_prompt}"
            ])
        
        return "\n".join(prompt_parts)
    
    def _format_source_context(self, source_context: Dict[str, Any]) -> str:
        """Format source context for prompt inclusion"""
        if not source_context["rows"]:
            return "No source data selected."
        
        formatted_rows = []
        for i, row in enumerate(source_context["rows"], 1):
            row_text = f"Row {i}:"
            for key, value in row.items():
                if key != "id":  # Skip auto-generated ID
                    row_text += f"\n  {key}: {value}"
            formatted_rows.append(row_text)
        
        return "\n\n".join(formatted_rows)
    
    async def _synthesize_brainstorm_results(
        self,
        bucket_results: Dict[str, str],
        request: BrainstormRequest,
        source_context: Dict[str, Any]
    ) -> str:
        """
        Synthesize results from multiple buckets into final brainstorm content
        """
        if not bucket_results:
            return "No results generated from selected buckets."
        
        # Combine bucket results (like your result aggregation)
        synthesis_parts = [
            "=== BRAINSTORM RESULTS ===",
            f"Generated for: {source_context['table_name']} (Rows: {request.selected_rows})",
            f"Tone: {request.tone or 'neutral'}",
            f"Buckets used: {', '.join(request.selected_buckets)}",
            ""
        ]
        
        for bucket_name, result in bucket_results.items():
            synthesis_parts.extend([
                f"--- From {bucket_name.upper()} ---",
                result,
                ""
            ])
        
        if request.easter_egg:
            synthesis_parts.extend([
                "--- SPECIAL ELEMENT ---",
                f"Easter egg applied: {request.easter_egg}",
                ""
            ])
        
        synthesis_parts.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(synthesis_parts)
    
    async def _get_next_brainstorm_version(self, db_path: str) -> int:
        """Get next version number for brainstorm output"""
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute(
                "SELECT MAX(version) FROM brainstorm_outputs"
            )
            result = await cursor.fetchone()
            return (result[0] or 0) + 1
    
    async def _save_brainstorm_output(self, db_path: str, data: Dict[str, Any]) -> str:
        """
        Save brainstorm output to database
        Like your brainstorm_log_v2 table pattern
        """
        brainstorm_id = f"brainstorm_{data['version']}"
        
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("""
                INSERT INTO brainstorm_outputs 
                (version, source_table, source_rows, buckets_used, tone, easter_egg, prompt_used, content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["version"],
                data["source_table"],
                json.dumps(data["source_rows"]),
                json.dumps(data["buckets_used"]),
                data["tone"],
                data["easter_egg"],
                data["prompt_used"],
                data["content"]
            ))
            await conn.commit()
        
        return brainstorm_id
    
    async def get_brainstorm_history(self, project_id: str) -> BrainstormSummary:
        """Get brainstorm history for project"""
        project = await self.project_manager.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
        
        async with aiosqlite.connect(project.db_path) as conn:
            # Get total count and latest version
            cursor = await conn.execute(
                "SELECT COUNT(*), MAX(version) FROM brainstorm_outputs"
            )
            count_result = await cursor.fetchone()
            total_sessions = count_result[0] or 0
            latest_version = count_result[1] or 0
            
            # Get recent sessions
            cursor = await conn.execute("""
                SELECT * FROM brainstorm_outputs 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_rows = await cursor.fetchall()
            
            recent_sessions = []
            for row in recent_rows:
                recent_sessions.append(BrainstormResponse(
                    id=f"brainstorm_{row[1]}",  # version
                    project_id=project_id,
                    version=row[1],
                    source_table=row[2],
                    source_rows=json.loads(row[3]),
                    buckets_used=json.loads(row[4]),
                    tone=row[5],
                    easter_egg=row[6],
                    prompt_used=row[7],
                    content=row[8],
                    created_at=datetime.fromisoformat(row[9])
                ))
        
        return BrainstormSummary(
            project_id=project_id,
            latest_version=latest_version,
            total_sessions=total_sessions,
            recent_sessions=recent_sessions
        )
    
    async def get_brainstorm_by_version(self, project_id: str, version: int) -> Optional[BrainstormResponse]:
        """Get specific brainstorm by version number"""
        project = await self.project_manager.get_project(project_id)
        if not project:
            return None
        
        async with aiosqlite.connect(project.db_path) as conn:
            cursor = await conn.execute(
                "SELECT * FROM brainstorm_outputs WHERE version = ?",
                (version,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return BrainstormResponse(
                id=f"brainstorm_{row[1]}",
                project_id=project_id,
                version=row[1],
                source_table=row[2],
                source_rows=json.loads(row[3]),
                buckets_used=json.loads(row[4]),
                tone=row[5],
                easter_egg=row[6],
                prompt_used=row[7],
                content=row[8],
                created_at=datetime.fromisoformat(row[9])
            )

# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# This will be injected with dependencies in the API layer
brainstorm_module = None

def get_brainstorm_module(project_manager: ProjectManager, bucket_manager: BucketManager) -> BrainstormModule:
    """Dependency injection for brainstorm module"""
    global brainstorm_module
    if brainstorm_module is None:
        brainstorm_module = BrainstormModule(project_manager, bucket_manager)
    return brainstorm_module
