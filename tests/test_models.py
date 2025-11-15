"""Unit tests for data models."""

import pytest
from modules.models import (
    ExperienceItem,
    EducationItem,
    ResumeModel,
    JobRequirement,
    JobModel,
    SkillMatch,
    GapAnalysis
)


class TestExperienceItem:
    """Tests for ExperienceItem model."""

    def test_create_experience(self):
        """Test creating an experience item."""
        exp = ExperienceItem(
            title="Software Engineer",
            company="Tech Corp",
            start_date="Jan 2020",
            end_date="Present",
            bullets=["Built web apps", "Led team"],
            skills=["Python", "JavaScript"],
            is_current=True
        )

        assert exp.title == "Software Engineer"
        assert exp.company == "Tech Corp"
        assert exp.is_current == True
        assert len(exp.bullets) == 2
        assert len(exp.skills) == 2

    def test_to_dict(self):
        """Test converting experience to dictionary."""
        exp = ExperienceItem(
            title="Engineer",
            company="Company"
        )
        data = exp.to_dict()

        assert data['title'] == "Engineer"
        assert data['company'] == "Company"
        assert 'bullets' in data
        assert 'skills' in data


class TestEducationItem:
    """Tests for EducationItem model."""

    def test_create_education(self):
        """Test creating an education item."""
        edu = EducationItem(
            degree="BS Computer Science",
            institution="University",
            graduation_date="2020",
            gpa="3.8"
        )

        assert edu.degree == "BS Computer Science"
        assert edu.institution == "University"
        assert edu.gpa == "3.8"

    def test_to_dict(self):
        """Test converting education to dictionary."""
        edu = EducationItem(
            degree="MS",
            institution="School"
        )
        data = edu.to_dict()

        assert data['degree'] == "MS"
        assert data['institution'] == "School"


class TestResumeModel:
    """Tests for ResumeModel."""

    def test_create_resume(self):
        """Test creating a resume model."""
        resume = ResumeModel(
            name="John Doe",
            email="john@example.com",
            phone="555-1234",
            skills=["Python", "Java"],
            total_years_experience=5.0
        )

        assert resume.name == "John Doe"
        assert resume.email == "john@example.com"
        assert len(resume.skills) == 2
        assert resume.total_years_experience == 5.0

    def test_add_experience(self):
        """Test adding experience to resume."""
        resume = ResumeModel()
        exp = ExperienceItem(title="Engineer", company="Corp")
        resume.experiences.append(exp)

        assert len(resume.experiences) == 1
        assert resume.experiences[0].title == "Engineer"

    def test_to_dict_and_from_dict(self):
        """Test serialization round trip."""
        resume = ResumeModel(
            name="Jane Smith",
            email="jane@test.com",
            skills=["Python", "SQL"]
        )
        resume.experiences.append(
            ExperienceItem(title="Dev", company="StartupCo")
        )

        # Convert to dict
        data = resume.to_dict()

        # Convert back
        resume2 = ResumeModel.from_dict(data)

        assert resume2.name == resume.name
        assert resume2.email == resume.email
        assert len(resume2.experiences) == 1
        assert resume2.experiences[0].title == "Dev"


class TestJobModel:
    """Tests for JobModel."""

    def test_create_job(self):
        """Test creating a job model."""
        job = JobModel(
            title="Senior Engineer",
            company="BigCorp",
            required_skills=["Python", "AWS"],
            experience_level="Senior"
        )

        assert job.title == "Senior Engineer"
        assert job.company == "BigCorp"
        assert len(job.required_skills) == 2
        assert job.experience_level == "Senior"

    def test_add_requirements(self):
        """Test adding requirements to job."""
        job = JobModel(title="Developer")
        req = JobRequirement(
            description="5+ years Python",
            category="Required Skill",
            is_must_have=True,
            keywords=["Python", "5 years"]
        )
        job.requirements.append(req)

        assert len(job.requirements) == 1
        assert job.requirements[0].is_must_have == True

    def test_to_dict_and_from_dict(self):
        """Test serialization round trip."""
        job = JobModel(
            title="Data Engineer",
            company="DataCo",
            required_skills=["Python", "Spark"]
        )
        job.requirements.append(
            JobRequirement(
                description="Python expert",
                category="Skill",
                is_must_have=True
            )
        )

        # Convert to dict
        data = job.to_dict()

        # Convert back
        job2 = JobModel.from_dict(data)

        assert job2.title == job.title
        assert job2.company == job.company
        assert len(job2.requirements) == 1
        assert job2.requirements[0].description == "Python expert"


class TestSkillMatch:
    """Tests for SkillMatch model."""

    def test_create_skill_match(self):
        """Test creating a skill match."""
        match = SkillMatch(
            skill="Python",
            is_required=True,
            is_present=True,
            strength="strong",
            evidence=["Listed in skills", "Used in 3 projects"]
        )

        assert match.skill == "Python"
        assert match.is_required == True
        assert match.is_present == True
        assert match.strength == "strong"
        assert len(match.evidence) == 2

    def test_to_dict(self):
        """Test converting to dictionary."""
        match = SkillMatch(
            skill="Java",
            is_required=False,
            is_present=False,
            strength="missing"
        )
        data = match.to_dict()

        assert data['skill'] == "Java"
        assert data['is_present'] == False
        assert data['strength'] == "missing"


class TestGapAnalysis:
    """Tests for GapAnalysis model."""

    def test_create_gap_analysis(self):
        """Test creating a gap analysis."""
        gap = GapAnalysis(
            missing_required_skills=["AWS", "Docker"],
            coverage_percentage=75.0,
            total_requirements=10,
            met_requirements=7
        )

        assert len(gap.missing_required_skills) == 2
        assert gap.coverage_percentage == 75.0
        assert gap.total_requirements == 10
        assert gap.met_requirements == 7

    def test_add_matched_skills(self):
        """Test adding matched skills."""
        gap = GapAnalysis()
        match = SkillMatch(
            skill="Python",
            is_required=True,
            is_present=True,
            strength="strong"
        )
        gap.matched_skills.append(match)

        assert len(gap.matched_skills) == 1
        assert gap.matched_skills[0].skill == "Python"

    def test_to_dict_and_from_dict(self):
        """Test serialization round trip."""
        gap = GapAnalysis(
            missing_required_skills=["Kubernetes"],
            coverage_percentage=80.0
        )
        gap.matched_skills.append(
            SkillMatch(
                skill="Python",
                is_required=True,
                is_present=True,
                strength="strong"
            )
        )

        # Convert to dict
        data = gap.to_dict()

        # Convert back
        gap2 = GapAnalysis.from_dict(data)

        assert gap2.coverage_percentage == 80.0
        assert len(gap2.missing_required_skills) == 1
        assert len(gap2.matched_skills) == 1
        assert gap2.matched_skills[0].skill == "Python"
