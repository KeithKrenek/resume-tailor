"""
Metrics Service
Orchestrates all metric calculations for resume optimization quality evaluation.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from modules.metrics import (
    MetricScore,
    AuthenticityScorer,
    RoleAlignmentScorer,
    ATSScorer,
    LengthScorer
)


@dataclass
class MetricsResult:
    """Comprehensive metrics result for resume optimization."""
    authenticity: MetricScore
    role_alignment: MetricScore
    ats_optimization: MetricScore
    length_compliance: MetricScore
    overall_passed: bool
    overall_score: float
    failed_metrics: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'authenticity': self.authenticity.to_dict(),
            'role_alignment': self.role_alignment.to_dict(),
            'ats_optimization': self.ats_optimization.to_dict(),
            'length_compliance': self.length_compliance.to_dict(),
            'overall_passed': self.overall_passed,
            'overall_score': self.overall_score,
            'failed_metrics': self.failed_metrics,
            'recommendations': self.recommendations
        }


class MetricsService:
    """
    Service for calculating comprehensive resume optimization metrics.

    Evaluates:
    - Authenticity: Truthfulness of claims
    - Role Alignment: Match with job description
    - ATS Optimization: Applicant Tracking System compatibility
    - Length Compliance: Fits within target page count
    """

    def __init__(
        self,
        authenticity_threshold: float = 0.90,
        role_alignment_threshold: float = 0.85,
        ats_threshold: float = 0.80,
        length_threshold: float = 0.95,
        target_pages: int = 2
    ):
        """
        Initialize Metrics Service.

        Args:
            authenticity_threshold: Minimum authenticity score (default: 0.90)
            role_alignment_threshold: Minimum role alignment score (default: 0.85)
            ats_threshold: Minimum ATS optimization score (default: 0.80)
            length_threshold: Minimum length compliance score (default: 0.95)
            target_pages: Target page count for resume (default: 2)
        """
        self.authenticity_scorer = AuthenticityScorer(threshold=authenticity_threshold)
        self.role_alignment_scorer = RoleAlignmentScorer(threshold=role_alignment_threshold)
        self.ats_scorer = ATSScorer(threshold=ats_threshold)
        self.length_scorer = LengthScorer(target_pages=target_pages, threshold=length_threshold)

    def calculate_all_metrics(
        self,
        original_resume: str,
        optimized_resume: str,
        job_description: str
    ) -> MetricsResult:
        """
        Calculate all metrics for resume optimization.

        Args:
            original_resume: Original resume text
            optimized_resume: Optimized resume text
            job_description: Job description text

        Returns:
            MetricsResult with comprehensive scoring
        """
        # Calculate individual metrics
        authenticity = self.authenticity_scorer.calculate(
            original_resume, optimized_resume, job_description
        )
        role_alignment = self.role_alignment_scorer.calculate(
            original_resume, optimized_resume, job_description
        )
        ats_optimization = self.ats_scorer.calculate(
            original_resume, optimized_resume, job_description
        )
        length_compliance = self.length_scorer.calculate(
            original_resume, optimized_resume, job_description
        )

        # Calculate overall metrics
        all_metrics = [authenticity, role_alignment, ats_optimization, length_compliance]

        # Check which metrics failed
        failed_metrics = [m.name for m in all_metrics if not m.passed]

        # Calculate overall score (weighted average)
        # Weights: Authenticity (35%), Role Alignment (30%), ATS (25%), Length (10%)
        overall_score = (
            authenticity.score * 0.35 +
            role_alignment.score * 0.30 +
            ats_optimization.score * 0.25 +
            length_compliance.score * 0.10
        )

        # Overall pass/fail: all critical metrics must pass
        # Critical: Authenticity, Role Alignment
        # Important: ATS Optimization
        # Nice-to-have: Length Compliance
        critical_passed = authenticity.passed and role_alignment.passed
        important_passed = ats_optimization.passed
        overall_passed = critical_passed and important_passed

        # Aggregate recommendations (prioritize by metric weight)
        recommendations = []

        # Add critical metric recommendations first
        if not authenticity.passed:
            recommendations.append(f"🔴 CRITICAL - Authenticity: {authenticity.score:.2f} (threshold: {authenticity.threshold})")
            recommendations.extend(authenticity.recommendations)

        if not role_alignment.passed:
            recommendations.append(f"🔴 CRITICAL - Role Alignment: {role_alignment.score:.2f} (threshold: {role_alignment.threshold})")
            recommendations.extend(role_alignment.recommendations)

        # Add important metric recommendations
        if not ats_optimization.passed:
            recommendations.append(f"🟡 IMPORTANT - ATS Optimization: {ats_optimization.score:.2f} (threshold: {ats_optimization.threshold})")
            recommendations.extend(ats_optimization.recommendations)

        # Add nice-to-have recommendations
        if not length_compliance.passed:
            recommendations.append(f"🟢 MINOR - Length Compliance: {length_compliance.score:.2f} (threshold: {length_compliance.threshold})")
            recommendations.extend(length_compliance.recommendations)

        # If all passed, add success message
        if overall_passed:
            recommendations.append("✅ All critical metrics passed! Resume optimization meets quality standards.")

        return MetricsResult(
            authenticity=authenticity,
            role_alignment=role_alignment,
            ats_optimization=ats_optimization,
            length_compliance=length_compliance,
            overall_passed=overall_passed,
            overall_score=overall_score,
            failed_metrics=failed_metrics,
            recommendations=recommendations
        )

    def get_metric_summary(self, metrics: MetricsResult) -> str:
        """
        Generate human-readable summary of metrics.

        Args:
            metrics: MetricsResult to summarize

        Returns:
            Formatted summary string
        """
        summary = []
        summary.append("=" * 60)
        summary.append("RESUME OPTIMIZATION METRICS REPORT")
        summary.append("=" * 60)
        summary.append("")

        # Overall status
        status_emoji = "✅" if metrics.overall_passed else "❌"
        summary.append(f"{status_emoji} Overall Status: {'PASSED' if metrics.overall_passed else 'NEEDS IMPROVEMENT'}")
        summary.append(f"Overall Score: {metrics.overall_score:.2%}")
        summary.append("")

        # Individual metrics
        summary.append("Individual Metrics:")
        summary.append("-" * 60)

        for metric in [metrics.authenticity, metrics.role_alignment,
                       metrics.ats_optimization, metrics.length_compliance]:
            status = "✅ PASS" if metric.passed else "❌ FAIL"
            summary.append(f"{metric.name:20} {metric.score:.2%}  {status}  (threshold: {metric.threshold:.2%})")

        summary.append("")

        # Failed metrics
        if metrics.failed_metrics:
            summary.append("⚠️  Failed Metrics:")
            for metric_name in metrics.failed_metrics:
                summary.append(f"   - {metric_name}")
            summary.append("")

        # Recommendations
        if metrics.recommendations:
            summary.append("📋 Recommendations:")
            for i, rec in enumerate(metrics.recommendations[:10], 1):  # Top 10
                summary.append(f"   {i}. {rec}")

        summary.append("")
        summary.append("=" * 60)

        return "\n".join(summary)
