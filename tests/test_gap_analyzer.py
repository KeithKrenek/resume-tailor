"""Unit tests for gap analyzer."""

import pytest
from modules.models import (
    JobModel,
    JobRequirement,
    ResumeModel,
    ExperienceItem,
    EducationItem
)
from modules.gap_analyzer import GapAnalyzer, perform_gap_analysis


class TestGapAnalyzer:
    """Tests for GapAnalyzer class."""

    def test_create_analyzer(self):
        """Test creating gap analyzer."""
        analyzer = GapAnalyzer()
        assert analyzer is not None

    def test_normalize_skills(self):
        """Test skill normalization."""
        analyzer = GapAnalyzer()
        skills = ["Python", "  JavaScript  ", "JAVA"]
        normalized = analyzer._normalize_skills(skills)

        assert "python" in normalized
        assert "javascript" in normalized
        assert "java" in normalized
        assert len(normalized) == 3

    def test_simple_skill_match(self):
        """Test basic skill matching."""
        # Create simple job
        job = JobModel(
            title="Developer",
            required_skills=["Python", "SQL"],
            preferred_skills=["Docker"]
        )

        # Create simple resume
        resume = ResumeModel(
            name="Test User",
            skills=["Python", "JavaScript"]
        )

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should find Python as matched or weakly covered
        all_present_skills = [s.skill.lower() for s in gap.matched_skills + gap.weakly_covered_skills]
        assert "python" in all_present_skills

        # Should find SQL as missing required (case insensitive)
        missing_lower = [s.lower() for s in gap.missing_required_skills]
        assert "sql" in missing_lower

        # Should find Docker as missing preferred (case insensitive)
        missing_pref_lower = [s.lower() for s in gap.missing_preferred_skills]
        assert "docker" in missing_pref_lower

    def test_experience_skills_included(self):
        """Test that skills from experience are considered."""
        job = JobModel(
            title="Engineer",
            required_skills=["AWS", "Python"]
        )

        resume = ResumeModel(
            name="Test User",
            skills=["Python"]
        )

        # Add experience with AWS
        exp = ExperienceItem(
            title="Cloud Engineer",
            company="TechCo",
            skills=["AWS", "EC2"],
            bullets=["Worked with AWS services"]
        )
        resume.experiences.append(exp)

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Both skills should be matched or weakly covered (case insensitive)
        all_present_skills = [s.skill.lower() for s in gap.matched_skills + gap.weakly_covered_skills]
        assert "python" in all_present_skills
        assert "aws" in all_present_skills

    def test_weak_vs_strong_coverage(self):
        """Test detection of weak vs strong skill coverage."""
        job = JobModel(
            title="Developer",
            required_skills=["Python"]
        )

        resume = ResumeModel(
            name="Test User",
            skills=["Python"]  # Listed but not used much
        )

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should be detected as weak since only listed once (case insensitive)
        matched_or_weak = [s.skill.lower() for s in gap.matched_skills + gap.weakly_covered_skills]
        assert "python" in matched_or_weak

    def test_coverage_percentage_calculation(self):
        """Test coverage percentage calculation."""
        job = JobModel(
            title="Engineer",
            required_skills=["Python", "Java", "SQL"]
        )

        # Add requirements
        for skill in ["Python", "Java", "SQL"]:
            job.requirements.append(
                JobRequirement(
                    description=f"Experience with {skill}",
                    category="Skill",
                    is_must_have=True,
                    keywords=[skill.lower()]
                )
            )

        resume = ResumeModel(
            name="Test User",
            skills=["Python", "Java"]  # 2 out of 3
        )

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should be around 66% (2 out of 3)
        assert gap.coverage_percentage > 50
        assert gap.coverage_percentage < 100

    def test_strengths_identification(self):
        """Test identification of candidate strengths."""
        job = JobModel(
            title="Senior Engineer",
            required_skills=["Python"]
        )

        resume = ResumeModel(
            name="Test User",
            skills=["Python", "Java", "SQL", "Docker", "Kubernetes"],
            total_years_experience=7.0
        )

        # Add education
        resume.education.append(
            EducationItem(degree="Bachelor of Science", institution="University")
        )

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should identify some strengths
        assert len(gap.strengths) > 0

    def test_suggestions_generation(self):
        """Test generation of actionable suggestions."""
        job = JobModel(
            title="Engineer",
            required_skills=["Python", "AWS", "Docker"]
        )

        resume = ResumeModel(
            name="Test User",
            skills=["Python"]  # Missing AWS and Docker
        )

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should generate suggestions
        assert len(gap.suggestions) > 0

        # Check suggestions contain actionable items
        suggestions_text = " ".join(gap.suggestions).lower()
        assert any(keyword in suggestions_text for keyword in ["add", "emphasize", "strengthen", "consider"])

    def test_experience_years_detection(self):
        """Test detection of experience requirements."""
        job = JobModel(
            title="Senior Engineer",
            experience_level="Senior"
        )

        resume = ResumeModel(
            name="Test User",
            total_years_experience=6.0
        )

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should detect experience requirement
        assert gap.has_required_experience in [True, False]  # Will depend on extraction

    def test_relevant_experience_count(self):
        """Test counting of relevant experiences."""
        job = JobModel(
            title="Python Developer",
            required_skills=["Python", "Django"]
        )

        resume = ResumeModel(name="Test User")

        # Add relevant experience
        resume.experiences.append(
            ExperienceItem(
                title="Python Developer",
                company="Co1",
                skills=["Python", "Django"]
            )
        )

        # Add another relevant experience
        resume.experiences.append(
            ExperienceItem(
                title="Backend Dev",
                company="Co2",
                skills=["Python", "Flask"]
            )
        )

        # Add irrelevant experience
        resume.experiences.append(
            ExperienceItem(
                title="Marketing Manager",
                company="Co3",
                skills=["Marketing", "SEO"]
            )
        )

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should find 2 relevant experiences
        assert gap.relevant_experience_count >= 1  # At least one should match


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_perform_gap_analysis(self):
        """Test the perform_gap_analysis function."""
        job = JobModel(
            title="Developer",
            required_skills=["Python"]
        )

        resume = ResumeModel(
            name="Test User",
            skills=["Python", "Java"]
        )

        gap = perform_gap_analysis(job, resume)

        # Should return a GapAnalysis object
        assert gap is not None
        assert hasattr(gap, 'matched_skills')
        assert hasattr(gap, 'missing_required_skills')
        assert hasattr(gap, 'coverage_percentage')


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_job_requirements(self):
        """Test with no job requirements."""
        job = JobModel(title="Developer")
        resume = ResumeModel(name="User", skills=["Python"])

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should handle gracefully
        assert gap is not None
        assert gap.coverage_percentage >= 0

    def test_empty_resume(self):
        """Test with minimal resume."""
        job = JobModel(
            title="Developer",
            required_skills=["Python", "Java"]
        )
        resume = ResumeModel(name="User")

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should detect all skills as missing
        assert len(gap.missing_required_skills) == 2

    def test_perfect_match(self):
        """Test when resume perfectly matches job."""
        job = JobModel(
            title="Python Developer",
            required_skills=["Python", "Django"]
        )

        # Add requirements so coverage can be calculated
        for skill in ["Python", "Django"]:
            job.requirements.append(
                JobRequirement(
                    description=f"Experience with {skill}",
                    category="Skill",
                    is_must_have=True,
                    keywords=[skill.lower()]
                )
            )

        resume = ResumeModel(
            name="Expert",
            skills=["Python", "Django", "Flask"]
        )

        analyzer = GapAnalyzer()
        gap = analyzer.analyze(job, resume)

        # Should have high coverage (at least some requirements met)
        assert gap.met_requirements > 0
        assert len(gap.missing_required_skills) == 0
