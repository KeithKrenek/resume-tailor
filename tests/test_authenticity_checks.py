"""Unit tests for authenticity checking utilities."""

import pytest
from modules.models import (
    ResumeChange, ChangeType, ResumeModel, ExperienceItem, EducationItem
)
from utils.authenticity_checks import (
    extract_numbers,
    extract_company_names,
    extract_technologies,
    check_change_authenticity,
    get_potentially_risky_changes,
    generate_authenticity_report
)


class TestExtractNumbers:
    """Tests for extracting numeric values from text."""

    def test_extract_percentages(self):
        """Test extraction of percentage values."""
        text = "Improved performance by 25% and reduced costs by 3.5%"
        numbers = extract_numbers(text)
        assert '25%' in numbers
        assert '3.5%' in numbers

    def test_extract_dollar_amounts(self):
        """Test extraction of dollar amounts."""
        text = "Managed $5M budget and generated $100K in revenue"
        numbers = extract_numbers(text)
        assert any('5m' in n.lower() for n in numbers)
        assert any('100k' in n.lower() for n in numbers)

    def test_extract_multipliers(self):
        """Test extraction of multiplier notation."""
        text = "Achieved 3x growth and 10x improvement"
        numbers = extract_numbers(text)
        assert '3x' in numbers
        assert '10x' in numbers

    def test_extract_plus_notation(self):
        """Test extraction of plus notation."""
        text = "Led team of 100+ engineers with 500+ deployments"
        numbers = extract_numbers(text)
        assert '100+' in numbers
        assert '500+' in numbers

    def test_extract_time_periods(self):
        """Test extraction of time period references."""
        text = "Reduced latency from 5 seconds to 2 months average"
        numbers = extract_numbers(text)
        # Should find numbers with time units
        assert len(numbers) > 0

    def test_no_numbers_returns_empty(self):
        """Test that text without numbers returns empty list."""
        text = "Led team and improved processes"
        numbers = extract_numbers(text)
        assert len(numbers) == 0


class TestExtractCompanyNames:
    """Tests for extracting company names from text."""

    def test_extract_simple_company_name(self):
        """Test extraction of simple capitalized company name."""
        text = "Worked with Acme Corporation on the project"
        companies = extract_company_names(text)
        # Should extract capitalized words (Worked will be filtered, Acme or multi-word extracted)
        assert len(companies) > 0
        # Either extracts individual words or the full company name
        assert any('Acme' in c for c in companies)

    def test_filter_common_action_words(self):
        """Test that common action words are filtered out."""
        text = "Led team, Developed software, Built applications"
        companies = extract_company_names(text)
        assert 'Led' not in companies
        assert 'Developed' not in companies
        assert 'Built' not in companies

    def test_filter_common_tech_terms(self):
        """Test that common tech terms are filtered out."""
        text = "Used Python, JavaScript, and React"
        companies = extract_company_names(text)
        assert 'Python' not in companies
        assert 'React' not in companies

    def test_filter_month_names(self):
        """Test that month names are filtered out."""
        text = "Started in January and finished in December"
        companies = extract_company_names(text)
        assert 'January' not in companies
        assert 'December' not in companies

    def test_extract_multi_word_company(self):
        """Test extraction of multi-word company names."""
        text = "Collaborated with Global Tech Solutions team"
        companies = extract_company_names(text)
        # Should extract capitalized words
        assert len(companies) > 0


