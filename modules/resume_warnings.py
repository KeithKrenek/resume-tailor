"""
Resume Warnings Detection System

Proactively identifies common resume issues and provides
actionable recommendations to fix them.
"""

from dataclasses import dataclass
from typing import List
from enum import Enum
import re
from modules.models import ResumeModel


class WarningSeverity(Enum):
    """Warning severity levels."""
    CRITICAL = "critical"  # Must fix
    HIGH = "high"  # Should fix
    MEDIUM = "medium"  # Recommended to fix
    LOW = "low"  # Nice to fix


@dataclass
class ResumeWarning:
    """Individual resume warning."""
    severity: WarningSeverity
    title: str
    description: str
    recommendation: str
    category: str  # 'formatting', 'content', 'completeness', 'professionalism'

    @property
    def emoji(self) -> str:
        """Get emoji for severity level."""
        return {
            WarningSeverity.CRITICAL: "🔴",
            WarningSeverity.HIGH: "🟠",
            WarningSeverity.MEDIUM: "🟡",
            WarningSeverity.LOW: "🔵"
        }[self.severity]

    @property
    def color(self) -> str:
        """Get color for UI display."""
        return {
            WarningSeverity.CRITICAL: "error",
            WarningSeverity.HIGH: "warning",
            WarningSeverity.MEDIUM: "info",
            WarningSeverity.LOW: "info"
        }[self.severity]


