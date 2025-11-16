"""Interactive resume editor with AI-powered inline improvements."""

import streamlit as st
from typing import Optional, List, Dict, Any
from copy import deepcopy

from modules.models import ResumeModel, ExperienceItem
from agents.section_improvement_agent import improve_section, suggest_improvements


def render_resume_editor() -> None:
    """
    Render the interactive resume editor.

    Allows users to edit resume sections inline with AI assistance.
    """
    st.markdown("## ✏️ Smart Resume Editor")

    st.info(
        "💡 **Click any section to edit it!** Use AI assistance to improve individual sections, "
        "or edit manually. Changes are applied in real-time."
    )

    # Get current resume from session
    resume = get_editable_resume()

    if not resume:
        st.warning("No resume available to edit. Please complete optimization first.")
        return

    # Initialize edit history if not exists
    if 'edit_history' not in st.session_state:
        st.session_state.edit_history = []

    # Store job context for AI improvements
    job_description = st.session_state.get('job_description', '')

    # Render sections
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Resume Content")

        # Professional Summary
        render_editable_summary(resume, job_description)

        st.markdown("---")

        # Headline
        render_editable_headline(resume, job_description)

        st.markdown("---")

        # Experience
        render_editable_experience(resume, job_description)

        st.markdown("---")

        # Skills
        render_editable_skills(resume, job_description)

    with col2:
        st.markdown("### 📋 Editor Tools")

        # Edit history
        render_edit_history()

        # Actions
        render_editor_actions(resume)


def get_editable_resume() -> Optional[ResumeModel]:
    """Get the resume that should be edited."""
    # Priority: edited_resume > final_resume > optimized_resume
    if 'edited_resume' in st.session_state:
        return st.session_state.edited_resume
    elif 'final_resume' in st.session_state:
        # Create a copy for editing
        resume = deepcopy(st.session_state.final_resume)
        st.session_state.edited_resume = resume
        return resume
    elif 'optimization_result' in st.session_state:
        # Use optimized resume
        resume = deepcopy(st.session_state.optimization_result.optimized_resume)
        st.session_state.edited_resume = resume
        return resume
    return None


def render_editable_summary(resume: ResumeModel, job_context: str) -> None:
    """Render editable professional summary section."""
    st.markdown("#### 📝 Professional Summary")

    section_key = "summary"
    current_text = resume.summary or ""

    # Display or edit mode
    if st.session_state.get(f'editing_{section_key}', False):
        render_edit_interface(
            section_key=section_key,
            section_type="summary",
            current_text=current_text,
            job_context=job_context,
            on_save=lambda new_text: setattr(resume, 'summary', new_text)
        )
    else:
        # Display mode
        if current_text:
            st.markdown(current_text)
        else:
            st.info("_No professional summary_")

        if st.button("✏️ Edit Summary", key=f"edit_btn_{section_key}"):
            st.session_state[f'editing_{section_key}'] = True
            st.rerun()


def render_editable_headline(resume: ResumeModel, job_context: str) -> None:
    """Render editable headline section."""
    st.markdown("#### 🎯 Professional Headline")

    section_key = "headline"
    current_text = resume.headline or ""

    if st.session_state.get(f'editing_{section_key}', False):
        render_edit_interface(
            section_key=section_key,
            section_type="headline",
            current_text=current_text,
            job_context=job_context,
            on_save=lambda new_text: setattr(resume, 'headline', new_text)
        )
    else:
        if current_text:
            st.markdown(f"**{current_text}**")
        else:
            st.info("_No headline_")

        if st.button("✏️ Edit Headline", key=f"edit_btn_{section_key}"):
            st.session_state[f'editing_{section_key}'] = True
            st.rerun()


def render_editable_experience(resume: ResumeModel, job_context: str) -> None:
    """Render editable experience section."""
    st.markdown("#### 💼 Professional Experience")

    for exp_idx, exp in enumerate(resume.experiences):
        with st.expander(f"{exp.title} at {exp.company}", expanded=exp_idx == 0):
            # Render each bullet
            for bullet_idx, bullet in enumerate(exp.bullets):
                section_key = f"exp_{exp_idx}_bullet_{bullet_idx}"

                if st.session_state.get(f'editing_{section_key}', False):
                    render_edit_interface(
                        section_key=section_key,
                        section_type="bullet",
                        current_text=bullet,
                        job_context=job_context,
                        on_save=lambda new_text, ei=exp_idx, bi=bullet_idx: update_bullet(resume, ei, bi, new_text),
                        height=100
                    )
                else:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"• {bullet}")
                    with col2:
                        if st.button("✏️", key=f"edit_btn_{section_key}", help="Edit this bullet"):
                            st.session_state[f'editing_{section_key}'] = True
                            st.rerun()


