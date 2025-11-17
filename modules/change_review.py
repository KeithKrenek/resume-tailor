"""Step 3.5: Change Review & Approval module."""

import streamlit as st
from typing import Optional, List
import uuid

from modules.models import (
    ResumeOptimizationResult,
    ResumeChange,
    ChangeStatus,
    ChangeType,
    ResumeModel
)
from utils.session_manager import SESSION_KEYS
from config.settings import STEP_NAMES


def render_change_statistics(result: ResumeOptimizationResult) -> None:
    """
    Render statistics about change review progress.

    Args:
        result: Optimization result with changes
    """
    stats = result.get_change_stats()

    st.markdown("### 📊 Review Progress")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Changes",
            stats['total'],
            help="Total number of changes made during optimization"
        )

    with col2:
        pending_count = stats['pending']
        progress_pct = ((stats['total'] - pending_count) / stats['total'] * 100) if stats['total'] > 0 else 0
        st.metric(
            "Pending Review",
            pending_count,
            delta=f"{progress_pct:.0f}% reviewed",
            help="Changes still awaiting your review"
        )

    with col3:
        st.metric(
            "Accepted",
            stats['accepted'],
            help="Changes you've accepted or edited"
        )

    with col4:
        st.metric(
            "Rejected",
            stats['rejected'],
            help="Changes you've rejected"
        )

    # Progress bar
    if stats['total'] > 0:
        progress = (stats['total'] - stats['pending']) / stats['total']
        st.progress(progress)

        if stats['pending'] == 0:
            st.success("✅ All changes reviewed!")
        else:
            st.info(f"📋 {stats['pending']} change(s) remaining to review")

    # Flagged changes warning
    if stats['flagged'] > 0:
        st.warning(
            f"⚠️ **{stats['flagged']} change(s) flagged** as potentially risky. "
            "These changes may introduce new information not present in your original resume. "
            "Please review carefully."
        )


def render_change_filters() -> dict:
    """
    Render filter controls for changes.

    Returns:
        Dictionary with filter settings
    """
    st.markdown("### 🔍 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            options=["all", "pending", "accepted", "rejected"],
            index=0,
            help="Filter changes by review status"
        )

    with col2:
        show_flagged_only = st.checkbox(
            "Flagged Only",
            value=False,
            help="Show only changes flagged as potentially risky"
        )

    with col3:
        change_type_filter = st.selectbox(
            "Type",
            options=["all", "summary", "headline", "experience_bullet", "skills_section", "education", "other"],
            index=0,
            help="Filter changes by type"
        )

    return {
        'status': status_filter,
        'flagged_only': show_flagged_only,
        'change_type': change_type_filter
    }


def filter_changes(
    changes: List[ResumeChange],
    filters: dict
) -> List[ResumeChange]:
    """
    Filter changes based on filter settings.

    Args:
        changes: List of all changes
        filters: Filter settings dictionary

    Returns:
        Filtered list of changes
    """
    filtered = changes

    # Filter by status
    if filters['status'] == 'pending':
        filtered = [c for c in filtered if c.is_pending()]
    elif filters['status'] == 'accepted':
        filtered = [c for c in filtered if c.is_accepted()]
    elif filters['status'] == 'rejected':
        filtered = [c for c in filtered if c.is_rejected()]

    # Filter by flagged
    if filters['flagged_only']:
        filtered = [c for c in filtered if c.is_flagged]

    # Filter by change type
    if filters['change_type'] != 'all':
        filtered = [
            c for c in filtered
            if c.change_type.value == filters['change_type']
        ]

    return filtered


