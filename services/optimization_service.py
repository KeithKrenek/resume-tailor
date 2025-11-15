"""Service layer for optimization operations - testable without Streamlit."""

from typing import Tuple, Optional
from modules.models import JobModel, ResumeModel, GapAnalysis, ResumeOptimizationResult
from agents.resume_optimization_agent import optimize_resume


def run_optimization(
    job: JobModel,
    resume: ResumeModel,
    gap: GapAnalysis,
    style: str = "balanced",
    api_key: Optional[str] = None
) -> ResumeOptimizationResult:
    """
    Run resume optimization without Streamlit dependencies.

    This is a pure function that can be tested independently of the UI.

    Args:
        job: Structured job model
        resume: Structured resume model
        gap: Gap analysis results
        style: Optimization style ('conservative', 'balanced', 'aggressive')
        api_key: Anthropic API key (optional)

    Returns:
        ResumeOptimizationResult with optimized resume and changes

    Raises:
        ValueError: If optimization fails
    """
    # Validate style
    valid_styles = ['conservative', 'balanced', 'aggressive']
    if style not in valid_styles:
        raise ValueError(f"Invalid style: {style}. Must be one of {valid_styles}")

    # Run optimization
    success, result, error = optimize_resume(
        job=job,
        resume=resume,
        gap=gap,
        style=style,
        api_key=api_key
    )

    if not success or not result:
        raise ValueError(f"Optimization failed: {error}")

    return result


def validate_optimization_inputs(
    job: JobModel,
    resume: ResumeModel,
    gap: GapAnalysis
) -> Tuple[bool, str]:
    """
    Validate inputs before running optimization.

    Args:
        job: Structured job model
        resume: Structured resume model
        gap: Gap analysis results

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not job or not job.title:
        return False, "Job model is invalid or missing title"

    if not resume or not resume.name:
        return False, "Resume model is invalid or missing name"

    if not gap:
        return False, "Gap analysis is missing"

    if not resume.experiences:
        return False, "Resume has no work experience to optimize"

    return True, ""
