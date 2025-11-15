"""Service layer for analysis operations - testable without Streamlit."""

from typing import Tuple, Optional
from modules.models import JobModel, ResumeModel, GapAnalysis
from agents.job_analysis_agent import analyze_job_posting
from agents.resume_analysis_agent import analyze_resume
from modules.gap_analyzer import perform_gap_analysis


def run_analysis(
    job_description: str,
    resume_text: str,
    metadata: Optional[dict] = None,
    job_title: Optional[str] = None,
    company_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> Tuple[JobModel, ResumeModel, GapAnalysis]:
    """
    Run complete analysis pipeline without Streamlit dependencies.

    This is a pure function that can be tested independently of the UI.

    Args:
        job_description: Raw job description text
        resume_text: Raw resume text
        metadata: Optional resume metadata
        job_title: Pre-extracted job title
        company_name: Pre-extracted company name
        api_key: Anthropic API key (optional)

    Returns:
        Tuple of (JobModel, ResumeModel, GapAnalysis)

    Raises:
        ValueError: If analysis fails for any reason
    """
    # Step 1: Analyze job description
    job_success, job_model, job_error = analyze_job_posting(
        job_description=job_description,
        job_title=job_title,
        company_name=company_name,
        api_key=api_key
    )

    if not job_success or not job_model:
        raise ValueError(f"Job analysis failed: {job_error}")

    # Step 2: Analyze resume
    resume_success, resume_model, resume_error = analyze_resume(
        resume_text=resume_text,
        metadata=metadata,
        api_key=api_key
    )

    if not resume_success or not resume_model:
        raise ValueError(f"Resume analysis failed: {resume_error}")

    # Step 3: Perform gap analysis
    try:
        gap_analysis = perform_gap_analysis(job_model, resume_model)
    except Exception as e:
        raise ValueError(f"Gap analysis failed: {str(e)}")

    return job_model, resume_model, gap_analysis


def validate_inputs(job_description: str, resume_text: str) -> Tuple[bool, str]:
    """
    Validate inputs before running analysis.

    Args:
        job_description: Raw job description text
        resume_text: Raw resume text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not job_description or len(job_description.strip()) < 50:
        return False, "Job description is too short (minimum 50 characters)"

    if not resume_text or len(resume_text.strip()) < 100:
        return False, "Resume text is too short (minimum 100 characters)"

    return True, ""