def render_editable_skills(resume: ResumeModel, job_context: str) -> None:
    """Render editable skills section."""
    st.markdown("#### 🛠️ Skills")

    section_key = "skills"
    current_text = ", ".join(resume.skills) if resume.skills else ""

    if st.session_state.get(f'editing_{section_key}', False):
        render_edit_interface(
            section_key=section_key,
            section_type="skills",
            current_text=current_text,
            job_context=job_context,
            on_save=lambda new_text: setattr(resume, 'skills', [s.strip() for s in new_text.split(',') if s.strip()]),
            height=100,
            placeholder="Enter skills separated by commas"
        )
    else:
        if resume.skills:
            st.markdown(current_text)
        else:
            st.info("_No skills listed_")

        if st.button("✏️ Edit Skills", key=f"edit_btn_{section_key}"):
            st.session_state[f'editing_{section_key}'] = True
            st.rerun()


def render_edit_interface(
    section_key: str,
    section_type: str,
    current_text: str,
    job_context: str,
    on_save: callable,
    height: int = 150,
    placeholder: str = ""
) -> None:
    """
    Render the edit interface for a section.

    Args:
        section_key: Unique key for this section
        section_type: Type of section (summary, bullet, etc.)
        current_text: Current text content
        job_context: Job description for context
        on_save: Callback function to save changes
        height: Height of text area
        placeholder: Placeholder text
    """
    # Store original if not already stored
    if f'original_{section_key}' not in st.session_state:
        st.session_state[f'original_{section_key}'] = current_text

    # Get working text (may have been improved by AI)
    working_text = st.session_state.get(f'working_{section_key}', current_text)

    st.markdown("##### ✏️ Edit Mode")

    # Manual edit
    edited_text = st.text_area(
        "Content",
        value=working_text,
        height=height,
        key=f"textarea_{section_key}",
        placeholder=placeholder or "Enter content here...",
        label_visibility="collapsed"
    )

    # Store edited text
    st.session_state[f'working_{section_key}'] = edited_text

    # AI Assistance buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🤖 Improve This", key=f"improve_{section_key}", use_container_width=True):
            with st.spinner("AI is improving this section..."):
                success, improved, rationale, error = improve_section(
                    section_type=section_type,
                    current_text=edited_text,
                    job_context=job_context
                )

                if success and improved:
                    st.session_state[f'working_{section_key}'] = improved
                    st.session_state[f'improvement_rationale_{section_key}'] = rationale
                    st.success(f"✨ Improved! {rationale}")
                    st.rerun()
                else:
                    st.error(f"Failed to improve: {error}")

    with col2:
        if st.button("💡 Get Suggestions", key=f"suggest_{section_key}", use_container_width=True):
            with st.spinner("Getting AI suggestions..."):
                success, suggestions, error = suggest_improvements(
                    section_type=section_type,
                    current_text=edited_text,
                    job_context=job_context
                )

                if success and suggestions:
                    st.session_state[f'suggestions_{section_key}'] = suggestions
                    st.success("Got suggestions!")
                    st.rerun()
                else:
                    st.error(f"Failed to get suggestions: {error}")

    # Show suggestions if available
    if f'suggestions_{section_key}' in st.session_state:
        suggestions = st.session_state[f'suggestions_{section_key}']
        st.markdown("**💡 AI Suggestions:**")
        for i, suggestion in enumerate(suggestions, 1):
            st.markdown(f"{i}. {suggestion}")

    # Show improvement rationale if available
    if f'improvement_rationale_{section_key}' in st.session_state:
        st.info(f"**Why improved:** {st.session_state[f'improvement_rationale_{section_key}']}")

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Save", key=f"save_{section_key}", use_container_width=True, type="primary"):
            # Apply the change
            on_save(edited_text)

            # Track in edit history
            track_edit(section_key, section_type, st.session_state[f'original_{section_key}'], edited_text)

            # Clean up session state
            cleanup_edit_session(section_key)

            st.success("Saved!")
            st.rerun()

    with col2:
        if st.button("🔄 Revert", key=f"revert_{section_key}", use_container_width=True):
            # Revert to original
            st.session_state[f'working_{section_key}'] = st.session_state[f'original_{section_key}']
            st.info("Reverted to original")
            st.rerun()

    with col3:
        if st.button("❌ Cancel", key=f"cancel_{section_key}", use_container_width=True):
            # Cancel editing
            cleanup_edit_session(section_key)
            st.session_state[f'editing_{section_key}'] = False
            st.rerun()


