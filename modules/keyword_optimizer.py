"""
Advanced Keyword Optimization Intelligence

Provides sophisticated keyword analysis, density optimization,
semantic variation detection, and strategic placement recommendations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
import re
from collections import Counter
from modules.models import ResumeModel, JobModel


@dataclass
class KeywordAnalysis:
    """Analysis of a single keyword."""
    keyword: str
    frequency_in_job: int
    frequency_in_resume: int
    target_density: Tuple[int, int]  # (min, max) occurrences
    current_density: int
    is_required: bool = False
    is_preferred: bool = False

    # Semantic variations found
    variations: List[str] = field(default_factory=list)
    variations_in_resume: List[str] = field(default_factory=list)

    # Context analysis
    appears_in_summary: bool = False
    appears_in_experience: bool = False
    appears_in_skills: bool = False

    # Weighting
    importance_weight: float = 1.0  # 1.0 = normal, 2.0 = critical, 0.5 = nice-to-have

    @property
    def status(self) -> str:
        """Get keyword status."""
        if self.current_density == 0:
            return "missing"
        elif self.current_density < self.target_density[0]:
            return "underutilized"
        elif self.current_density > self.target_density[1]:
            return "overstuffed"
        else:
            return "optimal"

    @property
    def recommendation(self) -> str:
        """Get optimization recommendation."""
        if self.status == "missing":
            return f"Add {self.target_density[0]}-{self.target_density[1]} mentions"
        elif self.status == "underutilized":
            gap = self.target_density[0] - self.current_density
            return f"Add {gap} more mention(s)"
        elif self.status == "overstuffed":
            excess = self.current_density - self.target_density[1]
            return f"Remove {excess} mention(s) to avoid keyword stuffing"
        else:
            return "Optimal usage"

    @property
    def placement_quality(self) -> float:
        """
        Score placement quality (0.0 to 1.0).

        Best practice: Important keywords should appear in summary, experience, and skills.
        """
        score = 0.0

        # Summary: 40% of score (most important)
        if self.appears_in_summary:
            score += 0.4

        # Experience: 40% of score (context and proof)
        if self.appears_in_experience:
            score += 0.4

        # Skills: 20% of score (explicit declaration)
        if self.appears_in_skills:
            score += 0.2

        return score


@dataclass
class KeywordOptimizationReport:
    """Complete keyword optimization report."""

    # Individual keyword analyses
    keywords: List[KeywordAnalysis] = field(default_factory=list)

    # Summary statistics
    total_keywords_analyzed: int = 0
    missing_keywords: int = 0
    underutilized_keywords: int = 0
    optimal_keywords: int = 0
    overstuffed_keywords: int = 0

    # Overall scores
    keyword_coverage_score: float = 0.0  # 0.0 to 1.0
    keyword_density_score: float = 0.0  # 0.0 to 1.0
    keyword_placement_score: float = 0.0  # 0.0 to 1.0
    overall_keyword_score: float = 0.0  # 0.0 to 1.0

    # Strategic insights
    critical_missing_keywords: List[str] = field(default_factory=list)
    recommended_additions: List[Tuple[str, str]] = field(default_factory=list)  # (keyword, location)
    recommended_removals: List[str] = field(default_factory=list)

    # Semantic variations
    variation_suggestions: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def grade(self) -> str:
        """Get letter grade."""
        if self.overall_keyword_score >= 0.90:
            return "A"
        elif self.overall_keyword_score >= 0.80:
            return "B"
        elif self.overall_keyword_score >= 0.70:
            return "C"
        elif self.overall_keyword_score >= 0.60:
            return "D"
        else:
            return "F"


class KeywordOptimizer:
    """
    Advanced keyword optimization engine.

    Analyzes keyword usage, density, placement, and provides
    strategic recommendations for ATS optimization.
    """

    # Common semantic variations for technical terms
    SEMANTIC_VARIATIONS = {
        'python': ['python 3', 'python programming', 'pythonic', 'python development'],
        'javascript': ['js', 'javascript es6', 'javascript development', 'ecmascript'],
        'react': ['reactjs', 'react.js', 'react native'],
        'node': ['nodejs', 'node.js'],
        'aws': ['amazon web services', 'aws cloud'],
        'kubernetes': ['k8s', 'container orchestration'],
        'docker': ['containerization', 'docker containers'],
        'agile': ['scrum', 'agile methodology', 'agile development'],
        'machine learning': ['ml', 'machine learning algorithms'],
        'artificial intelligence': ['ai', 'artificial intelligence'],
        'sql': ['structured query language', 'sql database'],
        'ci/cd': ['continuous integration', 'continuous deployment', 'ci cd'],
        'rest': ['rest api', 'restful api', 'rest apis'],
        'git': ['version control', 'git version control'],
    }

    def __init__(self):
        """Initialize keyword optimizer."""
        pass

    def analyze(
        self,
        resume: ResumeModel,
        job: JobModel,
        target_density_multiplier: float = 1.5
    ) -> KeywordOptimizationReport:
        """
        Perform comprehensive keyword analysis.

        Args:
            resume: Resume to analyze
            job: Job description to optimize for
            target_density_multiplier: How many times more than job description
                                      should keyword appear in resume (default: 1.5x)

        Returns:
            KeywordOptimizationReport with detailed analysis
        """
        report = KeywordOptimizationReport()

        # Get all keywords from job
        all_job_keywords = self._extract_job_keywords(job)

        # Analyze each keyword
        for keyword, job_freq in all_job_keywords.items():
            analysis = self._analyze_keyword(
                keyword=keyword,
                job_freq=job_freq,
                resume=resume,
                job=job,
                target_multiplier=target_density_multiplier
            )
            report.keywords.append(analysis)

        # Calculate summary statistics
        self._calculate_statistics(report)

        # Generate strategic insights
        self._generate_insights(report, job)

        return report

    def _extract_job_keywords(self, job: JobModel) -> Dict[str, int]:
        """
        Extract keywords from job description with frequency counts.

        Returns:
            Dictionary mapping keyword to frequency in job description
        """
        keywords = Counter()

        # Add required skills (high weight)
        for skill in job.required_skills:
            keywords[skill.lower()] += 3  # Weight required skills more

        # Add preferred skills
        for skill in job.preferred_skills:
            keywords[skill.lower()] += 1

        # Extract from job description text
        # Note: In production, you'd parse the actual job description text
        # For now, we use the structured data

        return dict(keywords)

    def _analyze_keyword(
        self,
        keyword: str,
        job_freq: int,
        resume: ResumeModel,
        job: JobModel,
        target_multiplier: float
    ) -> KeywordAnalysis:
        """Analyze a single keyword."""

        # Count occurrences in resume
        resume_text = self._get_resume_text(resume).lower()
        current_count = resume_text.count(keyword.lower())

        # Find semantic variations
        variations = self._find_variations(keyword)
        variations_in_resume = [
            var for var in variations
            if var.lower() in resume_text
        ]

        # Add variation counts to current count
        for var in variations_in_resume:
            current_count += resume_text.count(var.lower())

        # Calculate target density
        # Rule: Keyword should appear 1.5x more in resume than in job description
        # Minimum: 2 occurrences for required skills, 1 for preferred
        # Maximum: 5x job frequency (to avoid stuffing)
        is_required = keyword.lower() in [s.lower() for s in job.required_skills]
        is_preferred = keyword.lower() in [s.lower() for s in job.preferred_skills]

        if is_required:
            min_target = max(2, int(job_freq * target_multiplier))
            importance_weight = 2.0
        elif is_preferred:
            min_target = max(1, int(job_freq * target_multiplier * 0.7))
            importance_weight = 1.0
        else:
            min_target = 1
            importance_weight = 0.5

        max_target = min(min_target + 3, job_freq * 5)  # Cap at 5x or +3

        # Analyze placement
        summary_text = (resume.summary or '').lower() + (resume.headline or '').lower()
        appears_in_summary = keyword.lower() in summary_text

        experience_text = ' '.join([
            ' '.join(exp.bullets or [])
            for exp in resume.experiences
        ]).lower()
        appears_in_experience = keyword.lower() in experience_text

        skills_text = ' '.join(resume.skills).lower()
        appears_in_skills = keyword.lower() in skills_text

        return KeywordAnalysis(
            keyword=keyword,
            frequency_in_job=job_freq,
            frequency_in_resume=current_count,
            target_density=(min_target, max_target),
            current_density=current_count,
            is_required=is_required,
            is_preferred=is_preferred,
            variations=variations,
            variations_in_resume=variations_in_resume,
            appears_in_summary=appears_in_summary,
            appears_in_experience=appears_in_experience,
            appears_in_skills=appears_in_skills,
            importance_weight=importance_weight
        )

    def _find_variations(self, keyword: str) -> List[str]:
        """Find semantic variations of a keyword."""
        keyword_lower = keyword.lower()

        # Check predefined variations
        if keyword_lower in self.SEMANTIC_VARIATIONS:
            return self.SEMANTIC_VARIATIONS[keyword_lower]

        # Generate automatic variations
        variations = []

        # Add plural/singular
        if keyword_lower.endswith('s'):
            variations.append(keyword_lower[:-1])
        else:
            variations.append(keyword_lower + 's')

        # Add common suffixes for technologies
        if not any(keyword_lower.endswith(suffix) for suffix in ['.js', 'js', 'py']):
            variations.append(f"{keyword_lower} programming")
            variations.append(f"{keyword_lower} development")

        return variations

    def _calculate_statistics(self, report: KeywordOptimizationReport):
        """Calculate summary statistics for report."""
        report.total_keywords_analyzed = len(report.keywords)

        if report.total_keywords_analyzed == 0:
            return

        # Count by status
        for kw in report.keywords:
            if kw.status == "missing":
                report.missing_keywords += 1
            elif kw.status == "underutilized":
                report.underutilized_keywords += 1
            elif kw.status == "optimal":
                report.optimal_keywords += 1
            elif kw.status == "overstuffed":
                report.overstuffed_keywords += 1

        # Calculate coverage score (what % of keywords are present)
        present_keywords = [kw for kw in report.keywords if kw.current_density > 0]
        report.keyword_coverage_score = len(present_keywords) / report.total_keywords_analyzed

        # Calculate density score (what % of keywords have optimal density)
        optimal_density = [kw for kw in report.keywords if kw.status == "optimal"]
        report.keyword_density_score = len(optimal_density) / report.total_keywords_analyzed

        # Calculate placement score (average placement quality, weighted by importance)
        total_weight = sum(kw.importance_weight for kw in report.keywords)
        weighted_placement = sum(
            kw.placement_quality * kw.importance_weight
            for kw in report.keywords
        )
        report.keyword_placement_score = weighted_placement / total_weight if total_weight > 0 else 0

        # Overall score (weighted average)
        # Coverage: 30%, Density: 40%, Placement: 30%
        report.overall_keyword_score = (
            report.keyword_coverage_score * 0.3 +
            report.keyword_density_score * 0.4 +
            report.keyword_placement_score * 0.3
        )

    def _generate_insights(self, report: KeywordOptimizationReport, job: JobModel):
        """Generate strategic optimization insights."""

        # Critical missing keywords (required skills not present)
        for kw in report.keywords:
            if kw.is_required and kw.current_density == 0:
                report.critical_missing_keywords.append(kw.keyword)

        # Recommended additions (missing or underutilized keywords)
        for kw in report.keywords:
            if kw.status == "missing":
                # Suggest where to add
                if kw.is_required:
                    location = "summary, experience, and skills sections"
                elif kw.appears_in_experience:
                    location = "skills section and summary"
                else:
                    location = "skills section"

                report.recommended_additions.append((kw.keyword, location))

            elif kw.status == "underutilized":
                # Suggest where to add more
                if not kw.appears_in_summary and kw.is_required:
                    report.recommended_additions.append((kw.keyword, "professional summary"))
                elif not kw.appears_in_experience:
                    report.recommended_additions.append((kw.keyword, "relevant experience bullets"))

        # Recommended removals (overstuffed keywords)
        for kw in report.keywords:
            if kw.status == "overstuffed":
                report.recommended_removals.append(kw.keyword)

        # Variation suggestions
        for kw in report.keywords:
            if kw.variations and not kw.variations_in_resume:
                report.variation_suggestions[kw.keyword] = kw.variations[:3]

    def _get_resume_text(self, resume: ResumeModel) -> str:
        """Get all text from resume."""
        parts = []

        if resume.summary:
            parts.append(resume.summary)
        if resume.headline:
            parts.append(resume.headline)

        for exp in resume.experiences:
            if exp.title:
                parts.append(exp.title)
            if exp.company:
                parts.append(exp.company)
            if exp.bullets:
                parts.extend(exp.bullets)

        if resume.skills:
            parts.extend(resume.skills)

        for edu in resume.education:
            if edu.degree:
                parts.append(edu.degree)
            if edu.institution:
                parts.append(edu.institution)

        return " ".join(parts)

    def get_keyword_heatmap(
        self,
        resume: ResumeModel,
        job: JobModel
    ) -> Dict[str, Dict[str, int]]:
        """
        Generate keyword heatmap showing where keywords appear.

        Returns:
            Dictionary mapping section name to keyword counts
        """
        heatmap = {
            'summary': {},
            'experience': {},
            'skills': {},
            'education': {}
        }

        # Get all job keywords
        all_keywords = self._extract_job_keywords(job)

        # Count in each section
        for keyword in all_keywords.keys():
            keyword_lower = keyword.lower()

            # Summary
            summary_text = (resume.summary or '').lower() + (resume.headline or '').lower()
            heatmap['summary'][keyword] = summary_text.count(keyword_lower)

            # Experience
            exp_text = ' '.join([
                ' '.join(exp.bullets or [])
                for exp in resume.experiences
            ]).lower()
            heatmap['experience'][keyword] = exp_text.count(keyword_lower)

            # Skills
            skills_text = ' '.join(resume.skills).lower()
            heatmap['skills'][keyword] = skills_text.count(keyword_lower)

            # Education
            edu_text = ' '.join([
                f"{edu.degree} {edu.institution}"
                for edu in resume.education
            ]).lower()
            heatmap['education'][keyword] = edu_text.count(keyword_lower)

        return heatmap


def analyze_keywords(
    resume: ResumeModel,
    job: JobModel,
    target_density: float = 1.5
) -> KeywordOptimizationReport:
    """
    Analyze keyword optimization.

    Args:
        resume: Resume to analyze
        job: Job to optimize for
        target_density: Target density multiplier (default: 1.5x)

    Returns:
        KeywordOptimizationReport
    """
    optimizer = KeywordOptimizer()
    return optimizer.analyze(resume, job, target_density)


def get_keyword_recommendations(
    resume: ResumeModel,
    job: JobModel
) -> List[str]:
    """
    Get quick keyword recommendations.

    Returns:
        List of actionable recommendations
    """
    report = analyze_keywords(resume, job)
    recommendations = []

    # Critical missing
    if report.critical_missing_keywords:
        recommendations.append(
            f"🔴 CRITICAL: Add required skills: {', '.join(report.critical_missing_keywords[:5])}"
        )

    # Top additions
    if report.recommended_additions:
        for keyword, location in report.recommended_additions[:3]:
            recommendations.append(f"➕ Add '{keyword}' to {location}")

    # Removals
    if report.recommended_removals:
        recommendations.append(
            f"➖ Reduce usage of: {', '.join(report.recommended_removals[:3])} (keyword stuffing)"
        )

    # Variations
    if report.variation_suggestions:
        for keyword, variations in list(report.variation_suggestions.items())[:2]:
            recommendations.append(
                f"🔄 Try variations of '{keyword}': {', '.join(variations[:2])}"
            )

    # Placement improvements
    poor_placement = [
        kw for kw in report.keywords
        if kw.placement_quality < 0.5 and kw.is_required
    ]
    if poor_placement:
        recommendations.append(
            f"📍 Improve placement of: {', '.join([kw.keyword for kw in poor_placement[:3]])}"
        )

    return recommendations
