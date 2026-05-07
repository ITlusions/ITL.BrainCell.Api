"""Timeline endpoint — chronological view of all items saved across BrainCell cells."""
import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

_UNION_SQL = """
    SELECT id::text, 'notes' AS cell_type, title, created_at FROM notes
    UNION ALL
    SELECT id::text, 'tasks' AS cell_type, title, created_at FROM tasks
    UNION ALL
    SELECT id::text, 'snippets' AS cell_type, title, created_at FROM snippets
    UNION ALL
    SELECT id::text, 'references' AS cell_type, title, created_at FROM references
    UNION ALL
    SELECT id::text, 'runbooks' AS cell_type, title, created_at FROM runbooks
    UNION ALL
    SELECT id::text, 'api_contracts' AS cell_type, title, created_at FROM api_contracts
    UNION ALL
    SELECT id::text, 'intel_reports' AS cell_type, title, created_at FROM intel_reports
    UNION ALL
    SELECT id::text, 'incidents' AS cell_type, title, created_at FROM incidents
    UNION ALL
    SELECT id::text, 'vuln_patches' AS cell_type, title, created_at FROM vuln_patches
    UNION ALL
    SELECT id::text, 'vuln_reports' AS cell_type, title, created_at FROM vuln_reports
    UNION ALL
    SELECT id::text, 'threats' AS cell_type, name AS title, created_at FROM threats
    UNION ALL
    SELECT id::text, 'dependencies' AS cell_type, name AS title, created_at FROM dependencies
    UNION ALL
    SELECT id::text, 'persons' AS cell_type, name AS title, created_at FROM persons
    UNION ALL
    SELECT id::text, 'kill_chains' AS cell_type, name AS title, created_at FROM kill_chains
    UNION ALL
    SELECT id::text, 'research_questions' AS cell_type, question AS title, created_at FROM research_questions
    UNION ALL
    SELECT id::text, 'files_discussed' AS cell_type, file_path AS title, created_at FROM files_discussed
    UNION ALL
    SELECT id::text, 'conversations' AS cell_type, topic AS title, created_at FROM conversations
    UNION ALL
    SELECT id::text, 'sessions' AS cell_type, session_name AS title, created_at FROM sessions
    UNION ALL
    SELECT id::text, 'architecture_notes' AS cell_type, component AS title, created_at FROM architecture_notes
    UNION ALL
    SELECT id::text, 'iocs' AS cell_type, value AS title, created_at FROM iocs
    UNION ALL
    SELECT id::text, 'decisions' AS cell_type, decision AS title, created_at FROM decisions
    UNION ALL
    SELECT id::text, 'errors' AS cell_type, message AS title, created_at FROM errors
    UNION ALL
    SELECT id::text, 'interactions' AS cell_type, content AS title, created_at FROM interactions
    ORDER BY created_at DESC
    LIMIT :limit OFFSET :offset
"""


@router.get("", summary="Global chronological timeline across all cells")
async def get_timeline(
    limit: int = Query(50, ge=1, le=200, description="Max items to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return items from all cells ordered by creation time (newest first)."""
    result = await db.execute(
        text(_UNION_SQL), {"limit": limit, "offset": offset}
    )
    rows = result.mappings().all()
    return [
        {
            "id": row["id"],
            "cell_type": row["cell_type"],
            "title": row["title"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }
        for row in rows
    ]
