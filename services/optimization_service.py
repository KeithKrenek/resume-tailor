"""Service layer for optimization operations - testable without Streamlit."""

from typing import Tuple, Optional
from modules.models import JobModel, ResumeModel, GapAnalysis, ResumeOptimizationResult
from agents.resume_optimization_agent import optimize_resume
from agents.authenticity_agent import create_authenticity_agent
from services.metrics_service import MetricsService
from utils.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)


def run_optimization(
    job: JobModel,
    resume: ResumeModel,
    gap: GapAnalysis,
    style: str = "balanced",
    api_key: Optional[str] = None,
    enable_authenticity_check: bool = True,
    enable_metrics: bool = True
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
        enable_authenticity_check: Whether to run LLM-based authenticity verification
        enable_metrics: Whether to calculate quality metrics

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
    logger.info(f"Running resume optimization with style: {style}")
    success, result, error = optimize_resume(
        job=job,
        resume=resume,
        gap=gap,
        style=style,
        api_key=api_key
    )

    if not success or not result:
        raise ValueError(f"Optimization failed: {error}")

    logger.info(f"Optimization complete with {len(result.changes)} changes")

    # Run authenticity verification if enabled
    if enable_authenticity_check:
        logger.info("Running LLM-based authenticity verification")
        try:
            # Create authenticity agent (uses Haiku for speed)
            auth_agent = create_authenticity_agent(
                api_key=api_key,
                model="claude-3-haiku-20240307"
            )

            # Get original resume text
            original_text = resume.raw_text or resume.to_markdown()

            # Run verification
            verification_success, auth_report = auth_agent.verify_updates(
                original_resume_text=original_text,
                optimized_resume=result.optimized_resume,
                changes=result.changes
            )

            if verification_success:
                # Attach authenticity report to result
                result.authenticity_report = auth_report.to_dict()
                logger.info(
                    f"Authenticity check complete: {len(auth_report.issues_found)} issues found, "
                    f"risk level: {auth_report.overall_risk_level}"
                )
            else:
                logger.warning("Authenticity verification completed with errors")
                # Still attach the report even if verification had issues
                result.authenticity_report = auth_report.to_dict()

        except Exception as e:
            logger.error(f"Authenticity verification failed: {e}", exc_info=True)
            # Don't fail the whole optimization, just log the error
            # The result will not have an authenticity_report field
            logger.warning("Continuing without authenticity report")

    # Calculate quality metrics if enabled
    if enable_metrics:
        logger.info("Calculating quality metrics")
        try:
            # Create metrics service
            metrics_service = MetricsService()

            # Get text representations
            original_text = resume.raw_text or resume.to_markdown()
            optimized_text = result.optimized_resume.raw_text or result.optimized_resume.to_markdown()
            job_text = job.raw_text or job.description or ""

            # Calculate metrics
            metrics_result = metrics_service.calculate_all_metrics(
                original_resume=original_text,
                optimized_resume=optimized_text,
                job_description=job_text
            )

            # Attach metrics to result
            result.metrics = metrics_result.to_dict()
            logger.info(
                f"Metrics calculated: Overall score {metrics_result.overall_score:.2%}, "
                f"Passed: {metrics_result.overall_passed}"
            )

        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}", exc_info=True)
            # Don't fail the whole optimization, just log the error
            logger.warning("Continuing without metrics")

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
