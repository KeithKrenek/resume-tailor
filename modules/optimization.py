"""Step 3: Resume Optimization module."""

import streamlit as st
from typing import Optional
import pandas as pd

from modules.models import (
    JobModel, ResumeModel, GapAnalysis,
    ResumeOptimizationResult, ChangeType
)
from services.optimization_service import run_optimization, validate_optimization_inputs
from utils.output_manager import OutputManager
from utils.session_manager import (
    get_all_inputs,
    SESSION_KEYS,
    mark_step_complete,
    set_current_step
)
from config.settings import TOTAL_STEPS, STEP_NAMES


def render_progress_bar(current_step: int) -> None:
    """
    Render progress bar showing current step.

    Args:
        current_step: Current step number (1 to TOTAL_STEPS)
    """
    progress = current_step / TOTAL_STEPS
    step_name = STEP_NAMES.get(current_step, "Unknown")

    st.markdown(f"### 🎯 Progress: Step {current_step} of {TOTAL_STEPS} - {step_name}")
    st.progress(progress)
    st.markdown("---")


def perform_optimization(
    job: JobModel,
    resume: ResumeModel,
    gap: GapAnalysis,
    style: str
) -> tuple[Optional[ResumeOptimizationResult], list]:
    """
    Perform resume optimization using the service layer.

    Args:
        job: Job model
        resume: Resume model
        gap: Gap analysis
        style: Optimization style

    Returns:
        Tuple of (ResumeOptimizationResult, errors)
    """
    errors = []

    # Validate inputs first
    is_valid, error_msg = validate_optimization_inputs(job, resume, gap)
    if not is_valid:
        st.error(f"❌ {error_msg}")
        return None, [error_msg]

    with st.status("✨ Optimizing resume...", expanded=True) as status:
        st.write(f"Using {style} optimization style...")
        st.write("Analyzing gaps and rewriting content...")

        try:
            result = run_optimization(
                job=job,
                resume=resume,
                gap=gap,
                style=style
            )
            success = True
            error = ""
            st.write(f"✅ Optimization complete - {len(result.changes)} changes made")
            status.update(label="✅ Resume optimized", state="complete")
        except ValueError as e:
            result = None
            success = False
            error = str(e)
            st.error(f"❌ {error}")
            errors.append(error)
            status.update(label="❌ Optimization failed", state="error")
            return None, errors

    # Save results
    if result:
        with st.status("💾 Saving optimized resume...", expanded=False) as status:
            try:
                inputs = get_all_inputs()
                output_manager = OutputManager(inputs['output_folder'])

                # Save optimization result
                success, file_path = output_manager.save_optimization_result(result)
                if not success:
                    st.warning(f"⚠️ Could not save: {file_path}")
                else:
                    st.write(f"✅ Saved to {file_path}")

                status.update(label="✅ Results saved", state="complete")
            except Exception as e:
                st.error(f"❌ Save error: {str(e)}")
                errors.append(str(e))

    return result, errors


