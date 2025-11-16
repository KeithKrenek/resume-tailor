"""UI components for resume version management."""

import streamlit as st
from typing import Optional, List
from datetime import datetime
import pandas as pd

from modules.version_models import ResumeVersion, VersionMetadata, VersionComparison
from services.version_manager import VersionManager
from utils.output_manager import OutputManager


def render_version_save_dialog(
    optimization_result,
    final_resume,
    job_title: str,
    company_name: str,
    job_description: str,
    original_resume_text: str,
    optimization_style: str,
    optimization_tier: str
) -> bool:
    """
    Render dialog to save current version.

    Returns:
        True if version was saved
    """
    st.markdown("### 💾 Save This Version")

    st.info(
        "Save this optimized resume version for future reference. "
        "You can compare versions, track which ones you submitted, and manage your application history."
    )

    with st.form("save_version_form"):
        # Auto-fill metadata
        st.markdown(f"**Company:** {company_name}")
        st.markdown(f"**Job Title:** {job_title}")
        st.markdown(f"**Style:** {optimization_style.title()}")
        st.markdown(f"**Tier:** {optimization_tier.title()}")

        # Optional fields
        notes = st.text_area(
            "Notes (optional)",
            placeholder="E.g., 'Emphasized leadership skills', 'Tailored for startup culture'",
            help="Add any notes about this version for future reference"
        )

        tags_input = st.text_input(
            "Tags (optional, comma-separated)",
            placeholder="E.g., software-engineer, startup, remote",
            help="Tags to help organize and filter versions"
        )

        tags = [t.strip() for t in tags_input.split(',') if t.strip()] if tags_input else []

        col1, col2 = st.columns(2)

        with col1:
            save_clicked = st.form_submit_button("💾 Save Version", use_container_width=True, type="primary")

        with col2:
            cancel_clicked = st.form_submit_button("❌ Cancel", use_container_width=True)

        if save_clicked:
            # Initialize version manager
            version_manager = VersionManager()

            # Save version
            success, version_id, message = version_manager.save_version(
                optimization_result=optimization_result,
                final_resume=final_resume,
                job_title=job_title,
                company_name=company_name,
                job_description=job_description,
                original_resume_text=original_resume_text,
                optimization_style=optimization_style,
                optimization_tier=optimization_tier,
                notes=notes if notes else None,
                tags=tags
            )

            if success:
                st.success(f"✅ {message}")
                return True
            else:
                st.error(f"❌ {message}")
                return False

        if cancel_clicked:
            return False

    return False


def render_version_history() -> None:
    """Render version history browser."""
    st.markdown("## 📚 Version History")

    # Initialize version manager
    version_manager = VersionManager()

    # Get storage stats
    stats = version_manager.get_storage_stats()

    # Display stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Versions",
            stats.get('total_versions', 0),
            help="Total number of saved resume versions"
        )

    with col2:
        st.metric(
            "Storage Used",
            f"{stats.get('total_size_mb', 0):.2f} MB",
            help="Total storage space used by versions"
        )

    with col3:
        last_updated = stats.get('last_updated', 'Never')
        if last_updated != 'Never':
            try:
                dt = datetime.fromisoformat(last_updated)
                last_updated = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass

        st.metric(
            "Last Updated",
            last_updated,
            help="When the last version was saved or modified"
        )

    st.markdown("---")

    # Filters
    st.markdown("### 🔍 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        company_filter = st.text_input(
            "Company Name",
            placeholder="Filter by company...",
            help="Filter versions by company name"
        )

    with col2:
        tag_filter = st.selectbox(
            "Tag",
            options=["All"] + get_all_tags(version_manager),
            help="Filter versions by tag"
        )

    with col3:
        show_submitted = st.checkbox(
            "Submitted Only",
            value=False,
            help="Show only versions that have been submitted"
        )

    # List versions
    versions = version_manager.list_versions(
        company_filter=company_filter if company_filter else None,
        tag_filter=tag_filter if tag_filter != "All" else None,
        submitted_only=show_submitted
    )

    if not versions:
        st.info("No saved versions found. Complete an optimization and save it to start building your version history.")
        return

    st.markdown(f"### 📋 Versions ({len(versions)} found)")

    # Display versions as cards
    for version_metadata in versions:
        render_version_card(version_metadata, version_manager)


def get_all_tags(version_manager: VersionManager) -> List[str]:
    """Get all unique tags from all versions."""
    versions = version_manager.list_versions()
    all_tags = set()

    for v in versions:
        all_tags.update(v.tags)

    return sorted(list(all_tags))


