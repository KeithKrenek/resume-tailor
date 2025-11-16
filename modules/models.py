"""Data models for Resume Tailor application."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from enum import Enum
import json


@dataclass
class ExperienceItem:
    """Represents a single work experience entry."""
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None  # "Present" or actual date
    location: Optional[str] = None
    bullets: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    is_current: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'company': self.company,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'location': self.location,
            'bullets': self.bullets,
            'skills': self.skills,
            'is_current': self.is_current
        }


@dataclass
class EducationItem:
    """Represents a single education entry."""
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    honors: List[str] = field(default_factory=list)
    relevant_coursework: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'degree': self.degree,
            'institution': self.institution,
            'field_of_study': self.field_of_study,
            'graduation_date': self.graduation_date,
            'gpa': self.gpa,
            'honors': self.honors,
            'relevant_coursework': self.relevant_coursework
        }


@dataclass
class ResumeModel:
    """Structured representation of a resume."""
    # Contact Information
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None

    # Professional Summary
    headline: Optional[str] = None
    summary: Optional[str] = None

    # Experience & Skills
    experiences: List[ExperienceItem] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    education: List[EducationItem] = field(default_factory=list)

    # Additional Sections
    certifications: List[str] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    awards: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)

    # Metadata
    total_years_experience: Optional[float] = None
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'linkedin': self.linkedin,
            'github': self.github,
            'portfolio': self.portfolio,
            'headline': self.headline,
            'summary': self.summary,
            'experiences': [exp.to_dict() for exp in self.experiences],
            'skills': self.skills,
            'education': [edu.to_dict() for edu in self.education],
            'certifications': self.certifications,
            'projects': self.projects,
            'awards': self.awards,
            'languages': self.languages,
            'total_years_experience': self.total_years_experience,
            'raw_text': self.raw_text
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_markdown(self) -> str:
        """
        Convert resume to markdown format.

        Returns:
            Formatted markdown representation of the resume
        """
        parts = []

        # Header with name
        if self.name:
            parts.append(f"# {self.name}\n")

        # Contact information
        contact_parts = []
        if self.email:
            contact_parts.append(f"✉️ {self.email}")
        if self.phone:
            contact_parts.append(f"📞 {self.phone}")
        if self.location:
            contact_parts.append(f"📍 {self.location}")

        if contact_parts:
            parts.append(" | ".join(contact_parts))
            parts.append("")

        # Links
        link_parts = []
        if self.linkedin:
            link_parts.append(f"[LinkedIn]({self.linkedin})")
        if self.github:
            link_parts.append(f"[GitHub]({self.github})")
        if self.portfolio:
            link_parts.append(f"[Portfolio]({self.portfolio})")

        if link_parts:
            parts.append(" | ".join(link_parts))
            parts.append("")

        # Headline
        if self.headline:
            parts.append(f"**{self.headline}**\n")

        # Summary
        if self.summary:
            parts.append("## Professional Summary\n")
            parts.append(self.summary.strip())
            parts.append("")

        # Experience
        if self.experiences:
            parts.append("## Professional Experience\n")
            for exp in self.experiences:
                # Company and title
                header = f"### {exp.title}"
                if exp.company:
                    header += f" • {exp.company}"
                parts.append(header)

                # Dates and location
                date_parts = []
                if exp.start_date or exp.end_date:
                    date_str = f"{exp.start_date or 'N/A'} – {exp.end_date or 'Present'}"
                    date_parts.append(date_str)
                if exp.location:
                    date_parts.append(exp.location)

                if date_parts:
                    parts.append(f"*{' | '.join(date_parts)}*\n")
                else:
                    parts.append("")

                # Bullets
                for bullet in exp.bullets:
                    parts.append(f"- {bullet}")

                # Skills for this experience
                if exp.skills:
                    parts.append(f"\n**Skills**: {', '.join(exp.skills)}")

                parts.append("")

        # Skills
        if self.skills:
            parts.append("## Skills\n")
            parts.append(", ".join(self.skills))
            parts.append("")

        # Education
        if self.education:
            parts.append("## Education\n")
            for edu in self.education:
                header = f"### {edu.degree}"
                if edu.institution:
                    header += f" • {edu.institution}"
                parts.append(header)

                # Education uses graduation_date, not start_date/end_date
                if edu.graduation_date:
                    parts.append(f"*Graduated: {edu.graduation_date}*")
                if edu.gpa:
                    parts.append(f"GPA: {edu.gpa}")

                parts.append("")

        # Certifications
        if self.certifications:
            parts.append("## Certifications\n")
            for cert in self.certifications:
                parts.append(f"- {cert}")
            parts.append("")

        # Projects
        if self.projects:
            parts.append("## Projects\n")
            for project in self.projects:
                parts.append(f"- {project}")
            parts.append("")

        # Awards
        if self.awards:
            parts.append("## Awards & Honors\n")
            for award in self.awards:
                parts.append(f"- {award}")
            parts.append("")

        # Languages
        if self.languages:
            parts.append("## Languages\n")
            parts.append(", ".join(self.languages))
            parts.append("")

        return "\n".join(parts).strip()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResumeModel':
        """Create from dictionary."""
        # Parse experiences
        experiences = [
            ExperienceItem(**exp) for exp in data.get('experiences', [])
        ]
        # Parse education
        education = [
            EducationItem(**edu) for edu in data.get('education', [])
        ]

        return cls(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            location=data.get('location'),
            linkedin=data.get('linkedin'),
            github=data.get('github'),
            portfolio=data.get('portfolio'),
            headline=data.get('headline'),
            summary=data.get('summary'),
            experiences=experiences,
            skills=data.get('skills', []),
            education=education,
            certifications=data.get('certifications', []),
            projects=data.get('projects', []),
            awards=data.get('awards', []),
            languages=data.get('languages', []),
            total_years_experience=data.get('total_years_experience'),
            raw_text=data.get('raw_text')
        )


@dataclass
class JobRequirement:
    """Represents a single job requirement."""
    description: str
    category: str  # "Required Skill", "Preferred Skill", "Responsibility", "Qualification"
    is_must_have: bool
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'description': self.description,
            'category': self.category,
            'is_must_have': self.is_must_have,
            'keywords': self.keywords
        }


@dataclass
class JobModel:
    """Structured representation of a job posting."""
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None  # "Full-time", "Contract", etc.
    experience_level: Optional[str] = None  # "Senior", "Mid-level", etc.
    salary_range: Optional[str] = None

    # Job Details
    description: Optional[str] = None
    responsibilities: List[str] = field(default_factory=list)
    requirements: List[JobRequirement] = field(default_factory=list)
    nice_to_haves: List[str] = field(default_factory=list)

    # Skills
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)

    # Other
    benefits: List[str] = field(default_factory=list)
    company_description: Optional[str] = None
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'salary_range': self.salary_range,
            'description': self.description,
            'responsibilities': self.responsibilities,
            'requirements': [req.to_dict() for req in self.requirements],
            'nice_to_haves': self.nice_to_haves,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'benefits': self.benefits,
            'company_description': self.company_description,
            'raw_text': self.raw_text
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobModel':
        """Create from dictionary."""
        requirements = [
            JobRequirement(**req) for req in data.get('requirements', [])
        ]

        return cls(
            title=data.get('title', ''),
            company=data.get('company'),
            location=data.get('location'),
            job_type=data.get('job_type'),
            experience_level=data.get('experience_level'),
            salary_range=data.get('salary_range'),
            description=data.get('description'),
            responsibilities=data.get('responsibilities', []),
            requirements=requirements,
            nice_to_haves=data.get('nice_to_haves', []),
            required_skills=data.get('required_skills', []),
            preferred_skills=data.get('preferred_skills', []),
            benefits=data.get('benefits', []),
            company_description=data.get('company_description'),
            raw_text=data.get('raw_text')
        )


@dataclass
class SkillMatch:
    """Represents how well a skill matches between job and resume."""
    skill: str
    is_required: bool
    is_present: bool
    strength: str  # "strong", "weak", "missing"
    evidence: List[str] = field(default_factory=list)  # Where it appears in resume

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'skill': self.skill,
            'is_required': self.is_required,
            'is_present': self.is_present,
            'strength': self.strength,
            'evidence': self.evidence
        }


@dataclass
class GapAnalysis:
    """Analysis of gaps between job requirements and resume."""
    # Skill Analysis
    matched_skills: List[SkillMatch] = field(default_factory=list)
    missing_required_skills: List[str] = field(default_factory=list)
    missing_preferred_skills: List[str] = field(default_factory=list)
    weakly_covered_skills: List[SkillMatch] = field(default_factory=list)

    # Experience Analysis
    has_required_experience: bool = False
    experience_gap_years: Optional[float] = None
    relevant_experience_count: int = 0

    # Requirements Coverage
    total_requirements: int = 0
    met_requirements: int = 0
    coverage_percentage: float = 0.0

    # Recommendations
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    # Metadata
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'matched_skills': [skill.to_dict() for skill in self.matched_skills],
            'missing_required_skills': self.missing_required_skills,
            'missing_preferred_skills': self.missing_preferred_skills,
            'weakly_covered_skills': [skill.to_dict() for skill in self.weakly_covered_skills],
            'has_required_experience': self.has_required_experience,
            'experience_gap_years': self.experience_gap_years,
            'relevant_experience_count': self.relevant_experience_count,
            'total_requirements': self.total_requirements,
            'met_requirements': self.met_requirements,
            'coverage_percentage': self.coverage_percentage,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'suggestions': self.suggestions,
            'analysis_timestamp': self.analysis_timestamp
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GapAnalysis':
        """Create from dictionary."""
        matched_skills = [
            SkillMatch(**skill) for skill in data.get('matched_skills', [])
        ]
        weakly_covered = [
            SkillMatch(**skill) for skill in data.get('weakly_covered_skills', [])
        ]

        return cls(
            matched_skills=matched_skills,
            missing_required_skills=data.get('missing_required_skills', []),
            missing_preferred_skills=data.get('missing_preferred_skills', []),
            weakly_covered_skills=weakly_covered,
            has_required_experience=data.get('has_required_experience', False),
            experience_gap_years=data.get('experience_gap_years'),
            relevant_experience_count=data.get('relevant_experience_count', 0),
            total_requirements=data.get('total_requirements', 0),
            met_requirements=data.get('met_requirements', 0),
            coverage_percentage=data.get('coverage_percentage', 0.0),
            strengths=data.get('strengths', []),
            weaknesses=data.get('weaknesses', []),
            suggestions=data.get('suggestions', []),
            analysis_timestamp=data.get('analysis_timestamp', datetime.now().isoformat())
        )

# ============================================================================
# Resume Optimization Models
# ============================================================================

class ChangeType(str, Enum):
    """Type of resume change made during optimization."""
    SUMMARY = "summary"
    HEADLINE = "headline"
    EXPERIENCE_BULLET = "experience_bullet"
    SKILLS_SECTION = "skills_section"
    EDUCATION = "education"
    OTHER = "other"


class ChangeStatus(str, Enum):
    """Status of a resume change during the review process."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EDITED = "edited"


