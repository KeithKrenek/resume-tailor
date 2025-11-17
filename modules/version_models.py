"""Data models for resume version management."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
import json

from modules.models import ResumeOptimizationResult, ResumeModel


@dataclass
class VersionMetadata:
    """Metadata about a resume version."""
    version_id: str
    version_number: int
    timestamp: str  # ISO format
    job_title: str
    company_name: str
    optimization_style: str  # "conservative", "balanced", "aggressive"
    optimization_tier: str  # "basic", "standard", "premium"
    total_changes: int
    accepted_changes: int
    rejected_changes: int
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_submitted: bool = False  # Track if this version was submitted
    submitted_date: Optional[str] = None  # When it was submitted
    response_received: Optional[bool] = None  # Did you get a response?

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'version_id': self.version_id,
            'version_number': self.version_number,
            'timestamp': self.timestamp,
            'job_title': self.job_title,
            'company_name': self.company_name,
            'optimization_style': self.optimization_style,
            'optimization_tier': self.optimization_tier,
            'total_changes': self.total_changes,
            'accepted_changes': self.accepted_changes,
            'rejected_changes': self.rejected_changes,
            'notes': self.notes,
            'tags': self.tags,
            'is_submitted': self.is_submitted,
            'submitted_date': self.submitted_date,
            'response_received': self.response_received
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionMetadata':
        """Create from dictionary."""
        return cls(
            version_id=data['version_id'],
            version_number=data['version_number'],
            timestamp=data['timestamp'],
            job_title=data['job_title'],
            company_name=data['company_name'],
            optimization_style=data['optimization_style'],
            optimization_tier=data['optimization_tier'],
            total_changes=data['total_changes'],
            accepted_changes=data['accepted_changes'],
            rejected_changes=data['rejected_changes'],
            notes=data.get('notes'),
            tags=data.get('tags', []),
            is_submitted=data.get('is_submitted', False),
            submitted_date=data.get('submitted_date'),
            response_received=data.get('response_received')
        )

    def get_display_name(self) -> str:
        """Get human-readable display name."""
        dt = datetime.fromisoformat(self.timestamp)
        date_str = dt.strftime("%Y-%m-%d %H:%M")
        return f"v{self.version_number} - {self.company_name} - {self.job_title} ({date_str})"

    def get_short_name(self) -> str:
        """Get short display name."""
        return f"v{self.version_number} - {self.company_name}"


@dataclass
class ResumeVersion:
    """A saved version of an optimized resume."""
    metadata: VersionMetadata
    optimization_result: ResumeOptimizationResult
    final_resume: ResumeModel  # The resume after applying accepted changes
    job_description: str
    original_resume_text: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metadata': self.metadata.to_dict(),
            'optimization_result': self.optimization_result.to_dict(),
            'final_resume': self.final_resume.to_dict(),
            'job_description': self.job_description,
            'original_resume_text': self.original_resume_text
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResumeVersion':
        """Create from dictionary."""
        return cls(
            metadata=VersionMetadata.from_dict(data['metadata']),
            optimization_result=ResumeOptimizationResult.from_dict(data['optimization_result']),
            final_resume=ResumeModel.from_dict(data['final_resume']),
            job_description=data['job_description'],
            original_resume_text=data['original_resume_text']
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'ResumeVersion':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of metrics for this version."""
        metrics = self.optimization_result.metrics or {}
        stats = self.optimization_result.get_change_stats()

        return {
            'overall_score': metrics.get('overall_score', 0.0),
            'overall_passed': metrics.get('overall_passed', False),
            'total_changes': stats['total'],
            'accepted_changes': stats['accepted'],
            'rejected_changes': stats['rejected'],
            'authenticity_score': metrics.get('authenticity', {}).get('score', 0.0) if isinstance(metrics.get('authenticity'), dict) else 0.0,
            'role_alignment_score': metrics.get('role_alignment', {}).get('score', 0.0) if isinstance(metrics.get('role_alignment'), dict) else 0.0,
            'ats_score': metrics.get('ats_optimization', {}).get('score', 0.0) if isinstance(metrics.get('ats_optimization'), dict) else 0.0
        }


@dataclass
class VersionComparison:
    """Comparison between two resume versions."""
    version_a: ResumeVersion
    version_b: ResumeVersion

    def get_metrics_delta(self) -> Dict[str, float]:
        """Get difference in metrics between versions."""
        metrics_a = self.version_a.get_metrics_summary()
        metrics_b = self.version_b.get_metrics_summary()

        return {
            'overall_score': metrics_b['overall_score'] - metrics_a['overall_score'],
            'authenticity_score': metrics_b['authenticity_score'] - metrics_a['authenticity_score'],
            'role_alignment_score': metrics_b['role_alignment_score'] - metrics_a['role_alignment_score'],
            'ats_score': metrics_b['ats_score'] - metrics_a['ats_score'],
            'total_changes': metrics_b['total_changes'] - metrics_a['total_changes'],
            'accepted_changes': metrics_b['accepted_changes'] - metrics_a['accepted_changes']
        }

    def get_text_diff(self) -> Dict[str, Tuple[str, str]]:
        """Get text differences between versions."""
        return {
            'summary': (
                self.version_a.final_resume.summary or "",
                self.version_b.final_resume.summary or ""
            ),
            'headline': (
                self.version_a.final_resume.headline or "",
                self.version_b.final_resume.headline or ""
            ),
            'skills': (
                ", ".join(self.version_a.final_resume.skills),
                ", ".join(self.version_b.final_resume.skills)
            )
        }
