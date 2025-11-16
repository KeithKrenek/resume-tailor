"""
Version management for resume optimizations.
Tracks iterations and allows rollback.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ResumeVersion:
    """A single version of an optimized resume."""
    version_number: int
    timestamp: datetime
    optimized_resume: Any  # ResumeModel
    metrics: Dict[str, Any]  # MetricsResult as dict
    changes: List[Any]  # List of ResumeChange
    iteration_number: int  # Which iteration produced this
    config: Dict[str, Any]  # Optimization config used
    improvement_summary: List[str] = field(default_factory=list)

    def get_overall_score(self) -> float:
        """Calculate overall quality score from metrics."""
        if not self.metrics:
            return 0.0
        return self.metrics.get('overall_score', 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'version_number': self.version_number,
            'timestamp': self.timestamp.isoformat(),
            'optimized_resume': self.optimized_resume.to_dict() if hasattr(self.optimized_resume, 'to_dict') else str(self.optimized_resume),
            'metrics': self.metrics,
            'changes': [c.to_dict() if hasattr(c, 'to_dict') else str(c) for c in self.changes],
            'iteration_number': self.iteration_number,
            'config': self.config,
            'improvement_summary': self.improvement_summary
        }


class VersionManager:
    """Manages resume optimization versions."""

    def __init__(self, max_versions: int = 10):
        """
        Initialize version manager.

        Args:
            max_versions: Maximum versions to keep in history
        """
        self.max_versions = max_versions
        self.versions: List[ResumeVersion] = []

    def add_version(
        self,
        optimized_resume: Any,
        metrics: Dict[str, Any],
        changes: List[Any],
        iteration_number: int,
        config: Dict[str, Any],
        improvement_summary: Optional[List[str]] = None
    ) -> ResumeVersion:
        """
        Add a new version to history.

        Args:
            optimized_resume: The optimized resume model
            metrics: Metrics for this version (as dict)
            changes: List of changes made
            iteration_number: Which iteration this is
            config: Configuration used
            improvement_summary: Summary of improvements

        Returns:
            The created ResumeVersion
        """
        version = ResumeVersion(
            version_number=len(self.versions) + 1,
            timestamp=datetime.now(),
            optimized_resume=optimized_resume,
            metrics=metrics,
            changes=changes,
            iteration_number=iteration_number,
            config=config,
            improvement_summary=improvement_summary or []
        )

        self.versions.append(version)

        # Trim old versions if over limit
        if len(self.versions) > self.max_versions:
            self.versions = self.versions[-self.max_versions:]
            # Renumber versions
            for i, v in enumerate(self.versions, 1):
                v.version_number = i

        return version

    def get_version(self, version_number: int) -> Optional[ResumeVersion]:
        """Get a specific version by number."""
        for v in self.versions:
            if v.version_number == version_number:
                return v
        return None

    def get_latest_version(self) -> Optional[ResumeVersion]:
        """Get the most recent version."""
        return self.versions[-1] if self.versions else None

    def get_best_version(self) -> Optional[ResumeVersion]:
        """Get the version with highest overall score."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.get_overall_score())

    def get_all_versions(self) -> List[ResumeVersion]:
        """Get all versions in chronological order."""
        return self.versions.copy()

    def compare_versions(self, v1_num: int, v2_num: int) -> Dict[str, Any]:
        """
        Compare two versions.

        Returns:
            Dict with comparison metrics
        """
        v1 = self.get_version(v1_num)
        v2 = self.get_version(v2_num)

        if not v1 or not v2:
            return {}

        # Extract metric scores safely
        def get_metric_score(version, metric_name):
            if not version.metrics:
                return 0.0
            metric = version.metrics.get(metric_name, {})
            if isinstance(metric, dict):
                return metric.get('score', 0.0)
            return 0.0

        return {
            "version_1": v1_num,
            "version_2": v2_num,
            "score_delta": v2.get_overall_score() - v1.get_overall_score(),
            "authenticity_delta": get_metric_score(v2, 'authenticity') - get_metric_score(v1, 'authenticity'),
            "role_alignment_delta": get_metric_score(v2, 'role_alignment') - get_metric_score(v1, 'role_alignment'),
            "ats_delta": get_metric_score(v2, 'ats_optimization') - get_metric_score(v1, 'ats_optimization'),
            "length_delta": get_metric_score(v2, 'length_compliance') - get_metric_score(v1, 'length_compliance'),
            "time_between": (v2.timestamp - v1.timestamp).total_seconds(),
        }

    def get_version_count(self) -> int:
        """Get total number of versions."""
        return len(self.versions)

    def clear_versions(self):
        """Clear all versions from history."""
        self.versions = []

    def get_improvement_trajectory(self) -> List[Dict[str, Any]]:
        """
        Get the trajectory of improvements across iterations.

        Returns:
            List of dicts with iteration number and scores
        """
        trajectory = []
        for v in self.versions:
            trajectory.append({
                'iteration': v.iteration_number,
                'version': v.version_number,
                'overall_score': v.get_overall_score(),
                'timestamp': v.timestamp.isoformat()
            })
        return trajectory
