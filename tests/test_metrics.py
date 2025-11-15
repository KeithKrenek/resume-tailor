"""
Tests for metrics framework.

Tests the quantitative metrics system for evaluating resume optimization quality.
"""

import pytest
from modules.metrics import (
    MetricScore,
    AuthenticityScorer,
    RoleAlignmentScorer,
    ATSScorer,
    LengthScorer
)
from services.metrics_service import MetricsService, MetricsResult


# Sample data for testing
SAMPLE_JOB_DESCRIPTION = """
Senior Software Engineer - Python/AWS

Requirements:
- 5+ years experience with Python
- Experience with AWS services (EC2, S3, Lambda)
- Strong understanding of Docker and Kubernetes
- Experience with PostgreSQL and Redis
- Excellent communication skills
- Experience with React and TypeScript is preferred
- Understanding of Agile methodologies
"""

SAMPLE_ORIGINAL_RESUME = """
John Doe
Software Engineer

Experience:
Software Engineer at Tech Corp
2018 - Present
- Developed web applications using Python and Django
- Worked with databases including PostgreSQL
- Collaborated with team members
- Participated in code reviews

Skills: Python, Django, PostgreSQL, Git, Linux
"""

SAMPLE_OPTIMIZED_RESUME = """
John Doe
Senior Software Engineer

Experience:
Senior Software Engineer at Tech Corp
2018 - Present
- Architected and deployed scalable Python microservices on AWS (EC2, Lambda, S3)
- Optimized PostgreSQL database performance, reducing query times by 40%
- Containerized applications using Docker and orchestrated with Kubernetes
- Implemented Redis caching layer, improving response times by 35%
- Led Agile development team of 5 engineers
- Collaborated with cross-functional teams to deliver high-quality software

Skills: Python, Django, AWS, Docker, Kubernetes, PostgreSQL, Redis, Git, Linux, Agile
"""


class TestMetricScore:
    """Test MetricScore dataclass."""

    def test_metric_score_creation(self):
        """Test creating a MetricScore."""
        score = MetricScore(
            name="Test Metric",
            score=0.85,
            passed=True,
            threshold=0.80,
            details={"foo": "bar"},
            recommendations=["Recommendation 1"]
        )

        assert score.name == "Test Metric"
        assert score.score == 0.85
        assert score.passed is True
        assert score.threshold == 0.80
        assert score.details == {"foo": "bar"}
        assert score.recommendations == ["Recommendation 1"]

    def test_metric_score_to_dict(self):
        """Test converting MetricScore to dictionary."""
        score = MetricScore(
            name="Test Metric",
            score=0.85,
            passed=True,
            threshold=0.80,
            details={"foo": "bar"},
            recommendations=["Rec 1"]
        )

        result = score.to_dict()

        assert isinstance(result, dict)
        assert result['name'] == "Test Metric"
        assert result['score'] == 0.85
        assert result['passed'] is True


class TestAuthenticityScorer:
    """Test AuthenticityScorer."""

    def test_authenticity_scorer_creation(self):
        """Test creating an AuthenticityScorer."""
        scorer = AuthenticityScorer(threshold=0.90)
        assert scorer.threshold == 0.90
        assert scorer.get_threshold() == 0.90

    def test_authenticity_basic_check(self):
        """Test basic authenticity check."""
        scorer = AuthenticityScorer(threshold=0.90)

        result = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        assert isinstance(result, MetricScore)
        assert result.name == "Authenticity"
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.passed, bool)
        assert isinstance(result.recommendations, list)

    def test_authenticity_detects_new_numbers(self):
        """Test that authenticity scorer detects new numbers."""
        scorer = AuthenticityScorer(threshold=0.90)

        # Resume with new metrics not in original
        fabricated_resume = SAMPLE_ORIGINAL_RESUME + "\n- Increased sales by 500%"

        result = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=fabricated_resume,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        # Should detect red flags
        assert result.details.get('red_flags_count', 0) > 0


class TestRoleAlignmentScorer:
    """Test RoleAlignmentScorer."""

    def test_role_alignment_scorer_creation(self):
        """Test creating a RoleAlignmentScorer."""
        scorer = RoleAlignmentScorer(threshold=0.85)
        assert scorer.threshold == 0.85
        assert scorer.get_threshold() == 0.85

    def test_role_alignment_basic_check(self):
        """Test basic role alignment check."""
        scorer = RoleAlignmentScorer(threshold=0.85)

        result = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        assert isinstance(result, MetricScore)
        assert result.name == "Role Alignment"
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.passed, bool)

    def test_role_alignment_better_after_optimization(self):
        """Test that optimized resume scores higher than original."""
        scorer = RoleAlignmentScorer(threshold=0.85)

        # Score original resume
        result_original = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_ORIGINAL_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        # Score optimized resume
        result_optimized = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        # Optimized should score higher
        assert result_optimized.score > result_original.score

    def test_role_alignment_keyword_extraction(self):
        """Test keyword extraction from job description."""
        scorer = RoleAlignmentScorer()

        keywords = scorer._extract_keywords(SAMPLE_JOB_DESCRIPTION)
        tech_terms = scorer._extract_technical_terms(SAMPLE_JOB_DESCRIPTION)

        # Should extract some keywords
        assert len(keywords) > 0

        # Should extract technical terms
        assert 'python' in tech_terms
        assert 'aws' in tech_terms or 'docker' in tech_terms


