"""
ATS (Applicant Tracking System) Validation Module

Simulates how major ATS systems parse resumes and provides
validation feedback to ensure compatibility.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime
from modules.models import ResumeModel


@dataclass
class ATSParseResult:
    """Result of ATS parsing simulation."""

    # Successfully extracted fields
    extracted_name: Optional[str] = None
    extracted_email: Optional[str] = None
    extracted_phone: Optional[str] = None
    extracted_location: Optional[str] = None

    # Work experience
    extracted_positions: List[Dict[str, str]] = field(default_factory=list)
    total_positions_found: int = 0

    # Skills
    extracted_skills: List[str] = field(default_factory=list)
    total_skills_found: int = 0

    # Education
    extracted_education: List[Dict[str, str]] = field(default_factory=list)
    total_education_found: int = 0

    # Parsing quality metrics
    parse_success_rate: float = 0.0  # 0.0 to 1.0
    field_extraction_score: float = 0.0  # 0.0 to 1.0

    # Issues found
    parsing_errors: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # ATS compatibility score
    ats_compatibility_score: float = 0.0  # 0.0 to 1.0
    ats_grade: str = "F"

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    @property
    def is_ats_friendly(self) -> bool:
        """Check if resume is ATS friendly (>= 80% compatibility)."""
        return self.ats_compatibility_score >= 0.80

    @property
    def critical_issues_count(self) -> int:
        """Count critical parsing errors."""
        return len([e for e in self.parsing_errors if e.get('severity') == 'critical'])


@dataclass
class ATSSystemConfig:
    """Configuration for different ATS systems."""
    name: str
    supports_tables: bool = False
    supports_columns: bool = False
    supports_headers_footers: bool = False
    supports_text_boxes: bool = False
    supports_images: bool = False
    date_formats: List[str] = field(default_factory=lambda: [
        r'\d{1,2}/\d{4}',  # MM/YYYY
        r'\d{4}',  # YYYY
        r'[A-Z][a-z]{2}\s+\d{4}',  # Mon YYYY
    ])

    @classmethod
    def workday(cls):
        """Workday ATS configuration."""
        return cls(
            name="Workday",
            supports_tables=False,
            supports_columns=False,
            supports_headers_footers=False
        )

    @classmethod
    def greenhouse(cls):
        """Greenhouse ATS configuration."""
        return cls(
            name="Greenhouse",
            supports_tables=True,
            supports_columns=False,
            supports_headers_footers=False
        )

    @classmethod
    def lever(cls):
        """Lever ATS configuration."""
        return cls(
            name="Lever",
            supports_tables=True,
            supports_columns=True,
            supports_headers_footers=False
        )

    @classmethod
    def taleo(cls):
        """Oracle Taleo ATS configuration."""
        return cls(
            name="Taleo",
            supports_tables=False,
            supports_columns=False,
            supports_headers_footers=False
        )


class ATSValidator:
    """
    Validates resume compatibility with ATS systems.

    Simulates parsing behavior of major ATS platforms and identifies
    issues that would prevent proper extraction of information.
    """

    def __init__(self, ats_system: Optional[ATSSystemConfig] = None):
        """
        Initialize ATS validator.

        Args:
            ats_system: ATS system configuration (defaults to Workday - most restrictive)
        """
        self.ats_system = ats_system or ATSSystemConfig.workday()

    def validate(self, resume: ResumeModel) -> ATSParseResult:
        """
        Validate resume for ATS compatibility.

        Args:
            resume: Resume to validate

        Returns:
            ATSParseResult with detailed parsing simulation
        """
        result = ATSParseResult()

        # Simulate field extraction
        self._extract_contact_info(resume, result)
        self._extract_work_experience(resume, result)
        self._extract_skills(resume, result)
        self._extract_education(resume, result)

        # Calculate scores
        self._calculate_scores(resume, result)

        # Generate recommendations
        self._generate_recommendations(resume, result)

        return result

    def _extract_contact_info(self, resume: ResumeModel, result: ATSParseResult):
        """Simulate ATS extraction of contact information."""
        # Name extraction
        if resume.name:
            # ATS can usually extract name if it's in plain text
            result.extracted_name = resume.name
        else:
            result.parsing_errors.append({
                'field': 'name',
                'severity': 'critical',
                'issue': 'Name not found',
                'fix': 'Add your full name at the top of the resume in plain text'
            })

        # Email extraction
        if resume.email:
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, resume.email):
                result.extracted_email = resume.email
            else:
                result.parsing_errors.append({
                    'field': 'email',
                    'severity': 'high',
                    'issue': 'Email format may not be recognized',
                    'fix': 'Use standard email format: name@domain.com'
                })
        else:
            result.parsing_errors.append({
                'field': 'email',
                'severity': 'critical',
                'issue': 'Email not found',
                'fix': 'Add email address in plain text (not in header/footer)'
            })

        # Phone extraction
        if resume.phone:
            # Check phone format
            # ATS prefers formats like: (123) 456-7890, 123-456-7890, +1-123-456-7890
            phone_clean = re.sub(r'[^\d+]', '', resume.phone)
            if len(phone_clean) >= 10:
                result.extracted_phone = resume.phone
            else:
                result.parsing_errors.append({
                    'field': 'phone',
                    'severity': 'medium',
                    'issue': 'Phone number format may not be recognized',
                    'fix': 'Use format: (123) 456-7890 or +1-123-456-7890'
                })
        else:
            result.warnings.append("Phone number not found - highly recommended for ATS")

        # Location
        if resume.location:
            result.extracted_location = resume.location

    def _extract_work_experience(self, resume: ResumeModel, result: ATSParseResult):
        """Simulate ATS extraction of work experience."""
        if not resume.experiences:
            result.parsing_errors.append({
                'field': 'experience',
                'severity': 'critical',
                'issue': 'No work experience found',
                'fix': 'Add work experience section with job titles, companies, and dates'
            })
            return

        for i, exp in enumerate(resume.experiences):
            extracted_exp = {}
            has_critical_issue = False

            # Job title
            if exp.title:
                extracted_exp['title'] = exp.title
            else:
                result.parsing_errors.append({
                    'field': f'experience[{i}].title',
                    'severity': 'high',
                    'issue': f'Job title missing for position {i+1}',
                    'fix': 'Add job title for each position'
                })
                has_critical_issue = True

            # Company
            if exp.company:
                extracted_exp['company'] = exp.company
            else:
                result.parsing_errors.append({
                    'field': f'experience[{i}].company',
                    'severity': 'high',
                    'issue': f'Company name missing for position {i+1}',
                    'fix': 'Add company name for each position'
                })
                has_critical_issue = True

            # Dates - CRITICAL for ATS
            if exp.start_date or exp.end_date:
                # Validate date format
                date_recognized = False

                for date_str in [exp.start_date, exp.end_date]:
                    if date_str:
                        # Check if date matches common ATS formats
                        for pattern in self.ats_system.date_formats:
                            if re.search(pattern, date_str):
                                date_recognized = True
                                break

                if date_recognized:
                    extracted_exp['dates'] = f"{exp.start_date or 'N/A'} - {exp.end_date or 'Present'}"
                else:
                    result.parsing_errors.append({
                        'field': f'experience[{i}].dates',
                        'severity': 'high',
                        'issue': f'Date format not recognized for position {i+1}: {exp.start_date} - {exp.end_date}',
                        'fix': 'Use format: MM/YYYY - MM/YYYY or Mon YYYY - Mon YYYY'
                    })
            else:
                result.parsing_errors.append({
                    'field': f'experience[{i}].dates',
                    'severity': 'critical',
                    'issue': f'No dates provided for position {i+1}',
                    'fix': 'Add start and end dates (or "Present") for each position'
                })
                has_critical_issue = True

            # Bullets/responsibilities
            if exp.bullets and len(exp.bullets) > 0:
                extracted_exp['responsibilities'] = exp.bullets[:3]  # ATS usually extracts first few
            else:
                result.warnings.append(f"No bullet points found for position {i+1}")

            if not has_critical_issue:
                result.extracted_positions.append(extracted_exp)

        result.total_positions_found = len(result.extracted_positions)

    def _extract_skills(self, resume: ResumeModel, result: ATSParseResult):
        """Simulate ATS extraction of skills."""
        if not resume.skills or len(resume.skills) == 0:
            result.parsing_errors.append({
                'field': 'skills',
                'severity': 'high',
                'issue': 'No skills section found',
                'fix': 'Add a dedicated Skills section with relevant keywords'
            })
            return

        # ATS looks for skills in dedicated sections
        # Skills embedded in experience are often missed
        result.extracted_skills = resume.skills.copy()
        result.total_skills_found = len(result.extracted_skills)

        # Validate skill format
        if len(resume.skills) > 50:
            result.warnings.append("Too many skills (>50) may appear unfocused to recruiters")
        elif len(resume.skills) < 5:
            result.warnings.append("Too few skills (<5) may not provide enough keyword matches")

    def _extract_education(self, resume: ResumeModel, result: ATSParseResult):
        """Simulate ATS extraction of education."""
        if not resume.education or len(resume.education) == 0:
            result.warnings.append("No education section found - may be required for some roles")
            return

        for i, edu in enumerate(resume.education):
            extracted_edu = {}

            if edu.degree:
                extracted_edu['degree'] = edu.degree
            else:
                result.warnings.append(f"Degree name missing for education entry {i+1}")

            if edu.institution:
                extracted_edu['institution'] = edu.institution
            else:
                result.warnings.append(f"Institution name missing for education entry {i+1}")

            if edu.graduation_date:
                extracted_edu['graduation'] = edu.graduation_date

            result.extracted_education.append(extracted_edu)

        result.total_education_found = len(result.extracted_education)

    def _calculate_scores(self, resume: ResumeModel, result: ATSParseResult):
        """Calculate ATS compatibility scores."""
        # Field extraction score (how many critical fields were extracted)
        total_critical_fields = 6  # name, email, phone, positions, skills, education
        extracted_fields = 0

        if result.extracted_name:
            extracted_fields += 1
        if result.extracted_email:
            extracted_fields += 1
        if result.extracted_phone:
            extracted_fields += 1
        if result.total_positions_found > 0:
            extracted_fields += 1
        if result.total_skills_found > 0:
            extracted_fields += 1
        if result.total_education_found > 0:
            extracted_fields += 1

        result.field_extraction_score = extracted_fields / total_critical_fields

        # Parse success rate (how many expected items were successfully parsed)
        expected_positions = len(resume.experiences) if resume.experiences else 0
        expected_education = len(resume.education) if resume.education else 0

        total_expected = expected_positions + expected_education + 4  # +4 for contact fields
        total_extracted = (
            result.total_positions_found +
            result.total_education_found +
            (1 if result.extracted_name else 0) +
            (1 if result.extracted_email else 0) +
            (1 if result.extracted_phone else 0) +
            (1 if result.extracted_location else 0)
        )

        result.parse_success_rate = total_extracted / total_expected if total_expected > 0 else 0

        # Overall ATS compatibility score
        # Weighted: 40% field extraction, 40% parse success, 20% error penalty
        critical_errors = result.critical_issues_count
        error_penalty = min(0.2, critical_errors * 0.05)  # -5% per critical error, max -20%

        result.ats_compatibility_score = (
            result.field_extraction_score * 0.4 +
            result.parse_success_rate * 0.4 +
            0.2 - error_penalty
        )

        # Assign grade
        if result.ats_compatibility_score >= 0.90:
            result.ats_grade = "A"
        elif result.ats_compatibility_score >= 0.80:
            result.ats_grade = "B"
        elif result.ats_compatibility_score >= 0.70:
            result.ats_grade = "C"
        elif result.ats_compatibility_score >= 0.60:
            result.ats_grade = "D"
        else:
            result.ats_grade = "F"

    def _generate_recommendations(self, resume: ResumeModel, result: ATSParseResult):
        """Generate ATS optimization recommendations."""
        recommendations = []

        # Critical issues first
        critical_errors = [e for e in result.parsing_errors if e['severity'] == 'critical']
        if critical_errors:
            recommendations.append(f"🔴 CRITICAL: Fix {len(critical_errors)} blocking issues before submitting")
            for error in critical_errors[:3]:  # Show top 3
                recommendations.append(f"  • {error['fix']}")

        # High priority issues
        high_errors = [e for e in result.parsing_errors if e['severity'] == 'high']
        if high_errors:
            recommendations.append(f"🟠 HIGH: Address {len(high_errors)} important issues")
            for error in high_errors[:2]:  # Show top 2
                recommendations.append(f"  • {error['fix']}")

        # Best practices
        if result.ats_compatibility_score < 0.80:
            recommendations.append("📋 Use simple, single-column layout without tables or text boxes")
            recommendations.append("📋 Place contact information at the top in plain text")
            recommendations.append("📋 Use standard section headings: Experience, Education, Skills")

        # Format-specific recommendations
        if not self.ats_system.supports_tables:
            recommendations.append(f"⚠️ {self.ats_system.name} doesn't support tables - use simple formatting")

        if not self.ats_system.supports_columns:
            recommendations.append(f"⚠️ {self.ats_system.name} doesn't support multi-column layouts")

        # Date format recommendations
        positions_with_bad_dates = [
            e for e in result.parsing_errors
            if 'dates' in e['field'] and 'format' in e['issue'].lower()
        ]
        if positions_with_bad_dates:
            recommendations.append("📅 Use consistent date format: MM/YYYY or Mon YYYY")

        result.recommendations = recommendations


def validate_resume_ats(
    resume: ResumeModel,
    ats_system: str = "workday"
) -> ATSParseResult:
    """
    Validate resume for ATS compatibility.

    Args:
        resume: Resume to validate
        ats_system: ATS system to simulate ("workday", "greenhouse", "lever", "taleo")

    Returns:
        ATSParseResult with validation details
    """
    # Get ATS config
    ats_configs = {
        "workday": ATSSystemConfig.workday(),
        "greenhouse": ATSSystemConfig.greenhouse(),
        "lever": ATSSystemConfig.lever(),
        "taleo": ATSSystemConfig.taleo()
    }

    config = ats_configs.get(ats_system.lower(), ATSSystemConfig.workday())

    # Run validation
    validator = ATSValidator(config)
    return validator.validate(resume)


def compare_ats_systems(resume: ResumeModel) -> Dict[str, ATSParseResult]:
    """
    Compare resume parsing across multiple ATS systems.

    Args:
        resume: Resume to test

    Returns:
        Dictionary mapping ATS system name to parse results
    """
    systems = ["workday", "greenhouse", "lever", "taleo"]
    results = {}

    for system in systems:
        results[system] = validate_resume_ats(resume, system)

    return results