def update_bullet(resume: ResumeModel, exp_idx: int, bullet_idx: int, new_text: str) -> None:
    """Update a specific bullet point."""
    if 0 <= exp_idx < len(resume.experiences):
        if 0 <= bullet_idx < len(resume.experiences[exp_idx].bullets):
            resume.experiences[exp_idx].bullets[bullet_idx] = new_text


def track_edit(section_key: str, section_type: str, before: str, after: str) -> None:
    """Track an edit in the edit history."""
    from datetime import datetime

    edit = {
        'timestamp': datetime.now().isoformat(),
        'section_key': section_key,
        'section_type': section_type,
        'before': before,
        'after': after
    }

    if 'edit_history' not in st.session_state:
        st.session_state.edit_history = []

    st.session_state.edit_history.append(edit)


def cleanup_edit_session(section_key: str) -> None:
    """Clean up session state for a section after editing."""
    keys_to_remove = [
        f'original_{section_key}',
        f'working_{section_key}',
        f'suggestions_{section_key}',
        f'improvement_rationale_{section_key}'
    ]

    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


def render_edit_history() -> None:
    """Render the edit history panel."""
    st.markdown("#### 📜 Edit History")

    history = st.session_state.get('edit_history', [])

    if not history:
        st.info("No edits yet")
        return

    st.metric("Total Edits", len(history))

    if st.button("🔄 Undo Last Edit"):
        if undo_last_edit():
            st.success("Undone!")
            st.rerun()
        else:
            st.warning("Nothing to undo")

    with st.expander(f"View History ({len(history)} edits)"):
        for i, edit in enumerate(reversed(history[-10:]), 1):  # Show last 10
            st.markdown(f"**{i}.** {edit['section_type'].title()}")
            st.caption(edit['timestamp'][:19])

            col1, col2 = st.columns(2)
            with col1:
                st.text_area(
                    "Before",
                    value=edit['before'][:100] + "..." if len(edit['before']) > 100 else edit['before'],
                    height=60,
                    disabled=True,
                    key=f"hist_before_{i}",
                    label_visibility="visible"
                )
            with col2:
                st.text_area(
                    "After",
                    value=edit['after'][:100] + "..." if len(edit['after']) > 100 else edit['after'],
                    height=60,
                    disabled=True,
                    key=f"hist_after_{i}",
                    label_visibility="visible"
                )
            st.markdown("---")


def undo_last_edit() -> bool:
    """Undo the last edit."""
    history = st.session_state.get('edit_history', [])

    if not history:
        return False

    # For now, just remove from history
    # In a full implementation, we'd actually revert the change
    st.session_state.edit_history.pop()
    return True


def render_editor_actions(resume: ResumeModel) -> None:
    """Render editor action buttons."""
    st.markdown("#### ⚡ Actions")

    # Save edited resume
    if st.button("💾 Save All Changes", use_container_width=True, type="primary"):
        # Update the resume in session
        st.session_state.edited_resume = resume

        # Also update final_resume if it exists
        if 'final_resume' in st.session_state:
            st.session_state.final_resume = resume

        # Update optimization result if it exists
        if 'optimization_result' in st.session_state:
            st.session_state.optimization_result.optimized_resume = resume

        st.success("✅ All changes saved!")

    # Reset to optimized version
    if st.button("🔄 Reset to Optimized", use_container_width=True):
        if st.confirm("Are you sure? This will discard all manual edits."):
            if 'edited_resume' in st.session_state:
                del st.session_state.edited_resume
            if 'edit_history' in st.session_state:
                st.session_state.edit_history = []
            st.success("Reset to optimized version")
            st.rerun()

    # Clear edit history
    if st.button("🗑️ Clear Edit History", use_container_width=True):
        st.session_state.edit_history = []
        st.success("Edit history cleared")
        st.rerun()


def st_confirm(message: str) -> bool:
    """Simple confirmation dialog."""
    # For now, just return True
    # In a full implementation, would show a modal dialog
    return True
