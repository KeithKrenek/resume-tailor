"""Validation functions for input data."""

import re
from typing import Tuple, Dict, List, Any
import validators as val

from config.settings import (
    MIN_JOB_DESC_LENGTH,
    MAX_JOB_DESC_LENGTH,
    MIN_RESUME_LENGTH,
    MAX_RESUME_LENGTH,
    MIN_WORDS_IN_RESUME,
    JOB_DESC_KEYWORDS,
    MIN_JOB_KEYWORDS_MATCH,
    RESUME_KEYWORDS
)


def validate_job_description(text: str) -> Tuple[bool, str]:
    """
    Validate job description text.

    Args:
        text: Job description text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Job description cannot be empty"

    text = text.strip()
    text_lower = text.lower()

    # Check length constraints
    if len(text) < MIN_JOB_DESC_LENGTH:
        return False, f"Job description is too short (minimum {MIN_JOB_DESC_LENGTH} characters, got {len(text)})"

    if len(text) > MAX_JOB_DESC_LENGTH:
        return False, f"Job description is too long (maximum {MAX_JOB_DESC_LENGTH} characters, got {len(text)})"

    # Check for job-related keywords
    keyword_matches = sum(1 for keyword in JOB_DESC_KEYWORDS if keyword in text_lower)

    if keyword_matches < MIN_JOB_KEYWORDS_MATCH:
        return False, f"Job description should contain job-related terms like: {', '.join(JOB_DESC_KEYWORDS[:5])}..."

    return True, ""


def validate_resume_text(text: str) -> Tuple[bool, str]:
    """
    Validate resume text content.

    Args:
        text: Resume text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Resume content cannot be empty"

    text = text.strip()
    text_lower = text.lower()

    # Check length constraints
    if len(text) < MIN_RESUME_LENGTH:
        return False, f"Resume is too short (minimum {MIN_RESUME_LENGTH} characters, got {len(text)})"

    if len(text) > MAX_RESUME_LENGTH:
        return False, f"Resume is too long (maximum {MAX_RESUME_LENGTH} characters, got {len(text)})"

    # Check word count
    words = text.split()
    if len(words) < MIN_WORDS_IN_RESUME:
        return False, f"Resume should contain at least {MIN_WORDS_IN_RESUME} words (got {len(words)})"

    # Check for email or phone (basic resume indicators)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    has_email = bool(re.search(email_pattern, text))
    has_phone = bool(re.search(phone_pattern, text))

    if not has_email and not has_phone:
        return False, "Resume should contain at least an email address or phone number"

    # Check for resume-like content
    keyword_matches = sum(1 for keyword in RESUME_KEYWORDS if keyword in text_lower)
    if keyword_matches < 1:
        return False, f"Resume should contain resume-related terms like: {', '.join(RESUME_KEYWORDS[:4])}..."

    return True, ""


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"

    url = url.strip()

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Validate using validators library
    if val.url(url):
        return True, ""
    else:
        return False, "Invalid URL format. Please enter a valid URL (e.g., https://example.com)"


def validate_folder_path(path: str) -> Tuple[bool, str]:
    """
    Validate folder path (basic validation).

    Args:
        path: Folder path string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or not path.strip():
        return False, "Folder path cannot be empty"

    path = path.strip()

    # Check for invalid characters (basic check)
    invalid_chars = ['<', '>', '|', '\0']
    if any(char in path for char in invalid_chars):
        return False, "Folder path contains invalid characters"

    return True, ""


def extract_basic_info(text: str) -> Dict[str, Any]:
    """
    Extract basic information from resume text.

    Args:
        text: Resume text

    Returns:
        Dictionary with extracted information
    """
    info = {
        'email': None,
        'phone': None,
        'word_count': 0,
        'char_count': 0,
        'has_education': False,
        'has_experience': False,
        'has_skills': False
    }

    if not text:
        return info

    text_lower = text.lower()

    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        info['email'] = email_match.group()

    # Extract phone
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        info['phone'] = phone_match.group()

    # Count words and characters
    info['word_count'] = len(text.split())
    info['char_count'] = len(text)

    # Check for sections
    info['has_education'] = any(keyword in text_lower for keyword in ['education', 'university', 'degree', 'bachelor', 'master', 'phd'])
    info['has_experience'] = any(keyword in text_lower for keyword in ['experience', 'work', 'employment', 'position', 'role'])
    info['has_skills'] = any(keyword in text_lower for keyword in ['skills', 'technologies', 'tools', 'proficient'])

    return info


def get_text_statistics(text: str) -> Dict[str, int]:
    """
    Get statistics about text content.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with text statistics
    """
    if not text:
        return {'chars': 0, 'words': 0, 'lines': 0}

    return {
        'chars': len(text),
        'words': len(text.split()),
        'lines': len(text.splitlines())
    }


def validate_all_inputs(
    job_description: str,
    resume_text: str,
    job_url: str = None,
    company_url: str = None,
    output_folder: str = None
) -> Tuple[bool, List[str]]:
    """
    Validate all inputs at once.

    Args:
        job_description: Job description text
        resume_text: Resume text
        job_url: Optional job posting URL
        company_url: Optional company URL
        output_folder: Optional output folder path

    Returns:
        Tuple of (all_valid, list_of_error_messages)
    """
    errors = []

    # Validate job description
    valid, error = validate_job_description(job_description)
    if not valid:
        errors.append(f"Job Description: {error}")

    # Validate resume
    valid, error = validate_resume_text(resume_text)
    if not valid:
        errors.append(f"Resume: {error}")

    # Validate URLs if provided
    if job_url and job_url.strip():
        valid, error = validate_url(job_url)
        if not valid:
            errors.append(f"Job URL: {error}")

    if company_url and company_url.strip():
        valid, error = validate_url(company_url)
        if not valid:
            errors.append(f"Company URL: {error}")

    # Validate folder path if provided
    if output_folder and output_folder.strip():
        valid, error = validate_folder_path(output_folder)
        if not valid:
            errors.append(f"Output Folder: {error}")

    return len(errors) == 0, errors
