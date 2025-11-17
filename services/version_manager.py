"""Service for managing resume version history."""

import os
import json
import uuid
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from modules.version_models import ResumeVersion, VersionMetadata, VersionComparison
from modules.models import ResumeOptimizationResult, ResumeModel
from utils.logging_config import get_logger

logger = get_logger(__name__)


class VersionManager:
    """Manages resume version storage and retrieval."""

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize version manager.

        Args:
            storage_path: Path to store versions (defaults to ~/resume_tailor_versions)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / "resume_tailor_versions"

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Metadata index file
        self.index_file = self.storage_path / "versions_index.json"

        # Initialize index if it doesn't exist
        if not self.index_file.exists():
            self._save_index({})

    def _load_index(self) -> Dict[str, Any]:
        """Load the versions index."""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return {}

    def _save_index(self, index: Dict[str, Any]) -> None:
        """Save the versions index."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def _get_next_version_number(self) -> int:
        """Get the next version number."""
        index = self._load_index()
        if not index or 'versions' not in index:
            return 1

        versions = index['versions']
        if not versions:
            return 1

        max_version = max(v['version_number'] for v in versions.values())
        return max_version + 1

    def save_version(
        self,
        optimization_result: ResumeOptimizationResult,
        final_resume: ResumeModel,
        job_title: str,
        company_name: str,
        job_description: str,
        original_resume_text: str,
        optimization_style: str = "balanced",
        optimization_tier: str = "standard",
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Save a resume version.

        Args:
            optimization_result: The optimization result
            final_resume: The final resume after applying changes
            job_title: Job title
            company_name: Company name
            job_description: Original job description
            original_resume_text: Original resume text
            optimization_style: Style used for optimization
            optimization_tier: Tier used for optimization
            notes: Optional user notes
            tags: Optional tags

        Returns:
            Tuple of (success, version_id, message)
        """
        try:
            # Generate version ID
            version_id = str(uuid.uuid4())

            # Get version number
            version_number = self._get_next_version_number()

            # Get change statistics
            stats = optimization_result.get_change_stats()

            # Create metadata
            metadata = VersionMetadata(
                version_id=version_id,
                version_number=version_number,
                timestamp=datetime.now().isoformat(),
                job_title=job_title,
                company_name=company_name,
                optimization_style=optimization_style,
                optimization_tier=optimization_tier,
                total_changes=stats['total'],
                accepted_changes=stats['accepted'],
                rejected_changes=stats['rejected'],
                notes=notes,
                tags=tags or []
            )

            # Create version
            version = ResumeVersion(
                metadata=metadata,
                optimization_result=optimization_result,
                final_resume=final_resume,
                job_description=job_description,
                original_resume_text=original_resume_text
            )

            # Save version to file
            version_file = self.storage_path / f"{version_id}.json"
            with open(version_file, 'w') as f:
                f.write(version.to_json())

            # Update index
            index = self._load_index()
            if 'versions' not in index:
                index['versions'] = {}

            index['versions'][version_id] = metadata.to_dict()
            index['last_updated'] = datetime.now().isoformat()
            self._save_index(index)

            logger.info(f"Saved version {version_number} ({version_id})")
            return True, version_id, f"Version {version_number} saved successfully"

        except Exception as e:
            logger.error(f"Failed to save version: {e}", exc_info=True)
            return False, None, f"Failed to save version: {str(e)}"

    def load_version(self, version_id: str) -> Optional[ResumeVersion]:
        """
        Load a specific version.

        Args:
            version_id: Version ID to load

        Returns:
            ResumeVersion or None if not found
        """
        try:
            version_file = self.storage_path / f"{version_id}.json"

            if not version_file.exists():
                logger.warning(f"Version file not found: {version_id}")
                return None

            with open(version_file, 'r') as f:
                json_str = f.read()

            version = ResumeVersion.from_json(json_str)
            logger.info(f"Loaded version {version.metadata.version_number}")
            return version

        except Exception as e:
            logger.error(f"Failed to load version {version_id}: {e}", exc_info=True)
            return None

    def list_versions(
        self,
        company_filter: Optional[str] = None,
        tag_filter: Optional[str] = None,
        submitted_only: bool = False
    ) -> List[VersionMetadata]:
        """
        List all saved versions.

        Args:
            company_filter: Filter by company name (case-insensitive)
            tag_filter: Filter by tag
            submitted_only: Only show submitted versions

        Returns:
            List of VersionMetadata sorted by timestamp (newest first)
        """
        try:
            index = self._load_index()

            if 'versions' not in index or not index['versions']:
                return []

            versions = [
                VersionMetadata.from_dict(v)
                for v in index['versions'].values()
            ]

            # Apply filters
            if company_filter:
                company_lower = company_filter.lower()
                versions = [
                    v for v in versions
                    if company_lower in v.company_name.lower()
                ]

            if tag_filter:
                versions = [
                    v for v in versions
                    if tag_filter in v.tags
                ]

            if submitted_only:
                versions = [
                    v for v in versions
                    if v.is_submitted
                ]

            # Sort by timestamp (newest first)
            versions.sort(key=lambda v: v.timestamp, reverse=True)

            return versions

        except Exception as e:
            logger.error(f"Failed to list versions: {e}", exc_info=True)
            return []

    def delete_version(self, version_id: str) -> Tuple[bool, str]:
        """
        Delete a version.

        Args:
            version_id: Version ID to delete

        Returns:
            Tuple of (success, message)
        """
        try:
            # Delete version file
            version_file = self.storage_path / f"{version_id}.json"

            if not version_file.exists():
                return False, f"Version {version_id} not found"

            version_file.unlink()

            # Update index
            index = self._load_index()
            if 'versions' in index and version_id in index['versions']:
                version_num = index['versions'][version_id]['version_number']
                del index['versions'][version_id]
                index['last_updated'] = datetime.now().isoformat()
                self._save_index(index)

                logger.info(f"Deleted version {version_num} ({version_id})")
                return True, f"Version {version_num} deleted successfully"
            else:
                return False, "Version not found in index"

        except Exception as e:
            logger.error(f"Failed to delete version {version_id}: {e}", exc_info=True)
            return False, f"Failed to delete version: {str(e)}"

    def update_version_metadata(
        self,
        version_id: str,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_submitted: Optional[bool] = None,
        submitted_date: Optional[str] = None,
        response_received: Optional[bool] = None
    ) -> Tuple[bool, str]:
        """
        Update version metadata.

        Args:
            version_id: Version ID to update
            notes: Updated notes
            tags: Updated tags
            is_submitted: Whether version was submitted
            submitted_date: Date submitted
            response_received: Whether response was received

        Returns:
            Tuple of (success, message)
        """
        try:
            # Load version
            version = self.load_version(version_id)
            if not version:
                return False, "Version not found"

            # Update metadata
            if notes is not None:
                version.metadata.notes = notes
            if tags is not None:
                version.metadata.tags = tags
            if is_submitted is not None:
                version.metadata.is_submitted = is_submitted
            if submitted_date is not None:
                version.metadata.submitted_date = submitted_date
            if response_received is not None:
                version.metadata.response_received = response_received

            # Save updated version
            version_file = self.storage_path / f"{version_id}.json"
            with open(version_file, 'w') as f:
                f.write(version.to_json())

            # Update index
            index = self._load_index()
            if 'versions' in index and version_id in index['versions']:
                index['versions'][version_id] = version.metadata.to_dict()
                index['last_updated'] = datetime.now().isoformat()
                self._save_index(index)

            logger.info(f"Updated metadata for version {version.metadata.version_number}")
            return True, "Metadata updated successfully"

        except Exception as e:
            logger.error(f"Failed to update metadata: {e}", exc_info=True)
            return False, f"Failed to update metadata: {str(e)}"

    def compare_versions(
        self,
        version_a_id: str,
        version_b_id: str
    ) -> Optional[VersionComparison]:
        """
        Compare two versions.

        Args:
            version_a_id: First version ID
            version_b_id: Second version ID

        Returns:
            VersionComparison or None if versions not found
        """
        try:
            version_a = self.load_version(version_a_id)
            version_b = self.load_version(version_b_id)

            if not version_a or not version_b:
                logger.warning("One or both versions not found for comparison")
                return None

            return VersionComparison(version_a=version_a, version_b=version_b)

        except Exception as e:
            logger.error(f"Failed to compare versions: {e}", exc_info=True)
            return None

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        try:
            index = self._load_index()
            versions = index.get('versions', {})

            total_size = 0
            for version_id in versions.keys():
                version_file = self.storage_path / f"{version_id}.json"
                if version_file.exists():
                    total_size += version_file.stat().st_size

            return {
                'total_versions': len(versions),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'storage_path': str(self.storage_path),
                'last_updated': index.get('last_updated', 'Never')
            }

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}