@dataclass
class ResumeChange:
    """Represents a single change made to a resume during optimization."""
    id: str
    change_type: ChangeType
    location: str  # e.g., "experience[0].bullets[2]" or "summary"
    before: str
    after: str
    rationale: str  # Short explanation for the change
    status: ChangeStatus = ChangeStatus.PENDING  # Review status
    is_flagged: bool = False  # Whether this change is flagged as risky
    edited_value: Optional[str] = None  # User-edited version of 'after' if status is EDITED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'change_type': self.change_type.value if isinstance(self.change_type, ChangeType) else self.change_type,
            'location': self.location,
            'before': self.before,
            'after': self.after,
            'rationale': self.rationale,
            'status': self.status.value if isinstance(self.status, ChangeStatus) else self.status,
            'is_flagged': self.is_flagged,
            'edited_value': self.edited_value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResumeChange':
        """Create from dictionary."""
        # Handle backward compatibility for old data without status
        status_value = data.get('status', ChangeStatus.PENDING.value)
        status = ChangeStatus(status_value) if isinstance(status_value, str) else status_value

        return cls(
            id=data['id'],
            change_type=ChangeType(data['change_type']),
            location=data['location'],
            before=data['before'],
            after=data['after'],
            rationale=data['rationale'],
            status=status,
            is_flagged=data.get('is_flagged', False),
            edited_value=data.get('edited_value')
        )

    def get_final_value(self) -> str:
        """Get the final value to use (edited_value if edited, otherwise after)."""
        if self.status == ChangeStatus.EDITED and self.edited_value is not None:
            return self.edited_value
        return self.after

    def is_accepted(self) -> bool:
        """Check if change is accepted or edited (both count as approved)."""
        return self.status in (ChangeStatus.ACCEPTED, ChangeStatus.EDITED)

    def is_rejected(self) -> bool:
        """Check if change is rejected."""
        return self.status == ChangeStatus.REJECTED

    def is_pending(self) -> bool:
        """Check if change is still pending review."""
        return self.status == ChangeStatus.PENDING


