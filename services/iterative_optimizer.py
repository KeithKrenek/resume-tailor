"""
Iterative optimization service.
Runs multiple optimization passes with convergence detection.
"""

import logging
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass

from modules.models import JobModel, ResumeModel, GapAnalysis, ResumeOptimizationResult
from services.optimization_service import run_optimization
from services.metrics_service import MetricsService
from utils.version_manager import VersionManager, ResumeVersion
from config.optimization_config import OptimizationConfig

logger = logging.getLogger(__name__)


@dataclass
class IterativeOptimizationResult:
    """Result of iterative optimization process."""
    best_version: ResumeVersion
    all_versions: List[ResumeVersion]
    iterations_run: int
    converged: bool
    convergence_reason: str
    total_time_seconds: float
    final_result: ResumeOptimizationResult  # The actual result for the best version

    def get_final_resume(self) -> ResumeModel:
        """Get the best optimized resume."""
        return self.best_version.optimized_resume

    def get_final_metrics(self) -> dict:
        """Get metrics for the best version."""
        return self.best_version.metrics

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'best_version': self.best_version.to_dict(),
            'all_versions': [v.to_dict() for v in self.all_versions],
            'iterations_run': self.iterations_run,
            'converged': self.converged,
            'convergence_reason': self.convergence_reason,
            'total_time_seconds': self.total_time_seconds
        }