def render_optimization_controls() -> tuple[str, str, bool, str, bool]:
    """
    Render optimization control panel.

    Returns:
        Tuple of (tier, style, run_optimization, model_id, enable_research)
    """
    from config.optimization_config import OptimizationTier

    st.markdown("### ⚙️ Optimization Settings")

    # Model selection
    st.markdown("#### 🤖 AI Model Selection")

    try:
        from utils.model_provider import get_available_models

        available_models = get_available_models()

        if available_models:
            model_options = [
                f"{m.display_name} (${m.cost_per_1k_output:.3f}/1k tokens)"
                for m in available_models
            ]

            model_choice = st.selectbox(
                "Choose AI Model",
                options=model_options,
                index=0,  # Default to first available (usually Claude Sonnet)
                help="Different models offer varying quality, speed, and cost tradeoffs"
            )

            # Extract selected model
            selected_model_idx = model_options.index(model_choice)
            selected_model = available_models[selected_model_idx]
            model_id = selected_model.model_id

            # Show model info
            with st.expander("ℹ️ Model Information"):
                st.write(f"**Provider:** {selected_model.provider.value}")
                st.write(f"**Cost:** ${selected_model.cost_per_1k_input:.4f} per 1k input tokens")
                st.write(f"**Cost:** ${selected_model.cost_per_1k_output:.4f} per 1k output tokens")
                st.write(f"**Context Window:** {selected_model.context_window:,} tokens")
        else:
            st.warning("No AI models available. Please set API keys in .env file.")
            model_id = "claude-sonnet-4-20250514"  # Fallback
    except Exception as e:
        st.warning(f"Could not load model options: {e}")
        model_id = "claude-sonnet-4-20250514"  # Fallback

    st.markdown("---")

    # Tier selection
    st.markdown("#### 📊 Optimization Tier")

    tier_choice = st.radio(
        "Choose optimization tier",
        options=[
            "Basic - Fast & Affordable ($0.50, ~2 min, 1 iteration)",
            "Standard - Balanced Quality ($2.00, ~8 min, up to 3 iterations) ⭐ Recommended",
            "Premium - Maximum Quality ($5.00, ~20 min, up to 5 iterations)"
        ],
        index=1,  # Default to Standard
        help="""
        - **Basic**: Single-pass optimization, essential metrics only
        - **Standard**: Multi-pass refinement with full metrics tracking
        - **Premium**: Maximum iterations with version history and convergence detection
        """
    )

    # Parse tier choice
    if "Basic" in tier_choice:
        tier = "basic"
    elif "Premium" in tier_choice:
        tier = "premium"
    else:
        tier = "standard"

    # Get tier config
    config = OptimizationTier.get_tier(tier)

    # Show what's included
    with st.expander("📋 What's included in this tier?"):
        st.write(f"**Max Iterations:** {config.max_iterations}")
        st.write(f"**Convergence Threshold:** {config.convergence_threshold:.0%}")
        st.write(f"**Metrics Tracked:** {', '.join(config.metrics_to_calculate)}")
        st.write(f"**Output Formats:** {', '.join(config.output_formats)}")
        st.write(f"**Version History:** {'✓' if config.enable_version_history else '✗'}")
        st.write(f"**Estimated Time:** ~{config.estimated_time_seconds // 60} minutes")
        st.write(f"**Estimated Cost:** ~${config.estimated_cost_usd:.2f}")

    st.markdown("---")

    # Style selector
    st.markdown("#### 🎨 Optimization Style")

    style = st.selectbox(
        "Choose style",
        options=["conservative", "balanced", "aggressive"],
        index=1,  # Default to "balanced"
        help="""
        - **Conservative**: Minimal changes, only obvious improvements
        - **Balanced**: Moderate improvements with keyword optimization
        - **Aggressive**: Comprehensive rewrite for maximum job match
        """
    )

    # Style description
    descriptions = {
        "conservative": "🛡️ Makes minimal, safe changes while preserving your voice",
        "balanced": "⚖️ Optimizes for job match while maintaining authenticity",
        "aggressive": "🚀 Maximizes keyword density and ATS compatibility"
    }
    st.info(descriptions[style])

    st.markdown("---")

    # Company research option
    st.markdown("#### 🔍 Company Research")

    enable_research = st.checkbox(
        "Enable Company & Industry Research",
        value=config.enable_company_research,
        help="Use AI to research the company and industry for better optimization (adds ~30 seconds)"
    )

    if enable_research:
        st.info("💡 Research will provide company culture insights and industry-specific keywords")

    # Run button
    run_optimization = st.button(
        "✨ Optimize Resume",
        type="primary",
        use_container_width=True
    )

    return tier, style, run_optimization, model_id, enable_research