class TestExtractTechnologies:
    """Tests for extracting technology names from text."""

    def test_extract_acronyms(self):
        """Test extraction of technology acronyms."""
        text = "Built REST APIs using AWS and SQL databases"
        technologies = extract_technologies(text)
        assert 'REST' in technologies or 'AWS' in technologies or 'SQL' in technologies

    def test_extract_common_frameworks(self):
        """Test extraction of common framework names."""
        text = "Developed applications using React, Node, and Docker"
        technologies = extract_technologies(text)
        assert 'React' in technologies
        assert 'Node' in technologies
        assert 'Docker' in technologies

    def test_extract_tech_with_suffixes(self):
        """Test extraction of technologies with common suffixes."""
        text = "Used NodeJS and MySQL for the backend"
        technologies = extract_technologies(text)
        # Should extract NodeJS and MySQL
        assert len(technologies) > 0

    def test_no_duplicates(self):
        """Test that duplicate technologies are removed."""
        text = "React React React"
        technologies = extract_technologies(text)
        assert technologies.count('React') == 1

    def test_empty_text_returns_empty_list(self):
        """Test that empty text returns empty list."""
        technologies = extract_technologies("")
        assert technologies == []


class TestCheckChangeAuthenticity:
    """Tests for checking individual change authenticity."""

    def _create_test_resume(self) -> ResumeModel:
        """Helper to create a test resume."""
        return ResumeModel(
            name="John Doe",
            email="john@example.com",
            phone="555-1234",
            summary="Software engineer with experience in Python",
            experiences=[
                ExperienceItem(
                    title="Software Engineer",
                    company="Tech Corp",
                    start_date="2020",
                    end_date="Present",
                    bullets=[
                        "Developed web applications using Python and Django",
                        "Led team of 5 developers"
                    ],
                    skills=["Python", "Django"]
                )
            ],
            skills=["Python", "Django", "JavaScript"],
            education=[]
        )

    def test_safe_change_no_warnings(self):
        """Test that safe rephrasings don't trigger warnings."""
        resume = self._create_test_resume()
        change = ResumeChange(
            id="test1",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experiences[0].bullets[0]",
            before="Developed web applications using Python and Django",
            after="Built web applications leveraging Python and Django framework",
            rationale="Improved wording"
        )

        is_risky, warnings = check_change_authenticity(change, resume)
        assert not is_risky
        assert len(warnings) == 0

    def test_new_metrics_trigger_warning(self):
        """Test that introducing new metrics triggers warning."""
        resume = self._create_test_resume()
        change = ResumeChange(
            id="test2",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experiences[0].bullets[0]",
            before="Developed web applications",
            after="Developed web applications, improving performance by 50% and reducing costs by $100K",
            rationale="Added metrics"
        )

        is_risky, warnings = check_change_authenticity(change, resume)
        assert is_risky
        assert len(warnings) > 0
        assert any('metrics' in w.lower() for w in warnings)

    def test_new_company_triggers_warning(self):
        """Test that mentioning new companies triggers warning."""
        resume = self._create_test_resume()
        change = ResumeChange(
            id="test3",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experiences[0].bullets[0]",
            before="Developed web applications",
            after="Developed web applications for Acme Industries and Global Solutions",
            rationale="Added clients"
        )

        is_risky, warnings = check_change_authenticity(change, resume)
        assert is_risky
        assert len(warnings) > 0
        assert any('organizations' in w.lower() for w in warnings)

    def test_new_technology_triggers_warning(self):
        """Test that introducing completely new technologies triggers warning."""
        resume = self._create_test_resume()
        change = ResumeChange(
            id="test4",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experiences[0].bullets[0]",
            before="Developed web applications",
            after="Developed web applications using Kubernetes and AWS infrastructure",
            rationale="Added tech stack"
        )

        is_risky, warnings = check_change_authenticity(change, resume)
        assert is_risky
        # Should flag new technologies not in original resume
        assert any('technolog' in w.lower() for w in warnings)

    def test_existing_technology_no_warning(self):
        """Test that using existing technologies doesn't trigger warning."""
        resume = self._create_test_resume()
        change = ResumeChange(
            id="test5",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experiences[0].bullets[0]",
            before="Developed applications",
            after="Developed applications using Python and JavaScript",
            rationale="Mentioned existing skills"
        )

        is_risky, warnings = check_change_authenticity(change, resume)
        # Should not be risky since Python and JavaScript are in the resume
        assert not is_risky or len(warnings) == 0

    def test_significant_expansion_triggers_warning(self):
        """Test that significantly expanding content triggers warning."""
        resume = self._create_test_resume()
        change = ResumeChange(
            id="test6",
            change_type=ChangeType.EXPERIENCE_BULLET,
            location="experiences[0].bullets[0]",
            before="Led team",
            after="Led team of software engineers in developing comprehensive full-stack web applications "
                  "with microservices architecture, implementing continuous integration and deployment pipelines, "
                  "and establishing best practices for code review and quality assurance across the organization",
            rationale="Expanded description"
        )

        is_risky, warnings = check_change_authenticity(change, resume)
        assert is_risky
        assert any('expanded' in w.lower() for w in warnings)

    def test_skills_section_not_checked(self):
        """Test that skills section changes are not checked for fabrication."""
        resume = self._create_test_resume()
        change = ResumeChange(
            id="test7",
            change_type=ChangeType.SKILLS_SECTION,
            location="skills",
            before="Python, Django",
            after="Python, Django, Kubernetes, AWS, Docker",
            rationale="Added skills"
        )

        is_risky, warnings = check_change_authenticity(change, resume)
        # Skills section changes should not trigger warnings
        assert not is_risky
        assert len(warnings) == 0

    def test_education_not_checked(self):
        """Test that education changes are not checked for fabrication."""
        resume = self._create_test_resume()
        change = ResumeChange(
            id="test8",
            change_type=ChangeType.EDUCATION,
            location="education[0]",
            before="BS Computer Science",
            after="BS Computer Science with honors, 4.0 GPA",
            rationale="Added details"
        )

        is_risky, warnings = check_change_authenticity(change, resume)
        # Education changes should not trigger warnings
        assert not is_risky
        assert len(warnings) == 0


