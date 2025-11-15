#!/usr/bin/env python3
"""Quick test script for output generation functionality."""

from modules.models import ResumeModel, ExperienceItem, EducationItem
from utils.document_generator import generate_html, generate_docx
import sys


def create_test_resume():
    """Create a sample resume for testing."""
    return ResumeModel(
        name="John Doe",
        email="john.doe@example.com",
        phone="+1-234-567-8900",
        location="San Francisco, CA",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe",
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
            )
        ],
        skills=["Python", "JavaScript", "React", "Node.js", "AWS"],
        education=[
            EducationItem(
                degree="B.S. Computer Science",
                institution="State University",
                field_of_study="Computer Science",
                graduation_date="2016",
                gpa="3.8"
            )
        ],
        certifications=["AWS Certified Solutions Architect"],
        total_years_experience=8.0
    )


def test_html_generation():
    """Test HTML generation."""
    print("Testing HTML generation...")
    resume = create_test_resume()

    try:
        html = generate_html(resume)
        assert len(html) > 0, "HTML content is empty"
        assert "John Doe" in html, "Name not found in HTML"
        assert "Senior Software Engineer" in html, "Title not found in HTML"
        assert "<!DOCTYPE html>" in html, "HTML structure missing"
        print("✓ HTML generation successful")
        print(f"  Generated {len(html)} bytes of HTML")
        return True
    except Exception as e:
        print(f"✗ HTML generation failed: {e}")
        return False


def test_docx_generation():
    """Test DOCX generation."""
    print("Testing DOCX generation...")
    resume = create_test_resume()

    try:
        docx_bytes = generate_docx(resume)
        assert len(docx_bytes) > 0, "DOCX content is empty"
        assert isinstance(docx_bytes, bytes), "DOCX is not bytes"
        assert docx_bytes[:2] == b'PK', "DOCX signature missing (not a valid ZIP/DOCX)"
        print("✓ DOCX generation successful")
        print(f"  Generated {len(docx_bytes)} bytes of DOCX")
        return True
    except Exception as e:
        print(f"✗ DOCX generation failed: {e}")
        return False


def test_markdown_generation():
    """Test Markdown generation."""
    print("Testing Markdown generation...")
    resume = create_test_resume()

    try:
        markdown = resume.to_markdown()
        assert len(markdown) > 0, "Markdown content is empty"
        assert "# John Doe" in markdown, "Name heading not found"
        assert "## Professional Summary" in markdown, "Summary section not found"
        print("✓ Markdown generation successful")
        print(f"  Generated {len(markdown)} bytes of Markdown")
        return True
    except Exception as e:
        print(f"✗ Markdown generation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Output Generation Module")
    print("=" * 60)
    print()

    results = []

    results.append(test_html_generation())
    print()

    results.append(test_docx_generation())
    print()

    results.append(test_markdown_generation())
    print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("=" * 60)
        return 0
    else:
        print(f"✗ Some tests failed ({passed}/{total} passed)")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
