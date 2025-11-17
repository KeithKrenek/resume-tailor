"""Session state management for Streamlit app."""

import streamlit as st
from typing import Dict, Any, Optional
from pathlib import Path

from config.settings import SESSION_KEYS, DEFAULT_OUTPUT_FOLDER, TOTAL_STEPS


def initialize_session_state() -> None:
    """Initialize Streamlit session state with default values."""

    # Job-related data
    if SESSION_KEYS['job_description'] not in st.session_state:
        st.session_state[SESSION_KEYS['job_description']] = ""

    if SESSION_KEYS['job_url'] not in st.session_state:
        st.session_state[SESSION_KEYS['job_url']] = ""

    if SESSION_KEYS['company_url'] not in st.session_state:
        st.session_state[SESSION_KEYS['company_url']] = ""

    if SESSION_KEYS['scraped_job_data'] not in st.session_state:
        st.session_state[SESSION_KEYS['scraped_job_data']] = None

    # Resume data
    if SESSION_KEYS['resume_text'] not in st.session_state:
        st.session_state[SESSION_KEYS['resume_text']] = ""

    if SESSION_KEYS['resume_metadata'] not in st.session_state:
        st.session_state[SESSION_KEYS['resume_metadata']] = {}

    # Output folder
    if SESSION_KEYS['output_folder'] not in st.session_state:
        st.session_state[SESSION_KEYS['output_folder']] = DEFAULT_OUTPUT_FOLDER

    # Step completion tracking
    if SESSION_KEYS['step_1_complete'] not in st.session_state:
        st.session_state[SESSION_KEYS['step_1_complete']] = False

    if SESSION_KEYS['step_2_complete'] not in st.session_state:
        st.session_state[SESSION_KEYS['step_2_complete']] = False

    if SESSION_KEYS['step_3_complete'] not in st.session_state:
        st.session_state[SESSION_KEYS['step_3_complete']] = False

    if SESSION_KEYS['change_review_complete'] not in st.session_state:
        st.session_state[SESSION_KEYS['change_review_complete']] = False

    if SESSION_KEYS['current_step'] not in st.session_state:
        st.session_state[SESSION_KEYS['current_step']] = 1

    # Extracted information (from agent)
    if SESSION_KEYS['company_name'] not in st.session_state:
        st.session_state[SESSION_KEYS['company_name']] = ""

    if SESSION_KEYS['job_title'] not in st.session_state:
        st.session_state[SESSION_KEYS['job_title']] = ""


def save_job_inputs(
    job_description: str,
    job_url: str = "",
    company_url: str = "",
    scraped_data: Optional[Dict] = None
) -> None:
    """
    Save job-related inputs to session state.

    Args:
        job_description: Job description text
        job_url: Job posting URL (optional)
        company_url: Company URL (optional)
        scraped_data: Scraped job data (optional)
    """
    st.session_state[SESSION_KEYS['job_description']] = job_description
    st.session_state[SESSION_KEYS['job_url']] = job_url
    st.session_state[SESSION_KEYS['company_url']] = company_url
    if scraped_data:
        st.session_state[SESSION_KEYS['scraped_job_data']] = scraped_data


def save_resume_inputs(resume_text: str, metadata: Dict[str, Any]) -> None:
    """
    Save resume inputs to session state.

    Args:
        resume_text: Resume text content
        metadata: Resume metadata (email, phone, etc.)
    """
    st.session_state[SESSION_KEYS['resume_text']] = resume_text
    st.session_state[SESSION_KEYS['resume_metadata']] = metadata


def save_output_folder(folder_path: str) -> None:
    """
    Save output folder path to session state.

    Args:
        folder_path: Path to output folder
    """
    st.session_state[SESSION_KEYS['output_folder']] = folder_path


def save_extracted_info(company_name: str = "", job_title: str = "") -> None:
    """
    Save extracted company name and job title to session state.

    Args:
        company_name: Extracted company name
        job_title: Extracted job title
    """
    if company_name:
        st.session_state[SESSION_KEYS['company_name']] = company_name
    if job_title:
        st.session_state[SESSION_KEYS['job_title']] = job_title


def mark_step_complete(step: int) -> None:
    """
    Mark a step as complete.

    Args:
        step: Step number to mark as complete
    """
    if step == 1:
        st.session_state[SESSION_KEYS['step_1_complete']] = True
    elif step == 2:
        st.session_state[SESSION_KEYS['step_2_complete']] = True
    elif step == 3:
        st.session_state[SESSION_KEYS['step_3_complete']] = True


def is_step_complete(step: int) -> bool:
    """
    Check if a step is complete.

    Args:
        step: Step number to check

    Returns:
        True if step is complete, False otherwise
    """
    if step == 1:
        return st.session_state.get(SESSION_KEYS['step_1_complete'], False)
    elif step == 2:
        return st.session_state.get(SESSION_KEYS['step_2_complete'], False)
    elif step == 3:
        return st.session_state.get(SESSION_KEYS['step_3_complete'], False)
    return False


def set_current_step(step: int) -> None:
    """
    Set the current step.

    Args:
        step: Step number (1 to TOTAL_STEPS)
    """
    if 1 <= step <= TOTAL_STEPS:
        st.session_state[SESSION_KEYS['current_step']] = step


def get_current_step() -> int:
    """
    Get the current step number.

    Returns:
        Current step number
    """
    return st.session_state.get(SESSION_KEYS['current_step'], 1)


def clear_session_state() -> None:
    """Clear all session state (reset application)."""
    for key in SESSION_KEYS.values():
        if key in st.session_state:
            if key == SESSION_KEYS['output_folder']:
                st.session_state[key] = DEFAULT_OUTPUT_FOLDER
            elif key == SESSION_KEYS['current_step']:
                st.session_state[key] = 1
            elif key == SESSION_KEYS['resume_metadata']:
                st.session_state[key] = {}
            elif key in [SESSION_KEYS['step_1_complete'], SESSION_KEYS['step_2_complete'], SESSION_KEYS['step_3_complete'], SESSION_KEYS['change_review_complete']]:
                st.session_state[key] = False
            else:
                st.session_state[key] = ""


def get_all_inputs() -> Dict[str, Any]:
    """
    Get all inputs from session state.

    Returns:
        Dictionary with all input data
    """
    return {
        'job_description': st.session_state.get(SESSION_KEYS['job_description'], ""),
        'job_url': st.session_state.get(SESSION_KEYS['job_url'], ""),
        'company_url': st.session_state.get(SESSION_KEYS['company_url'], ""),
        'resume_text': st.session_state.get(SESSION_KEYS['resume_text'], ""),
        'resume_metadata': st.session_state.get(SESSION_KEYS['resume_metadata'], {}),
        'output_folder': st.session_state.get(SESSION_KEYS['output_folder'], DEFAULT_OUTPUT_FOLDER),
        'company_name': st.session_state.get(SESSION_KEYS['company_name'], ""),
        'job_title': st.session_state.get(SESSION_KEYS['job_title'], ""),
        'scraped_job_data': st.session_state.get(SESSION_KEYS['scraped_job_data'], None)
    }


def ensure_output_folder_exists() -> bool:
    """
    Ensure output folder exists, create if it doesn't.

    Returns:
        True if folder exists or was created successfully
    """
    try:
        folder = st.session_state.get(SESSION_KEYS['output_folder'], DEFAULT_OUTPUT_FOLDER)
        Path(folder).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False
