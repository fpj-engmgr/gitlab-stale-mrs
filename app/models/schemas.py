from sqlalchemy import Column, Integer, String, DateTime, Index
from app.models.database import Base


class MergeRequest(Base):
    """Simplified MR model - only what we need for stale tracking."""
    __tablename__ = "merge_requests"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(String, index=True, nullable=True)
    mr_id = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=False)
    project_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    state = Column(String, nullable=False)
    web_url = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    merged_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_group_state', 'group_id', 'state'),
        Index('idx_state_created', 'state', 'created_at'),
    )


class CacheMetadata(Base):
    """Track when data was last refreshed."""
    __tablename__ = "cache_metadata"

    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String, unique=True, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    group_id = Column(String, nullable=True, index=True)
