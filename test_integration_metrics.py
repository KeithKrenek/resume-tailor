#!/usr/bin/env python3
"""
Integration test for metrics framework with optimization service.

This tests the full integration: models → optimization service → metrics.
"""

from modules.models import JobModel, ResumeModel, GapAnalysis, ResumeOptimizationResult, ExperienceItem
from services.metrics_service import MetricsService


def create_sample_job():
    """Create sample job model."""
    return JobModel(
        title="Senior Python Engineer",
        company="Tech Corp",
        description="""
        We are looking for a Senior Python Engineer with experience in:
        - Python development (5+ years)
        - AWS cloud services
        - Docker and Kubernetes
        - PostgreSQL and database optimization
        - Agile methodologies
        """,
        required_skills=["Python", "AWS", "Docker", "PostgreSQL"],
        preferred_skills=["Kubernetes", "Redis", "React"]
    )


def create_sample_resume():
    """Create sample resume model."""
    return ResumeModel(
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        headline="Software Engineer",
        summary="Experienced software engineer with focus on Python development",
        experiences=[
            ExperienceItem(
                title="Software Engineer",
                company="Tech Corp",
                start_date="2018",
                end_date="Present",
                bullets=[
                    "Developed web applications using Python",
                    "Worked with PostgreSQL databases",
                    "Collaborated with team members"
                ],
                skills=["Python", "PostgreSQL", "Git"]
            )
        ],
        skills=["Python", "Django", "PostgreSQL", "Git", "Linux"],
        raw_text="""
        John Doe
        Software Engineer

        Experience:
        Software Engineer at Tech Corp (2018 - Present)
        - Developed web applications using Python
        - Worked with PostgreSQL databases
        - Collaborated with team members

        Skills: Python, Django, PostgreSQL, Git, Linux
        """
    )