class ResumeWarningDetector:
    """Detects common resume issues and generates warnings."""

    def detect_warnings(self, resume: ResumeModel) -> List[ResumeWarning]:
        """
        Detect all warnings in a resume.

        Args:
            resume: Resume to analyze

        Returns:
            List of warnings, sorted by severity
        """
        warnings = []

        # Run all detection methods
        warnings.extend(self._check_length(resume))
        warnings.extend(self._check_contact_info(resume))
        warnings.extend(self._check_professionalism(resume))
        warnings.extend(self._check_formatting(resume))
        warnings.extend(self._check_content_quality(resume))
        warnings.extend(self._check_completeness(resume))
        warnings.extend(self._check_skills(resume))
        warnings.extend(self._check_dates(resume))

        # Sort by severity (critical first)
        severity_order = {
            WarningSeverity.CRITICAL: 0,
            WarningSeverity.HIGH: 1,
            WarningSeverity.MEDIUM: 2,
            WarningSeverity.LOW: 3
        }
        warnings.sort(key=lambda w: severity_order[w.severity])

        return warnings

    def _check_length(self, resume: ResumeModel) -> List[ResumeWarning]:
        """Check resume length."""
        warnings = []

        # Estimate character count
        total_chars = self._count_resume_chars(resume)
        estimated_pages = total_chars / 3000  # Rough estimate

        if total_chars > 9000:  # > 3 pages
            warnings.append(ResumeWarning(
                severity=WarningSeverity.HIGH,
                title="Resume Too Long",
                description=f"Resume is approximately {estimated_pages:.1f} pages ({total_chars:,} characters)",
                recommendation="Reduce to 2 pages maximum. Remove older or less relevant experience.",
                category="formatting"
            ))
        elif total_chars > 7500:  # 2.5-3 pages
            warnings.append(ResumeWarning(
                severity=WarningSeverity.MEDIUM,
                title="Resume Slightly Long",
                description=f"Resume is approximately {estimated_pages:.1f} pages ({total_chars:,} characters)",
                recommendation="Consider condensing to 2 pages or less for better readability.",
                category="formatting"
            ))
        elif total_chars < 2000:  # < 0.67 pages
            warnings.append(ResumeWarning(
                severity=WarningSeverity.MEDIUM,
                title="Resume Too Short",
                description=f"Resume is approximately {estimated_pages:.1f} pages ({total_chars:,} characters)",
                recommendation="Add more detail about your experience, achievements, and skills.",
                category="content"
            ))

        return warnings

    def _check_contact_info(self, resume: ResumeModel) -> List[ResumeWarning]:
        """Check contact information."""
        warnings = []

        if not resume.email:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.CRITICAL,
                title="Missing Email Address",
                description="No email address found in resume",
                recommendation="Add a professional email address. Use firstname.lastname@domain.com format.",
                category="completeness"
            ))
        elif resume.email:
            # Check for unprofessional email patterns
            unprofessional_patterns = [
                r'[0-9]{3,}',  # Too many numbers
                r'(cool|hot|sexy|cute|baby|love)',  # Unprofessional words
                r'(69|420)',  # Unprofessional numbers
            ]
            email_lower = resume.email.lower()

            for pattern in unprofessional_patterns:
                if re.search(pattern, email_lower):
                    warnings.append(ResumeWarning(
                        severity=WarningSeverity.HIGH,
                        title="Unprofessional Email Address",
                        description=f"Email address may appear unprofessional: {resume.email}",
                        recommendation="Use a professional format: firstname.lastname@domain.com",
                        category="professionalism"
                    ))
                    break

        if not resume.phone:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.HIGH,
                title="Missing Phone Number",
                description="No phone number found in resume",
                recommendation="Add a phone number for recruiters to contact you.",
                category="completeness"
            ))

        if not resume.linkedin and not resume.portfolio and not resume.github:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.MEDIUM,
                title="Missing Professional Links",
                description="No LinkedIn, GitHub, or portfolio links found",
                recommendation="Add your LinkedIn profile URL at minimum. GitHub is highly valuable for technical roles.",
                category="completeness"
            ))

        return warnings

    def _check_professionalism(self, resume: ResumeModel) -> List[ResumeWarning]:
        """Check for professionalism issues."""
        warnings = []

        # Check for first-person pronouns (I, me, my)
        resume_text = self._get_resume_text(resume).lower()
        first_person_pronouns = ['i ', 'me ', 'my ', 'mine ']

        pronoun_count = sum(resume_text.count(pronoun) for pronoun in first_person_pronouns)

        if pronoun_count > 5:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.MEDIUM,
                title="Excessive First-Person Pronouns",
                description=f"Found {pronoun_count} instances of 'I', 'me', 'my'",
                recommendation="Remove first-person pronouns. Use action verbs and direct statements.",
                category="professionalism"
            ))

        # Check for buzzwords/clichés
        buzzwords = [
            'synergy', 'rockstar', 'ninja', 'guru', 'wizard',
            'think outside the box', 'go-getter', 'team player',
            'hard worker', 'detail-oriented'
        ]

        buzzword_found = []
        for word in buzzwords:
            if word in resume_text:
                buzzword_found.append(word)

        if buzzword_found:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.LOW,
                title="Buzzwords Detected",
                description=f"Found overused terms: {', '.join(buzzword_found[:3])}",
                recommendation="Replace buzzwords with specific achievements and concrete examples.",
                category="content"
            ))

        return warnings

    def _check_formatting(self, resume: ResumeModel) -> List[ResumeWarning]:
        """Check formatting issues."""
        warnings = []

        # Check bullet point counts
        positions_with_too_few = []
        positions_with_too_many = []

        for exp in resume.experiences:
            bullet_count = len(exp.bullets) if exp.bullets else 0

            if bullet_count < 2 and bullet_count > 0:
                positions_with_too_few.append(exp.title or exp.company)
            elif bullet_count > 8:
                positions_with_too_many.append(exp.title or exp.company)

        if positions_with_too_few:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.MEDIUM,
                title="Too Few Bullet Points",
                description=f"{len(positions_with_too_few)} position(s) have fewer than 2 bullets",
                recommendation="Add 3-5 bullet points per position to adequately describe your responsibilities.",
                category="formatting"
            ))

        if positions_with_too_many:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.MEDIUM,
                title="Too Many Bullet Points",
                description=f"{len(positions_with_too_many)} position(s) have more than 8 bullets",
                recommendation="Reduce to 5-7 bullet points per position. Combine or remove less impactful items.",
                category="formatting"
            ))

        # Check for overly long bullets
        long_bullet_count = 0
        for exp in resume.experiences:
            if exp.bullets:
                for bullet in exp.bullets:
                    if len(bullet) > 250:
                        long_bullet_count += 1

        if long_bullet_count > 0:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.MEDIUM,
                title="Overly Long Bullet Points",
                description=f"{long_bullet_count} bullet point(s) exceed 250 characters",
                recommendation="Keep bullets concise (1-2 lines). Split long bullets into multiple points.",
                category="formatting"
            ))

        return warnings

    def _check_content_quality(self, resume: ResumeModel) -> List[ResumeWarning]:
        """Check content quality issues."""
        warnings = []

        # Count quantified achievements
        total_bullets = 0
        quantified_bullets = 0
        number_pattern = re.compile(r'\d+[%$]?|\$\d+|[0-9,]+')

        for exp in resume.experiences:
            if exp.bullets:
                for bullet in exp.bullets:
                    total_bullets += 1
                    if number_pattern.search(bullet):
                        quantified_bullets += 1

        if total_bullets > 0:
            quantified_ratio = quantified_bullets / total_bullets

            if quantified_ratio < 0.3:
                warnings.append(ResumeWarning(
                    severity=WarningSeverity.HIGH,
                    title="Insufficient Quantified Achievements",
                    description=f"Only {quantified_ratio:.0%} of bullets include numbers or metrics",
                    recommendation="Add specific metrics: percentages, dollar amounts, time saved, team sizes, etc.",
                    category="content"
                ))

        # Check for action verbs
        action_verb_count = self._count_action_verb_bullets(resume)
        if total_bullets > 0:
            action_verb_ratio = action_verb_count / total_bullets

            if action_verb_ratio < 0.5:
                warnings.append(ResumeWarning(
                    severity=WarningSeverity.MEDIUM,
                    title="Weak Action Verbs",
                    description=f"Only {action_verb_ratio:.0%} of bullets start with strong action verbs",
                    recommendation="Start bullets with powerful verbs: 'Developed', 'Implemented', 'Led', 'Achieved', etc.",
                    category="content"
                ))

        # Check for passive voice indicators
        resume_text = self._get_resume_text(resume).lower()
        passive_indicators = ['was responsible for', 'were responsible for', 'duties included']
        passive_count = sum(resume_text.count(indicator) for indicator in passive_indicators)

        if passive_count > 3:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.MEDIUM,
                title="Passive Voice Detected",
                description=f"Found {passive_count} instances of passive language",
                recommendation="Use active voice. Instead of 'was responsible for', say 'Managed' or 'Led'.",
                category="content"
            ))

        return warnings

    def _check_completeness(self, resume: ResumeModel) -> List[ResumeWarning]:
        """Check resume completeness."""
        warnings = []

        if not resume.summary and not resume.headline:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.HIGH,
                title="Missing Professional Summary",
                description="No professional summary or headline found",
                recommendation="Add a 2-3 sentence summary highlighting your key qualifications and career goals.",
                category="completeness"
            ))

        if not resume.experiences or len(resume.experiences) == 0:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.CRITICAL,
                title="Missing Work Experience",
                description="No work experience found in resume",
                recommendation="Add your work history with job titles, companies, dates, and achievements.",
                category="completeness"
            ))

        if not resume.skills or len(resume.skills) < 5:
            skill_count = len(resume.skills) if resume.skills else 0
            warnings.append(ResumeWarning(
                severity=WarningSeverity.HIGH,
                title="Insufficient Skills Listed",
                description=f"Only {skill_count} skills listed",
                recommendation="Add at least 8-12 relevant technical and professional skills.",
                category="completeness"
            ))

        if not resume.education or len(resume.education) == 0:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.HIGH,
                title="Missing Education",
                description="No education information found",
                recommendation="Add your degree(s), institution(s), and graduation year(s).",
                category="completeness"
            ))

        return warnings

    def _check_skills(self, resume: ResumeModel) -> List[ResumeWarning]:
        """Check skills section."""
        warnings = []

        if resume.skills:
            skill_count = len(resume.skills)

            if skill_count > 30:
                warnings.append(ResumeWarning(
                    severity=WarningSeverity.MEDIUM,
                    title="Too Many Skills Listed",
                    description=f"{skill_count} skills listed - appears unfocused",
                    recommendation="Reduce to 10-15 most relevant skills. Quality over quantity.",
                    category="content"
                ))

            # Check for generic skills that add little value
            generic_skills = ['microsoft office', 'word', 'excel', 'powerpoint', 'email', 'internet']
            found_generic = [s for s in resume.skills if s.lower() in generic_skills]

            if found_generic:
                warnings.append(ResumeWarning(
                    severity=WarningSeverity.LOW,
                    title="Generic Skills Detected",
                    description=f"Found basic skills: {', '.join(found_generic)}",
                    recommendation="Remove basic skills unless specifically required. Focus on specialized technical skills.",
                    category="content"
                ))

        return warnings

    def _check_dates(self, resume: ResumeModel) -> List[ResumeWarning]:
        """Check date formatting and gaps."""
        warnings = []

        # Check for missing dates
        positions_missing_dates = []
        for exp in resume.experiences:
            if not exp.start_date and not exp.end_date:
                positions_missing_dates.append(exp.title or exp.company)

        if positions_missing_dates:
            warnings.append(ResumeWarning(
                severity=WarningSeverity.HIGH,
                title="Missing Employment Dates",
                description=f"{len(positions_missing_dates)} position(s) missing dates",
                recommendation="Add start and end dates (MM/YYYY format) for all positions.",
                category="completeness"
            ))

        return warnings

    def _get_resume_text(self, resume: ResumeModel) -> str:
        """Get all text from resume."""
        parts = []

        if resume.summary:
            parts.append(resume.summary)
        if resume.headline:
            parts.append(resume.headline)

        for exp in resume.experiences:
            if exp.bullets:
                parts.extend(exp.bullets)

        return " ".join(parts)

    def _count_resume_chars(self, resume: ResumeModel) -> int:
        """Count total characters in resume."""
        total = 0

        if resume.name:
            total += len(resume.name)
        if resume.summary:
            total += len(resume.summary)
        if resume.headline:
            total += len(resume.headline)

        for exp in resume.experiences:
            if exp.title:
                total += len(exp.title)
            if exp.company:
                total += len(exp.company)
            if exp.bullets:
                total += sum(len(b) for b in exp.bullets)

        if resume.skills:
            total += sum(len(s) for s in resume.skills)

        for edu in resume.education:
            if edu.degree:
                total += len(edu.degree)
            if edu.institution:
                total += len(edu.institution)

        return total

    def _count_action_verb_bullets(self, resume: ResumeModel) -> int:
        """Count bullets starting with action verbs."""
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
                    first_word = bullet.strip().split()[0].lower().rstrip('.:,-') if bullet.strip() else ''
                    if first_word in action_verbs:
                        count += 1

        return count


# Convenience function
def detect_resume_warnings(resume: ResumeModel) -> List[ResumeWarning]:
    """Detect warnings in a resume."""
    detector = ResumeWarningDetector()
    return detector.detect_warnings(resume)
