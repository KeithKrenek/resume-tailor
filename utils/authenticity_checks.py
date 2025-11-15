"""Authenticity checking utilities for resume optimization."""

import re
from typing import List
from modules.models import ResumeChange, ChangeType, ResumeModel


def extract_numbers(text: str) -> List[str]:
    """
    Extract numeric values from text.

    Looks for:
    - Percentages (e.g., "20%", "3.5%")
    - Dollar amounts (e.g., "$5M", "$100K", "$2.5B")
    - Counts (e.g., "500 users", "3x improvement")
    - Time periods (e.g., "2 years", "6 months")

    Returns:
        List of numeric patterns found
    """
    patterns = [
        r'\d+\.?\d*%',  # Percentages: 20%, 3.5%
        r'\$\d+\.?\d*[KMB]?',  # Dollar amounts: $5M, $100K
        r'\d+x',  # Multipliers: 3x, 10x
        r'\d+\+',  # Plus notation: 100+, 500+
        r'\d+\.?\d*\s*(million|billion|thousand|k|m|b)',  # Written numbers
        r'\d+\s*(users|customers|clients|employees|hours|days|weeks|months|years)',  # Counts with units
    ]

    numbers = []
    text_lower = text.lower()

    for pattern in patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        numbers.extend(matches)

    return numbers


def extract_company_names(text: str) -> List[str]:
    """
    Extract potential company names from text.

    Simple heuristic: looks for capitalized words that might be companies.
    This is intentionally conservative to reduce false positives.

    Returns:
        List of potential company names
    """
    # Look for capitalized words/phrases (very basic)
    # This will have false positives, but better safe than sorry
    pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    matches = re.findall(pattern, text)

    # Filter out common non-company words
    common_words = {
        'Led', 'Managed', 'Developed', 'Created', 'Built', 'Designed',
        'Implemented', 'Launched', 'Drove', 'Improved', 'Reduced',
        'Increased', 'The', 'A', 'An', 'In', 'On', 'At', 'For', 'With',
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December',
        'Python', 'JavaScript', 'Java', 'React', 'Node', 'AWS', 'Docker'
    }

    return [m for m in matches if m not in common_words]


def extract_technologies(text: str) -> List[str]:
    """
    Extract technology names from text.

    Looks for common tech patterns and capitalized tech terms.

    Returns:
        List of potential technology names
    """
    # Common technology patterns
    tech_patterns = [
        r'\b[A-Z]{2,}\b',  # Acronyms: AWS, API, SQL
        r'\b[A-Z][a-z]+(?:JS|QL|DB)\b',  # NodeJS, MySQL, MongoDB
        r'\b(?:React|Angular|Vue|Django|Flask|Node|Spring|Kubernetes|Docker)\b',  # Common frameworks
    ]

    technologies = []
    for pattern in tech_patterns:
        matches = re.findall(pattern, text)
        technologies.extend(matches)

    return list(set(technologies))  # Remove duplicates