class IterativeOptimizer:
    """
    Iterative optimization engine.
    Runs multiple optimization passes until convergence.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize iterative optimizer.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self.version_manager = VersionManager(max_versions=config.max_iterations + 2)
        self.metrics_service = MetricsService()

    def optimize(
        self,
        job: JobModel,
        resume: ResumeModel,
        gap: GapAnalysis,
        style: str = "balanced",
        api_key: Optional[str] = None
    ) -> IterativeOptimizationResult:
        """
        Run iterative optimization.

        Args:
            job: Job model
            resume: Original resume model
            gap: Gap analysis
            style: Optimization style (conservative, balanced, aggressive)
            api_key: API key for optimization

        Returns:
            IterativeOptimizationResult with best version
        """
        start_time = time.time()

        logger.info(f"Starting iterative optimization (max {self.config.max_iterations} iterations)")

        current_resume = resume
        previous_metrics = None
        converged = False
        convergence_reason = "Max iterations reached"
        last_result = None

        for iteration in range(1, self.config.max_iterations + 1):
            logger.info(f"Starting iteration {iteration}/{self.config.max_iterations}")

            try:
                # Run single optimization pass
                result = self._run_single_optimization(
                    job=job,
                    resume=current_resume,
                    gap=gap,
                    style=style,
                    iteration=iteration,
                    previous_metrics=previous_metrics,
                    api_key=api_key
                )

                last_result = result

                # Store version
                version = self.version_manager.add_version(
                    optimized_resume=result.optimized_resume,
                    metrics=result.metrics or {},
                    changes=result.changes,
                    iteration_number=iteration,
                    config=self.config.to_dict(),
                    improvement_summary=result.summary_of_improvements
                )

                current_metrics = result.metrics
                if current_metrics:
                    overall_score = current_metrics.get('overall_score', 0.0)
                    overall_passed = current_metrics.get('overall_passed', False)
                    logger.info(f"Iteration {iteration} complete. Overall score: {overall_score:.2%}, Passed: {overall_passed}")
                else:
                    logger.warning(f"Iteration {iteration} complete but no metrics available")

                # Check convergence
                if self._check_convergence(current_metrics, previous_metrics, iteration):
                    converged = True
                    convergence_reason = self._get_convergence_reason(current_metrics, previous_metrics)
                    logger.info(f"Converged: {convergence_reason}")
                    break

                # Update for next iteration
                current_resume = result.optimized_resume
                previous_metrics = current_metrics

            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}", exc_info=True)
                # If we have at least one version, return best so far
                if self.version_manager.get_all_versions():
                    convergence_reason = f"Error in iteration {iteration}: {str(e)}"
                    break
                else:
                    raise

        # Get best version (highest overall score)
        best_version = self.version_manager.get_best_version()
        all_versions = self.version_manager.get_all_versions()

        total_time = time.time() - start_time

        logger.info(f"Optimization complete. Ran {len(all_versions)} iterations in {total_time:.1f}s")
        if best_version:
            logger.info(f"Best version: #{best_version.version_number} with score {best_version.get_overall_score():.2%}")

        # Create final result from best version
        final_result = last_result  # Use last result as base
        if best_version and final_result:
            # Update final result with best version's data
            final_result.optimized_resume = best_version.optimized_resume
            final_result.metrics = best_version.metrics
            final_result.changes = best_version.changes
            final_result.summary_of_improvements = best_version.improvement_summary

        return IterativeOptimizationResult(
            best_version=best_version,
            all_versions=all_versions,
            iterations_run=len(all_versions),
            converged=converged,
            convergence_reason=convergence_reason,
            total_time_seconds=total_time,
            final_result=final_result
        )

    def _run_single_optimization(
        self,
        job: JobModel,
        resume: ResumeModel,
        gap: GapAnalysis,
        style: str,
        iteration: int,
        previous_metrics: Optional[dict],
        api_key: Optional[str]
    ) -> ResumeOptimizationResult:
        """
        Run a single optimization pass.

        Args:
            job: Job model
            resume: Resume to optimize (may be already optimized from previous iteration)
            gap: Gap analysis
            style: Optimization style
            iteration: Current iteration number
            previous_metrics: Metrics from previous iteration (None for first iteration)
            api_key: API key

        Returns:
            ResumeOptimizationResult
        """
        # For iterations > 1, identify weak areas and focus on them
        focus_areas = None
        if iteration > 1 and previous_metrics:
            focus_areas = self._identify_weak_areas(previous_metrics)
            logger.info(f"Iteration {iteration} focusing on: {focus_areas}")

        # Run optimization
        # Note: For now, we don't have custom_instructions in run_optimization
        # So we'll just run standard optimization
        # TODO: Future enhancement - pass focus_areas to optimization agent
        result = run_optimization(
            job=job,
            resume=resume,
            gap=gap,
            style=style,
            api_key=api_key,
            enable_authenticity_check=True,
            enable_metrics=True
        )

        return result

    def _identify_weak_areas(self, metrics: dict) -> List[str]:
        """
        Identify which metrics are below threshold.

        Returns:
            List of areas to focus on
        """
        weak_areas = []

        if not metrics:
            return weak_areas

        # Check each metric
        for metric_name in ['authenticity', 'role_alignment', 'ats_optimization', 'length_compliance']:
            metric = metrics.get(metric_name, {})
            if isinstance(metric, dict):
                passed = metric.get('passed', True)
                if not passed:
                    weak_areas.append(metric_name)

        return weak_areas

    def _check_convergence(
        self,
        current_metrics: Optional[dict],
        previous_metrics: Optional[dict],
        iteration: int
    ) -> bool:
        """
        Check if optimization has converged.

        Convergence occurs when:
        1. All critical metrics pass threshold, OR
        2. Improvement over previous iteration is < improvement_threshold
        """
        if not current_metrics:
            return False

        # Check if all critical metrics pass
        overall_passed = current_metrics.get('overall_passed', False)
        if overall_passed:
            overall_score = current_metrics.get('overall_score', 0.0)
            if overall_score >= self.config.convergence_threshold:
                return True

        # For first iteration, can't check improvement
        if iteration == 1 or previous_metrics is None:
            return False

        # Check if improvement plateaued
        current_score = current_metrics.get('overall_score', 0.0)
        previous_score = previous_metrics.get('overall_score', 0.0)
        improvement = current_score - previous_score

        if improvement < self.config.improvement_threshold:
            return True

        return False

    def _get_convergence_reason(
        self,
        current_metrics: Optional[dict],
        previous_metrics: Optional[dict]
    ) -> str:
        """Get human-readable convergence reason."""

        if not current_metrics:
            return "No metrics available"

        overall_passed = current_metrics.get('overall_passed', False)
        overall_score = current_metrics.get('overall_score', 0.0)

        if overall_passed and overall_score >= self.config.convergence_threshold:
            return f"All critical metrics passed threshold (score: {overall_score:.1%} >= {self.config.convergence_threshold:.1%})"

        if previous_metrics:
            current_score = current_metrics.get('overall_score', 0.0)
            previous_score = previous_metrics.get('overall_score', 0.0)
            improvement = current_score - previous_score

            if improvement < self.config.improvement_threshold:
                return f"Improvement plateaued (improvement: {improvement:.1%} < threshold: {self.config.improvement_threshold:.1%})"

        return "Unknown convergence reason"