class TestATSScorer:
    """Test ATSScorer."""

    def test_ats_scorer_creation(self):
        """Test creating an ATSScorer."""
        scorer = ATSScorer(threshold=0.80)
        assert scorer.threshold == 0.80
        assert scorer.get_threshold() == 0.80

    def test_ats_basic_check(self):
        """Test basic ATS check."""
        scorer = ATSScorer(threshold=0.80)

        result = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        assert isinstance(result, MetricScore)
        assert result.name == "ATS Optimization"
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.details, dict)

    def test_ats_keyword_density(self):
        """Test keyword density calculation."""
        scorer = ATSScorer()

        result = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        # Should have keyword density details
        assert 'keyword_density_pct' in result.details
        assert isinstance(result.details['keyword_density_pct'], (int, float))

    def test_ats_structure_score(self):
        """Test structure scoring."""
        scorer = ATSScorer()

        result = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        # Should have structure score
        assert 'structure_score' in result.details
        assert 'has_standard_sections' in result.details


class TestLengthScorer:
    """Test LengthScorer."""

    def test_length_scorer_creation(self):
        """Test creating a LengthScorer."""
        scorer = LengthScorer(target_pages=2, threshold=0.95)
        assert scorer.target_pages == 2
        assert scorer.threshold == 0.95
        assert scorer.get_threshold() == 0.95

    def test_length_basic_check(self):
        """Test basic length check."""
        scorer = LengthScorer(target_pages=2)

        result = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        assert isinstance(result, MetricScore)
        assert result.name == "Length Compliance"
        assert 0.0 <= result.score <= 1.0

    def test_length_estimation(self):
        """Test page length estimation."""
        scorer = LengthScorer(target_pages=2)

        # Estimate pages for sample resume
        estimated = scorer._estimate_pages(SAMPLE_OPTIMIZED_RESUME)

        # Should estimate reasonable page count
        assert 0.1 <= estimated <= 10.0

    def test_length_details(self):
        """Test that details contain useful information."""
        scorer = LengthScorer(target_pages=2)

        result = scorer.calculate(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        # Should have useful details
        assert 'estimated_pages' in result.details
        assert 'total_words' in result.details
        assert 'total_characters' in result.details


class TestMetricsService:
    """Test MetricsService."""

    def test_metrics_service_creation(self):
        """Test creating a MetricsService."""
        service = MetricsService()
        assert service is not None
        assert service.authenticity_scorer is not None
        assert service.role_alignment_scorer is not None
        assert service.ats_scorer is not None
        assert service.length_scorer is not None

    def test_metrics_service_custom_thresholds(self):
        """Test creating service with custom thresholds."""
        service = MetricsService(
            authenticity_threshold=0.95,
            role_alignment_threshold=0.90,
            ats_threshold=0.85,
            length_threshold=0.90,
            target_pages=1
        )

        assert service.authenticity_scorer.threshold == 0.95
        assert service.role_alignment_scorer.threshold == 0.90
        assert service.ats_scorer.threshold == 0.85
        assert service.length_scorer.threshold == 0.90
        assert service.length_scorer.target_pages == 1

    def test_calculate_all_metrics(self):
        """Test calculating all metrics."""
        service = MetricsService()

        result = service.calculate_all_metrics(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        assert isinstance(result, MetricsResult)
        assert isinstance(result.authenticity, MetricScore)
        assert isinstance(result.role_alignment, MetricScore)
        assert isinstance(result.ats_optimization, MetricScore)
        assert isinstance(result.length_compliance, MetricScore)
        assert isinstance(result.overall_passed, bool)
        assert isinstance(result.overall_score, float)
        assert isinstance(result.failed_metrics, list)
        assert isinstance(result.recommendations, list)

    def test_metrics_result_to_dict(self):
        """Test converting MetricsResult to dict."""
        service = MetricsService()

        result = service.calculate_all_metrics(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert 'authenticity' in result_dict
        assert 'role_alignment' in result_dict
        assert 'ats_optimization' in result_dict
        assert 'length_compliance' in result_dict
        assert 'overall_passed' in result_dict
        assert 'overall_score' in result_dict

    def test_get_metric_summary(self):
        """Test generating metric summary text."""
        service = MetricsService()

        result = service.calculate_all_metrics(
            original_resume=SAMPLE_ORIGINAL_RESUME,
            optimized_resume=SAMPLE_OPTIMIZED_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        summary = service.get_metric_summary(result)

        assert isinstance(summary, str)
        assert "RESUME OPTIMIZATION METRICS REPORT" in summary
        assert "Overall Score" in summary


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
