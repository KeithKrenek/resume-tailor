"""Unit tests for resume markdown export functionality."""

import pytest
from modules.models import ResumeModel, ExperienceItem, EducationItem


class TestResumeMarkdownBasic:
    """Tests for basic markdown export functionality."""

    def test_minimal_resume_markdown(self):
        """Test markdown export of minimal resume."""
        resume = ResumeModel(
            name="John Doe",
            email="john@example.com"
        )

        markdown = resume.to_markdown()

        assert "# John Doe" in markdown
        assert "john@example.com" in markdown

    def test_name_header_format(self):
        """Test that name is formatted as H1 header."""
        resume = ResumeModel(name="Jane Smith")
        markdown = resume.to_markdown()

        assert markdown.startswith("# Jane Smith")

    def test_contact_information_format(self):
        """Test contact information formatting with separators."""
        resume = ResumeModel(
            name="Test User",
            email="test@example.com",
            phone="555-1234",
            location="Portland, OR"
        )

        markdown = resume.to_markdown()

        # Check for email icon and value
        assert "✉️ test@example.com" in markdown
        # Check for phone icon and value
        assert "📞 555-1234" in markdown
        # Check for location icon and value
        assert "📍 Portland, OR" in markdown
        # Check for pipe separator
        assert "|" in markdown

    def test_links_formatting(self):
        """Test social links are formatted as markdown links."""
        resume = ResumeModel(
            name="Test User",
            linkedin="https://linkedin.com/in/testuser",
            github="https://github.com/testuser",
            portfolio="https://testuser.com"
        )

        markdown = resume.to_markdown()

        assert "[LinkedIn](https://linkedin.com/in/testuser)" in markdown
        assert "[GitHub](https://github.com/testuser)" in markdown
        assert "[Portfolio](https://testuser.com)" in markdown

    def test_headline_formatting(self):
        """Test headline is formatted as bold text."""
        resume = ResumeModel(
            name="Test User",
            headline="Senior Software Engineer"
        )

        markdown = resume.to_markdown()

        assert "**Senior Software Engineer**" in markdown

    def test_empty_resume_no_crash(self):
        """Test that completely empty resume doesn't crash."""
        resume = ResumeModel()
        markdown = resume.to_markdown()

        # Should return empty or minimal markdown without crashing
        assert isinstance(markdown, str)


class TestResumeMarkdownSummary:
    """Tests for professional summary section."""

    def test_summary_section_header(self):
        """Test that summary includes section header."""
        resume = ResumeModel(
            name="Test User",
            summary="Experienced software engineer with 10 years of expertise."
        )

        markdown = resume.to_markdown()

        assert "## Professional Summary" in markdown
        assert "Experienced software engineer with 10 years of expertise." in markdown

    def test_no_summary_no_section(self):
        """Test that missing summary doesn't create section."""
        resume = ResumeModel(name="Test User")
        markdown = resume.to_markdown()

        assert "## Professional Summary" not in markdown