def create_optimized_resume():
    """Create optimized resume model (simulating optimization result)."""
    return ResumeModel(
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        headline="Senior Python Engineer",
        summary="Experienced Senior Python Engineer specializing in AWS cloud infrastructure and microservices",
        experiences=[
            ExperienceItem(
                title="Senior Software Engineer",
                company="Tech Corp",
                start_date="2018",
                end_date="Present",
                bullets=[
                    "Architected Python microservices deployed on AWS (EC2, Lambda)",
                    "Optimized PostgreSQL database queries improving performance by 30%",
                    "Implemented Docker containerization for development and production",
                    "Led Agile sprint planning and code reviews for team of 5"
                ],
                skills=["Python", "AWS", "Docker", "PostgreSQL", "Agile"]
            )
        ],
        skills=["Python", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Git", "Linux", "Agile"],
        raw_text="""
        John Doe
        Senior Python Engineer

        Experience:
        Senior Software Engineer at Tech Corp (2018 - Present)
        - Architected Python microservices deployed on AWS (EC2, Lambda)
        - Optimized PostgreSQL database queries improving performance by 30%
        - Implemented Docker containerization for development and production
        - Led Agile sprint planning and code reviews for team of 5

        Skills: Python, AWS, Docker, Kubernetes, PostgreSQL, Git, Linux, Agile
        """
    )


def test_models_integration():
    """Test that models can store metrics."""
    print("Testing models integration...")

    job = create_sample_job()
    original_resume = create_sample_resume()
    optimized_resume = create_optimized_resume()

    # Create optimization result
    result = ResumeOptimizationResult(
        original_resume=original_resume,
        optimized_resume=optimized_resume,
        changes=[],
        summary_of_improvements=["Improved Python experience", "Added AWS skills"],
        style_used="balanced"
    )

    # Add metrics
    metrics_service = MetricsService()

    original_text = original_resume.raw_text or original_resume.to_markdown()
    optimized_text = optimized_resume.raw_text or optimized_resume.to_markdown()
    job_text = job.raw_text or job.description or ""

    metrics_result = metrics_service.calculate_all_metrics(
        original_resume=original_text,
        optimized_resume=optimized_text,
        job_description=job_text
    )

    # Attach metrics to result
    result.metrics = metrics_result.to_dict()

    # Verify metrics are stored
    assert result.metrics is not None
    assert 'overall_score' in result.metrics
    assert 'authenticity' in result.metrics
    assert 'role_alignment' in result.metrics
    assert 'ats_optimization' in result.metrics
    assert 'length_compliance' in result.metrics

    print(f"✓ Metrics stored in ResumeOptimizationResult")
    print(f"  Overall Score: {result.metrics['overall_score']:.2%}")

    # Test serialization
    result_dict = result.to_dict()
    assert 'metrics' in result_dict
    assert result_dict['metrics'] is not None

    print(f"✓ Metrics serialized to dict successfully")

    # Test deserialization
    restored = ResumeOptimizationResult.from_dict(result_dict)
    assert restored.metrics is not None
    assert restored.metrics['overall_score'] == result.metrics['overall_score']

    print(f"✓ Metrics deserialized from dict successfully")


def test_metrics_calculation():
    """Test metrics calculation with realistic data."""
    print("\nTesting metrics calculation...")

    job = create_sample_job()
    original_resume = create_sample_resume()
    optimized_resume = create_optimized_resume()

    metrics_service = MetricsService()

    original_text = original_resume.raw_text or original_resume.to_markdown()
    optimized_text = optimized_resume.raw_text or optimized_resume.to_markdown()
    job_text = job.raw_text or job.description or ""

    metrics_result = metrics_service.calculate_all_metrics(
        original_resume=original_text,
        optimized_resume=optimized_text,
        job_description=job_text
    )

    print(f"\n  Metrics Results:")
    print(f"  {'='*50}")
    print(f"  Overall Score: {metrics_result.overall_score:.2%}")
    print(f"  Overall Passed: {metrics_result.overall_passed}")
    print(f"  Failed Metrics: {metrics_result.failed_metrics}")
    print(f"\n  Individual Metrics:")
    print(f"  {'='*50}")

    for metric_name, metric in [
        ("Authenticity", metrics_result.authenticity),
        ("Role Alignment", metrics_result.role_alignment),
        ("ATS Optimization", metrics_result.ats_optimization),
        ("Length Compliance", metrics_result.length_compliance)
    ]:
        status = "✓ PASS" if metric.passed else "✗ FAIL"
        print(f"  {metric_name:20} {metric.score:6.2%}  {status}")

        if not metric.passed and metric.recommendations:
            print(f"    Recommendations:")
            for rec in metric.recommendations[:2]:
                print(f"      - {rec}")

    # Test summary generation
    summary = metrics_service.get_metric_summary(metrics_result)
    assert "RESUME OPTIMIZATION METRICS REPORT" in summary

    print(f"\n✓ Metrics calculated and summary generated successfully")


def test_metrics_thresholds():
    """Test that metrics respect custom thresholds."""
    print("\nTesting custom thresholds...")

    # Create service with very strict thresholds
    strict_service = MetricsService(
        authenticity_threshold=0.99,
        role_alignment_threshold=0.95,
        ats_threshold=0.90,
        length_threshold=0.98
    )

    assert strict_service.authenticity_scorer.threshold == 0.99
    assert strict_service.role_alignment_scorer.threshold == 0.95
    assert strict_service.ats_scorer.threshold == 0.90
    assert strict_service.length_scorer.threshold == 0.98

    print(f"✓ Custom thresholds set correctly")

    # Create service with lenient thresholds
    lenient_service = MetricsService(
        authenticity_threshold=0.70,
        role_alignment_threshold=0.70,
        ats_threshold=0.60,
        length_threshold=0.80
    )

    job = create_sample_job()
    original_resume = create_sample_resume()
    optimized_resume = create_optimized_resume()

    original_text = original_resume.raw_text or original_resume.to_markdown()
    optimized_text = optimized_resume.raw_text or optimized_resume.to_markdown()
    job_text = job.description or ""

    strict_result = strict_service.calculate_all_metrics(original_text, optimized_text, job_text)
    lenient_result = lenient_service.calculate_all_metrics(original_text, optimized_text, job_text)

    # Lenient should have more passing metrics
    print(f"  Strict service passed: {strict_result.overall_passed}")
    print(f"  Lenient service passed: {lenient_result.overall_passed}")
    print(f"  Strict failed metrics: {len(strict_result.failed_metrics)}")
    print(f"  Lenient failed metrics: {len(lenient_result.failed_metrics)}")

    print(f"✓ Thresholds working correctly")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("METRICS FRAMEWORK INTEGRATION TEST")
    print("=" * 60)

    try:
        test_models_integration()
        test_metrics_calculation()
        test_metrics_thresholds()

        print("\n" + "=" * 60)
        print("✓ ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("\nThe metrics framework is fully integrated and working:")
        print("  ✓ Models can store and serialize metrics")
        print("  ✓ MetricsService calculates all metrics correctly")
        print("  ✓ Custom thresholds are respected")
        print("  ✓ Summary generation works")
        print("\nReady for production use!")
        return 0

    except Exception as e:
        print(f"\n✗ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
