import os
import json
from pathlib import Path
from typing import List, Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str
    gitlab_group: str = ""
    database_url: str = "sqlite:///./stale_mrs.db"
    cache_duration_hours: int = 1  # Shorter cache for stale MR tracking
    stale_mr_days: int = 7  # Default threshold for stale MRs
    groups_file: str = "groups.json"
    port: int = 8001  # Default port (different from main dashboard's 8000)

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_groups(self) -> List[Dict[str, Any]]:
        """Load groups from groups.json or fall back to single group."""
        groups_file = Path(self.groups_file)

        if not groups_file.exists():
            # Backward compatibility: single-group mode
            if not self.gitlab_group:
                raise ValueError("Either groups.json must exist or GITLAB_GROUP must be set")
            return [{
                "id": "default",
                "name": self.gitlab_group.split('/')[-1].title(),
                "path": self.gitlab_group,
                "type": "group",
                "enabled": True
            }]

        with open(groups_file, 'r') as f:
            data = json.load(f)
            groups = data.get('groups', [])

            # Validate required fields
            for group in groups:
                if not all(k in group for k in ['id', 'name', 'path']):
                    raise ValueError(f"Group missing required fields: {group}")

            return [g for g in groups if g.get('enabled', True)]


settings = Settings()
