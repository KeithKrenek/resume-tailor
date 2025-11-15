"""Tests for document generation utilities."""

import pytest
from pathlib import Path
import tempfile
from modules.models import ResumeModel, ExperienceItem, EducationItem
from utils.document_generator import (
    generate_html,
    generate_docx,
    save_resume_files
)


@pytest.fixture
def sample_resume():
    """Create a sample resume for testing."""
    return ResumeModel(
        name="John Doe",
        email="john.doe@example.com",
        phone="+1-234-567-8900",
        location="San Francisco, CA",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe",
        portfolio="https://johndoe.dev",
        headline="Senior Software Engineer",
        summary="Experienced software engineer with 8+ years developing scalable web applications.",
        experiences=[
            ExperienceItem(
                title="Senior Software Engineer",
                company="Tech Corp",
                start_date="Jan 2020",
                end_date="Present",
                location="San Francisco, CA",
                bullets=[
                    "Led development of microservices architecture serving 1M+ users",
                    "Improved application performance by 40% through optimization",
                    "Mentored team of 5 junior engineers"
                ],
                skills=["Python", "Django", "AWS", "Docker"],
                is_current=True
            ),
            ExperienceItem(
                title="Software Engineer",
                company="StartupCo",
                start_date="Jun 2016",
                end_date="Dec 2019",
                location="Remote",
                bullets=[
                    "Built RESTful APIs using Python and Flask",
                    "Implemented CI/CD pipelines reducing deployment time by 60%"
                ],
                skills=["Python", "Flask", "PostgreSQL"]
            )
        ],
        skills=["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "PostgreSQL"],
        education=[
            EducationItem(
                degree="B.S. Computer Science",
                institution="State University",
                field_of_study="Computer Science",
                graduation_date="2016",
                gpa="3.8",
                honors=["Cum Laude", "Dean's List"]
            )
        ],
        certifications=["AWS Certified Solutions Architect", "Certified Kubernetes Administrator"],
        projects=[
            {"name": "Open Source Project", "description": "Contributed to popular Python library"},
            "Built a personal portfolio website with React and Next.js"
        ],
        awards=["Employee of the Year 2022"],
        languages=["English (Native)", "Spanish (Conversational)"],
        total_years_experience=8.0
    )


def test_generate_html(sample_resume):
    """Test HTML generation."""
    html_content = generate_html(sample_resume)

    # Check that HTML is generated
    assert html_content is not None
    assert len(html_content) > 0

    # Check for key resume elements
    assert "John Doe" in html_content
    assert "john.doe@example.com" in html_content
    assert "Senior Software Engineer" in html_content
    assert "Tech Corp" in html_content
    assert "State University" in html_content

    # Check for proper HTML structure
    assert "<!DOCTYPE html>" in html_content
    assert "<html" in html_content
    assert "</html>" in html_content
    assert "<style>" in html_content  # CSS should be included


def test_generate_docx(sample_resume):
    """Test DOCX generation."""
    docx_bytes = generate_docx(sample_resume)

    # Check that bytes are generated
    assert docx_bytes is not None
    assert len(docx_bytes) > 0
    assert isinstance(docx_bytes, bytes)

    # Check that it starts with the DOCX file signature (PK)
    assert docx_bytes[:2] == b'PK'  # ZIP file signature


def test_save_resume_files(sample_resume):
    """Test saving resume to multiple formats."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        base_filename = "test_resume"

        # Save files
        results = save_resume_files(sample_resume, output_dir, base_filename)

        # Check that all expected formats are in results
        assert 'docx' in results
        assert 'html' in results
        assert 'markdown' in results
        assert 'pdf' in results

        # Check that DOCX, HTML, and Markdown files were created
        assert results['docx'] is not None
        assert results['docx'].exists()
        assert results['docx'].stat().st_size > 0

        assert results['html'] is not None
        assert results['html'].exists()
        assert results['html'].stat().st_size > 0

        assert results['markdown'] is not None
        assert results['markdown'].exists()
        assert results['markdown'].stat().st_size > 0

        # PDF may be None if weasyprint is not installed
        if results['pdf'] is not None:
            assert results['pdf'].exists()
            assert results['pdf'].stat().st_size > 0


def test_html_escaping(sample_resume):
    """Test that HTML special characters are properly escaped."""
    # Add some HTML special characters to the resume
    sample_resume.summary = "Test <script>alert('xss')</script> & other chars"

    html_content = generate_html(sample_resume)

    # Check that special characters are escaped
    assert "<script>" not in html_content
    assert "&lt;script&gt;" in html_content or "alert" not in html_content


def test_minimal_resume():
    """Test generation with minimal resume data."""
    minimal_resume = ResumeModel(
        name="Jane Smith",
        email="jane@example.com"
    )

    # Should not crash with minimal data
    html_content = generate_html(minimal_resume)
    assert "Jane Smith" in html_content
    assert "jane@example.com" in html_content

    docx_bytes = generate_docx(minimal_resume)
    assert len(docx_bytes) > 0


def test_resume_with_complex_projects():
    """Test resume with different project formats."""
    resume = ResumeModel(
        name="Test User",
        projects=[
            {"name": "Project A", "description": "Description A"},
            "Simple project string",
            {"name": "Project C", "details": "Details C"}
        ]
    )

    html_content = generate_html(resume)
    assert "Project A" in html_content
    assert "Simple project string" in html_content

    docx_bytes = generate_docx(resume)
    assert len(docx_bytes) > 0


def test_resume_markdown_generation(sample_resume):
    """Test that markdown generation works correctly."""
    markdown = sample_resume.to_markdown()

    # Check for key elements in markdown
    assert "# John Doe" in markdown
    assert "john.doe@example.com" in markdown
    assert "## Professional Summary" in markdown
    assert "## Professional Experience" in markdown
    assert "### Senior Software Engineer" in markdown
    assert "Tech Corp" in markdown
