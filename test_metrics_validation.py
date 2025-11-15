#!/usr/bin/env python3
"""
Validation script for metrics framework.

Tests basic functionality of all metrics scorers and service.
"""

from modules.metrics import (
    MetricScore,
    AuthenticityScorer,
    RoleAlignmentScorer,
    ATSScorer,
    LengthScorer
)
from services.metrics_service import MetricsService

# Sample data
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


def test_metric_score():
    """Test MetricScore creation and conversion."""
    print("Testing MetricScore...")
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

    result_dict = score.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict['name'] == "Test Metric"

    print("✓ MetricScore tests passed")


def test_authenticity_scorer():
    """Test AuthenticityScorer."""
    print("\nTesting AuthenticityScorer...")
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

    print(f"  Score: {result.score:.2%}")
    print(f"  Passed: {result.passed}")
    print(f"  Details: {result.details}")
    print("✓ AuthenticityScorer tests passed")


def test_role_alignment_scorer():
    """Test RoleAlignmentScorer."""
    print("\nTesting RoleAlignmentScorer...")
    scorer = RoleAlignmentScorer(threshold=0.85)

    result = scorer.calculate(
        original_resume=SAMPLE_ORIGINAL_RESUME,
        optimized_resume=SAMPLE_OPTIMIZED_RESUME,
        job_description=SAMPLE_JOB_DESCRIPTION
    )

    assert isinstance(result, MetricScore)
    assert result.name == "Role Alignment"
    assert 0.0 <= result.score <= 1.0

    print(f"  Score: {result.score:.2%}")
    print(f"  Passed: {result.passed}")
    print(f"  Matched keywords: {result.details.get('matched_keywords', 0)}")
    print(f"  Missing keywords: {result.details.get('missing_keywords', 0)}")
    print("✓ RoleAlignmentScorer tests passed")


def test_ats_scorer():
    """Test ATSScorer."""
    print("\nTesting ATSScorer...")
    scorer = ATSScorer(threshold=0.80)

    result = scorer.calculate(
        original_resume=SAMPLE_ORIGINAL_RESUME,
        optimized_resume=SAMPLE_OPTIMIZED_RESUME,
        job_description=SAMPLE_JOB_DESCRIPTION
    )

    assert isinstance(result, MetricScore)
    assert result.name == "ATS Optimization"
    assert 0.0 <= result.score <= 1.0

    print(f"  Score: {result.score:.2%}")
    print(f"  Passed: {result.passed}")
    print(f"  Keyword density: {result.details.get('keyword_density_pct', 0)}%")
    print(f"  Format score: {result.details.get('format_score', 0):.2%}")
    print("✓ ATSScorer tests passed")


def test_length_scorer():
    """Test LengthScorer."""
    print("\nTesting LengthScorer...")
    scorer = LengthScorer(target_pages=2, threshold=0.95)

    result = scorer.calculate(
        original_resume=SAMPLE_ORIGINAL_RESUME,
        optimized_resume=SAMPLE_OPTIMIZED_RESUME,
        job_description=SAMPLE_JOB_DESCRIPTION
    )

    assert isinstance(result, MetricScore)
    assert result.name == "Length Compliance"
    assert 0.0 <= result.score <= 1.0

    print(f"  Score: {result.score:.2%}")
    print(f"  Passed: {result.passed}")
    print(f"  Estimated pages: {result.details.get('estimated_pages', 0):.2f}")
    print(f"  Total words: {result.details.get('total_words', 0)}")
    print("✓ LengthScorer tests passed")


def test_metrics_service():
    """Test MetricsService."""
    print("\nTesting MetricsService...")
    service = MetricsService()

    result = service.calculate_all_metrics(
        original_resume=SAMPLE_ORIGINAL_RESUME,
        optimized_resume=SAMPLE_OPTIMIZED_RESUME,
        job_description=SAMPLE_JOB_DESCRIPTION
    )

    assert result.authenticity is not None
    assert result.role_alignment is not None
    assert result.ats_optimization is not None
    assert result.length_compliance is not None
    assert isinstance(result.overall_passed, bool)
    assert isinstance(result.overall_score, float)

    print(f"\n  Overall Score: {result.overall_score:.2%}")
    print(f"  Overall Passed: {result.overall_passed}")
    print(f"  Failed Metrics: {result.failed_metrics}")
    print(f"\n  Individual Scores:")
    print(f"    Authenticity: {result.authenticity.score:.2%} ({'PASS' if result.authenticity.passed else 'FAIL'})")
    print(f"    Role Alignment: {result.role_alignment.score:.2%} ({'PASS' if result.role_alignment.passed else 'FAIL'})")
    print(f"    ATS Optimization: {result.ats_optimization.score:.2%} ({'PASS' if result.ats_optimization.passed else 'FAIL'})")
    print(f"    Length Compliance: {result.length_compliance.score:.2%} ({'PASS' if result.length_compliance.passed else 'FAIL'})")

    # Test to_dict
    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert 'authenticity' in result_dict
    assert 'overall_score' in result_dict

    # Test summary generation
    summary = service.get_metric_summary(result)
    assert isinstance(summary, str)
    assert "RESUME OPTIMIZATION METRICS REPORT" in summary

    print("\n✓ MetricsService tests passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("METRICS FRAMEWORK VALIDATION")
    print("=" * 60)

    try:
        test_metric_score()
        test_authenticity_scorer()
        test_role_alignment_scorer()
        test_ats_scorer()
        test_length_scorer()
        test_metrics_service()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
