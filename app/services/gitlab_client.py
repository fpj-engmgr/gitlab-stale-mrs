import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import gitlab
from app.config import settings

logger = logging.getLogger(__name__)


class GitLabClient:
    """Simplified GitLab client focused on fetching open MRs."""

    def __init__(self, group_path: str = None, group_id: str = None):
        self.gl = gitlab.Gitlab(settings.gitlab_url, private_token=settings.gitlab_token)
        self.group_path = group_path or settings.gitlab_group
        self.group_id = group_id or "default"

    def get_open_merge_requests(self) -> List[Dict[str, Any]]:
        """Fetch all currently open MRs from the group/projects."""
        logger.info(f"Fetching open MRs for group: {self.group_path}")

        try:
            # Try to get as a group first
            try:
                group = self.gl.groups.get(self.group_path)
                source_type = "group"
                source = group
            except gitlab.exceptions.GitlabGetError:
                # If not a group, try as a project
                project = self.gl.projects.get(self.group_path)
                source_type = "project"
                source = project

            # Fetch all open MRs
            mrs = []
            if source_type == "group":
                # Get all open MRs from the group
                group_mrs = source.mergerequests.list(
                    state='opened',
                    get_all=True,
                    per_page=100
                )
                mrs.extend(group_mrs)
            else:
                # Get MRs from single project
                project_mrs = source.mergerequests.list(
                    state='opened',
                    get_all=True,
                    per_page=100
                )
                mrs.extend(project_mrs)

            logger.info(f"Found {len(mrs)} open MRs in {self.group_path}")

            # Convert to our format
            result = []
            for mr in mrs:
                # Get project info
                try:
                    if source_type == "group":
                        project = self.gl.projects.get(mr.project_id)
                        project_name = project.name
                    else:
                        project_name = source.name
                except Exception as e:
                    logger.warning(f"Could not get project for MR {mr.iid}: {e}")
                    project_name = f"Project {mr.project_id}"

                mr_data = {
                    'group_id': self.group_id,
                    'mr_id': mr.iid,
                    'project_id': mr.project_id,
                    'project_name': project_name,
                    'title': mr.title,
                    'author': mr.author.get('name', mr.author.get('username', 'Unknown')),
                    'state': mr.state,
                    'web_url': mr.web_url,
                    'created_at': datetime.fromisoformat(mr.created_at.replace('Z', '+00:00')),
                    'updated_at': datetime.fromisoformat(mr.updated_at.replace('Z', '+00:00')) if mr.updated_at else None,
                    'merged_at': None,
                    'closed_at': None
                }
                result.append(mr_data)

            return result

        except Exception as e:
            logger.error(f"Error fetching MRs from {self.group_path}: {e}")
            raise
