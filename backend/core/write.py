"""
Nell Beta 2 - Write Module
Direct port of your write.py logic to FastAPI
"""

import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiosqlite

from .models import (
    WriteRequest, WriteResponse, WriteEdit, WriteSummary
)
from .project_manager import ProjectManager
from .lightrag_manager import LightRAGManager
from .brainstorm import BrainstormModule

# =============================================================================
# WRITE MODULE CLASS
# =============================================================================

class WriteModule:
    """
    Handles content generation using brainstorm results and project context
    Direct port of your write.py workflow
    """
    
    def __init__(
        self, 
        project_manager: ProjectManager, 
        bucket_manager: LightRAGManager,
        brainstorm_module: BrainstormModule
    ):
        self.project_manager = project_manager
        self.bucket_manager = bucket_manager
        self.brainstorm_module = brainstorm_module
        
        # Writing style presets (from your write.py tone handling)
        self.writing_styles = {
            "neutral": "Write in a clear, balanced style",
            "cheesy-romcom": "Write in a lighthearted, romantic comedy style with playful dialogue and sweet moments",
            "romantic-dramedy": "Write in a heartfelt romantic drama style with emotional depth and character development",
            "shakespearean-romance": "Write in an elevated, poetic style inspired by Shakespearean romance with rich language",
            "professional": "Write in a professional, business-appropriate style with clear structure",
            "academic": "Write in a scholarly, analytical style with proper academic tone",
            "creative": "Write in an innovative, artistic style with creative flair"
        }
    
    async def generate_write(self, request: WriteRequest) -> WriteResponse:
        """
        Generate written content using brainstorm results and source context
        Direct port of your write.py main logic
        """
        # Validate project exists
        project = await self.project_manager.get_project(request.project_id)
        if not project:
            raise ValueError("Project not found")
        
        # Get brainstorm context (like your brainstorm table reading)
        brainstorm_context = await self._get_brainstorm_context(
            project.db_path,
            request.brainstorm_version
        )
        
        # Get source table context (like your character/scene data)
        source_context = await self._get_source_context(
            project.db_path,
            request.source_table,
            request.selected_rows
        )
        
        # Get next version number
        next_version = await self._get_next_write_version(project.db_path)
        
        # Build comprehensive write prompt
        write_prompt = await self._build_write_prompt(
            request,
            brainstorm_context,
            source_context
        )
        
        # Generate content using LLM (like your final generation step)
        generated_content = await self._generate_content(
            request.project_id,
            write_prompt,
            brainstorm_context
        )
        
        # Calculate word count
        word_count = len(generated_content.split())
        
        # Save to database (like your finalized_draft_v2 tables)
        write_id = await self._save_write_output(
            project.db_path,
            {
                "version": next_version,
                "brainstorm_version": request.brainstorm_version,
                "source_table": request.source_table,
                "source_rows": request.selected_rows,
                "tone": request.tone or "neutral",
                "instructions": request.custom_instructions,
                "content": generated_content,
                "word_count": word_count
            }
        )
        
        return WriteResponse(
            id=write_id,
            project_id=request.project_id,
            version=next_version,
            brainstorm_version=request.brainstorm_version,
            source_table=request.source_table,
            source_rows=request.selected_rows,
            tone=request.tone or "neutral",
            instructions=request.custom_instructions,
            content=generated_content,
            word_count=word_count,
            created_at=datetime.now()
        )
    
    async def _get_brainstorm_context(
        self, 
        db_path: str, 
        brainstorm_version: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Get brainstorm context from specified version or latest
        Like your brainstorm table reading in write.py
        """
        async with aiosqlite.connect(db_path) as conn:
            if brainstorm_version:
                # Get specific version
                cursor = await conn.execute(
                    "SELECT * FROM brainstorm_outputs WHERE version = ?",
                    (brainstorm_version,)
                )
            else:
                # Get latest version
                cursor = await conn.execute(
                    "SELECT * FROM brainstorm_outputs ORDER BY version DESC LIMIT 1"
                )
            
            row = await cursor.fetchone()
            if not row:
                return None
            
            return {
                "version": row[1],
                "source_table": row[2],
                "source_rows": json.loads(row[3]),
                "buckets_used": json.loads(row[4]),
                "tone": row[5],
                "easter_egg": row[6],
                "content": row[8],
                "created_at": row[9]
            }
    
    async def _get_source_context(
        self, 
        db_path: str, 
        table_name: str, 
        row_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Get source context from selected table rows
        Like your character/scene data processing
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
    
    async def _build_write_prompt(
        self,
        request: WriteRequest,
        brainstorm_context: Optional[Dict[str, Any]],
        source_context: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive write prompt combining all context
        Based on your write.py prompt construction
        """
        # Get writing style instruction
        style_instruction = self.writing_styles.get(
            request.tone, 
            self.writing_styles["neutral"]
        )
        
        # Build prompt components
        prompt_parts = [
            "=== WRITING TASK ===",
            f"Style: {style_instruction}",
            ""
        ]
        
        # Add source context (like your character/scene info)
        if source_context["rows"]:
            prompt_parts.extend([
                f"SOURCE MATERIAL from {source_context['table_name']}:",
                self._format_source_context(source_context),
                ""
            ])
        
        # Add brainstorm context (like your brainstorm insights)
        if brainstorm_context:
            prompt_parts.extend([
                f"BRAINSTORM INSIGHTS (Version {brainstorm_context['version']}):",
                brainstorm_context["content"][:2000] + "..." if len(brainstorm_context["content"]) > 2000 else brainstorm_context["content"],
                ""
            ])
        
        # Add writing instructions
        prompt_parts.extend([
            "WRITING INSTRUCTIONS:",
            "1. Create engaging, well-structured content based on the source material and brainstorm insights",
            "2. Maintain consistency with the specified tone and style",
            "3. Develop ideas from the brainstorm into polished written content",
            "4. Ensure natural flow and coherent narrative/structure"
        ])
        
        # Add custom instructions if provided
        if request.custom_instructions:
            prompt_parts.extend([
                "",
                f"ADDITIONAL INSTRUCTIONS: {request.custom_instructions}"
            ])
        
        prompt_parts.extend([
            "",
            "Generate the written content now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _format_source_context(self, source_context: Dict[str, Any]) -> str:
        """Format source context for prompt inclusion"""
        if not source_context["rows"]:
            return "No source data selected."
        
        formatted_rows = []
        for i, row in enumerate(source_context["rows"], 1):
            row_text = f"Item {i}:"
            for key, value in row.items():
                if key != "id":  # Skip auto-generated ID
                    row_text += f"\n  {key}: {value}"
            formatted_rows.append(row_text)
        
        return "\n\n".join(formatted_rows)
    
    async def _generate_content(
        self,
        project_id: str,
        write_prompt: str,
        brainstorm_context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate final content using LLM
        Like your final content generation in write.py
        """
        try:
            # Use bucket manager's LLM integration for generation
            # This leverages the same LightRAG LLM setup used for bucket queries
            client = self.bucket_manager.get_client(project_id)
            
            # For now, we'll use a simple approach - in a full implementation,
            # you'd want to integrate with your preferred LLM API directly
            
            # Placeholder for actual LLM generation
            # In practice, this would call GPT-4o or your preferred model
            generated_content = f"""
=== GENERATED CONTENT ===

{write_prompt}

[Note: This is a placeholder for actual LLM-generated content. 
In the full implementation, this would be replaced with a call to GPT-4o 
or your preferred language model, using the constructed prompt above.]

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return generated_content.strip()
            
        except Exception as e:
            return f"Error generating content: {str(e)}"
    
    async def _get_next_write_version(self, db_path: str) -> int:
        """Get next version number for write output"""
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute(
                "SELECT MAX(version) FROM write_outputs"
            )
            result = await cursor.fetchone()
            return (result[0] or 0) + 1
    
    async def _save_write_output(self, db_path: str, data: Dict[str, Any]) -> str:
        """
        Save write output to database
        Like your finalized_draft_v2 table pattern
        """
        write_id = f"write_{data['version']}"
        
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("""
                INSERT INTO write_outputs 
                (version, brainstorm_version, source_table, source_rows, tone, instructions, content, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["version"],
                data["brainstorm_version"],
                data["source_table"],
                json.dumps(data["source_rows"]),
                data["tone"],
                data["instructions"],
                data["content"],
                data["word_count"]
            ))
            await conn.commit()
        
        return write_id
    
    async def edit_content(self, edit_request: WriteEdit) -> WriteResponse:
        """
        Edit existing written content
        Based on your write_edit.py patterns
        """
        # Extract project_id and version from write_id
        if not edit_request.write_id.startswith("write_"):
            raise ValueError("Invalid write ID format")
        
        version = int(edit_request.write_id.split("_")[1])
        
        # Find the project that contains this write output
        # This is a simplified approach - in practice you'd want better tracking
        project = await self._find_project_by_write_id(edit_request.write_id)
        if not project:
            raise ValueError("Write output not found")
        
        # Get original write content
        original_write = await self.get_write_by_version(project.id, version)
        if not original_write:
            raise ValueError("Original write not found")
        
        # Build edit prompt
        edit_prompt = f"""
=== CONTENT EDITING TASK ===

ORIGINAL CONTENT:
{original_write.content}

EDIT INSTRUCTIONS:
{edit_request.edit_instructions}

Please revise the original content according to the edit instructions while maintaining the overall style and quality.
"""
        
        # Generate edited content
        edited_content = await self._generate_content(
            project.id,
            edit_prompt,
            None
        )
        
        # Save edit to edit_history table
        async with aiosqlite.connect(project.db_path) as conn:
            await conn.execute("""
                INSERT INTO edit_history (write_id, edit_instructions, content)
                VALUES (?, ?, ?)
            """, (version, edit_request.edit_instructions, edited_content))
            await conn.commit()
        
        # Return updated write response
        return WriteResponse(
            id=original_write.id,
            project_id=original_write.project_id,
            version=original_write.version,
            brainstorm_version=original_write.brainstorm_version,
            source_table=original_write.source_table,
            source_rows=original_write.source_rows,
            tone=original_write.tone,
            instructions=f"{original_write.instructions or ''}\n\nEDIT: {edit_request.edit_instructions}",
            content=edited_content,
            word_count=len(edited_content.split()),
            created_at=datetime.now()
        )
    
    async def _find_project_by_write_id(self, write_id: str):
        """Helper to find project containing a write output"""
        # Simplified implementation - you'd want better indexing in practice
        projects = await self.project_manager.list_projects()
        
        for project in projects.projects:
            write = await self.get_write_by_version(
                project.id, 
                int(write_id.split("_")[1])
            )
            if write:
                return project
        return None
    
    async def get_write_history(self, project_id: str) -> WriteSummary:
        """Get write history for project"""
        project = await self.project_manager.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
        
        async with aiosqlite.connect(project.db_path) as conn:
            # Get total count and latest version
            cursor = await conn.execute(
                "SELECT COUNT(*), MAX(version) FROM write_outputs"
            )
            count_result = await cursor.fetchone()
            total_drafts = count_result[0] or 0
            latest_version = count_result[1] or 0
            
            # Get recent drafts
            cursor = await conn.execute("""
                SELECT * FROM write_outputs 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_rows = await cursor.fetchall()
            
            recent_drafts = []
            for row in recent_rows:
                recent_drafts.append(WriteResponse(
                    id=f"write_{row[1]}",  # version
                    project_id=project_id,
                    version=row[1],
                    brainstorm_version=row[2],
                    source_table=row[3],
                    source_rows=json.loads(row[4]),
                    tone=row[5],
                    instructions=row[6],
                    content=row[7],
                    word_count=row[8],
                    created_at=datetime.fromisoformat(row[9])
                ))
        
        return WriteSummary(
            project_id=project_id,
            latest_version=latest_version,
            total_drafts=total_drafts,
            recent_drafts=recent_drafts
        )
    
    async def get_write_by_version(self, project_id: str, version: int) -> Optional[WriteResponse]:
        """Get specific write output by version number"""
        project = await self.project_manager.get_project(project_id)
        if not project:
            return None
        
        async with aiosqlite.connect(project.db_path) as conn:
            cursor = await conn.execute(
                "SELECT * FROM write_outputs WHERE version = ?",
                (version,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return WriteResponse(
                id=f"write_{row[1]}",
                project_id=project_id,
                version=row[1],
                brainstorm_version=row[2],
                source_table=row[3],
                source_rows=json.loads(row[4]),
                tone=row[5],
                instructions=row[6],
                content=row[7],
                word_count=row[8],
                created_at=datetime.fromisoformat(row[9])
            )

# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# This will be injected with dependencies in the API layer
write_module = None

def get_write_module(
    project_manager: ProjectManager, 
    bucket_manager: LightRAGManager,
    brainstorm_module: BrainstormModule
) -> WriteModule:
    """Dependency injection for write module"""
    global write_module
    if write_module is None:
        write_module = WriteModule(project_manager, bucket_manager, brainstorm_module)
    return write_module
