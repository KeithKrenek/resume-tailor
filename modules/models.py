"""Data models for Resume Tailor application."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
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