class TestResumeMarkdownExperience:
    """Tests for professional experience section."""

    def test_experience_section_header(self):
        """Test that experience section has proper header."""
        resume = ResumeModel(
            name="Test User",
            experiences=[
                ExperienceItem(
                    title="Software Engineer",
                    company="Tech Corp",
                    start_date="Jan 2020",
                    end_date="Present",
                    bullets=["Developed applications"]
                )
            ]
        )

        markdown = resume.to_markdown()

        assert "## Professional Experience" in markdown

    def test_experience_title_and_company(self):
        """Test experience title and company formatting."""
        resume = ResumeModel(
            name="Test User",
            experiences=[
                ExperienceItem(
                    title="Senior Developer",
                    company="Acme Corp",
                    start_date="2020",
                    end_date="Present",
                    bullets=["Did stuff"]
                )
            ]
        )

        markdown = resume.to_markdown()

        # Should use H3 heading with bullet separator
        assert "### Senior Developer • Acme Corp" in markdown

    def test_experience_dates_and_location(self):
        """Test experience dates and location formatting."""
        resume = ResumeModel(
            name="Test User",
            experiences=[
                ExperienceItem(
                    title="Engineer",
                    company="Tech Co",
                    start_date="Jan 2020",
                    end_date="Dec 2022",
                    location="San Francisco, CA",
                    bullets=["Built things"]
                )
            ]
        )

        markdown = resume.to_markdown()

        # Check for italic date range
        assert "*Jan 2020 – Dec 2022" in markdown
        # Check for location
        assert "San Francisco, CA*" in markdown

    def test_experience_current_position(self):
        """Test current position shows 'Present' for end date."""
        resume = ResumeModel(
            name="Test User",
            experiences=[
                ExperienceItem(
                    title="Engineer",
                    company="Current Co",
                    start_date="Jan 2023",
                    end_date="Present",
                    bullets=["Working hard"],
                    is_current=True
                )
            ]
        )

        markdown = resume.to_markdown()

        assert "Present" in markdown

    def test_experience_bullets_formatting(self):
        """Test that experience bullets are formatted as markdown list."""
        resume = ResumeModel(
            name="Test User",
            experiences=[
                ExperienceItem(
                    title="Engineer",
                    company="Tech Co",
                    start_date="2020",
                    end_date="2022",
                    bullets=[
                        "Developed web applications using Python",
                        "Led team of 5 developers",
                        "Improved system performance by 50%"
                    ]
                )
            ]
        )

        markdown = resume.to_markdown()

        # All bullets should appear as list items
        assert "- Developed web applications using Python" in markdown
        assert "- Led team of 5 developers" in markdown
        assert "- Improved system performance by 50%" in markdown

    def test_experience_skills_formatting(self):
        """Test that experience skills are listed."""
        resume = ResumeModel(
            name="Test User",
            experiences=[
                ExperienceItem(
                    title="Engineer",
                    company="Tech Co",
                    start_date="2020",
                    end_date="2022",
                    bullets=["Built stuff"],
                    skills=["Python", "Django", "PostgreSQL"]
                )
            ]
        )

        markdown = resume.to_markdown()

        # Skills should be shown in bold with comma separation
        assert "**Skills**:" in markdown
        assert "Python, Django, PostgreSQL" in markdown

    def test_multiple_experiences(self):
        """Test formatting of multiple experience entries."""
        resume = ResumeModel(
            name="Test User",
            experiences=[
                ExperienceItem(
                    title="Senior Engineer",
                    company="Current Corp",
                    start_date="2022",
                    end_date="Present",
                    bullets=["Lead projects"]
                ),
                ExperienceItem(
                    title="Engineer",
                    company="Previous Corp",
                    start_date="2018",
                    end_date="2022",
                    bullets=["Built features"]
                )
            ]
        )

        markdown = resume.to_markdown()

        # Both experiences should appear
        assert "### Senior Engineer • Current Corp" in markdown
        assert "### Engineer • Previous Corp" in markdown


class TestResumeMarkdownSkills:
    """Tests for skills section."""

    def test_skills_section_header(self):
        """Test that skills section has proper header."""
        resume = ResumeModel(
            name="Test User",
            skills=["Python", "JavaScript", "React"]
        )

        markdown = resume.to_markdown()

        assert "## Skills" in markdown

    def test_skills_comma_separated(self):
        """Test that skills are comma-separated."""
        resume = ResumeModel(
            name="Test User",
            skills=["Python", "JavaScript", "React", "Node.js", "Docker"]
        )

        markdown = resume.to_markdown()

        assert "Python, JavaScript, React, Node.js, Docker" in markdown

    def test_no_skills_no_section(self):
        """Test that empty skills list doesn't create section."""
        resume = ResumeModel(name="Test User", skills=[])
        markdown = resume.to_markdown()

        assert "## Skills" not in markdown


