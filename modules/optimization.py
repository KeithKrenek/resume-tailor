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


def render_optimization_controls() -> tuple[str, bool]:
    """
    Render optimization control panel.

    Returns:
        Tuple of (style, run_optimization)
    """
    st.markdown("### ⚙️ Optimization Settings")

    # Style selector
    style = st.selectbox(
        "Optimization Style",
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

    # Run button
    run_optimization = st.button(
        "✨ Optimize Resume",
        type="primary",
        use_container_width=True
    )

    return style, run_optimization


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
            style, run_optimization = render_optimization_controls()

        with col2:
            st.markdown("### 📊 Current Gap Analysis")
            st.metric("Match Coverage", f"{gap_analysis.coverage_percentage}%")
            if gap_analysis.missing_required_skills:
                st.markdown(f"**Missing Skills:** {', '.join(gap_analysis.missing_required_skills[:5])}")

        if not run_optimization:
            st.info("👆 Configure settings above and click 'Optimize Resume' to begin.")
            return False

        # Run optimization
        st.markdown("---")
        result, errors = perform_optimization(job_model, resume_model, gap_analysis, style)

        if errors or not result:
            st.error("❌ Optimization failed. Please check errors and try again.")
            if st.button("← Back to Step 2"):
                set_current_step(2)
                st.rerun()
            return False

        # Store in session
        st.session_state['optimization_result'] = result
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
            # Clear cached result
            if 'optimization_result' in st.session_state:
                del st.session_state['optimization_result']
            st.rerun()

    with col3:
        if st.button("Continue to Output →", type="primary"):
            mark_step_complete(3)
            set_current_step(4)
            st.success("✅ Step 3 completed! Moving to output generation...")
            import time
            time.sleep(1)
            st.rerun()
            return True

    return False
