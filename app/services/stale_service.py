import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.schemas import MergeRequest, CacheMetadata
from app.services.gitlab_client import GitLabClient
from app.config import settings

logger = logging.getLogger(__name__)


class StaleService:
    """Service for tracking and reporting stale MRs."""

    def __init__(self, db: Session, group_id: Optional[str] = None):
        self.db = db
        self.group_id = group_id

    def should_refresh_cache(self) -> bool:
        """Check if cache needs refreshing."""
        cache_key = f"merge_requests_{self.group_id or 'all'}"
        metadata = self.db.query(CacheMetadata).filter(
            CacheMetadata.data_type == cache_key
        ).first()

        if not metadata:
            return True

        cache_age = datetime.utcnow() - metadata.last_updated
        max_age = timedelta(hours=settings.cache_duration_hours)
        return cache_age > max_age

    def refresh_merge_requests(self):
        """Refresh MR data from GitLab."""
        logger.info("Refreshing merge request data from GitLab")

        groups = settings.get_groups()

        # Clear existing data
        if self.group_id:
            self.db.query(MergeRequest).filter(
                MergeRequest.group_id == self.group_id
            ).delete()
        else:
            self.db.query(MergeRequest).delete()

        # Fetch from each group
        for group_config in groups:
            if not group_config.get('enabled', True):
                continue

            try:
                client = GitLabClient(
                    group_path=group_config['path'],
                    group_id=group_config['id']
                )
                mrs = client.get_open_merge_requests()

                # Save to database
                for mr_data in mrs:
                    mr = MergeRequest(**mr_data)
                    self.db.add(mr)

                logger.info(f"Saved {len(mrs)} MRs from {group_config['name']}")

            except Exception as e:
                logger.error(f"Error fetching MRs from {group_config['name']}: {e}")

        # Update cache metadata
        cache_key = f"merge_requests_{self.group_id or 'all'}"
        metadata = self.db.query(CacheMetadata).filter(
            CacheMetadata.data_type == cache_key
        ).first()

        if metadata:
            metadata.last_updated = datetime.utcnow()
        else:
            metadata = CacheMetadata(
                data_type=cache_key,
                last_updated=datetime.utcnow(),
                group_id=self.group_id
            )
            self.db.add(metadata)

        self.db.commit()
        logger.info("Merge request refresh complete")

    def get_stale_mrs(self, stale_days: int = None) -> Dict[str, Any]:
        """Get all stale MRs with configurable threshold."""
        if stale_days is None:
            stale_days = settings.stale_mr_days

        # Refresh if needed
        if self.should_refresh_cache():
            self.refresh_merge_requests()

        # Build query
        query = self.db.query(MergeRequest).filter(
            MergeRequest.state == "opened"
        )

        if self.group_id:
            query = query.filter(MergeRequest.group_id == self.group_id)

        all_open_mrs = query.all()

        # Calculate stale threshold
        stale_threshold = datetime.utcnow() - timedelta(days=stale_days)

        # Filter stale MRs
        stale_mrs = [
            mr for mr in all_open_mrs
            if mr.created_at < stale_threshold
        ]

        # Sort by oldest first (most urgent)
        stale_mrs.sort(key=lambda x: x.created_at)

        # Calculate days open for each
        result = []
        for mr in stale_mrs:
            days_open = (datetime.utcnow() - mr.created_at).days

            # Determine severity
            if days_open <= 14:
                severity = "moderate"
            elif days_open <= 30:
                severity = "high"
            else:
                severity = "critical"

            result.append({
                'mr_id': mr.mr_id,
                'project_id': mr.project_id,
                'project_name': mr.project_name,
                'title': mr.title,
                'author': mr.author,
                'web_url': mr.web_url,
                'created_at': mr.created_at.isoformat(),
                'days_open': days_open,
                'severity': severity,
                'group_id': mr.group_id
            })

        # Get last refresh time
        cache_key = f"merge_requests_{self.group_id or 'all'}"
        metadata = self.db.query(CacheMetadata).filter(
            CacheMetadata.data_type == cache_key
        ).first()

        return {
            'total_open': len(all_open_mrs),
            'stale_count': len(stale_mrs),
            'stale_threshold_days': stale_days,
            'stale_mrs': result,
            'last_updated': metadata.last_updated.isoformat() if metadata else None
        }

    def get_groups(self) -> List[Dict[str, Any]]:
        """Get list of configured groups."""
        groups = settings.get_groups()
        return [{
            'id': g['id'],
            'name': g['name'],
            'path': g['path']
        } for g in groups if g.get('enabled', True)]