class TestResumeMarkdownEducation:
    """Tests for education section."""

    def test_education_section_header(self):
        """Test that education section has proper header."""
        resume = ResumeModel(
            name="Test User",
            education=[
                EducationItem(
                    degree="BS Computer Science",
                    institution="State University",
                    graduation_date="2018"
                )
            ]
        )

        markdown = resume.to_markdown()

        assert "## Education" in markdown

    def test_education_degree_and_institution(self):
        """Test education degree and institution formatting."""
        resume = ResumeModel(
            name="Test User",
            education=[
                EducationItem(
                    degree="Master of Science in Computer Science",
                    institution="Tech University"
                )
            ]
        )

        markdown = resume.to_markdown()

        # Should use H3 heading with bullet separator
        assert "### Master of Science in Computer Science • Tech University" in markdown

    def test_education_with_gpa(self):
        """Test that GPA is displayed when present."""
        resume = ResumeModel(
            name="Test User",
            education=[
                EducationItem(
                    degree="BS Computer Science",
                    institution="University",
                    gpa="3.9"
                )
            ]
        )

        markdown = resume.to_markdown()

        assert "GPA: 3.9" in markdown

    def test_multiple_education_entries(self):
        """Test formatting of multiple education entries."""
        resume = ResumeModel(
            name="Test User",
            education=[
                EducationItem(
                    degree="MS Computer Science",
                    institution="Tech University",
                    graduation_date="2020"
                ),
                EducationItem(
                    degree="BS Computer Science",
                    institution="State College",
                    graduation_date="2018"
                )
            ]
        )

        markdown = resume.to_markdown()

        # Both education entries should appear
        assert "### MS Computer Science • Tech University" in markdown
        assert "### BS Computer Science • State College" in markdown


class TestResumeMarkdownCertifications:
    """Tests for certifications section."""

    def test_certifications_section_header(self):
        """Test that certifications section has proper header."""
        resume = ResumeModel(
            name="Test User",
            certifications=["AWS Certified Solutions Architect"]
        )

        markdown = resume.to_markdown()

        assert "## Certifications" in markdown

    def test_certifications_as_list(self):
        """Test that certifications are formatted as bullet list."""
        resume = ResumeModel(
            name="Test User",
            certifications=[
                "AWS Certified Solutions Architect",
                "Google Cloud Professional",
                "Certified Kubernetes Administrator"
            ]
        )

        markdown = resume.to_markdown()

        assert "- AWS Certified Solutions Architect" in markdown
        assert "- Google Cloud Professional" in markdown
        assert "- Certified Kubernetes Administrator" in markdown

    def test_no_certifications_no_section(self):
        """Test that empty certifications list doesn't create section."""
        resume = ResumeModel(name="Test User", certifications=[])
        markdown = resume.to_markdown()

        assert "## Certifications" not in markdown


class TestResumeMarkdownProjects:
    """Tests for projects section."""

    def test_projects_section_header(self):
        """Test that projects section has proper header."""
        resume = ResumeModel(
            name="Test User",
            projects=["Built open source library"]
        )

        markdown = resume.to_markdown()

        assert "## Projects" in markdown

    def test_projects_as_list(self):
        """Test that projects are formatted as bullet list."""
        resume = ResumeModel(
            name="Test User",
            projects=[
                "Open Source Contribution: React Library",
                "Personal Project: Portfolio Website"
            ]
        )

        markdown = resume.to_markdown()

        assert "- Open Source Contribution: React Library" in markdown
        assert "- Personal Project: Portfolio Website" in markdown

    def test_no_projects_no_section(self):
        """Test that empty projects list doesn't create section."""
        resume = ResumeModel(name="Test User", projects=[])
        markdown = resume.to_markdown()

        assert "## Projects" not in markdown


class TestResumeMarkdownAwards:
    """Tests for awards section."""

    def test_awards_section_header(self):
        """Test that awards section has proper header."""
        resume = ResumeModel(
            name="Test User",
            awards=["Employee of the Year 2022"]
        )

        markdown = resume.to_markdown()

        assert "## Awards & Honors" in markdown

    def test_awards_as_list(self):
        """Test that awards are formatted as bullet list."""
        resume = ResumeModel(
            name="Test User",
            awards=[
                "Employee of the Year 2022",
                "Best Innovation Award 2021"
            ]
        )

        markdown = resume.to_markdown()

        assert "- Employee of the Year 2022" in markdown
        assert "- Best Innovation Award 2021" in markdown

    def test_no_awards_no_section(self):
        """Test that empty awards list doesn't create section."""
        resume = ResumeModel(name="Test User", awards=[])
        markdown = resume.to_markdown()

        assert "## Awards & Honors" not in markdown


