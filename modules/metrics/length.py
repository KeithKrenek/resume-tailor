"""
Length Compliance Metric
Ensures resume fits within target page count.
"""

import re
from .base import MetricCalculator, MetricScore


class LengthScorer(MetricCalculator):
    """Calculates length compliance score based on page count estimation."""

    def __init__(self, target_pages: int = 2, threshold: float = 0.95):
        """
        Initialize Length Scorer.

        Args:
            target_pages: Target number of pages (default: 2)
            threshold: Minimum acceptable score (default: 0.95)
        """
        self.target_pages = target_pages
        self.threshold = threshold

    def calculate(self, original_resume: str, optimized_resume: str, job_description: str) -> MetricScore:
        """Calculate length compliance score."""

        # Estimate page count
        estimated_pages = self._estimate_pages(optimized_resume)

        # Calculate compliance score
        if estimated_pages <= self.target_pages:
            # Perfect score if within target
            score = 1.0
        elif estimated_pages <= self.target_pages + 0.2:
            # Small overage (within 20% of a page) - minor penalty
            overage = estimated_pages - self.target_pages
            score = 1.0 - (overage * 0.5)  # -0.5 per 0.1 page over
        else:
            # Larger overage - steeper penalty
            overage = estimated_pages - self.target_pages
            score = max(0.0, 1.0 - (overage * 0.3))

        # Generate recommendations
        recommendations = []
        if score < self.threshold:
            if estimated_pages > self.target_pages:
                excess = estimated_pages - self.target_pages
                recommendations.append(
                    f"Resume is approximately {excess:.1f} pages too long. "
                    f"Target: {self.target_pages} pages, Current: {estimated_pages:.1f} pages"
                )
                recommendations.append(
                    "Consider: removing older/less relevant experience, "
                    "condensing bullet points, or removing redundant skills"
                )
            else:
                recommendations.append(
                    f"Resume is too short ({estimated_pages:.1f} pages). "
                    f"Consider expanding key achievements and skills"
                )

        return MetricScore(
            name="Length Compliance",
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            details={
                "target_pages": self.target_pages,
                "estimated_pages": round(estimated_pages, 2),
                "total_characters": len(optimized_resume),
                "total_words": self._count_words(optimized_resume),
                "total_lines": len(optimized_resume.split('\n')),
                "compliance_status": "Within target" if estimated_pages <= self.target_pages else f"Exceeds by {estimated_pages - self.target_pages:.1f} pages"
            },
            recommendations=recommendations
        )

    def get_threshold(self) -> float:
        return self.threshold

    def _estimate_pages(self, resume: str) -> float:
        """
        Estimate number of pages for the resume.

        Uses a hybrid approach:
        - Character count (typical page: ~3000 characters)
        - Line count (typical page: ~45-50 lines)
        - Word count (typical page: ~500 words)

        Returns weighted average.
        """
        char_count = len(resume)
        word_count = self._count_words(resume)
        line_count = len(resume.split('\n'))

        # Estimation formulas
        # Standard page: ~3000 chars, ~500 words, ~45 lines (single-spaced with spacing)
        pages_by_chars = char_count / 3000.0
        pages_by_words = word_count / 500.0
        pages_by_lines = line_count / 45.0

        # Weighted average (chars and words more reliable than lines)
        estimated_pages = (pages_by_chars * 0.4) + (pages_by_words * 0.4) + (pages_by_lines * 0.2)

        return estimated_pages

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(re.findall(r'\b\w+\b', text))
