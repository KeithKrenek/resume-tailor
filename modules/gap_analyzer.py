"""Gap analysis between job requirements and resume content."""

from typing import List, Set
from modules.models import JobModel, ResumeModel, GapAnalysis, SkillMatch


class GapAnalyzer:
    """Analyzes gaps between job requirements and resume."""

    def __init__(self):
        """Initialize the gap analyzer."""
        pass

    def analyze(self, job: JobModel, resume: ResumeModel) -> GapAnalysis:
        """
        Perform comprehensive gap analysis.

        Args:
            job: Structured job posting
            resume: Structured resume

        Returns:
            GapAnalysis object with detailed comparison
        """
        # Extract all skills from job and resume
        job_required_skills = self._normalize_skills(job.required_skills)
        job_preferred_skills = self._normalize_skills(job.preferred_skills)
        resume_skills = self._normalize_skills(resume.skills)

        # Also extract skills from resume experiences
        experience_skills = set()
        for exp in resume.experiences:
            experience_skills.update(self._normalize_skills(exp.skills))

        # Combine all resume skills
        all_resume_skills = resume_skills | experience_skills

        # Analyze skill matches
        matched_skills = []
        missing_required = []
        missing_preferred = []
        weakly_covered = []

        # Check required skills
        for skill in job_required_skills:
            skill_match = self._check_skill_match(
                skill, all_resume_skills, resume, is_required=True
            )
            if skill_match.is_present:
                if skill_match.strength == "weak":
                    weakly_covered.append(skill_match)
                else:
                    matched_skills.append(skill_match)
            else:
                missing_required.append(skill)

        # Check preferred skills
        for skill in job_preferred_skills:
            if skill not in job_required_skills:  # Avoid duplicates
                skill_match = self._check_skill_match(
                    skill, all_resume_skills, resume, is_required=False
                )
                if skill_match.is_present:
                    matched_skills.append(skill_match)
                else:
                    missing_preferred.append(skill)

        # Analyze experience requirements
        has_required_exp, exp_gap = self._check_experience_requirements(job, resume)
        relevant_exp_count = self._count_relevant_experiences(job, resume)

        # Calculate requirements coverage
        total_reqs = len(job.requirements)
        met_reqs = self._count_met_requirements(job, resume)
        coverage = (met_reqs / total_reqs * 100) if total_reqs > 0 else 0

        # Generate strengths, weaknesses, and suggestions
        strengths = self._identify_strengths(job, resume, matched_skills)
        weaknesses = self._identify_weaknesses(missing_required, weakly_covered)
        suggestions = self._generate_suggestions(
            missing_required, missing_preferred, weakly_covered, job, resume
        )

        return GapAnalysis(
            matched_skills=matched_skills,
            missing_required_skills=list(missing_required),
            missing_preferred_skills=list(missing_preferred),
            weakly_covered_skills=weakly_covered,
            has_required_experience=has_required_exp,
            experience_gap_years=exp_gap,
            relevant_experience_count=relevant_exp_count,
            total_requirements=total_reqs,
            met_requirements=met_reqs,
            coverage_percentage=round(coverage, 1),
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions
        )

    def _normalize_skills(self, skills: List[str]) -> Set[str]:
        """Normalize skills for comparison (lowercase, stripped)."""
        return {skill.lower().strip() for skill in skills if skill}

    def _check_skill_match(
        self,
        skill: str,
        resume_skills: Set[str],
        resume: ResumeModel,
        is_required: bool
    ) -> SkillMatch:
        """
        Check if a skill is present in resume and determine strength.

        Args:
            skill: Skill to check
            resume_skills: Set of normalized resume skills
            resume: Full resume model
            is_required: Whether this is a required skill

        Returns:
            SkillMatch object
        """
        skill_lower = skill.lower().strip()
        evidence = []

        # Direct match in skills list
        if skill_lower in resume_skills:
            evidence.append(f"Listed in skills section")

        # Check in experience bullets (fuzzy match)
        for exp in resume.experiences:
            for bullet in exp.bullets:
                if skill_lower in bullet.lower():
                    evidence.append(f"Mentioned in {exp.title} at {exp.company}")
                    break

        # Check in experience skills
        for exp in resume.experiences:
            exp_skills = self._normalize_skills(exp.skills)
            if skill_lower in exp_skills:
                if f"Listed in skills section" not in evidence:
                    evidence.append(f"Used in {exp.title} role")

        # Determine strength
        is_present = len(evidence) > 0
        if not is_present:
            strength = "missing"
        elif len(evidence) >= 2:
            strength = "strong"
        else:
            strength = "weak"

        return SkillMatch(
            skill=skill,
            is_required=is_required,
            is_present=is_present,
            strength=strength,
            evidence=evidence
        )

    def _check_experience_requirements(
        self, job: JobModel, resume: ResumeModel
    ) -> tuple[bool, float]:
        """
        Check if resume meets experience requirements.

        Returns:
            Tuple of (has_required_experience, gap_in_years)
        """
        # Try to extract years from job experience level or requirements
        required_years = self._extract_required_years(job)
        resume_years = resume.total_years_experience or 0

        if required_years is None:
            return True, 0  # Can't determine requirement

        has_required = resume_years >= required_years
        gap = max(0, required_years - resume_years) if not has_required else 0

        return has_required, gap

    def _extract_required_years(self, job: JobModel) -> float:
        """Extract required years of experience from job."""
        # Check experience level
        if job.experience_level:
            level = job.experience_level.lower()
            if 'senior' in level or 'sr' in level:
                return 5.0
            elif 'mid' in level or 'intermediate' in level:
                return 3.0
            elif 'junior' in level or 'jr' in level or 'entry' in level:
                return 1.0

        # Check requirements text for patterns like "5+ years"
        for req in job.requirements:
            desc = req.description.lower()
            # Look for patterns like "5+ years", "5-7 years", "5 years"
            import re
            match = re.search(r'(\d+)\s*\+?\s*years?', desc)
            if match:
                return float(match.group(1))

        return None

    def _count_relevant_experiences(self, job: JobModel, resume: ResumeModel) -> int:
        """Count experiences relevant to the job."""
        job_skills = self._normalize_skills(job.required_skills + job.preferred_skills)
        relevant_count = 0

        for exp in resume.experiences:
            exp_skills = self._normalize_skills(exp.skills)
            # Check for skill overlap
            overlap = job_skills & exp_skills
            if overlap or any(
                any(skill.lower() in bullet.lower() for skill in job.required_skills)
                for bullet in exp.bullets
            ):
                relevant_count += 1

        return relevant_count

    def _count_met_requirements(self, job: JobModel, resume: ResumeModel) -> int:
        """Count how many job requirements are met."""
        met_count = 0
        resume_skills = self._normalize_skills(resume.skills)

        # Add experience skills
        for exp in resume.experiences:
            resume_skills.update(self._normalize_skills(exp.skills))

        # Combine all resume text for keyword search
        resume_text = (resume.summary or "") + " " + " ".join(
            bullet for exp in resume.experiences for bullet in exp.bullets
        )
        resume_text = resume_text.lower()

        for req in job.requirements:
            # Check if requirement keywords appear in resume
            keywords = self._normalize_skills(req.keywords)
            if keywords & resume_skills:
                met_count += 1
            elif any(kw in resume_text for kw in keywords):
                met_count += 1

        return met_count

    def _identify_strengths(
        self, job: JobModel, resume: ResumeModel, matched_skills: List[SkillMatch]
    ) -> List[str]:
        """Identify candidate strengths."""
        strengths = []

        # Strong skill matches
        strong_matches = [s for s in matched_skills if s.strength == "strong"]
        if len(strong_matches) >= 5:
            strengths.append(f"Strong technical skills ({len(strong_matches)} well-documented skills)")

        # Experience
        if resume.total_years_experience and resume.total_years_experience >= 5:
            strengths.append(f"{resume.total_years_experience} years of professional experience")

        # Relevant experience count
        relevant = self._count_relevant_experiences(job, resume)
        if relevant >= 2:
            strengths.append(f"{relevant} relevant positions in work history")

        # Education
        if resume.education:
            degrees = [edu.degree for edu in resume.education]
            if any('master' in d.lower() or 'phd' in d.lower() for d in degrees):
                strengths.append("Advanced degree")
            elif any('bachelor' in d.lower() or 'bs' in d.lower() or 'ba' in d.lower() for d in degrees):
                strengths.append("Bachelor's degree")

        # Certifications
        if resume.certifications:
            strengths.append(f"{len(resume.certifications)} professional certifications")

        return strengths

    def _identify_weaknesses(
        self, missing_required: List[str], weakly_covered: List[SkillMatch]
    ) -> List[str]:
        """Identify candidate weaknesses."""
        weaknesses = []

        if missing_required:
            weaknesses.append(f"Missing {len(missing_required)} required skills")

        if weakly_covered:
            weaknesses.append(f"{len(weakly_covered)} skills mentioned only briefly")

        return weaknesses

    def _generate_suggestions(
        self,
        missing_required: List[str],
        missing_preferred: List[str],
        weakly_covered: List[SkillMatch],
        job: JobModel,
        resume: ResumeModel
    ) -> List[str]:
        """Generate actionable suggestions."""
        suggestions = []

        # Missing required skills
        if missing_required:
            top_missing = missing_required[:3]
            suggestions.append(
                f"Add or emphasize experience with: {', '.join(top_missing)}"
            )

        # Weakly covered skills
        if weakly_covered:
            weak_skills = [s.skill for s in weakly_covered[:3]]
            suggestions.append(
                f"Strengthen coverage of: {', '.join(weak_skills)} with specific examples"
            )

        # Missing preferred skills
        if missing_preferred and len(missing_preferred) <= 3:
            suggestions.append(
                f"Consider adding: {', '.join(missing_preferred)} to stand out"
            )

        # Summary improvement
        if not resume.summary or len(resume.summary) < 100:
            suggestions.append(
                "Add or expand professional summary to highlight relevant experience"
            )

        # Quantification
        has_numbers = any(
            any(char.isdigit() for char in bullet)
            for exp in resume.experiences
            for bullet in exp.bullets
        )
        if not has_numbers:
            suggestions.append(
                "Quantify achievements with metrics and numbers"
            )

        return suggestions


# Convenience function
def perform_gap_analysis(job: JobModel, resume: ResumeModel) -> GapAnalysis:
    """
    Perform gap analysis between job and resume.

    Args:
        job: Structured job posting
        resume: Structured resume

    Returns:
        GapAnalysis object
    """
    analyzer = GapAnalyzer()
    return analyzer.analyze(job, resume)