def render_summary_metrics(result: ResumeOptimizationResult, gap_before=None, gap_after=None):
    """Render summary metrics of optimization."""
    st.markdown("### 📊 Optimization Summary")

    # Show gap analysis before/after if available
    if gap_before and gap_after:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            coverage_delta = gap_after.coverage_percentage - gap_before.coverage_percentage
            st.metric(
                "Match Coverage",
                f"{gap_after.coverage_percentage:.1f}%",
                delta=f"{coverage_delta:+.1f}%",
                help="Percentage of job requirements covered"
            )

        with col2:
            before_matched = len(gap_before.matched_skills)
            after_matched = len(gap_after.matched_skills)
            st.metric(
                "Skills Matched",
                after_matched,
                delta=after_matched - before_matched,
                help="Number of required skills present"
            )

        with col3:
            before_missing = len(gap_before.missing_required_skills)
            after_missing = len(gap_after.missing_required_skills)
            st.metric(
                "Missing Skills",
                after_missing,
                delta=after_missing - before_missing,
                delta_color="inverse",
                help="Required skills not found in resume"
            )

        with col4:
            st.metric(
                "Total Changes",
                result.get_total_changes(),
                help="Number of modifications made"
            )

    else:
        # Fallback to original metrics if gap analysis not available
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Changes", result.get_total_changes())

        with col2:
            change_counts = result.get_change_count_by_type()
            bullet_changes = change_counts.get('experience_bullet', 0)
            st.metric("Bullets Improved", bullet_changes)

        with col3:
            summary_changed = 1 if change_counts.get('summary', 0) > 0 else 0
            headline_changed = 1 if change_counts.get('headline', 0) > 0 else 0
            st.metric("Sections Updated", summary_changed + headline_changed)

        with col4:
            skills_changes = change_counts.get('skills_section', 0)
            st.metric("Skills Added/Modified", skills_changes)

    # Authenticity Check Section
    st.markdown("---")
    st.markdown("#### 🔍 Authenticity Check")

    report = result.get_authenticity_report()
    flagged_count = report.get("flagged_changes", 0)
    total_changes = report.get("total_changes", len(result.changes))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Flagged Changes",
            flagged_count,
            help="Changes that may introduce new content"
        )

    with col2:
        flag_rate = report.get("flag_rate", 0)
        st.metric(
            "Flag Rate",
            f"{flag_rate:.1f}%",
            help="Percentage of changes flagged for review"
        )

    with col3:
        is_safe = report.get("is_safe", True)
        if is_safe:
            st.success("✓ No concerns detected")
        else:
            st.warning(f"⚠️ Review {flagged_count} changes")

    # Show warning if there are risky changes
    if flagged_count > 0:
        categories = report.get("warning_categories", {})
        warnings = []
        if categories.get("new_metrics", 0) > 0:
            warnings.append(f"{categories['new_metrics']} with new metrics")
        if categories.get("new_organizations", 0) > 0:
            warnings.append(f"{categories['new_organizations']} with new organizations")
        if categories.get("new_technologies", 0) > 0:
            warnings.append(f"{categories['new_technologies']} with new technologies")
        if categories.get("expanded_content", 0) > 0:
            warnings.append(f"{categories['expanded_content']} with expanded content")

        if warnings:
            st.warning(
                f"**Authenticity Alert:** Found changes - " + ", ".join(warnings) + ".\n\n"
                "Please review these carefully before using the resume. "
                "Use the 'Show only flagged changes' filter in the Changes tab."
            )

        # Show recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            with st.expander("📋 Review Recommendations"):
                for rec in recommendations:
                    st.markdown(f"- {rec}")


def render_metrics_dashboard(result: ResumeOptimizationResult):
    """Render quality metrics dashboard."""
    if not result.metrics:
        return

    st.markdown("### 📊 Quality Metrics")
    metrics_data = result.metrics

    # Overall status
    overall_passed = metrics_data.get('overall_passed', False)
    overall_score = metrics_data.get('overall_score', 0.0)

    col1, col2 = st.columns([1, 3])
    with col1:
        if overall_passed:
            st.success(f"✅ **PASSED**\n\nOverall Score: {overall_score:.1%}")
        else:
            st.error(f"❌ **NEEDS IMPROVEMENT**\n\nOverall Score: {overall_score:.1%}")

    with col2:
        failed_metrics = metrics_data.get('failed_metrics', [])
        if failed_metrics:
            st.warning(f"**Failed Metrics:** {', '.join(failed_metrics)}")
        else:
            st.success("**All metrics passed!** Resume meets quality standards.")

    st.markdown("---")

    # Individual metrics cards
    col1, col2, col3, col4 = st.columns(4)

    metrics_list = [
        ('authenticity', col1, "🔍 Authenticity"),
        ('role_alignment', col2, "🎯 Role Alignment"),
        ('ats_optimization', col3, "🤖 ATS Optimization"),
        ('length_compliance', col4, "📏 Length")
    ]

    for metric_key, col, label in metrics_list:
        metric = metrics_data.get(metric_key, {})
        if not metric:
            continue

        with col:
            score = metric.get('score', 0.0)
            passed = metric.get('passed', False)
            threshold = metric.get('threshold', 0.0)

            # Determine color based on pass/fail
            if passed:
                st.metric(
                    label=label,
                    value=f"{score:.1%}",
                    delta=f"Target: {threshold:.0%}",
                    delta_color="normal"
                )
            else:
                st.metric(
                    label=label,
                    value=f"{score:.1%}",
                    delta=f"Target: {threshold:.0%}",
                    delta_color="inverse"
                )

    # Detailed breakdowns (collapsible)
    with st.expander("📋 Detailed Metrics Breakdown", expanded=False):
        for metric_key, metric_name in [
            ('authenticity', '🔍 Authenticity'),
            ('role_alignment', '🎯 Role Alignment'),
            ('ats_optimization', '🤖 ATS Optimization'),
            ('length_compliance', '📏 Length Compliance')
        ]:
            metric = metrics_data.get(metric_key, {})
            if not metric:
                continue

            st.markdown(f"#### {metric_name}")

            # Score and status
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Score:** {metric.get('score', 0.0):.2%}")
            with col2:
                st.markdown(f"**Threshold:** {metric.get('threshold', 0.0):.2%}")
            with col3:
                status = "✅ PASS" if metric.get('passed', False) else "❌ FAIL"
                st.markdown(f"**Status:** {status}")

            # Details
            details = metric.get('details', {})
            if details:
                st.markdown("**Details:**")
                for key, value in details.items():
                    if isinstance(value, (list, dict)):
                        # Skip complex structures in summary
                        continue
                    elif isinstance(value, float):
                        st.markdown(f"- {key.replace('_', ' ').title()}: {value:.2f}")
                    elif isinstance(value, bool):
                        st.markdown(f"- {key.replace('_', ' ').title()}: {'Yes' if value else 'No'}")
                    else:
                        st.markdown(f"- {key.replace('_', ' ').title()}: {value}")

            # Recommendations
            recommendations = metric.get('recommendations', [])
            if recommendations:
                st.markdown("**Recommendations:**")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

            st.markdown("---")

    # Overall recommendations
    overall_recommendations = metrics_data.get('recommendations', [])
    if overall_recommendations:
        with st.expander("💡 Overall Recommendations", expanded=not overall_passed):
            for i, rec in enumerate(overall_recommendations, 1):
                if rec.startswith('🔴'):
                    st.error(rec)
                elif rec.startswith('🟡'):
                    st.warning(rec)
                elif rec.startswith('🟢'):
                    st.info(rec)
                elif rec.startswith('✅'):
                    st.success(rec)
                else:
                    st.markdown(f"{i}. {rec}")


