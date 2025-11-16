"""
Optimization configuration with tier-based settings.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class OptimizationConfig:
    """Configuration for resume optimization process."""

    # Iteration settings
    max_iterations: int = 3
    convergence_threshold: float = 0.85  # Stop if all critical metrics pass
    improvement_threshold: float = 0.02  # Stop if improvement < 2%

    # Feature flags
    enable_company_research: bool = False
    enable_voice_preservation: bool = False
    track_unused_content: bool = False
    enable_version_history: bool = True

    # Metrics to track
    metrics_to_calculate: List[str] = field(default_factory=lambda: ["authenticity", "role_alignment", "ats", "length"])

    # Output settings
    output_formats: List[str] = field(default_factory=lambda: ["pdf", "docx", "html", "md"])

    # Performance
    estimated_time_seconds: Optional[int] = None
    estimated_cost_usd: Optional[float] = None

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'max_iterations': self.max_iterations,
            'convergence_threshold': self.convergence_threshold,
            'improvement_threshold': self.improvement_threshold,
            'enable_company_research': self.enable_company_research,
            'enable_voice_preservation': self.enable_voice_preservation,
            'track_unused_content': self.track_unused_content,
            'enable_version_history': self.enable_version_history,
            'metrics_to_calculate': self.metrics_to_calculate,
            'output_formats': self.output_formats,
            'estimated_time_seconds': self.estimated_time_seconds,
            'estimated_cost_usd': self.estimated_cost_usd
        }


class OptimizationTier:
    """Predefined optimization tier configurations."""

    BASIC = OptimizationConfig(
        max_iterations=1,
        convergence_threshold=0.80,
        enable_company_research=False,
        enable_voice_preservation=False,
        track_unused_content=False,
        enable_version_history=False,
        metrics_to_calculate=["authenticity", "role_alignment", "length"],
        output_formats=["pdf"],
        estimated_time_seconds=120,
        estimated_cost_usd=0.50
    )

    STANDARD = OptimizationConfig(
        max_iterations=3,
        convergence_threshold=0.85,
        enable_company_research=False,
        enable_voice_preservation=False,
        track_unused_content=False,
        enable_version_history=True,
        metrics_to_calculate=["authenticity", "role_alignment", "ats", "length"],
        output_formats=["pdf", "docx"],
        estimated_time_seconds=480,
        estimated_cost_usd=2.00
    )

    PREMIUM = OptimizationConfig(
        max_iterations=5,
        convergence_threshold=0.90,
        enable_company_research=True,
        enable_voice_preservation=False,  # Not implemented yet
        track_unused_content=True,
        enable_version_history=True,
        metrics_to_calculate=["authenticity", "role_alignment", "ats", "length"],
        output_formats=["pdf", "docx", "html", "md"],
        estimated_time_seconds=1200,
        estimated_cost_usd=5.00
    )

    @staticmethod
    def get_tier(tier_name: str) -> OptimizationConfig:
        """Get configuration for a tier by name."""
        tier_map = {
            "basic": OptimizationTier.BASIC,
            "standard": OptimizationTier.STANDARD,
            "premium": OptimizationTier.PREMIUM
        }
        return tier_map.get(tier_name.lower(), OptimizationTier.STANDARD)

    @staticmethod
    def get_all_tiers() -> dict:
        """Get all available tiers."""
        return {
            "basic": OptimizationTier.BASIC,
            "standard": OptimizationTier.STANDARD,
            "premium": OptimizationTier.PREMIUM
        }