def check_change_authenticity(
    change: ResumeChange,
    original_resume: ResumeModel
) -> tuple[bool, List[str]]:
    """
    Check if a resume change appears to introduce fabricated content.

    This is a heuristic check that flags potentially risky changes for human review.
    It's intentionally conservative - better to flag safe changes than miss fabrications.

    Args:
        change: The resume change to check
        original_resume: The original resume to compare against

    Returns:
        Tuple of (is_risky, list of warning messages)
    """
    warnings = []

    # Only check experience bullets and summary/headline (most likely to have fabrications)
    if change.change_type not in [ChangeType.EXPERIENCE_BULLET, ChangeType.SUMMARY, ChangeType.HEADLINE]:
        return False, []

    before_text = change.before
    after_text = change.after

    # Check 1: New numbers introduced
    before_numbers = set(extract_numbers(before_text))
    after_numbers = set(extract_numbers(after_text))
    new_numbers = after_numbers - before_numbers

    if new_numbers:
        warnings.append(f"Introduces new metrics: {', '.join(list(new_numbers)[:3])}")

    # Check 2: New company names mentioned (could be fabricated experience)
    before_companies = set(extract_company_names(before_text))
    after_companies = set(extract_company_names(after_text))
    new_companies = after_companies - before_companies

    # Filter against companies already in resume
    resume_companies = {exp.company for exp in original_resume.experiences}
    risky_companies = new_companies - resume_companies

    if risky_companies:
        warnings.append(f"Mentions new organizations: {', '.join(list(risky_companies)[:2])}")

    # Check 3: New technologies that aren't in the original resume
    original_text = original_resume.to_dict()  # Get full resume as dict
    original_resume_str = str(original_text).lower()

    before_tech = set([t.lower() for t in extract_technologies(before_text)])
    after_tech = set([t.lower() for t in extract_technologies(after_text)])
    new_tech = after_tech - before_tech

    # Only flag if the technology doesn't appear ANYWHERE in original resume
    risky_tech = [tech for tech in new_tech if tech.lower() not in original_resume_str]

    if risky_tech:
        warnings.append(f"Introduces new technologies: {', '.join(risky_tech[:3])}")

    # Check 4: Significant length increase (might indicate added content)
    length_increase = len(after_text) - len(before_text)
    if length_increase > 100:  # More than 100 characters added
        increase_pct = (length_increase / len(before_text)) * 100 if before_text else 0
        if increase_pct > 50:  # More than 50% longer
            warnings.append(f"Significantly expanded content (+{increase_pct:.0f}% length)")

    is_risky = len(warnings) > 0
    return is_risky, warnings


def get_potentially_risky_changes(
    changes: List[ResumeChange],
    original_resume: ResumeModel
) -> List[tuple[ResumeChange, List[str]]]:
    """
    Identify changes that may contain fabricated content.

    Args:
        changes: List of resume changes to check
        original_resume: The original resume for comparison

    Returns:
        List of tuples (change, warnings) for risky changes
    """
    risky_changes = []

    for change in changes:
        is_risky, warnings = check_change_authenticity(change, original_resume)
        if is_risky:
            risky_changes.append((change, warnings))

    return risky_changes


def generate_authenticity_report(
    changes: List[ResumeChange],
    original_resume: ResumeModel
) -> dict:
    """
    Generate a comprehensive authenticity report for all changes.

    Args:
        changes: List of resume changes
        original_resume: The original resume

    Returns:
        Dictionary with authenticity metrics and flagged changes
    """
    risky_changes = get_potentially_risky_changes(changes, original_resume)

    total_changes = len(changes)
    flagged_count = len(risky_changes)

    # Categorize warnings
    warning_categories = {
        'new_metrics': 0,
        'new_organizations': 0,
        'new_technologies': 0,
        'expanded_content': 0
    }

    for change, warnings in risky_changes:
        for warning in warnings:
            if 'metrics' in warning.lower():
                warning_categories['new_metrics'] += 1
            elif 'organizations' in warning.lower():
                warning_categories['new_organizations'] += 1
            elif 'technologies' in warning.lower():
                warning_categories['new_technologies'] += 1
            elif 'expanded' in warning.lower():
                warning_categories['expanded_content'] += 1

    return {
        'total_changes': total_changes,
        'flagged_changes': flagged_count,
        'flag_rate': (flagged_count / total_changes * 100) if total_changes > 0 else 0,
        'warning_categories': warning_categories,
        'risky_changes': risky_changes,
        'is_safe': flagged_count == 0,
        'recommendations': _generate_recommendations(warning_categories)
    }


def _generate_recommendations(warning_categories: dict) -> List[str]:
    """Generate recommendations based on warning categories."""
    recommendations = []

    if warning_categories['new_metrics'] > 0:
        recommendations.append(
            "Review changes with new metrics carefully - ensure all numbers are accurate"
        )

    if warning_categories['new_organizations'] > 0:
        recommendations.append(
            "Verify that any mentioned organizations are actually part of candidate's experience"
        )

    if warning_categories['new_technologies'] > 0:
        recommendations.append(
            "Confirm that new technologies mentioned were actually used by the candidate"
        )

    if warning_categories['expanded_content'] > 0:
        recommendations.append(
            "Review significantly expanded content to ensure no fabricated details were added"
        )

    if not recommendations:
        recommendations.append(
            "All changes appear safe - no obvious fabrication detected"
        )

    return recommendations
