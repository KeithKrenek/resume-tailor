#!/usr/bin/env python3
"""
Validation script for Phase 2: Iterative Optimization.

Tests tier configuration, version management, and iterative optimization.
"""

from config.optimization_config import OptimizationConfig, OptimizationTier
from utils.version_manager import VersionManager, ResumeVersion
from datetime import datetime


def test_optimization_config():
    """Test OptimizationConfig dataclass."""
    print("Testing OptimizationConfig...")

    config = OptimizationConfig(
        max_iterations=3,
        convergence_threshold=0.85,
        improvement_threshold=0.02
    )

    assert config.max_iterations == 3
    assert config.convergence_threshold == 0.85
    assert config.improvement_threshold == 0.02
    print("✓ OptimizationConfig created")

    # Test to_dict
    config_dict = config.to_dict()
    assert 'max_iterations' in config_dict
    assert config_dict['max_iterations'] == 3
    print("✓ to_dict() works")

    print("\n[1/5] OptimizationConfig: PASSED ✓")


def test_optimization_tiers():
    """Test OptimizationTier presets."""
    print("\nTesting OptimizationTier...")

    # Test BASIC tier
    basic = OptimizationTier.BASIC
    assert basic.max_iterations == 1
    assert basic.estimated_cost_usd == 0.50
    assert basic.enable_version_history == False
    print("✓ BASIC tier configured correctly")

    # Test STANDARD tier
    standard = OptimizationTier.STANDARD
    assert standard.max_iterations == 3
    assert standard.estimated_cost_usd == 2.00
    assert standard.enable_version_history == True
    print("✓ STANDARD tier configured correctly")

    # Test PREMIUM tier
    premium = OptimizationTier.PREMIUM
    assert premium.max_iterations == 5
    assert premium.estimated_cost_usd == 5.00
    assert premium.enable_version_history == True
    print("✓ PREMIUM tier configured correctly")

    # Test get_tier()
    tier = OptimizationTier.get_tier("standard")
    assert tier.max_iterations == 3
    print("✓ get_tier() works")

    # Test get_all_tiers()
    all_tiers = OptimizationTier.get_all_tiers()
    assert 'basic' in all_tiers
    assert 'standard' in all_tiers
    assert 'premium' in all_tiers
    print("✓ get_all_tiers() works")

    print("\n[2/5] OptimizationTier: PASSED ✓")


def test_version_manager():
    """Test VersionManager."""
    print("\nTesting VersionManager...")

    vm = VersionManager(max_versions=5)
    print("✓ VersionManager created")

    # Create mock resume and metrics
    class MockResume:
        def to_dict(self):
            return {"name": "Test Resume"}

    # Add first version
    version1 = vm.add_version(
        optimized_resume=MockResume(),
        metrics={'overall_score': 0.75, 'overall_passed': False},
        changes=[],
        iteration_number=1,
        config={'max_iterations': 3}
    )

    assert version1.version_number == 1
    assert version1.iteration_number == 1
    print("✓ add_version() works")

    # Add second version
    version2 = vm.add_version(
        optimized_resume=MockResume(),
        metrics={'overall_score': 0.85, 'overall_passed': True},
        changes=[],
        iteration_number=2,
        config={'max_iterations': 3}
    )

    assert version2.version_number == 2
    print("✓ Multiple versions tracked")

    # Test get_version()
    retrieved = vm.get_version(1)
    assert retrieved.version_number == 1
    print("✓ get_version() works")

    # Test get_latest_version()
    latest = vm.get_latest_version()
    assert latest.version_number == 2
    print("✓ get_latest_version() works")

    # Test get_best_version()
    best = vm.get_best_version()
    assert best.get_overall_score() == 0.85
    print("✓ get_best_version() works (selects highest score)")

    # Test get_all_versions()
    all_versions = vm.get_all_versions()
    assert len(all_versions) == 2
    print("✓ get_all_versions() works")

    # Test version count
    assert vm.get_version_count() == 2
    print("✓ get_version_count() works")

    # Test compare_versions()
    comparison = vm.compare_versions(1, 2)
    assert abs(comparison['score_delta'] - 0.10) < 0.01, f"Expected 0.10, got {comparison['score_delta']}"
    print("✓ compare_versions() works")

    # Test improvement trajectory
    trajectory = vm.get_improvement_trajectory()
    assert len(trajectory) == 2
    assert trajectory[0]['iteration'] == 1
    assert trajectory[1]['iteration'] == 2
    print("✓ get_improvement_trajectory() works")

    print("\n[3/5] VersionManager: PASSED ✓")


def test_resume_version():
    """Test ResumeVersion dataclass."""
    print("\nTesting ResumeVersion...")

    class MockResume:
        def to_dict(self):
            return {"name": "Test"}

    version = ResumeVersion(
        version_number=1,
        timestamp=datetime.now(),
        optimized_resume=MockResume(),
        metrics={'overall_score': 0.85},
        changes=[],
        iteration_number=1,
        config={}
    )

    assert version.version_number == 1
    assert version.get_overall_score() == 0.85
    print("✓ ResumeVersion created")
    print(f"✓ get_overall_score() returns {version.get_overall_score():.2%}")

    # Test to_dict
    version_dict = version.to_dict()
    assert 'version_number' in version_dict
    assert 'metrics' in version_dict
    print("✓ to_dict() works")

    print("\n[4/5] ResumeVersion: PASSED ✓")


def test_tier_configuration_integration():
    """Test that tier configurations make sense."""
    print("\nTesting tier configuration logic...")

    basic = OptimizationTier.BASIC
    standard = OptimizationTier.STANDARD
    premium = OptimizationTier.PREMIUM

    # Basic should be cheapest and fastest
    assert basic.max_iterations < standard.max_iterations
    assert basic.estimated_cost_usd < standard.estimated_cost_usd
    assert basic.estimated_time_seconds < standard.estimated_time_seconds
    print("✓ Basic tier is cheapest/fastest")

    # Standard should be in the middle
    assert standard.max_iterations < premium.max_iterations
    assert standard.estimated_cost_usd < premium.estimated_cost_usd
    print("✓ Standard tier is mid-tier")

    # Premium should have most features
    assert premium.max_iterations >= 5
    assert premium.enable_version_history == True
    print("✓ Premium tier has most features")

    # All tiers should have required metrics
    for tier_name in ['basic', 'standard', 'premium']:
        tier = OptimizationTier.get_tier(tier_name)
        assert 'authenticity' in tier.metrics_to_calculate
        print(f"✓ {tier_name.capitalize()} tier includes authenticity metric")

    print("\n[5/5] Tier Configuration Integration: PASSED ✓")


def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 2 VALIDATION")
    print("Iterative Optimization & Version Management")
    print("=" * 60)

    try:
        test_optimization_config()
        test_optimization_tiers()
        test_version_manager()
        test_resume_version()
        test_tier_configuration_integration()

        print("\n" + "=" * 60)
        print("✓ ALL PHASE 2 COMPONENT TESTS PASSED!")
        print("=" * 60)
        print("\nPhase 2 components are working correctly:")
        print("  ✓ OptimizationConfig with tiers (Basic/Standard/Premium)")
        print("  ✓ VersionManager for tracking iterations")
        print("  ✓ ResumeVersion for storing optimization results")
        print("  ✓ Tier presets with appropriate costs/features")
        print("  ✓ Version comparison and trajectory tracking")
        print("\nReady for integration testing!")
        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
