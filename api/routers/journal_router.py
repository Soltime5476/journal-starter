from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException

from api.config import Settings, get_settings
from api.models.entry import AnalysisResponse, Entry, EntryCreate
from api.repositories.postgres_repository import PostgresDB
from api.services.entry_service import EntryService
from api.services.llm_service import analyze_journal_entry

router = APIRouter()


async def get_entry_service(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[EntryService]:
    async with PostgresDB(settings.database_url) as db:
        yield EntryService(db)


@router.post("/entries", status_code=201)
async def create_entry(
    entry_data: EntryCreate, entry_service: EntryService = Depends(get_entry_service)
):
    """Create a new journal entry."""
    # Create the full entry with auto-generated fields
    entry = Entry(
        work=entry_data.work, struggle=entry_data.struggle, intention=entry_data.intention
    )

    # Store the entry in the database
    created_entry = await entry_service.create_entry(entry.model_dump())

    # Return success response (FastAPI handles datetime serialization automatically)
    return {"detail": "Entry created successfully", "entry": created_entry}


# Implements GET /entries endpoint to list all journal entries
# Example response: [{"id": "123", "work": "...", "struggle": "...", "intention": "..."}]
@router.get("/entries")
async def get_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Get all journal entries."""
    result = await entry_service.get_all_entries()
    return {"entries": result, "count": len(result)}


@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    result = await entry_service.get_entry(entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")

    return result


@router.patch("/entries/{entry_id}")
async def update_entry(
    entry_id: str, entry_update: dict, entry_service: EntryService = Depends(get_entry_service)
):
    """Update a journal entry.

    TODO (Task 3): Replace ``entry_update: dict`` with ``entry_update: EntryUpdate``
    (import it from ``api.models.entry``) so PATCH requests are validated the
    same way POST requests are. Without this, PATCH happily accepts
    empty strings and 300-character bodies — see ``TestUpdateEntry`` in
    tests/test_api.py.
    """
    result = await entry_service.update_entry(entry_id, entry_update)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")

    return result


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    await entry_service.delete_entry(entry_id)
    return {"detail": f"Entry {entry_id} deleted sucessfully"}


@router.delete("/entries")
async def delete_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Delete all journal entries"""
    await entry_service.delete_all_entries()
    return {"detail": "All entries deleted"}


@router.post("/entries/{entry_id}/analyze", response_model=AnalysisResponse)
async def analyze_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """
    Analyze a journal entry using AI.

    Returns sentiment, summary, key topics, entry_id, and created_at timestamp.

    Response format:
    {
        "entry_id": "string",
        "sentiment": "positive | negative | neutral",
        "summary": "2 sentence summary of the entry",
        "topics": ["topic1", "topic2", "topic3"],
        "created_at": "timestamp"
    }
    """
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    entry_text = "\n".join(entry.get(field, "") for field in ["work", "struggle, intention"])

    try:
        analysis = await analyze_journal_entry(entry_id, entry_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}") from None

    return analysis