class TestGetPotentiallyRiskyChanges:
    """Tests for getting all risky changes from a list."""

    def _create_test_resume(self) -> ResumeModel:
        """Helper to create a test resume."""
        return ResumeModel(
            name="Jane Smith",
            email="jane@example.com",
            summary="Senior developer",
            experiences=[
                ExperienceItem(
                    title="Developer",
                    company="StartupCo",
                    start_date="2018",
                    end_date="Present",
                    bullets=["Built web apps"],
                    skills=["Python"]
                )
            ],
            skills=["Python"],
            education=[]
        )

    def test_filter_only_risky_changes(self):
        """Test that only risky changes are returned."""
        resume = self._create_test_resume()

        changes = [
            # Safe change
            ResumeChange(
                id="safe1",
                change_type=ChangeType.EXPERIENCE_BULLET,
                location="experiences[0].bullets[0]",
                before="Built web apps",
                after="Developed web applications",
                rationale="Better wording"
            ),
            # Risky change - adds metrics
            ResumeChange(
                id="risky1",
                change_type=ChangeType.EXPERIENCE_BULLET,
                location="experiences[0].bullets[0]",
                before="Built web apps",
                after="Built web apps serving 10000 users with 99.9% uptime",
                rationale="Added metrics"
            ),
            # Another safe change
            ResumeChange(
                id="safe2",
                change_type=ChangeType.SUMMARY,
                location="summary",
                before="Senior developer",
                after="Experienced senior developer",
                rationale="Enhanced"
            )
        ]

        risky = get_potentially_risky_changes(changes, resume)

        # Should only return the risky change
        assert len(risky) >= 1
        risky_ids = [change.id for change, warnings in risky]
        assert "risky1" in risky_ids
        assert "safe1" not in risky_ids

    def test_empty_changes_list(self):
        """Test that empty changes list returns empty result."""
        resume = self._create_test_resume()
        risky = get_potentially_risky_changes([], resume)
        assert len(risky) == 0

    def test_all_safe_changes(self):
        """Test that all safe changes returns empty result."""
        resume = self._create_test_resume()

        changes = [
            ResumeChange(
                id="safe1",
                change_type=ChangeType.SUMMARY,
                location="summary",
                before="senior developer with experience",
                after="senior developer with extensive experience",
                rationale="Enhanced description"
            )
        ]

        risky = get_potentially_risky_changes(changes, resume)
        assert len(risky) == 0