class TestResumeMarkdownLanguages:
    """Tests for languages section."""

    def test_languages_section_header(self):
        """Test that languages section has proper header."""
        resume = ResumeModel(
            name="Test User",
            languages=["English", "Spanish"]
        )

        markdown = resume.to_markdown()

        assert "## Languages" in markdown

    def test_languages_comma_separated(self):
        """Test that languages are comma-separated."""
        resume = ResumeModel(
            name="Test User",
            languages=["English", "Spanish", "French", "Mandarin"]
        )

        markdown = resume.to_markdown()

        assert "English, Spanish, French, Mandarin" in markdown

    def test_no_languages_no_section(self):
        """Test that empty languages list doesn't create section."""
        resume = ResumeModel(name="Test User", languages=[])
        markdown = resume.to_markdown()

        assert "## Languages" not in markdown


class TestResumeMarkdownComprehensive:
    """Tests for comprehensive resume with all sections."""

    def test_full_resume_markdown(self):
        """Test markdown export of complete resume with all sections."""
        resume = ResumeModel(
            name="Alice Johnson",
            email="alice@example.com",
            phone="555-9876",
            location="Seattle, WA",
            linkedin="https://linkedin.com/in/alicejohnson",
            github="https://github.com/alicejohnson",
            headline="Senior Full-Stack Engineer",
            summary="Passionate software engineer with 8 years of experience.",
            experiences=[
                ExperienceItem(
                    title="Senior Engineer",
                    company="Tech Giant",
                    start_date="2020",
                    end_date="Present",
                    location="Seattle, WA",
                    bullets=[
                        "Led development of microservices architecture",
                        "Mentored junior developers"
                    ],
                    skills=["Python", "React", "AWS"]
                )
            ],
            skills=["Python", "JavaScript", "React", "AWS", "Docker"],
            education=[
                EducationItem(
                    degree="BS Computer Science",
                    institution="University of Washington",
                    graduation_date="2015",
                    gpa="3.8"
                )
            ],
            certifications=["AWS Certified Solutions Architect"],
            projects=["Open Source ML Library"],
            awards=["Innovation Award 2022"],
            languages=["English", "Spanish"]
        )

        markdown = resume.to_markdown()

        # Verify all major sections are present
        assert "# Alice Johnson" in markdown
        assert "## Professional Summary" in markdown
        assert "## Professional Experience" in markdown
        assert "## Skills" in markdown
        assert "## Education" in markdown
        assert "## Certifications" in markdown
        assert "## Projects" in markdown
        assert "## Awards & Honors" in markdown
        assert "## Languages" in markdown

    def test_section_ordering(self):
        """Test that sections appear in the expected order."""
        resume = ResumeModel(
            name="Test User",
            summary="Summary",
            experiences=[
                ExperienceItem(
                    title="Engineer",
                    company="Co",
                    start_date="2020",
                    end_date="2022",
                    bullets=["Worked"]
                )
            ],
            skills=["Python"],
            education=[
                EducationItem(degree="BS", institution="Uni")
            ]
        )

        markdown = resume.to_markdown()

        # Find positions of each section
        summary_pos = markdown.find("## Professional Summary")
        experience_pos = markdown.find("## Professional Experience")
        skills_pos = markdown.find("## Skills")
        education_pos = markdown.find("## Education")

        # Verify order: Summary -> Experience -> Skills -> Education
        assert summary_pos < experience_pos
        assert experience_pos < skills_pos
        assert skills_pos < education_pos

    def test_markdown_is_valid_format(self):
        """Test that output is valid markdown format."""
        resume = ResumeModel(
            name="Test User",
            summary="Summary text",
            experiences=[
                ExperienceItem(
                    title="Engineer",
                    company="Company",
                    start_date="2020",
                    end_date="2022",
                    bullets=["Bullet point"]
                )
            ]
        )

        markdown = resume.to_markdown()

        # Should be a non-empty string
        assert isinstance(markdown, str)
        assert len(markdown) > 0

        # Should contain markdown heading syntax
        assert "#" in markdown

        # Should contain bullet point syntax
        assert "-" in markdown
