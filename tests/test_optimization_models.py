"""Unit tests for resume optimization models."""

import pytest
from modules.models import (
    ChangeType,
    ResumeChange,
    ResumeOptimizationResult,
    ResumeModel,
    ExperienceItem
)


class TestChangeType:
    """Tests for ChangeType enum."""

    def test_change_type_values(self):
        """Test ChangeType enum values."""
        assert ChangeType.SUMMARY == "summary"
        assert ChangeType.HEADLINE == "headline"
        assert ChangeType.EXPERIENCE_BULLET == "experience_bullet"
        assert ChangeType.SKILLS_SECTION == "skills_section"
        assert ChangeType.EDUCATION == "education"
        assert ChangeType.OTHER == "other"

    def test_change_type_from_string(self):
        """Test creating ChangeType from string."""
        assert ChangeType("summary") == ChangeType.SUMMARY
        assert ChangeType("experience_bullet") == ChangeType.EXPERIENCE_BULLET


class TestResumeChange:
    """Tests for ResumeChange model."""

    def test_create_resume_change(self):
        """Test creating a resume change."""
        change = ResumeChange(
            id="change-1",
            change_type=ChangeType.SUMMARY,
            location="summary",
            before="Old summary text",
            after="New improved summary text",
            rationale="Better aligned with job requirements"
        )

        assert change.id == "change-1"
        assert change.change_type == ChangeType.SUMMARY
        assert change.location == "summary"
        assert "Old" in change.before
        assert "New" in change.after
        assert "Better aligned" in change.rationale

    def test_resume_change_to_dict(self):
        """Test converting ResumeChange to dictionary."""
        change = ResumeChange(
            id="change-2",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experiences[0].bullets[1]",
            before="Worked on projects",
            after="Led 5 high-impact projects resulting in 30% efficiency gain",
            rationale="Added quantification and impact"
        )

        data = change.to_dict()

        assert data['id'] == "change-2"
        assert data['change_type'] == "experience_bullet"
        assert data['location'] == "experiences[0].bullets[1]"
        assert data['before'] == "Worked on projects"
        assert data['after'] == "Led 5 high-impact projects resulting in 30% efficiency gain"

    def test_resume_change_from_dict(self):
        """Test creating ResumeChange from dictionary."""
        data = {
            'id': "change-3",
            'change_type': "skills_section",
            'location': "skills",
            'before': "Python, JavaScript",
            'after': "Python, JavaScript, Docker, Kubernetes",
            'rationale': "Added missing required skills"
        }

        change = ResumeChange.from_dict(data)

        assert change.id == "change-3"
        assert change.change_type == ChangeType.SKILLS_SECTION
        assert "Docker" in change.after

    def test_resume_change_round_trip(self):
        """Test serialization round trip."""
        original = ResumeChange(
            id="test-id",
            change_type=ChangeType.HEADLINE,
            location="headline",
            before="Software Engineer",
            after="Senior Full-Stack Engineer specializing in Cloud Architecture",
            rationale="More specific and aligned with job title"
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = ResumeChange.from_dict(data)

        assert restored.id == original.id
        assert restored.change_type == original.change_type
        assert restored.location == original.location
        assert restored.before == original.before
        assert restored.after == original.after
        assert restored.rationale == original.rationale


class TestResumeOptimizationResult:
    """Tests for ResumeOptimizationResult model."""

    def test_create_optimization_result(self):
        """Test creating an optimization result."""
        original_resume = ResumeModel(
            name="John Doe",
            email="john@example.com",
            summary="Software engineer with experience",
            skills=["Python", "Java"]
        )

        optimized_resume = ResumeModel(
            name="John Doe",
            email="john@example.com",
            summary="Senior Software Engineer with 7+ years of experience building scalable applications",
            skills=["Python", "Java", "Docker", "Kubernetes"]
        )

        result = ResumeOptimizationResult(
            original_resume=original_resume,
            optimized_resume=optimized_resume,
            style_used="balanced"
        )

        assert result.original_resume.name == "John Doe"
        assert result.optimized_resume.summary != result.original_resume.summary
        assert len(result.optimized_resume.skills) > len(result.original_resume.skills)
        assert result.style_used == "balanced"

    def test_add_changes(self):
        """Test adding changes to optimization result."""
        original = ResumeModel(name="Test", email="test@test.com")
        optimized = ResumeModel(name="Test", email="test@test.com", summary="New summary")

        result = ResumeOptimizationResult(
            original_resume=original,
            optimized_resume=optimized
        )

        change1 = ResumeChange(
            id="1",
            change_type=ChangeType.SUMMARY,
            location="summary",
            before="",
            after="New summary",
            rationale="Added summary"
        )

        change2 = ResumeChange(
            id="2",
            change_type=ChangeType.HEADLINE,
            location="headline",
            before="Engineer",
            after="Senior Engineer",
            rationale="Updated level"
        )

        result.changes.append(change1)
        result.changes.append(change2)

        assert len(result.changes) == 2
        assert result.get_total_changes() == 2

    def test_get_change_count_by_type(self):
        """Test getting change count by type."""
        original = ResumeModel(name="Test")
        optimized = ResumeModel(name="Test")

        result = ResumeOptimizationResult(
            original_resume=original,
            optimized_resume=optimized
        )

        # Add multiple changes of different types
        result.changes.append(ResumeChange(
            id="1", change_type=ChangeType.SUMMARY,
            location="summary", before="a", after="b", rationale="r"
        ))
        result.changes.append(ResumeChange(
            id="2", change_type=ChangeType.EXPERIENCE_BULLET,
            location="exp[0]", before="a", after="b", rationale="r"
        ))
        result.changes.append(ResumeChange(
            id="3", change_type=ChangeType.EXPERIENCE_BULLET,
            location="exp[1]", before="a", after="b", rationale="r"
        ))
        result.changes.append(ResumeChange(
            id="4", change_type=ChangeType.SKILLS_SECTION,
            location="skills", before="a", after="b", rationale="r"
        ))

        counts = result.get_change_count_by_type()

        assert counts['summary'] == 1
        assert counts['experience_bullet'] == 2
        assert counts['skills_section'] == 1

    def test_summary_of_improvements(self):
        """Test summary of improvements."""
        original = ResumeModel(name="Test")
        optimized = ResumeModel(name="Test")

        improvements = [
            "Added quantified achievements to experience bullets",
            "Incorporated missing required skills (Docker, Kubernetes)",
            "Rewrote summary to emphasize cloud architecture expertise"
        ]

        result = ResumeOptimizationResult(
            original_resume=original,
            optimized_resume=optimized,
            summary_of_improvements=improvements
        )

        assert len(result.summary_of_improvements) == 3
        assert "Docker" in result.summary_of_improvements[1]

    def test_optimization_result_to_dict(self):
        """Test converting optimization result to dictionary."""
        original = ResumeModel(
            name="Test User",
            email="test@test.com",
            skills=["Python"]
        )
        optimized = ResumeModel(
            name="Test User",
            email="test@test.com",
            skills=["Python", "Docker"]
        )

        result = ResumeOptimizationResult(
            original_resume=original,
            optimized_resume=optimized,
            style_used="aggressive"
        )

        data = result.to_dict()

        assert 'original_resume' in data
        assert 'optimized_resume' in data
        assert 'changes' in data
        assert data['style_used'] == "aggressive"
        assert data['optimized_resume']['skills'] == ["Python", "Docker"]

    def test_optimization_result_from_dict(self):
        """Test creating optimization result from dictionary."""
        data = {
            'original_resume': {
                'name': "John",
                'email': "john@test.com",
                'skills': ["Python"],
                'experiences': [],
                'education': []
            },
            'optimized_resume': {
                'name': "John",
                'email': "john@test.com",
                'skills': ["Python", "AWS"],
                'experiences': [],
                'education': []
            },
            'changes': [
                {
                    'id': "1",
                    'change_type': "skills_section",
                    'location': "skills",
                    'before': "Python",
                    'after': "Python, AWS",
                    'rationale': "Added AWS"
                }
            ],
            'summary_of_improvements': ["Added cloud skills"],
            'style_used': "balanced"
        }

        result = ResumeOptimizationResult.from_dict(data)

        assert result.original_resume.name == "John"
        assert len(result.optimized_resume.skills) == 2
        assert len(result.changes) == 1
        assert result.changes[0].change_type == ChangeType.SKILLS_SECTION
        assert result.style_used == "balanced"

    def test_optimization_result_round_trip(self):
        """Test full serialization round trip."""
        original = ResumeModel(
            name="Jane Doe",
            email="jane@test.com",
            summary="Engineer",
            skills=["Python", "Java"]
        )
        original.experiences.append(
            ExperienceItem(
                title="Developer",
                company="TechCo",
                bullets=["Built apps"]
            )
        )

        optimized = ResumeModel(
            name="Jane Doe",
            email="jane@test.com",
            summary="Senior Software Engineer with expertise in cloud technologies",
            skills=["Python", "Java", "AWS", "Docker"]
        )
        optimized.experiences.append(
            ExperienceItem(
                title="Developer",
                company="TechCo",
                bullets=["Built and deployed 10+ scalable cloud applications"]
            )
        )

        result = ResumeOptimizationResult(
            original_resume=original,
            optimized_resume=optimized,
            summary_of_improvements=["Improved summary", "Added cloud skills"],
            style_used="balanced"
        )

        result.changes.append(ResumeChange(
            id="1",
            change_type=ChangeType.SUMMARY,
            location="summary",
            before=original.summary,
            after=optimized.summary,
            rationale="Enhanced with cloud focus"
        ))

        # Convert to dict and back
        data = result.to_dict()
        restored = ResumeOptimizationResult.from_dict(data)

        assert restored.original_resume.name == original.name
        assert restored.optimized_resume.summary == optimized.summary
        assert len(restored.changes) == 1
        assert len(restored.summary_of_improvements) == 2
        assert restored.style_used == "balanced"
        assert len(restored.optimized_resume.experiences) == 1
        assert "scalable" in restored.optimized_resume.experiences[0].bullets[0]
