"""
Comprehensive Resume Scoring Module

Provides detailed scoring across multiple dimensions to help users
understand resume quality and areas for improvement.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import re
from modules.models import ResumeModel, JobModel


@dataclass
class ScoreComponent:
    """Individual score component."""
    score: float  # 0-100
    max_score: float = 100.0
    weight: float = 1.0
    label: str = ""
    details: str = ""
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

    @property
    def percentage(self) -> float:
        """Get score as percentage."""
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0

    @property
    def weighted_score(self) -> float:
        """Get weighted score."""
        return self.percentage * self.weight


@dataclass
class ResumeScore:
    """Complete resume scoring breakdown."""
    overall_score: float  # 0-100
    ats_score: ScoreComponent
    keyword_match: ScoreComponent
    length_score: ScoreComponent
    readability_score: ScoreComponent
    impact_score: ScoreComponent
    completeness_score: ScoreComponent

    @property
    def grade(self) -> str:
        """Get letter grade based on overall score."""
        if self.overall_score >= 90:
            return "A"
        elif self.overall_score >= 80:
            return "B"
        elif self.overall_score >= 70:
            return "C"
        elif self.overall_score >= 60:
            return "D"
        else:
            return "F"

    @property
    def status(self) -> str:
        """Get status message."""
        if self.overall_score >= 85:
            return "Excellent - Ready to submit"
        elif self.overall_score >= 75:
            return "Good - Minor improvements recommended"
        elif self.overall_score >= 65:
            return "Fair - Several improvements needed"
        else:
            return "Needs Work - Major improvements required"


class ResumeScorer:
    """Comprehensive resume scoring engine."""

    # Weights for overall score calculation
    WEIGHTS = {
        'ats': 0.25,
        'keyword_match': 0.20,
        'length': 0.15,
        'readability': 0.15,
        'impact': 0.15,
        'completeness': 0.10
    }

    def score_resume(
        self,
        resume: ResumeModel,
        job: JobModel = None
    ) -> ResumeScore:
        """
        Score a resume across multiple dimensions.

        Args:
            resume: Resume to score
            job: Optional job model for keyword matching

        Returns:
            ResumeScore with detailed breakdown
        """
        # Calculate individual scores
        ats_score = self._score_ats_compatibility(resume)
        keyword_score = self._score_keyword_match(resume, job) if job else None
        length_score = self._score_length(resume)
        readability_score = self._score_readability(resume)
        impact_score = self._score_impact(resume)
        completeness_score = self._score_completeness(resume)

        # Calculate overall score
        components = {
            'ats': ats_score,
            'keyword_match': keyword_score or ScoreComponent(score=0, label="N/A"),
            'length': length_score,
            'readability': readability_score,
            'impact': impact_score,
            'completeness': completeness_score
        }

        # Weighted average (excluding keyword match if no job provided)
        total_weight = sum(
            self.WEIGHTS[k] for k, v in components.items()
            if not (k == 'keyword_match' and job is None)
        )

        overall = sum(
            comp.percentage * self.WEIGHTS[k]
            for k, comp in components.items()
            if not (k == 'keyword_match' and job is None)
        ) / total_weight if total_weight > 0 else 0

        return ResumeScore(
            overall_score=overall,
            ats_score=ats_score,
            keyword_match=keyword_score or ScoreComponent(
                score=0,
                label="Keyword Match",
                details="No job description provided for comparison"
            ),
            length_score=length_score,
            readability_score=readability_score,
            impact_score=impact_score,
            completeness_score=completeness_score
        )

    def _score_ats_compatibility(self, resume: ResumeModel) -> ScoreComponent:
        """Score ATS compatibility (0-100)."""
        score = 100.0
        recommendations = []
        details_parts = []

        # Check for contact information
        if not resume.email:
            score -= 15
            recommendations.append("Add email address")
            details_parts.append("❌ Missing email")
        else:
            details_parts.append("✓ Email present")

        if not resume.phone:
            score -= 10
            recommendations.append("Add phone number")
            details_parts.append("❌ Missing phone")
        else:
            details_parts.append("✓ Phone present")

        # Check for standard sections
        if not resume.experiences or len(resume.experiences) == 0:
            score -= 25
            recommendations.append("Add work experience")
            details_parts.append("❌ No work experience")
        else:
            details_parts.append(f"✓ {len(resume.experiences)} positions")

        if not resume.skills or len(resume.skills) == 0:
            score -= 20
            recommendations.append("Add skills section")
            details_parts.append("❌ No skills listed")
        else:
            details_parts.append(f"✓ {len(resume.skills)} skills")

        if not resume.education or len(resume.education) == 0:
            score -= 15
            recommendations.append("Add education")
            details_parts.append("❌ No education")
        else:
            details_parts.append(f"✓ {len(resume.education)} degrees")

        # Check for proper date formatting in experiences
        date_issues = 0
        for exp in resume.experiences:
            if not exp.start_date and not exp.end_date:
                date_issues += 1

        if date_issues > 0:
            score -= min(10, date_issues * 2)
            recommendations.append(f"Add dates to {date_issues} experience(s)")
            details_parts.append(f"⚠️ {date_issues} positions missing dates")

        # Check for bullet points in experiences
        experiences_without_bullets = sum(
            1 for exp in resume.experiences if not exp.bullets or len(exp.bullets) == 0
        )
        if experiences_without_bullets > 0:
            score -= min(15, experiences_without_bullets * 5)
            recommendations.append(f"Add bullet points to {experiences_without_bullets} position(s)")

        return ScoreComponent(
            score=max(0, score),
            label="ATS Compatibility",
            details=" | ".join(details_parts),
            recommendations=recommendations
        )

    def _score_keyword_match(self, resume: ResumeModel, job: JobModel) -> ScoreComponent:
        """Score keyword match with job description (0-100)."""
        if not job:
            return ScoreComponent(score=0, label="Keyword Match", details="No job provided")

        # Get all keywords from job
        required_keywords = set(skill.lower() for skill in job.required_skills)
        preferred_keywords = set(skill.lower() for skill in job.preferred_skills)
        all_job_keywords = required_keywords | preferred_keywords

        if not all_job_keywords:
            return ScoreComponent(
                score=0,
                label="Keyword Match",
                details="No keywords found in job description"
            )

        # Get all text from resume
        resume_text = self._get_resume_text(resume).lower()

        # Count matches
        required_matches = sum(1 for kw in required_keywords if kw in resume_text)
        preferred_matches = sum(1 for kw in preferred_keywords if kw in resume_text)

        # Calculate score (required skills worth more)
        required_score = (required_matches / len(required_keywords) * 70) if required_keywords else 0
        preferred_score = (preferred_matches / len(preferred_keywords) * 30) if preferred_keywords else 0

        score = required_score + preferred_score

        # Generate recommendations
        recommendations = []
        missing_required = required_keywords - set(
            kw for kw in required_keywords if kw in resume_text
        )
        if missing_required:
            recommendations.append(
                f"Add missing required skills: {', '.join(list(missing_required)[:3])}"
            )

        details = (
            f"Required: {required_matches}/{len(required_keywords)} | "
            f"Preferred: {preferred_matches}/{len(preferred_keywords)}"
        )

        return ScoreComponent(
            score=score,
            label="Keyword Match",
            details=details,
            recommendations=recommendations
        )

    def _score_length(self, resume: ResumeModel) -> ScoreComponent:
        """Score resume length (0-100)."""
        # Estimate page count based on content
        total_chars = len(self._get_resume_text(resume))

        # Rough estimate: 3000 chars per page
        estimated_pages = total_chars / 3000

        recommendations = []

        # Optimal: 1.5-2 pages (4500-6000 chars)
        if 4500 <= total_chars <= 6000:
            score = 100
            details = f"Optimal length (~{estimated_pages:.1f} pages, {total_chars:,} chars)"
        elif 3000 <= total_chars < 4500:
            # 1-1.5 pages - good for junior roles
            score = 95
            details = f"Good length (~{estimated_pages:.1f} pages, {total_chars:,} chars)"
            recommendations.append("Consider adding more detail if you're experienced")
        elif 6000 < total_chars <= 7500:
            # 2-2.5 pages - acceptable for senior roles
            score = 85
            details = f"Slightly long (~{estimated_pages:.1f} pages, {total_chars:,} chars)"
            recommendations.append("Consider condensing to 2 pages or less")
        elif total_chars < 3000:
            # Too short
            score = 60
            details = f"Too short (~{estimated_pages:.1f} pages, {total_chars:,} chars)"
            recommendations.append("Add more detail about your experience")
        else:
            # Too long (>2.5 pages)
            score = 50
            details = f"Too long (~{estimated_pages:.1f} pages, {total_chars:,} chars)"
            recommendations.append("Reduce to 2 pages maximum")
            recommendations.append("Remove older or less relevant experience")

        return ScoreComponent(
            score=score,
            label="Length",
            details=details,
            recommendations=recommendations
        )

    def _score_readability(self, resume: ResumeModel) -> ScoreComponent:
        """Score readability and formatting (0-100)."""
        score = 100.0
        recommendations = []
        details_parts = []

        # Check bullet point count per experience
        bullets_issues = 0
        for exp in resume.experiences:
            bullet_count = len(exp.bullets) if exp.bullets else 0
            if bullet_count < 2:
                bullets_issues += 1
                score -= 5
            elif bullet_count > 7:
                bullets_issues += 1
                score -= 3
                recommendations.append(f"Reduce bullets in {exp.title} to 5-7")

        if bullets_issues == 0:
            details_parts.append("✓ Bullet counts optimal")
        else:
            details_parts.append(f"⚠️ {bullets_issues} positions with suboptimal bullet count")

        # Check for overly long bullets
        long_bullets = 0
        for exp in resume.experiences:
            if exp.bullets:
                for bullet in exp.bullets:
                    if len(bullet) > 200:
                        long_bullets += 1

        if long_bullets > 0:
            score -= min(15, long_bullets * 3)
            recommendations.append(f"Shorten {long_bullets} overly long bullet(s)")
            details_parts.append(f"⚠️ {long_bullets} bullets too long")
        else:
            details_parts.append("✓ Bullet lengths good")

        # Check for action verbs
        action_verb_count = self._count_action_verbs(resume)
        total_bullets = sum(len(exp.bullets) for exp in resume.experiences if exp.bullets)

        if total_bullets > 0:
            action_verb_ratio = action_verb_count / total_bullets
            if action_verb_ratio < 0.5:
                score -= 10
                recommendations.append("Start more bullets with strong action verbs")
                details_parts.append(f"⚠️ Only {action_verb_ratio:.0%} bullets use action verbs")
            else:
                details_parts.append(f"✓ {action_verb_ratio:.0%} bullets use action verbs")

        return ScoreComponent(
            score=max(0, score),
            label="Readability",
            details=" | ".join(details_parts),
            recommendations=recommendations
        )

    def _score_impact(self, resume: ResumeModel) -> ScoreComponent:
        """Score impact and achievement focus (0-100)."""
        score = 100.0
        recommendations = []
        details_parts = []

        # Count quantified achievements (numbers, percentages, dollar amounts)
        quantified_count = 0
        total_bullets = 0

        number_pattern = re.compile(r'\d+[%$]?|\$\d+|[0-9,]+')

        for exp in resume.experiences:
            if exp.bullets:
                for bullet in exp.bullets:
                    total_bullets += 1
                    if number_pattern.search(bullet):
                        quantified_count += 1

        if total_bullets > 0:
            quantified_ratio = quantified_count / total_bullets

            if quantified_ratio >= 0.4:
                details_parts.append(f"✓ {quantified_ratio:.0%} bullets quantified")
            elif quantified_ratio >= 0.2:
                score -= 15
                recommendations.append("Add more quantified achievements")
                details_parts.append(f"⚠️ Only {quantified_ratio:.0%} bullets quantified")
            else:
                score -= 30
                recommendations.append("Add numbers and metrics to demonstrate impact")
                details_parts.append(f"❌ Only {quantified_ratio:.0%} bullets quantified")

        # Check for achievement-focused language
        achievement_keywords = [
            'increased', 'decreased', 'improved', 'reduced', 'achieved',
            'delivered', 'exceeded', 'generated', 'saved', 'won'
        ]

        achievement_count = 0
        resume_text = self._get_resume_text(resume).lower()
        for keyword in achievement_keywords:
            achievement_count += resume_text.count(keyword)

        if achievement_count >= 5:
            details_parts.append(f"✓ {achievement_count} achievement keywords")
        else:
            score -= 10
            recommendations.append("Use more achievement-focused language")
            details_parts.append(f"⚠️ Only {achievement_count} achievement keywords")

        # Check for passive voice (basic check)
        passive_indicators = ['was', 'were', 'been', 'being']
        passive_count = sum(resume_text.count(word) for word in passive_indicators)

        if passive_count > 10:
            score -= 10
            recommendations.append("Reduce passive voice, use active language")
            details_parts.append(f"⚠️ {passive_count} passive voice indicators")

        return ScoreComponent(
            score=max(0, score),
            label="Impact",
            details=" | ".join(details_parts),
            recommendations=recommendations
        )

    def _score_completeness(self, resume: ResumeModel) -> ScoreComponent:
        """Score resume completeness (0-100)."""
        score = 0.0
        max_points = 0.0
        recommendations = []
        details_parts = []

        # Name (required)
        max_points += 10
        if resume.name:
            score += 10
            details_parts.append("✓ Name")
        else:
            recommendations.append("Add your name")
            details_parts.append("❌ Name missing")

        # Contact info (required)
        max_points += 20
        if resume.email:
            score += 10
            details_parts.append("✓ Email")
        else:
            recommendations.append("Add email")
            details_parts.append("❌ Email missing")

        if resume.phone:
            score += 10
            details_parts.append("✓ Phone")
        else:
            recommendations.append("Add phone number")

        # Professional summary/headline
        max_points += 15
        if resume.summary:
            score += 10
            details_parts.append("✓ Summary")
        else:
            recommendations.append("Add professional summary")

        if resume.headline:
            score += 5
            details_parts.append("✓ Headline")
        else:
            recommendations.append("Add professional headline")

        # Experience
        max_points += 25
        if resume.experiences and len(resume.experiences) >= 2:
            score += 25
            details_parts.append(f"✓ {len(resume.experiences)} positions")
        elif resume.experiences and len(resume.experiences) == 1:
            score += 15
            recommendations.append("Add more work experience if applicable")
        else:
            recommendations.append("Add work experience")
            details_parts.append("❌ No experience")

        # Skills
        max_points += 15
        if resume.skills and len(resume.skills) >= 5:
            score += 15
            details_parts.append(f"✓ {len(resume.skills)} skills")
        elif resume.skills:
            score += 10
            recommendations.append("Add more relevant skills")
        else:
            recommendations.append("Add skills section")
            details_parts.append("❌ No skills")

        # Education
        max_points += 10
        if resume.education:
            score += 10
            details_parts.append(f"✓ {len(resume.education)} degree(s)")
        else:
            recommendations.append("Add education")
            details_parts.append("❌ No education")

        # Links (nice to have)
        max_points += 5
        if resume.linkedin or resume.github or resume.portfolio:
            score += 5
            links = []
            if resume.linkedin:
                links.append("LinkedIn")
            if resume.github:
                links.append("GitHub")
            if resume.portfolio:
                links.append("Portfolio")
            details_parts.append(f"✓ Links: {', '.join(links)}")
        else:
            recommendations.append("Add LinkedIn or portfolio links")

        # Calculate percentage
        final_score = (score / max_points * 100) if max_points > 0 else 0

        return ScoreComponent(
            score=final_score,
            label="Completeness",
            details=" | ".join(details_parts),
            recommendations=recommendations
        )

    def _get_resume_text(self, resume: ResumeModel) -> str:
        """Get all text content from resume."""
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

    def _count_action_verbs(self, resume: ResumeModel) -> int:
        """Count bullets starting with strong action verbs."""
        action_verbs = {
            'achieved', 'administered', 'analyzed', 'architected', 'automated',
            'built', 'collaborated', 'created', 'delivered', 'designed',
            'developed', 'directed', 'drove', 'engineered', 'enhanced',
            'established', 'executed', 'expanded', 'generated', 'implemented',
            'improved', 'increased', 'launched', 'led', 'managed',
            'optimized', 'orchestrated', 'organized', 'pioneered', 'reduced',
            'resolved', 'spearheaded', 'streamlined', 'transformed'
        }

        count = 0
        for exp in resume.experiences:
            if exp.bullets:
                for bullet in exp.bullets:
                    # Get first word
                    first_word = bullet.strip().split()[0].lower() if bullet.strip() else ''
                    # Remove common prefixes
                    first_word = first_word.rstrip('.:,-')
                    if first_word in action_verbs:
                        count += 1

        return count


# Convenience function
def score_resume(resume: ResumeModel, job: JobModel = None) -> ResumeScore:
    """Score a resume with optional job comparison."""
    scorer = ResumeScorer()
    return scorer.score_resume(resume, job)
