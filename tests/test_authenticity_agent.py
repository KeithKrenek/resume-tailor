"""Tests for authenticity agent."""

import pytest
from modules.models import ResumeModel, ExperienceItem, ResumeChange, ChangeType
from agents.authenticity_agent import (
    AuthenticityAgent,
    AuthenticityIssue,
    AuthenticityReport,
    create_authenticity_agent
)


@pytest.fixture
def sample_resume():
    """Create a sample resume for testing."""
    return ResumeModel(
        name="John Doe",
        email="john@example.com",
        raw_text="""
        John Doe
        Senior Software Engineer

        Experience:
        - Built a web application with React and Node.js
        - Worked with a team of 5 engineers
        - Improved code quality through code reviews
        """,
        experiences=[
            ExperienceItem(
                title="Software Engineer",
                company="Tech Corp",
                bullets=[
                    "Built a web application with React and Node.js",
                    "Worked with a team of 5 engineers",
                    "Improved code quality through code reviews"
                ]
            )
        ],
        skills=["Python", "JavaScript", "React"]
    )


@pytest.fixture
def sample_changes_fabrication():
    """Create sample changes with fabrications."""
    return [
        ResumeChange(
            id="change_1",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experience[0].bullets[0]",
            before="Built a web application with React and Node.js",
            after="Architected and deployed a cloud-native web application serving 1M+ users with 99.99% uptime using React, Node.js, and AWS",
            rationale="Added metrics and cloud context"
        ),
        ResumeChange(
            id="change_2",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experience[0].bullets[1]",
            before="Worked with a team of 5 engineers",
            after="Led a team of 5 engineers, mentoring junior developers and conducting technical interviews",
            rationale="Clarified leadership role"
        )
    ]


@pytest.fixture
def sample_changes_safe():
    """Create sample changes that are safe."""
    return [
        ResumeChange(
            id="change_1",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experience[0].bullets[0]",
            before="Built a web application with React and Node.js",
            after="Developed a web application using React and Node.js",
            rationale="Improved wording"
        )
    ]


def test_authenticity_issue_creation():
    """Test creating an AuthenticityIssue."""
    issue = AuthenticityIssue(
        type="fabrication",
        severity="high",
        location="experience[0].bullets[0]",
        original_text="Did something",
        modified_text="Led award-winning initiative",
        explanation="Added 'award-winning' without evidence",
        recommendation="Remove 'award-winning' modifier"
    )

    assert issue.type == "fabrication"
    assert issue.severity == "high"

    # Test to_dict
    issue_dict = issue.to_dict()
    assert issue_dict['type'] == "fabrication"
    assert issue_dict['severity'] == "high"

    # Test from_dict
    issue_from_dict = AuthenticityIssue.from_dict(issue_dict)
    assert issue_from_dict.type == issue.type
    assert issue_from_dict.severity == issue.severity


def test_authenticity_report_creation():
    """Test creating an AuthenticityReport."""
    issues = [
        AuthenticityIssue(
            type="fabrication",
            severity="high",
            location="test",
            original_text="original",
            modified_text="modified",
            explanation="test explanation",
            recommendation="test recommendation"
        )
    ]

    report = AuthenticityReport(
        total_changes_analyzed=5,
        issues_found=issues,
        is_safe=False,
        overall_risk_level="high",
        summary="Found 1 fabrication",
        recommendations=["Review carefully"]
    )

    assert report.total_changes_analyzed == 5
    assert len(report.issues_found) == 1
    assert not report.is_safe
    assert report.overall_risk_level == "high"

    # Test helper methods
    fabrications = report.get_fabrications()
    assert len(fabrications) == 1

    exaggerations = report.get_exaggerations()
    assert len(exaggerations) == 0

    high_severity = report.get_high_severity_issues()
    assert len(high_severity) == 1


def test_authenticity_report_to_from_dict():
    """Test converting AuthenticityReport to/from dict."""
    issues = [
        AuthenticityIssue(
            type="exaggeration",
            severity="medium",
            location="test",
            original_text="original",
            modified_text="modified",
            explanation="test explanation",
            recommendation="test recommendation"
        )
    ]

    report = AuthenticityReport(
        total_changes_analyzed=3,
        issues_found=issues,
        is_safe=True,
        overall_risk_level="low",
        summary="All good",
        recommendations=[]
    )

    # Convert to dict
    report_dict = report.to_dict()
    assert report_dict['total_changes_analyzed'] == 3
    assert len(report_dict['issues_found']) == 1
    assert report_dict['is_safe'] is True

    # Convert back from dict
    report_from_dict = AuthenticityReport.from_dict(report_dict)
    assert report_from_dict.total_changes_analyzed == report.total_changes_analyzed
    assert len(report_from_dict.issues_found) == len(report.issues_found)
    assert report_from_dict.is_safe == report.is_safe


def test_create_authenticity_agent():
    """Test creating an AuthenticityAgent via factory function."""
    # This test requires ANTHROPIC_API_KEY to be set
    try:
        agent = create_authenticity_agent(model="claude-3-haiku-20240307")
        assert agent is not None
        assert agent.model == "claude-3-haiku-20240307"
    except (ValueError, ImportError) as e:
        # Skip test if API key not available or anthropic not installed
        pytest.skip(f"Skipping test: {e}")


def test_authenticity_agent_initialization():
    """Test AuthenticityAgent initialization."""
    # This test requires ANTHROPIC_API_KEY to be set
    try:
        agent = AuthenticityAgent(model="claude-3-haiku-20240307")
        assert agent.model == "claude-3-haiku-20240307"
        assert agent.client is not None
    except (ValueError, ImportError) as e:
        # Skip test if API key not available or anthropic not installed
        pytest.skip(f"Skipping test: {e}")


# Integration tests (commented out to avoid API calls in CI/CD)
"""
def test_verify_updates_with_fabrications(sample_resume, sample_changes_fabrication):
    '''Test verifying updates with fabrications.'''
    try:
        agent = create_authenticity_agent()

        success, report = agent.verify_updates(
            original_resume_text=sample_resume.raw_text,
            optimized_resume=sample_resume,
            changes=sample_changes_fabrication
        )

        # Should succeed
        assert success is True
        assert isinstance(report, AuthenticityReport)

        # Should have found some issues (this is LLM-based, so exact count may vary)
        assert report.total_changes_analyzed == len(sample_changes_fabrication)

        print(f"Found {len(report.issues_found)} issues")
        print(f"Risk level: {report.overall_risk_level}")
        print(f"Is safe: {report.is_safe}")

    except (ValueError, ImportError) as e:
        pytest.skip(f"Skipping test: {e}")


def test_verify_updates_with_safe_changes(sample_resume, sample_changes_safe):
    '''Test verifying updates with safe changes.'''
    try:
        agent = create_authenticity_agent()

        success, report = agent.verify_updates(
            original_resume_text=sample_resume.raw_text,
            optimized_resume=sample_resume,
            changes=sample_changes_safe
        )

        # Should succeed
        assert success is True
        assert isinstance(report, AuthenticityReport)

        # Should find few or no issues
        assert report.total_changes_analyzed == len(sample_changes_safe)

        print(f"Found {len(report.issues_found)} issues")
        print(f"Risk level: {report.overall_risk_level}")
        print(f"Is safe: {report.is_safe}")

    except (ValueError, ImportError) as e:
        pytest.skip(f"Skipping test: {e}")
"""
