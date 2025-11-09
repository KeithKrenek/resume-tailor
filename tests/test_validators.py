"""Unit tests for validation functions."""

import pytest
from modules.validators import (
    validate_job_description,
    validate_resume_text,
    validate_url,
    validate_folder_path,
    extract_basic_info,
    get_text_statistics,
    validate_all_inputs
)


class TestJobDescriptionValidation:
    """Tests for job description validation."""

    def test_valid_job_description(self):
        """Test validation of a valid job description."""
        job_desc = """
        We are seeking a Senior Software Engineer with 5+ years of experience.

        Responsibilities:
        - Design and develop scalable applications
        - Lead technical discussions

        Requirements:
        - Bachelor's degree in Computer Science
        - Experience with Python and JavaScript

        Qualifications:
        - Strong problem-solving skills
        - Excellent communication skills
        """
        is_valid, error = validate_job_description(job_desc)
        assert is_valid
        assert error == ""

    def test_empty_job_description(self):
        """Test validation of empty job description."""
        is_valid, error = validate_job_description("")
        assert not is_valid
        assert "cannot be empty" in error.lower()

    def test_short_job_description(self):
        """Test validation of too short job description."""
        is_valid, error = validate_job_description("Short text")
        assert not is_valid
        assert "too short" in error.lower()

    def test_missing_keywords(self):
        """Test validation of job description without keywords."""
        job_desc = "A" * 200  # Long enough but no job keywords
        is_valid, error = validate_job_description(job_desc)
        assert not is_valid
        assert "job-related terms" in error.lower()


class TestResumeValidation:
    """Tests for resume validation."""

    def test_valid_resume(self):
        """Test validation of a valid resume."""
        resume = """
        John Doe
        john.doe@email.com
        (555) 123-4567

        Experience:
        Software Engineer at Tech Company
        - Developed web applications
        - Led team of 5 developers

        Education:
        BS in Computer Science
        University of Technology

        Skills:
        Python, JavaScript, React, Node.js
        """
        is_valid, error = validate_resume_text(resume)
        assert is_valid
        assert error == ""

    def test_empty_resume(self):
        """Test validation of empty resume."""
        is_valid, error = validate_resume_text("")
        assert not is_valid
        assert "cannot be empty" in error.lower()

    def test_resume_without_contact(self):
        """Test validation of resume without email or phone."""
        resume = """
        John Doe

        Experience in software development.
        """ * 10  # Make it long enough
        is_valid, error = validate_resume_text(resume)
        assert not is_valid
        assert "email" in error.lower() or "phone" in error.lower()

    def test_short_resume(self):
        """Test validation of too short resume."""
        is_valid, error = validate_resume_text("Short resume")
        assert not is_valid
        assert "too short" in error.lower()


class TestUrlValidation:
    """Tests for URL validation."""

    def test_valid_url_with_protocol(self):
        """Test validation of URL with protocol."""
        is_valid, error = validate_url("https://example.com")
        assert is_valid
        assert error == ""

    def test_valid_url_without_protocol(self):
        """Test validation of URL without protocol."""
        is_valid, error = validate_url("example.com")
        assert is_valid
        assert error == ""

    def test_invalid_url(self):
        """Test validation of invalid URL."""
        is_valid, error = validate_url("not a url")
        assert not is_valid
        assert "invalid" in error.lower()

    def test_empty_url(self):
        """Test validation of empty URL."""
        is_valid, error = validate_url("")
        assert not is_valid
        assert "cannot be empty" in error.lower()


class TestFolderPathValidation:
    """Tests for folder path validation."""

    def test_valid_folder_path(self):
        """Test validation of valid folder path."""
        is_valid, error = validate_folder_path("/home/user/documents")
        assert is_valid
        assert error == ""

    def test_empty_folder_path(self):
        """Test validation of empty folder path."""
        is_valid, error = validate_folder_path("")
        assert not is_valid
        assert "cannot be empty" in error.lower()

    def test_invalid_characters(self):
        """Test validation of folder path with invalid characters."""
        is_valid, error = validate_folder_path("/home/user/<invalid>")
        assert not is_valid
        assert "invalid characters" in error.lower()


class TestBasicInfoExtraction:
    """Tests for basic info extraction."""

    def test_extract_email(self):
        """Test email extraction."""
        text = "Contact me at john.doe@example.com"
        info = extract_basic_info(text)
        assert info['email'] == "john.doe@example.com"

    def test_extract_phone(self):
        """Test phone extraction."""
        text = "Call me at (555) 123-4567"
        info = extract_basic_info(text)
        assert info['phone'] is not None

    def test_detect_sections(self):
        """Test section detection."""
        text = """
        Education: BS in Computer Science
        Experience: 5 years at Tech Company
        Skills: Python, JavaScript
        """
        info = extract_basic_info(text)
        assert info['has_education']
        assert info['has_experience']
        assert info['has_skills']

    def test_word_count(self):
        """Test word count."""
        text = "This is a test with ten words in total yes"
        info = extract_basic_info(text)
        assert info['word_count'] == 10


class TestTextStatistics:
    """Tests for text statistics."""

    def test_statistics_normal_text(self):
        """Test statistics for normal text."""
        text = "Line 1\nLine 2\nLine 3"
        stats = get_text_statistics(text)
        assert stats['chars'] > 0
        assert stats['words'] == 6
        assert stats['lines'] == 3

    def test_statistics_empty_text(self):
        """Test statistics for empty text."""
        stats = get_text_statistics("")
        assert stats['chars'] == 0
        assert stats['words'] == 0
        assert stats['lines'] == 0


class TestValidateAllInputs:
    """Tests for validating all inputs at once."""

    def test_all_valid_inputs(self):
        """Test validation when all inputs are valid."""
        job_desc = """
        Senior Software Engineer position with great benefits.

        Responsibilities include development and testing.
        Requirements: 5+ years experience.
        Qualifications: BS degree preferred.
        """ * 2

        resume = """
        John Doe
        john@email.com

        Experience:
        Software Engineer with 5 years of experience

        Education:
        BS Computer Science

        Skills:
        Python, Java, JavaScript
        """

        all_valid, errors = validate_all_inputs(
            job_description=job_desc,
            resume_text=resume,
            job_url="https://example.com/jobs/123",
            company_url="https://company.com",
            output_folder="/home/user/output"
        )

        assert all_valid
        assert len(errors) == 0

    def test_invalid_inputs(self):
        """Test validation when inputs are invalid."""
        all_valid, errors = validate_all_inputs(
            job_description="Short",
            resume_text="Short",
            job_url="invalid url",
            company_url="bad url",
            output_folder=""
        )

        assert not all_valid
        assert len(errors) > 0