def render_change_card(
    change: ResumeChange,
    index: int,
    total: int,
    result: ResumeOptimizationResult
) -> None:
    """
    Render a single change card with action buttons.

    Args:
        change: The change to render
        index: Index of this change in filtered list
        total: Total number of filtered changes
        result: The optimization result containing all changes
    """
    # Create a unique key prefix for this change
    key_prefix = f"change_{change.id}"

    # Container for the change
    with st.container():
        # Header with type and location
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            type_emoji = {
                ChangeType.SUMMARY: "📝",
                ChangeType.HEADLINE: "🎯",
                ChangeType.EXPERIENCE_BULLET: "💼",
                ChangeType.SKILLS_SECTION: "🛠️",
                ChangeType.EDUCATION: "🎓",
                ChangeType.OTHER: "📄"
            }
            emoji = type_emoji.get(change.change_type, "📄")
            st.markdown(f"### {emoji} {change.change_type.value.replace('_', ' ').title()}")

        with col2:
            st.markdown(f"**Location:** `{change.location}`")

        with col3:
            # Status badge
            if change.status == ChangeStatus.ACCEPTED:
                st.success("✅ Accepted")
            elif change.status == ChangeStatus.REJECTED:
                st.error("❌ Rejected")
            elif change.status == ChangeStatus.EDITED:
                st.info("✏️ Edited")
            else:
                st.warning("⏳ Pending")

        # Flagged warning
        if change.is_flagged:
            st.warning(
                "⚠️ **Flagged for Review**: This change may introduce new information. "
                "Please verify accuracy before accepting."
            )

        # Rationale
        st.markdown(f"**Rationale:** {change.rationale}")

        # Before/After comparison
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Before:**")
            st.text_area(
                "Before",
                value=change.before,
                height=150,
                disabled=True,
                label_visibility="collapsed",
                key=f"{key_prefix}_before"
            )

        with col2:
            st.markdown("**After:**")
            if change.status == ChangeStatus.EDITED and change.edited_value:
                # Show edited version
                st.text_area(
                    "After (edited)",
                    value=change.edited_value,
                    height=150,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"{key_prefix}_after_edited"
                )
                st.caption("✏️ This is your edited version")
            else:
                st.text_area(
                    "After",
                    value=change.after,
                    height=150,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"{key_prefix}_after"
                )

        # Action buttons
        st.markdown("**Actions:**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button(
                "✅ Accept",
                key=f"{key_prefix}_accept",
                use_container_width=True,
                disabled=change.status == ChangeStatus.ACCEPTED,
                type="primary" if change.is_pending() else "secondary"
            ):
                change.status = ChangeStatus.ACCEPTED
                st.success("Change accepted!")
                st.rerun()

        with col2:
            if st.button(
                "❌ Reject",
                key=f"{key_prefix}_reject",
                use_container_width=True,
                disabled=change.status == ChangeStatus.REJECTED
            ):
                change.status = ChangeStatus.REJECTED
                st.success("Change rejected!")
                st.rerun()

        with col3:
            if st.button(
                "✏️ Edit",
                key=f"{key_prefix}_edit_btn",
                use_container_width=True
            ):
                # Set flag to show edit dialog
                st.session_state[f"{key_prefix}_show_edit"] = True
                st.rerun()

        with col4:
            if st.button(
                "🤖 Ask AI to Revise",
                key=f"{key_prefix}_ai_revise",
                use_container_width=True
            ):
                # Set flag to show AI revise dialog
                st.session_state[f"{key_prefix}_show_ai_revise"] = True
                st.rerun()

        # Edit dialog
        if st.session_state.get(f"{key_prefix}_show_edit", False):
            with st.form(key=f"{key_prefix}_edit_form"):
                st.markdown("#### ✏️ Edit Change")
                edited_text = st.text_area(
                    "Edit the changed text:",
                    value=change.edited_value if change.edited_value else change.after,
                    height=150,
                    key=f"{key_prefix}_edit_input"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Edit", use_container_width=True):
                        change.edited_value = edited_text
                        change.status = ChangeStatus.EDITED
                        st.session_state[f"{key_prefix}_show_edit"] = False
                        st.success("Edit saved!")
                        st.rerun()

                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state[f"{key_prefix}_show_edit"] = False
                        st.rerun()

        # AI Revise dialog
        if st.session_state.get(f"{key_prefix}_show_ai_revise", False):
            with st.form(key=f"{key_prefix}_ai_revise_form"):
                st.markdown("#### 🤖 Ask AI to Revise")
                st.markdown("Provide guidance on how you'd like this change to be revised:")

                revision_guidance = st.text_area(
                    "Revision instructions:",
                    placeholder="E.g., 'Make it less aggressive', 'Focus more on leadership', 'Remove the metrics'",
                    height=100,
                    key=f"{key_prefix}_revision_input"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("🚀 Request Revision", use_container_width=True):
                        if revision_guidance.strip():
                            # Call AI to revise
                            with st.spinner("🤖 AI is revising..."):
                                try:
                                    revised_text = request_ai_revision(
                                        change=change,
                                        guidance=revision_guidance,
                                        result=result
                                    )

                                    if revised_text:
                                        change.edited_value = revised_text
                                        change.status = ChangeStatus.EDITED
                                        st.session_state[f"{key_prefix}_show_ai_revise"] = False
                                        st.success("AI revision complete!")
                                        st.rerun()
                                    else:
                                        st.error("AI revision failed. Please try again or edit manually.")
                                except Exception as e:
                                    st.error(f"Error during AI revision: {str(e)}")
                        else:
                            st.warning("Please provide revision instructions.")

                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state[f"{key_prefix}_show_ai_revise"] = False
                        st.rerun()

        st.markdown("---")


def request_ai_revision(
    change: ResumeChange,
    guidance: str,
    result: ResumeOptimizationResult
) -> Optional[str]:
    """
    Request AI to revise a change based on user guidance.

    Args:
        change: The change to revise
        guidance: User's guidance for revision
        result: The optimization result for context

    Returns:
        Revised text or None if failed
    """
    try:
        # Import the agent
        from agents.change_revision_agent import revise_change

        # Call the revision agent
        success, revised_text, error = revise_change(
            original_text=change.before,
            ai_suggested_text=change.after,
            user_guidance=guidance,
            change_type=change.change_type.value,
            rationale=change.rationale
        )

        if success and revised_text:
            return revised_text
        else:
            st.error(f"Revision failed: {error}")
            return None

    except Exception as e:
        st.error(f"Error calling revision agent: {str(e)}")
        return None


def render_bulk_actions(result: ResumeOptimizationResult, filtered_changes: List[ResumeChange]) -> None:
    """
    Render bulk action buttons.

    Args:
        result: The optimization result
        filtered_changes: Currently filtered changes
    """
    st.markdown("### ⚡ Bulk Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "✅ Accept All Visible",
            use_container_width=True,
            help="Accept all currently visible changes"
        ):
            for change in filtered_changes:
                if change.is_pending():
                    change.status = ChangeStatus.ACCEPTED
            st.success(f"Accepted {len(filtered_changes)} change(s)!")
            st.rerun()

    with col2:
        if st.button(
            "❌ Reject All Visible",
            use_container_width=True,
            help="Reject all currently visible changes"
        ):
            for change in filtered_changes:
                if change.is_pending():
                    change.status = ChangeStatus.REJECTED
            st.success(f"Rejected {len(filtered_changes)} change(s)!")
            st.rerun()

    with col3:
        if st.button(
            "✅ Accept All Non-Flagged",
            use_container_width=True,
            help="Accept all changes that aren't flagged as risky"
        ):
            count = 0
            for change in result.changes:
                if change.is_pending() and not change.is_flagged:
                    change.status = ChangeStatus.ACCEPTED
                    count += 1
            st.success(f"Accepted {count} non-flagged change(s)!")
            st.rerun()

    with col4:
        if st.button(
            "🔄 Reset All to Pending",
            use_container_width=True,
            help="Reset all changes to pending status"
        ):
            for change in result.changes:
                change.status = ChangeStatus.PENDING
                change.edited_value = None
            st.success("Reset all changes!")
            st.rerun()


def auto_flag_risky_changes(result: ResumeOptimizationResult) -> None:
    """
    Automatically flag changes that appear risky based on heuristics.

    Args:
        result: The optimization result
    """
    # Get potentially risky changes from the result
    risky_changes = result.get_potentially_risky_changes()

    # Mark them as flagged
    risky_ids = {change.id for change, warnings in risky_changes}

    for change in result.changes:
        if change.id in risky_ids:
            change.is_flagged = True


def render_change_review_page(result: ResumeOptimizationResult) -> bool:
    """
    Render the complete change review page.

    Args:
        result: The optimization result to review

    Returns:
        True if review is complete and user clicked Continue
    """
    st.title("🔍 Step 3.5: Review Changes")
    st.markdown("""
    Review each change made to your resume. You can:
    - ✅ **Accept** changes you're happy with
    - ❌ **Reject** changes you don't want
    - ✏️ **Edit** changes to customize them
    - 🤖 **Ask AI to Revise** based on your feedback
    """)
    st.markdown("---")

    # Auto-flag risky changes if not already done
    if not any(c.is_flagged for c in result.changes):
        auto_flag_risky_changes(result)

    # Render statistics
    render_change_statistics(result)

    st.markdown("---")

    # Render filters
    filters = render_change_filters()

    st.markdown("---")

    # Filter changes
    filtered_changes = filter_changes(result.changes, filters)

    # Render bulk actions
    if filtered_changes:
        render_bulk_actions(result, filtered_changes)
        st.markdown("---")

    # Render changes
    if not filtered_changes:
        st.info("No changes match the current filters.")
    else:
        st.markdown(f"### 📋 Changes ({len(filtered_changes)} shown)")

        for i, change in enumerate(filtered_changes):
            render_change_card(change, i, len(filtered_changes), result)

    st.markdown("---")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back to Optimization", use_container_width=True):
            return False

    with col2:
        # Show warning if there are pending changes
        stats = result.get_change_stats()
        if stats['pending'] > 0:
            st.warning(f"⚠️ {stats['pending']} pending change(s)")

    with col3:
        # Only allow continue if at least some changes are accepted
        can_continue = result.has_any_accepted_changes()

        if not can_continue:
            st.button(
                "Continue to Output →",
                disabled=True,
                use_container_width=True,
                help="Please accept at least one change to continue"
            )
            st.caption("Accept at least one change to continue")
        else:
            if st.button("Continue to Output →", type="primary", use_container_width=True):
                # Mark review as complete
                st.session_state[SESSION_KEYS.get('change_review_complete', 'change_review_complete')] = True
                return True

    return False
