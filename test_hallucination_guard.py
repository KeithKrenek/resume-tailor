#!/usr/bin/env python3
"""Integration test for the Hallucination Guard (Authenticity Agent)."""

import os
import sys
from modules.models import ResumeModel, ExperienceItem, ResumeChange, ChangeType
from agents.authenticity_agent import create_authenticity_agent, AuthenticityAgent


def test_agent_creation():
    """Test that we can create an authenticity agent."""
    print("=" * 60)
    print("Testing Hallucination Guard - Agent Creation")
    print("=" * 60)

    try:
        agent = create_authenticity_agent(model="claude-3-haiku-20240307")
        print("✓ AuthenticityAgent created successfully")
        print(f"  Model: {agent.model}")
        print(f"  API Key configured: {'Yes' if agent.api_key else 'No'}")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Make sure 'anthropic' is installed: pip install anthropic")
        return False
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("  Make sure ANTHROPIC_API_KEY environment variable is set")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_data_structures():
    """Test the data structures."""
    print("\n" + "=" * 60)
    print("Testing Data Structures")
    print("=" * 60)

    try:
        from agents.authenticity_agent import AuthenticityIssue, AuthenticityReport

        # Create a sample issue
        issue = AuthenticityIssue(
            type="fabrication",
            severity="high",
            location="experience[0].bullets[0]",
            original_text="Built a web app",
            modified_text="Led development of award-winning web app serving 1M users",
            explanation="Added metrics and 'award-winning' without evidence",
            recommendation="Remove fabricated metrics and qualifiers"
        )

        print("✓ AuthenticityIssue created successfully")
        print(f"  Type: {issue.type}")
        print(f"  Severity: {issue.severity}")

        # Test serialization
        issue_dict = issue.to_dict()
        issue_from_dict = AuthenticityIssue.from_dict(issue_dict)

        assert issue_from_dict.type == issue.type
        assert issue_from_dict.severity == issue.severity

        print("✓ Serialization working correctly")

        # Create a report
        report = AuthenticityReport(
            total_changes_analyzed=5,
            issues_found=[issue],
            is_safe=False,
            overall_risk_level="high",
            summary="Found 1 fabrication with high severity",
            recommendations=["Review and correct fabricated content"]
        )

        print("✓ AuthenticityReport created successfully")
        print(f"  Total changes: {report.total_changes_analyzed}")
        print(f"  Issues found: {len(report.issues_found)}")
        print(f"  Is safe: {report.is_safe}")
        print(f"  Risk level: {report.overall_risk_level}")

        # Test helper methods
        fabrications = report.get_fabrications()
        high_severity = report.get_high_severity_issues()

        print(f"✓ Helper methods working")
        print(f"  Fabrications: {len(fabrications)}")
        print(f"  High severity: {len(high_severity)}")

        return True

    except Exception as e:
        print(f"✗ Data structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models_integration():
    """Test integration with ResumeOptimizationResult."""
    print("\n" + "=" * 60)
    print("Testing Models Integration")
    print("=" * 60)

    try:
        from modules.models import ResumeOptimizationResult

        # Create a simple resume
        original = ResumeModel(name="Test User", email="test@example.com")
        optimized = ResumeModel(name="Test User", email="test@example.com")

        # Create result without authenticity report
        result = ResumeOptimizationResult(
            original_resume=original,
            optimized_resume=optimized,
            changes=[]
        )

        print("✓ ResumeOptimizationResult created")
        print(f"  Has LLM report: {result.has_llm_authenticity_report()}")
        assert result.has_llm_authenticity_report() is False

        # Add an authenticity report
        result.authenticity_report = {
            'total_changes_analyzed': 0,
            'issues_found': [],
            'is_safe': True,
            'overall_risk_level': 'low',
            'summary': 'No issues found',
            'recommendations': []
        }

        print("✓ Authenticity report attached")
        print(f"  Has LLM report: {result.has_llm_authenticity_report()}")
        assert result.has_llm_authenticity_report() is True

        # Test get_authenticity_report
        report = result.get_authenticity_report()
        print("✓ get_authenticity_report() working")
        print(f"  Is safe: {report.get('is_safe')}")
        print(f"  Total changes: {report.get('total_changes')}")

        return True

    except Exception as e:
        print(f"✗ Models integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_service_integration():
    """Test integration with optimization service."""
    print("\n" + "=" * 60)
    print("Testing Service Integration")
    print("=" * 60)

    try:
        from services.optimization_service import run_optimization

        # Check that the function accepts enable_authenticity_check parameter
        import inspect
        sig = inspect.signature(run_optimization)
        params = sig.parameters

        assert 'enable_authenticity_check' in params
        print("✓ run_optimization has enable_authenticity_check parameter")

        default_value = params['enable_authenticity_check'].default
        print(f"  Default value: {default_value}")
        assert default_value is True

        print("✓ Service layer integration ready")

        return True

    except Exception as e:
        print(f"✗ Service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "HALLUCINATION GUARD TEST SUITE" + " " * 17 + "║")
    print("║" + " " * 12 + "Phase 2: AI-Powered Verification" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    results = []

    # Test 1: Agent creation
    results.append(test_agent_creation())

    # Test 2: Data structures
    results.append(test_data_structures())

    # Test 3: Models integration
    results.append(test_models_integration())

    # Test 4: Service integration
    results.append(test_service_integration())

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("\n🎉 Hallucination Guard is ready to use!")
        print("\nFeatures:")
        print("  • LLM-based authenticity verification using Claude Haiku")
        print("  • Detects fabrications and exaggerations")
        print("  • Provides structured reports with severity levels")
        print("  • Integrated into optimization pipeline")
        print("  • Rich UI display of issues")
        print("=" * 60)
        return 0
    else:
        failed = total - passed
        print(f"✗ {failed} test(s) failed ({passed}/{total} passed)")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
