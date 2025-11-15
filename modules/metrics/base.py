"""Base classes for metric calculation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class MetricScore:
    """Generic metric score result."""
    name: str
    score: float  # 0.0 to 1.0
    passed: bool  # True if meets threshold
    threshold: float
    details: Dict[str, Any]  # Additional breakdown
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'score': self.score,
            'passed': self.passed,
            'threshold': self.threshold,
            'details': self.details,
            'recommendations': self.recommendations
        }


class MetricCalculator(ABC):
    """Base class for all metric calculators."""

    @abstractmethod
    def calculate(self, original_resume: str, optimized_resume: str, job_description: str) -> MetricScore:
        """
        Calculate metric score.

        Args:
            original_resume: Original resume text
            optimized_resume: Optimized resume text
            job_description: Target job description

        Returns:
            MetricScore with score and recommendations
        """
        pass

    @abstractmethod
    def get_threshold(self) -> float:
        """Return the minimum acceptable score for this metric."""
        pass
