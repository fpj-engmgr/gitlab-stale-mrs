from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import csv
from io import StringIO
from datetime import datetime
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


@router.get("/api/export-csv")
async def export_stale_mrs_csv(
    stale_days: Optional[int] = None,
    group_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Export stale MRs to CSV file.

    Parameters:
    - stale_days: Number of days to consider an MR stale (default from settings)
    - group_id: Optional filter by group
    """
    try:
        service = StaleService(db, group_id=group_id)
        data = service.get_stale_mrs(stale_days=stale_days)

        # Create CSV in memory
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                'title', 'project_name', 'author', 'days_open',
                'created_at', 'severity', 'web_url'
            ],
            extrasaction='ignore'  # Ignore extra fields like project_id, mr_id, group_id
        )
        writer.writeheader()
        writer.writerows(data['stale_mrs'])
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error exporting CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")

    # Generate filename with timestamp and filters
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    group_suffix = f"_{group_id}" if group_id else "_all_groups"
    filename = f"stale_mrs_{stale_days or data['stale_threshold_days']}d{group_suffix}_{timestamp}.csv"

    # Return as downloadable CSV
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


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