@dataclass
class ResumeOptimizationResult:
    """Result of resume optimization process."""
    original_resume: ResumeModel
    optimized_resume: ResumeModel
    changes: List[ResumeChange] = field(default_factory=list)
    summary_of_improvements: List[str] = field(default_factory=list)
    optimization_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    style_used: str = "balanced"  # "conservative", "balanced", "aggressive"
    authenticity_report: Optional[Dict[str, Any]] = None  # LLM-based authenticity report
    metrics: Optional[Dict[str, Any]] = None  # Quantitative quality metrics

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'original_resume': self.original_resume.to_dict(),
            'optimized_resume': self.optimized_resume.to_dict(),
            'changes': [change.to_dict() for change in self.changes],
            'summary_of_improvements': self.summary_of_improvements,
            'optimization_timestamp': self.optimization_timestamp,
            'style_used': self.style_used,
            'authenticity_report': self.authenticity_report,
            'metrics': self.metrics
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResumeOptimizationResult':
        """Create from dictionary."""
        changes = [ResumeChange.from_dict(c) for c in data.get('changes', [])]

        return cls(
            original_resume=ResumeModel.from_dict(data['original_resume']),
            optimized_resume=ResumeModel.from_dict(data['optimized_resume']),
            changes=changes,
            summary_of_improvements=data.get('summary_of_improvements', []),
            optimization_timestamp=data.get('optimization_timestamp', datetime.now().isoformat()),
            style_used=data.get('style_used', 'balanced'),
            authenticity_report=data.get('authenticity_report'),
            metrics=data.get('metrics')
        )
    
    def get_change_count_by_type(self) -> Dict[str, int]:
        """Get count of changes by type."""
        counts = {}
        for change in self.changes:
            change_type = change.change_type.value if isinstance(change.change_type, ChangeType) else change.change_type
            counts[change_type] = counts.get(change_type, 0) + 1
        return counts
    
    def get_total_changes(self) -> int:
        """Get total number of changes."""
        return len(self.changes)

    def get_potentially_risky_changes(self) -> List[Tuple['ResumeChange', List[str]]]:
        """
        Get changes that may contain fabricated content.

        Uses heuristic checks to identify changes that introduce:
        - New metrics/numbers
        - New organizations
        - New technologies
        - Significantly expanded content

        Returns:
            List of tuples (change, list of warning messages) for risky changes
        """
        from utils.authenticity_checks import get_potentially_risky_changes
        return get_potentially_risky_changes(self.changes, self.original_resume)

    def get_authenticity_report(self) -> dict:
        """
        Get comprehensive authenticity report.

        Prioritizes LLM-based report if available, falls back to heuristic-based.

        Returns:
            Dictionary with:
            - total_changes: Total number of changes analyzed
            - flagged_changes: Number of flagged changes/issues
            - flag_rate: Percentage of changes flagged
            - is_safe: Boolean indicating if all changes appear safe
            - recommendations: List of recommendations for review
            - issues_found: List of specific issues (if LLM-based)
            - overall_risk_level: Risk level (if LLM-based)
            - summary: Summary text (if LLM-based)
            - risky_changes: List of (change, warnings) tuples (if heuristic-based)
            - warning_categories: Breakdown by warning type
        """
        # Use LLM-based report if available
        if self.authenticity_report is not None:
            # Enrich with additional metrics for UI compatibility
            report = self.authenticity_report.copy()

            # Add computed fields for backward compatibility
            issues_count = len(report.get('issues_found', []))
            report['flagged_changes'] = issues_count
            report['total_changes'] = report.get('total_changes_analyzed', len(self.changes))

            if report['total_changes'] > 0:
                report['flag_rate'] = (issues_count / report['total_changes']) * 100
            else:
                report['flag_rate'] = 0.0

            # Map issues to categories for UI
            warning_categories = {}
            for issue in report.get('issues_found', []):
                issue_type = issue.get('type', 'unknown')
                warning_categories[issue_type] = warning_categories.get(issue_type, 0) + 1

            report['warning_categories'] = warning_categories

            return report

        # Fall back to heuristic-based report
        from utils.authenticity_checks import generate_authenticity_report
        return generate_authenticity_report(self.changes, self.original_resume)

    def has_llm_authenticity_report(self) -> bool:
        """Check if LLM-based authenticity report is available."""
        return self.authenticity_report is not None

    def get_authenticity_issues(self) -> List[Dict[str, Any]]:
        """
        Get list of authenticity issues from LLM report.

        Returns:
            List of issue dictionaries, empty if no LLM report available
        """
        if self.authenticity_report:
            return self.authenticity_report.get('issues_found', [])
        return []

    def get_accepted_changes(self) -> List[ResumeChange]:
        """Get all accepted or edited changes."""
        return [c for c in self.changes if c.is_accepted()]

    def get_rejected_changes(self) -> List[ResumeChange]:
        """Get all rejected changes."""
        return [c for c in self.changes if c.is_rejected()]

    def get_pending_changes(self) -> List[ResumeChange]:
        """Get all pending changes."""
        return [c for c in self.changes if c.is_pending()]

    def get_flagged_changes(self) -> List[ResumeChange]:
        """Get all flagged changes regardless of status."""
        return [c for c in self.changes if c.is_flagged]

    def get_change_stats(self) -> Dict[str, int]:
        """Get statistics about change statuses."""
        stats = {
            'total': len(self.changes),
            'accepted': len(self.get_accepted_changes()),
            'rejected': len(self.get_rejected_changes()),
            'pending': len(self.get_pending_changes()),
            'flagged': len(self.get_flagged_changes())
        }
        return stats

    def all_changes_reviewed(self) -> bool:
        """Check if all changes have been reviewed (no pending)."""
        return len(self.get_pending_changes()) == 0

    def has_any_accepted_changes(self) -> bool:
        """Check if there are any accepted changes."""
        return len(self.get_accepted_changes()) > 0
