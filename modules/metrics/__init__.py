"""
Metrics package for evaluating resume optimization quality.

This package provides quantitative scoring across multiple dimensions:
- Authenticity: Ensures claims are supported by original resume
- Role Alignment: Measures match with job requirements
- ATS Optimization: Keyword and formatting analysis
- Length Compliance: Checks if resume fits target length
"""

from .base import MetricCalculator, MetricScore
from .authenticity import AuthenticityScorer
from .role_alignment import RoleAlignmentScorer
from .ats import ATSScorer
from .length import LengthScorer

__all__ = [
    'MetricCalculator',
    'MetricScore',
    'AuthenticityScorer',
    'RoleAlignmentScorer',
    'ATSScorer',
    'LengthScorer',
]
