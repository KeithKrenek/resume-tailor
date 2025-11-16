"""Service for building final resume from accepted changes."""

import re
from typing import List, Dict, Any, Optional, Tuple
from copy import deepcopy

from modules.models import (
    ResumeModel,
    ResumeOptimizationResult,
    ResumeChange,
    ChangeType,
    ChangeStatus
)
from utils.logging_config import get_logger

logger = get_logger(__name__)


def apply_accepted_changes(result: ResumeOptimizationResult) -> ResumeModel:
    """
    Apply only the accepted/edited changes to create final resume.

    Args:
        result: Optimization result with changes

    Returns:
        ResumeModel with only accepted changes applied
    """
    # Start with a deep copy of the original resume
    final_resume = deepcopy(result.original_resume)

    # Get accepted changes
    accepted_changes = result.get_accepted_changes()

    logger.info(f"Applying {len(accepted_changes)} accepted changes")

    # Sort changes by location to apply in consistent order
    # Apply summary/headline changes first, then experience, then skills
    priority_order = {
        ChangeType.HEADLINE: 1,
        ChangeType.SUMMARY: 2,
        ChangeType.EXPERIENCE_BULLET: 3,
        ChangeType.SKILLS_SECTION: 4,
        ChangeType.EDUCATION: 5,
        ChangeType.OTHER: 6
    }

    sorted_changes = sorted(
        accepted_changes,
        key=lambda c: priority_order.get(c.change_type, 999)
    )

    # Apply each change
    for change in sorted_changes:
        try:
            apply_change(final_resume, change)
        except Exception as e:
            logger.error(f"Failed to apply change {change.id}: {str(e)}", exc_info=True)
            # Continue with other changes even if one fails

    logger.info("All accepted changes applied successfully")
    return final_resume


def apply_change(resume: ResumeModel, change: ResumeChange) -> None:
    """
    Apply a single change to the resume.

    Args:
        resume: Resume model to modify
        change: Change to apply

    Raises:
        ValueError: If change cannot be applied
    """
    # Get the final value (edited if exists, otherwise after)
    final_value = change.get_final_value()

    if change.change_type == ChangeType.HEADLINE:
        resume.headline = final_value

    elif change.change_type == ChangeType.SUMMARY:
        resume.summary = final_value

    elif change.change_type == ChangeType.SKILLS_SECTION:
        # Parse skills from the text (usually comma-separated)
        skills = [s.strip() for s in final_value.split(',') if s.strip()]
        resume.skills = skills

    elif change.change_type == ChangeType.EXPERIENCE_BULLET:
        # Parse location: e.g., "experience[0].bullets[2]"
        exp_idx, bullet_idx = parse_experience_location(change.location)

        if exp_idx is not None and bullet_idx is not None:
            if 0 <= exp_idx < len(resume.experiences):
                exp = resume.experiences[exp_idx]

                if 0 <= bullet_idx < len(exp.bullets):
                    # Replace the bullet
                    exp.bullets[bullet_idx] = final_value
                else:
                    logger.warning(f"Bullet index {bullet_idx} out of range for experience {exp_idx}")
            else:
                logger.warning(f"Experience index {exp_idx} out of range")
        else:
            logger.warning(f"Could not parse experience location: {change.location}")

    elif change.change_type == ChangeType.EDUCATION:
        # Parse location to find which education item to modify
        edu_idx = parse_education_location(change.location)

        if edu_idx is not None and 0 <= edu_idx < len(resume.education):
            # For education, we might be changing degree, institution, etc.
            # The location might specify which field
            if 'degree' in change.location.lower():
                resume.education[edu_idx].degree = final_value
            elif 'institution' in change.location.lower():
                resume.education[edu_idx].institution = final_value
            # Add more field handling as needed

    elif change.change_type == ChangeType.OTHER:
        # Handle other types of changes
        # Could be contact info, projects, etc.
        if 'email' in change.location.lower():
            resume.email = final_value
        elif 'phone' in change.location.lower():
            resume.phone = final_value
        elif 'location' in change.location.lower():
            resume.location = final_value
        # Add more handling as needed

    logger.debug(f"Applied change {change.id} at {change.location}")


def parse_experience_location(location: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse experience location string.

    Args:
        location: Location string like "experience[0].bullets[2]"

    Returns:
        Tuple of (experience_index, bullet_index) or (None, None) if parse fails
    """
    # Pattern: experience[N].bullets[M]
    pattern = r'experience\[(\d+)\]\.bullets\[(\d+)\]'
    match = re.search(pattern, location)

    if match:
        exp_idx = int(match.group(1))
        bullet_idx = int(match.group(2))
        return exp_idx, bullet_idx

    return None, None


def parse_education_location(location: str) -> Optional[int]:
    """
    Parse education location string.

    Args:
        location: Location string like "education[0].degree"

    Returns:
        Education index or None if parse fails
    """
    # Pattern: education[N]
    pattern = r'education\[(\d+)\]'
    match = re.search(pattern, location)

    if match:
        return int(match.group(1))

    return None


def get_change_summary(result: ResumeOptimizationResult) -> Dict[str, Any]:
    """
    Get summary of changes applied vs rejected.

    Args:
        result: Optimization result

    Returns:
        Dictionary with change statistics
    """
    stats = result.get_change_stats()

    # Get breakdown by type
    accepted_by_type: Dict[str, int] = {}
    rejected_by_type: Dict[str, int] = {}

    for change in result.changes:
        change_type = change.change_type.value

        if change.is_accepted():
            accepted_by_type[change_type] = accepted_by_type.get(change_type, 0) + 1
        elif change.is_rejected():
            rejected_by_type[change_type] = rejected_by_type.get(change_type, 0) + 1

    return {
        'total_changes': stats['total'],
        'accepted_count': stats['accepted'],
        'rejected_count': stats['rejected'],
        'pending_count': stats['pending'],
        'accepted_by_type': accepted_by_type,
        'rejected_by_type': rejected_by_type,
        'acceptance_rate': (stats['accepted'] / stats['total'] * 100) if stats['total'] > 0 else 0
    }


def validate_final_resume(resume: ResumeModel) -> Tuple[bool, List[str]]:
    """
    Validate the final resume for completeness.

    Args:
        resume: Resume to validate

    Returns:
        Tuple of (is_valid, list of warnings)
    """
    warnings = []

    if not resume.name:
        warnings.append("Resume is missing a name")

    if not resume.email and not resume.phone:
        warnings.append("Resume is missing contact information")

    if not resume.experiences or len(resume.experiences) == 0:
        warnings.append("Resume has no work experience")

    if not resume.skills or len(resume.skills) == 0:
        warnings.append("Resume has no skills listed")

    for i, exp in enumerate(resume.experiences):
        if not exp.bullets or len(exp.bullets) == 0:
            warnings.append(f"Experience {i} ({exp.title}) has no bullet points")

    is_valid = len(warnings) == 0

    return is_valid, warnings