class TestGenerateAuthenticityReport:
    """Tests for generating comprehensive authenticity report."""

    def _create_test_resume(self) -> ResumeModel:
        """Helper to create a test resume."""
        return ResumeModel(
            name="Test User",
            email="test@example.com",
            experiences=[
                ExperienceItem(
                    title="Engineer",
                    company="TechCo",
                    start_date="2020",
                    end_date="Present",
                    bullets=["Wrote code"],
                    skills=["Python"]
                )
            ],
            skills=["Python"],
            education=[]
        )

    def test_report_with_safe_changes(self):
        """Test report generation with all safe changes."""
        resume = self._create_test_resume()

        changes = [
            ResumeChange(
                id="c1",
                change_type=ChangeType.SUMMARY,
                location="summary",
                before="Experienced engineer with expertise",
                after="Experienced engineer with strong expertise",
                rationale="Clarified"
            )
        ]

        report = generate_authenticity_report(changes, resume)

        assert report['total_changes'] == 1
        assert report['flagged_changes'] == 0
        assert report['flag_rate'] == 0
        assert report['is_safe'] is True
        assert len(report['recommendations']) > 0

    def test_report_with_risky_changes(self):
        """Test report generation with risky changes."""
        resume = self._create_test_resume()

        changes = [
            # Add new metrics
            ResumeChange(
                id="c1",
                change_type=ChangeType.EXPERIENCE_BULLET,
                location="experiences[0].bullets[0]",
                before="Wrote code",
                after="Wrote code improving performance by 80%",
                rationale="Added impact"
            ),
            # Add new technology
            ResumeChange(
                id="c2",
                change_type=ChangeType.EXPERIENCE_BULLET,
                location="experiences[0].bullets[0]",
                before="Developed apps",
                after="Developed apps using Kubernetes",
                rationale="Added tech"
            )
        ]

        report = generate_authenticity_report(changes, resume)

        assert report['total_changes'] == 2
        assert report['flagged_changes'] > 0
        assert report['flag_rate'] > 0
        assert report['is_safe'] is False

    def test_report_categorizes_warnings(self):
        """Test that report correctly categorizes different warning types."""
        resume = self._create_test_resume()

        changes = [
            # New metrics
            ResumeChange(
                id="c1",
                change_type=ChangeType.EXPERIENCE_BULLET,
                location="experiences[0].bullets[0]",
                before="Improved system",
                after="Improved system by 50%",
                rationale="Added metric"
            ),
            # New organization
            ResumeChange(
                id="c2",
                change_type=ChangeType.EXPERIENCE_BULLET,
                location="experiences[0].bullets[0]",
                before="Worked on project",
                after="Worked on project for Acme Corporation",
                rationale="Added client"
            )
        ]

        report = generate_authenticity_report(changes, resume)

        categories = report['warning_categories']
        assert 'new_metrics' in categories
        assert 'new_organizations' in categories
        assert 'new_technologies' in categories
        assert 'expanded_content' in categories

    def test_report_includes_recommendations(self):
        """Test that report includes actionable recommendations."""
        resume = self._create_test_resume()

        changes = [
            ResumeChange(
                id="c1",
                change_type=ChangeType.EXPERIENCE_BULLET,
                location="experiences[0].bullets[0]",
                before="Led team",
                after="Led team of 100+ engineers",
                rationale="Added size"
            )
        ]

        report = generate_authenticity_report(changes, resume)

        assert 'recommendations' in report
        assert len(report['recommendations']) > 0
        assert isinstance(report['recommendations'][0], str)

    def test_empty_changes_report(self):
        """Test report with no changes."""
        resume = self._create_test_resume()
        report = generate_authenticity_report([], resume)

        assert report['total_changes'] == 0
        assert report['flagged_changes'] == 0
        assert report['flag_rate'] == 0
        assert report['is_safe'] is True