def render_version_card(metadata: VersionMetadata, version_manager: VersionManager) -> None:
    """Render a single version card."""
    with st.expander(f"📄 {metadata.get_display_name()}", expanded=False):
        col1, col2 = st.columns([2, 1])

        with col1:
            # Metadata
            st.markdown(f"**Version:** {metadata.version_number}")
            st.markdown(f"**Company:** {metadata.company_name}")
            st.markdown(f"**Job Title:** {metadata.job_title}")
            st.markdown(f"**Style:** {metadata.optimization_style.title()}")
            st.markdown(f"**Tier:** {metadata.optimization_tier.title()}")

            # Stats
            st.markdown(f"**Changes:** {metadata.accepted_changes}/{metadata.total_changes} accepted")

            # Submission status
            if metadata.is_submitted:
                status_icon = "✅" if metadata.response_received else "📤"
                status_text = "Response received" if metadata.response_received else "Awaiting response"
                st.markdown(f"{status_icon} **Submitted:** {metadata.submitted_date} - {status_text}")
            else:
                st.markdown("📝 **Status:** Not submitted")

            # Tags
            if metadata.tags:
                tags_str = ", ".join([f"`{tag}`" for tag in metadata.tags])
                st.markdown(f"**Tags:** {tags_str}")

            # Notes
            if metadata.notes:
                st.markdown(f"**Notes:** {metadata.notes}")

        with col2:
            # Actions
            st.markdown("**Actions:**")

            # View/Export button
            if st.button(f"👁️ View", key=f"view_{metadata.version_id}", use_container_width=True):
                st.session_state['view_version_id'] = metadata.version_id
                st.rerun()

            # Use this version button
            if st.button(f"📌 Use This", key=f"use_{metadata.version_id}", use_container_width=True):
                use_version(metadata.version_id, version_manager)

            # Edit metadata button
            if st.button(f"✏️ Edit", key=f"edit_{metadata.version_id}", use_container_width=True):
                st.session_state['edit_version_id'] = metadata.version_id
                st.rerun()

            # Delete button
            if st.button(f"🗑️ Delete", key=f"delete_{metadata.version_id}", use_container_width=True):
                success, message = version_manager.delete_version(metadata.version_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("---")


def use_version(version_id: str, version_manager: VersionManager) -> None:
    """Load a version and use it as the current optimization result."""
    version = version_manager.load_version(version_id)

    if version:
        # Update session state with this version
        st.session_state['optimization_result'] = version.optimization_result
        st.session_state['final_resume'] = version.final_resume

        st.success(f"✅ Now using Version {version.metadata.version_number}")
        st.info("You can now proceed to Step 4 to export this version.")
    else:
        st.error("Failed to load version")


def render_version_comparison() -> None:
    """Render version comparison UI."""
    st.markdown("## 🔄 Compare Versions")

    st.info(
        "Compare two resume versions side-by-side to see differences in content, "
        "metrics, and optimization approaches."
    )

    version_manager = VersionManager()
    versions = version_manager.list_versions()

    if len(versions) < 2:
        st.warning("You need at least 2 saved versions to compare. Save more versions to use this feature.")
        return

    # Version selectors
    col1, col2 = st.columns(2)

    version_options = [f"v{v.version_number} - {v.company_name} - {v.job_title}" for v in versions]
    version_map = {opt: versions[i].version_id for i, opt in enumerate(version_options)}

    with col1:
        st.markdown("### Version A")
        version_a_option = st.selectbox(
            "Select first version",
            options=version_options,
            key="version_a_selector"
        )

    with col2:
        st.markdown("### Version B")
        version_b_option = st.selectbox(
            "Select second version",
            options=version_options,
            index=min(1, len(version_options) - 1),
            key="version_b_selector"
        )

    if st.button("🔄 Compare Versions", type="primary", use_container_width=True):
        version_a_id = version_map[version_a_option]
        version_b_id = version_map[version_b_option]

        if version_a_id == version_b_id:
            st.warning("Please select two different versions to compare.")
            return

        comparison = version_manager.compare_versions(version_a_id, version_b_id)

        if comparison:
            render_comparison_results(comparison)
        else:
            st.error("Failed to compare versions")


def render_comparison_results(comparison: VersionComparison) -> None:
    """Render comparison results."""
    st.markdown("---")
    st.markdown("## 📊 Comparison Results")

    # Metadata comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### Version {comparison.version_a.metadata.version_number}")
        st.markdown(f"**Company:** {comparison.version_a.metadata.company_name}")
        st.markdown(f"**Job:** {comparison.version_a.metadata.job_title}")
        st.markdown(f"**Style:** {comparison.version_a.metadata.optimization_style}")
        st.markdown(f"**Date:** {comparison.version_a.metadata.timestamp[:10]}")

    with col2:
        st.markdown(f"### Version {comparison.version_b.metadata.version_number}")
        st.markdown(f"**Company:** {comparison.version_b.metadata.company_name}")
        st.markdown(f"**Job:** {comparison.version_b.metadata.job_title}")
        st.markdown(f"**Style:** {comparison.version_b.metadata.optimization_style}")
        st.markdown(f"**Date:** {comparison.version_b.metadata.timestamp[:10]}")

    st.markdown("---")

    # Metrics comparison
    st.markdown("### 📈 Metrics Comparison")

    delta = comparison.get_metrics_delta()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Overall Score",
            f"{comparison.version_b.get_metrics_summary()['overall_score']:.1%}",
            delta=f"{delta['overall_score']:+.1%}"
        )

    with col2:
        st.metric(
            "Authenticity",
            f"{comparison.version_b.get_metrics_summary()['authenticity_score']:.1%}",
            delta=f"{delta['authenticity_score']:+.1%}"
        )

    with col3:
        st.metric(
            "Role Alignment",
            f"{comparison.version_b.get_metrics_summary()['role_alignment_score']:.1%}",
            delta=f"{delta['role_alignment_score']:+.1%}"
        )

    with col4:
        st.metric(
            "ATS Score",
            f"{comparison.version_b.get_metrics_summary()['ats_score']:.1%}",
            delta=f"{delta['ats_score']:+.1%}"
        )

    st.markdown("---")

    # Text comparison
    st.markdown("### 📝 Content Comparison")

    text_diff = comparison.get_text_diff()

    # Summary comparison
    with st.expander("Professional Summary", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Version A:**")
            st.text_area(
                "Summary A",
                value=text_diff['summary'][0],
                height=150,
                disabled=True,
                label_visibility="collapsed",
                key="summary_a"
            )

        with col2:
            st.markdown("**Version B:**")
            st.text_area(
                "Summary B",
                value=text_diff['summary'][1],
                height=150,
                disabled=True,
                label_visibility="collapsed",
                key="summary_b"
            )

    # Headline comparison
    with st.expander("Headline", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Version A:**")
            st.markdown(text_diff['headline'][0] or "_No headline_")

        with col2:
            st.markdown("**Version B:**")
            st.markdown(text_diff['headline'][1] or "_No headline_")

    # Skills comparison
    with st.expander("Skills", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Version A:**")
            st.markdown(text_diff['skills'][0])

        with col2:
            st.markdown("**Version B:**")
            st.markdown(text_diff['skills'][1])


def render_version_editor(version_id: str, version_manager: VersionManager) -> None:
    """Render version metadata editor."""
    version = version_manager.load_version(version_id)

    if not version:
        st.error("Version not found")
        return

    st.markdown(f"## ✏️ Edit Version {version.metadata.version_number}")

    with st.form("edit_version_form"):
        # Notes
        notes = st.text_area(
            "Notes",
            value=version.metadata.notes or "",
            help="Add or update notes about this version"
        )

        # Tags
        tags_str = ", ".join(version.metadata.tags) if version.metadata.tags else ""
        tags_input = st.text_input(
            "Tags (comma-separated)",
            value=tags_str,
            help="Tags to help organize versions"
        )

        tags = [t.strip() for t in tags_input.split(',') if t.strip()]

        # Submission tracking
        st.markdown("#### 📤 Submission Tracking")

        is_submitted = st.checkbox(
            "Mark as submitted",
            value=version.metadata.is_submitted,
            help="Check if you've submitted this resume version"
        )

        submitted_date = None
        response_received = None

        if is_submitted:
            col1, col2 = st.columns(2)

            with col1:
                submitted_date_input = st.date_input(
                    "Submission Date",
                    value=datetime.fromisoformat(version.metadata.submitted_date) if version.metadata.submitted_date else datetime.now(),
                    help="When you submitted this resume"
                )
                submitted_date = submitted_date_input.isoformat()

            with col2:
                response_received = st.checkbox(
                    "Response Received",
                    value=version.metadata.response_received or False,
                    help="Check if you received a response for this application"
                )

        col1, col2 = st.columns(2)

        with col1:
            save_clicked = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")

        with col2:
            cancel_clicked = st.form_submit_button("❌ Cancel", use_container_width=True)

        if save_clicked:
            success, message = version_manager.update_version_metadata(
                version_id=version_id,
                notes=notes if notes else None,
                tags=tags,
                is_submitted=is_submitted,
                submitted_date=submitted_date if is_submitted else None,
                response_received=response_received if is_submitted else None
            )

            if success:
                st.success(message)
                # Clear edit flag
                if 'edit_version_id' in st.session_state:
                    del st.session_state['edit_version_id']
                st.rerun()
            else:
                st.error(message)

        if cancel_clicked:
            if 'edit_version_id' in st.session_state:
                del st.session_state['edit_version_id']
            st.rerun()