def render_version_history(iterative_result):
    """Render version history from iterative optimization."""
    if not iterative_result or not hasattr(iterative_result, 'all_versions'):
        return

    all_versions = iterative_result.all_versions
    if not all_versions or len(all_versions) <= 1:
        return

    st.markdown("### 📚 Version History")

    # Check if version history is enabled
    tier = st.session_state.get('optimization_tier', 'standard')
    from config.optimization_config import OptimizationTier
    config = OptimizationTier.get_tier(tier)

    if not config.enable_version_history:
        st.info("💡 Version history is available in Standard and Premium tiers")
        return

    st.info(f"📊 {len(all_versions)} iteration(s) completed")

    # Version selector
    version_options = [
        f"Version {v.version_number} (Iteration {v.iteration_number}) - Score: {v.get_overall_score():.1%}"
        for v in all_versions
    ]

    selected_version_idx = st.selectbox(
        "View different versions",
        options=range(len(all_versions)),
        format_func=lambda i: version_options[i],
        index=len(all_versions) - 1  # Default to latest
    )

    selected_version = all_versions[selected_version_idx]

    # Show version details
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Overall Score", f"{selected_version.get_overall_score():.1%}")
    with col2:
        st.metric("Iteration", selected_version.iteration_number)
    with col3:
        st.metric("Version", selected_version.version_number)
    with col4:
        st.metric("Timestamp", selected_version.timestamp.strftime("%H:%M:%S"))

    # Show metrics for this version
    if selected_version.metrics:
        st.markdown("**Metrics for this version:**")
        metrics_cols = st.columns(4)

        metrics_data = selected_version.metrics

        with metrics_cols[0]:
            auth_metric = metrics_data.get('authenticity', {})
            if isinstance(auth_metric, dict):
                score = auth_metric.get('score', 0.0)
                passed = auth_metric.get('passed', False)
                st.metric("🔍 Authenticity", f"{score:.1%}", delta="PASS" if passed else "FAIL")

        with metrics_cols[1]:
            role_metric = metrics_data.get('role_alignment', {})
            if isinstance(role_metric, dict):
                score = role_metric.get('score', 0.0)
                passed = role_metric.get('passed', False)
                st.metric("🎯 Role Align", f"{score:.1%}", delta="PASS" if passed else "FAIL")

        with metrics_cols[2]:
            ats_metric = metrics_data.get('ats_optimization', {})
            if isinstance(ats_metric, dict):
                score = ats_metric.get('score', 0.0)
                passed = ats_metric.get('passed', False)
                st.metric("🤖 ATS", f"{score:.1%}", delta="PASS" if passed else "FAIL")

        with metrics_cols[3]:
            length_metric = metrics_data.get('length_compliance', {})
            if isinstance(length_metric, dict):
                score = length_metric.get('score', 0.0)
                passed = length_metric.get('passed', False)
                st.metric("📏 Length", f"{score:.1%}", delta="PASS" if passed else "FAIL")

    # Compare with best version
    best_version = iterative_result.best_version
    if selected_version.version_number != best_version.version_number:
        st.markdown("---")
        st.markdown(f"**Comparison with best version (Version {best_version.version_number}):**")

        comp_cols = st.columns(4)

        if selected_version.metrics and best_version.metrics:
            # Helper function to get metric score
            def get_metric_score(metrics, metric_name):
                metric = metrics.get(metric_name, {})
                if isinstance(metric, dict):
                    return metric.get('score', 0.0)
                return 0.0

            with comp_cols[0]:
                delta = get_metric_score(selected_version.metrics, 'authenticity') - get_metric_score(best_version.metrics, 'authenticity')
                st.metric("Authenticity Δ", f"{delta:+.1%}")

            with comp_cols[1]:
                delta = get_metric_score(selected_version.metrics, 'role_alignment') - get_metric_score(best_version.metrics, 'role_alignment')
                st.metric("Role Alignment Δ", f"{delta:+.1%}")

            with comp_cols[2]:
                delta = get_metric_score(selected_version.metrics, 'ats_optimization') - get_metric_score(best_version.metrics, 'ats_optimization')
                st.metric("ATS Δ", f"{delta:+.1%}")

            with comp_cols[3]:
                delta = get_metric_score(selected_version.metrics, 'length_compliance') - get_metric_score(best_version.metrics, 'length_compliance')
                st.metric("Length Δ", f"{delta:+.1%}")

    # Button to use this version
    if selected_version.version_number != iterative_result.best_version.version_number:
        if st.button(f"📌 Use Version {selected_version.version_number} Instead"):
            # Update the optimization result to use this version
            st.session_state.optimization_result.optimized_resume = selected_version.optimized_resume
            st.session_state.optimization_result.metrics = selected_version.metrics
            st.session_state.optimization_result.changes = selected_version.changes
            st.success(f"✓ Switched to Version {selected_version.version_number}")
            st.rerun()

    # Show improvement trajectory
    with st.expander("📈 Improvement Trajectory"):
        import pandas as pd

        trajectory_data = []
        for v in all_versions:
            trajectory_data.append({
                'Iteration': v.iteration_number,
                'Version': v.version_number,
                'Overall Score': f"{v.get_overall_score():.1%}",
                'Timestamp': v.timestamp.strftime("%H:%M:%S")
            })

        df = pd.DataFrame(trajectory_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_improvements_list(result: ResumeOptimizationResult):
    """Render list of high-level improvements."""
    if result.summary_of_improvements:
        st.markdown("### ✨ Key Improvements")
        for improvement in result.summary_of_improvements:
            st.success(f"✓ {improvement}")


def render_side_by_side_comparison(result: ResumeOptimizationResult):
    """Render side-by-side comparison of original vs optimized."""
    st.markdown("### 📝 Side-by-Side Comparison")

    # Summary/Headline section
    with st.expander("💼 Professional Summary & Headline", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original**")
            if result.original_resume.headline:
                st.markdown(f"**Headline:** {result.original_resume.headline}")
            if result.original_resume.summary:
                st.text_area(
                    "Summary",
                    value=result.original_resume.summary,
                    height=100,
                    disabled=True,
                    label_visibility="collapsed"
                )

        with col2:
            st.markdown("**Optimized** ✨")
            if result.optimized_resume.headline:
                st.markdown(f"**Headline:** {result.optimized_resume.headline}")
            if result.optimized_resume.summary:
                st.text_area(
                    "Summary",
                    value=result.optimized_resume.summary,
                    height=100,
                    disabled=True,
                    label_visibility="collapsed"
                )

    # Experience section
    with st.expander(f"💼 Work Experience ({len(result.optimized_resume.experiences)} positions)", expanded=True):
        for i, (orig_exp, opt_exp) in enumerate(zip(
            result.original_resume.experiences,
            result.optimized_resume.experiences
        )):
            st.markdown(f"#### {i+1}. {opt_exp.title} at {opt_exp.company}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Original Bullets:**")
                for bullet in orig_exp.bullets[:5]:
                    st.markdown(f"• {bullet}")

            with col2:
                st.markdown("**Optimized Bullets:** ✨")
                for bullet in opt_exp.bullets[:5]:
                    st.markdown(f"• {bullet}")

            if i < len(result.optimized_resume.experiences) - 1:
                st.markdown("---")

    # Skills section
    with st.expander("🛠️ Skills", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original Skills:**")
            st.markdown(", ".join(result.original_resume.skills))

        with col2:
            st.markdown("**Optimized Skills:** ✨")
            st.markdown(", ".join(result.optimized_resume.skills))


def render_changes_table(result: ResumeOptimizationResult):
    """Render detailed changes table."""
    st.markdown("### 📋 Detailed Changes")

    if not result.changes:
        st.info("No changes were made.")
        return

    # Get risky changes
    risky_changes_list = result.get_potentially_risky_changes()
    risky_change_ids = {change.id for change, warnings in risky_changes_list}

    # Show authenticity alert if there are risky changes
    if risky_changes_list:
        with st.expander("⚠️ Authenticity Check - Review Recommended", expanded=False):
            st.warning(
                f"**{len(risky_changes_list)} change(s) flagged for review**\n\n"
                "These changes may introduce new information not present in the original resume. "
                "Please verify accuracy before using."
            )
            for change, warnings in risky_changes_list[:5]:  # Show first 5
                st.markdown(f"**{change.location}**")
                for warning in warnings:
                    st.markdown(f"- {warning}")
                st.markdown("---")

    # Filter controls
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        change_types = list(set(c.change_type.value for c in result.changes))
        selected_types = st.multiselect(
            "Filter by type:",
            options=change_types,
            default=change_types
        )
    with col2:
        show_flagged = st.checkbox("Show only flagged changes", value=False)
    with col3:
        max_changes = st.number_input(
            "Show first N:",
            min_value=5,
            max_value=len(result.changes),
            value=min(20, len(result.changes))
        )

    # Filter changes
    filtered_changes = [
        c for c in result.changes
        if c.change_type.value in selected_types
    ]

    if show_flagged:
        filtered_changes = [c for c in filtered_changes if c.id in risky_change_ids]

    filtered_changes = filtered_changes[:max_changes]

    # Create DataFrame
    changes_data = []
    for change in filtered_changes:
        type_text = change.change_type.value.replace('_', ' ').title()
        risk_text = ""

        # Check if this change is risky
        if change.id in risky_change_ids:
            risk_text = "⚠️ WARNING"
            # Get specific warnings for this change
            change_warnings = next((w for c, w in risky_changes_list if c.id == change.id), [])
            if change_warnings:
                # Show first warning as tooltip
                risk_text += f" ({change_warnings[0]})"

        changes_data.append({
            'Type': type_text,
            'Location': change.location,
            'Before': change.before[:80] + "..." if len(change.before) > 80 else change.before,
            'After': change.after[:80] + "..." if len(change.after) > 80 else change.after,
            'Rationale': change.rationale,
            'Risk': risk_text
        })

    df = pd.DataFrame(changes_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Detailed view of selected change
    if changes_data:
        with st.expander("🔍 View Full Change Details"):
            change_idx = st.selectbox(
                "Select change to view:",
                options=range(len(filtered_changes)),
                format_func=lambda i: f"{filtered_changes[i].location} - {filtered_changes[i].change_type.value}"
            )

            if change_idx is not None:
                change = filtered_changes[change_idx]

                # Show warning if this change is risky
                if change.id in risky_change_ids:
                    warnings = next((w for c, w in risky_changes_list if c.id == change.id), [])
                    if warnings:
                        st.warning("⚠️ **Authenticity Check**: " + " | ".join(warnings))

                st.markdown(f"**Type:** {change.change_type.value}")
                st.markdown(f"**Location:** {change.location}")
                st.markdown(f"**Rationale:** {change.rationale}")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Before:**")
                    st.text_area("Before", value=change.before, height=150, disabled=True, label_visibility="collapsed")
                with col2:
                    st.markdown("**After:**")
                    st.text_area("After", value=change.after, height=150, disabled=True, label_visibility="collapsed")


def render_optimization_page() -> bool:
    """
    Render the complete optimization page (Step 3).

    Returns:
        True if step is complete and user clicked Continue
    """
    # Check if we should show change review instead
    if st.session_state.get('show_change_review', False):
        from modules.change_review import render_change_review_page

        result = st.session_state.get('optimization_result')
        if result:
            # Render change review page
            review_complete = render_change_review_page(result)

            if review_complete:
                # User clicked "Continue to Output"
                # Apply accepted changes to generate final resume
                from services.resume_builder import apply_accepted_changes

                final_resume = apply_accepted_changes(result)

                # Update the optimization result with the final resume
                result.optimized_resume = final_resume

                # Store final resume in session
                st.session_state['final_resume'] = final_resume

                # Mark change review as complete
                st.session_state[SESSION_KEYS['change_review_complete']] = True

                # Clear the flag
                st.session_state['show_change_review'] = False

                # Show save version dialog
                st.session_state['show_save_version_dialog'] = True

                # Move to next step
                mark_step_complete(3)
                set_current_step(4)
                st.rerun()
                return True
            else:
                # User clicked "Back to Optimization"
                st.session_state['show_change_review'] = False
                st.rerun()
                return False
        else:
            # No optimization result, go back
            st.session_state['show_change_review'] = False
            st.rerun()
            return False

    # Progress bar
    render_progress_bar(3)

    # Header
    st.title("✨ Step 3: Resume Optimization")
    st.markdown("""
    Using AI to optimize your resume for the target job while maintaining truthfulness and your professional voice.
    """)
    st.markdown("---")

    # Load required models from session
    job_model = st.session_state.get('job_model')
    resume_model = st.session_state.get('resume_model')
    gap_analysis = st.session_state.get('gap_analysis')

    # Handle missing state (user jumped directly here)
    if not all([job_model, resume_model, gap_analysis]):
        st.error("⚠️ Missing required data from previous steps.")
        st.info("Please complete Steps 1 and 2 first.")
        if st.button("← Go to Step 1"):
            set_current_step(1)
            st.rerun()
        return False

    # Check if optimization already done
    if 'optimization_result' in st.session_state:
        result = st.session_state['optimization_result']
        st.success("✅ Optimization already completed. Showing cached results.")
    else:
        # Render controls
        col1, col2 = st.columns([1, 2])

        with col1:
            tier, style, run_optimization, model_id, enable_research = render_optimization_controls()

        with col2:
            st.markdown("### 📊 Current Gap Analysis")
            st.metric("Match Coverage", f"{gap_analysis.coverage_percentage}%")
            if gap_analysis.missing_required_skills:
                st.markdown(f"**Missing Skills:** {', '.join(gap_analysis.missing_required_skills[:5])}")

        if not run_optimization:
            st.info("👆 Configure settings above and click 'Optimize Resume' to begin.")
            return False

        # Store selections in session
        st.session_state['selected_model_id'] = model_id
        st.session_state['enable_research'] = enable_research

        # Run company research if enabled
        company_research = None
        industry_research = None

        if enable_research:
            inputs = get_all_inputs()
            company_name = inputs.get('company_name')

            if company_name:
                with st.status("🔍 Researching company and industry...", expanded=True) as status:
                    try:
                        from agents.research_agent import research_company, research_industry

                        st.write(f"Researching {company_name}...")
                        success, company_research, error = research_company(
                            company_name=company_name,
                            company_url=inputs.get('company_url')
                        )

                        if success and company_research:
                            st.write(f"✅ Company research complete")
                            st.write(f"   Industry: {company_research.industry}")

                            # Research the industry
                            if company_research.industry:
                                st.write(f"Researching {company_research.industry} industry...")
                                success_ind, industry_research, error_ind = research_industry(
                                    industry_name=company_research.industry
                                )

                                if success_ind:
                                    st.write(f"✅ Industry research complete")

                            status.update(label="✅ Research complete", state="complete")

                            # Store in session
                            st.session_state['company_research'] = company_research
                            st.session_state['industry_research'] = industry_research

                            # Show summary
                            st.info(f"📊 {company_research.summary}")

                        else:
                            st.warning(f"⚠️ Could not research company: {error}")
                            status.update(label="⚠️ Research partially complete", state="error")

                    except Exception as e:
                        st.warning(f"⚠️ Research error: {e}")
                        status.update(label="⚠️ Research failed", state="error")
            else:
                st.warning("⚠️ No company name available for research. Proceeding without research.")

        # Run optimization
        st.markdown("---")

        # Get tier configuration
        from config.optimization_config import OptimizationTier
        from services.optimization_service import run_iterative_optimization

        tier_config = OptimizationTier.get_tier(tier)

        # Show progress
        with st.status(f"✨ Optimizing resume using {tier.title()} tier...", expanded=True) as status:
            st.write(f"Using {style} optimization style...")
            st.write(f"Maximum iterations: {tier_config.max_iterations}")

            try:
                # Run iterative optimization
                iterative_result = run_iterative_optimization(
                    job=job_model,
                    resume=resume_model,
                    gap=gap_analysis,
                    style=style,
                    config=tier_config
                )

                result = iterative_result.final_result

                st.write(f"✅ Optimization complete!")
                st.write(f"Iterations run: {iterative_result.iterations_run}")
                st.write(f"Convergence: {iterative_result.convergence_reason}")
                st.write(f"Time: {iterative_result.total_time_seconds:.1f}s")

                status.update(label="✅ Resume optimized", state="complete")

            except Exception as e:
                st.error(f"❌ Optimization failed: {str(e)}")
                status.update(label="❌ Optimization failed", state="error")
                if st.button("← Back to Step 2"):
                    set_current_step(2)
                    st.rerun()
                return False

        # Store results in session
        st.session_state['optimization_result'] = result
        st.session_state['iterative_result'] = iterative_result
        st.session_state['optimization_tier'] = tier

        # Show convergence info
        if iterative_result.converged:
            st.success(f"🎯 **Converged**: {iterative_result.convergence_reason}")
        else:
            st.info(f"📊 **Stopped**: {iterative_result.convergence_reason}")

        st.balloons()
        st.success("✅ Optimization complete!")

    # Display results
    st.markdown("---")

    # Compute gap analysis for optimized resume
    from modules.gap_analyzer import perform_gap_analysis_for_result
    try:
        gap_after = perform_gap_analysis_for_result(job_model, result)
    except Exception as e:
        st.warning(f"Could not compute gap analysis for optimized resume: {e}")
        gap_after = None

    # Summary metrics with before/after comparison
    render_summary_metrics(result, gap_before=gap_analysis, gap_after=gap_after)

    st.markdown("---")

    # Quality metrics dashboard
    render_metrics_dashboard(result)

    st.markdown("---")

    # Version history (if available)
    iterative_result = st.session_state.get('iterative_result')
    if iterative_result:
        render_version_history(iterative_result)
        st.markdown("---")

    # High-level improvements
    render_improvements_list(result)

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "👥 Side-by-Side",
        "📋 All Changes",
        "📄 Optimized Resume"
    ])

    with tab1:
        render_side_by_side_comparison(result)

    with tab2:
        render_changes_table(result)

    with tab3:
        st.markdown("### 📄 Complete Optimized Resume")

        # Download buttons
        col1, col2 = st.columns([3, 1])
        with col2:
            # Generate markdown version
            optimized_md = result.optimized_resume.to_markdown()
            st.download_button(
                label="📥 Download Markdown",
                data=optimized_md,
                file_name=f"optimized_resume_{result.optimized_resume.name or 'resume'}.md".replace(" ", "_"),
                mime="text/markdown",
                help="Download the optimized resume as a Markdown file"
            )

        st.markdown("---")

        st.markdown(f"**Name:** {result.optimized_resume.name}")
        if result.optimized_resume.email:
            st.markdown(f"**Email:** {result.optimized_resume.email}")

        if result.optimized_resume.headline:
            st.markdown(f"**Headline:** {result.optimized_resume.headline}")

        if result.optimized_resume.summary:
            st.markdown("**Summary:**")
            st.markdown(result.optimized_resume.summary)

        st.markdown("**Experience:**")
        for exp in result.optimized_resume.experiences:
            st.markdown(f"### {exp.title} at {exp.company}")
            if exp.start_date or exp.end_date:
                st.markdown(f"*{exp.start_date or '?'} - {exp.end_date or 'Present'}*")
            for bullet in exp.bullets:
                st.markdown(f"- {bullet}")
            st.markdown("")

    st.markdown("---")

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back to Step 2"):
            set_current_step(2)
            st.rerun()

    with col2:
        if st.button("🔄 Re-optimize"):
            # Clear cached result and change review status
            if 'optimization_result' in st.session_state:
                del st.session_state['optimization_result']
            if SESSION_KEYS['change_review_complete'] in st.session_state:
                st.session_state[SESSION_KEYS['change_review_complete']] = False
            if 'show_change_review' in st.session_state:
                st.session_state['show_change_review'] = False
            st.rerun()

    with col3:
        # Check if change review is enabled and completed
        change_review_complete = st.session_state.get(SESSION_KEYS['change_review_complete'], False)

        if not change_review_complete:
            # Show button to go to change review
            if st.button("Review Changes →", type="primary"):
                # Go to change review instead of output
                st.session_state['show_change_review'] = True
                st.rerun()
                return False
        else:
            # Change review is complete, can proceed to output
            if st.button("Continue to Output →", type="primary"):
                mark_step_complete(3)
                set_current_step(4)
                st.success("✅ Step 3 completed! Moving to output generation...")
                import time
                time.sleep(1)
                st.rerun()
                return True

    return False
