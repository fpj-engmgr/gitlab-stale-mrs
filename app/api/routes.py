from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.models.database import get_db
from app.services.stale_service import StaleService

router = APIRouter()


@router.get("/api/groups")
async def get_groups(db: Session = Depends(get_db)):
    """Get list of configured groups."""
    service = StaleService(db)
    groups = service.get_groups()
    return {
        "groups": groups,
        "mode": "multi" if len(groups) > 1 else "single"
    }


@router.get("/api/stale-mrs")
async def get_stale_mrs(
    stale_days: Optional[int] = None,
    group_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all stale merge requests.

    Parameters:
    - stale_days: Number of days to consider an MR stale (default from settings)
    - group_id: Optional filter by group
    """
    service = StaleService(db, group_id=group_id)
    return service.get_stale_mrs(stale_days=stale_days)


@router.post("/api/refresh")
async def refresh_data(db: Session = Depends(get_db)):
    """Force refresh of MR data from GitLab."""
    service = StaleService(db)
    service.refresh_merge_requests()
    return {"status": "success", "message": "Data refreshed successfully"}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
