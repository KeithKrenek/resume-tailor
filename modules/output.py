"""
Output generation module for Resume Tailor.

This module handles the final step: generating downloadable resume files
in various formats (PDF, DOCX, HTML, Markdown).
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Optional

from modules.models import ResumeModel, ResumeOptimizationResult
from utils.document_generator import (
    generate_pdf,
    generate_docx,
    generate_html,
    save_resume_files
)
from utils.session_manager import (
    get_current_step,
    set_current_step,
    mark_step_complete,
    get_all_inputs
)


def render_output_generation_page():
    """
    Render the output generation page (Step 4).

    This page allows users to:
    1. Preview the optimized resume
    2. Download in multiple formats (PDF, DOCX, HTML, Markdown)
    3. Save files to the output directory
    4. Manage resume versions
    """
    st.title("📄 Step 4: Output Generation")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Export Resume", "✏️ Edit Resume", "📚 Version History", "🔄 Compare Versions"])

    with tab1:
        render_export_tab()

    with tab2:
        render_editor_tab()

    with tab3:
        render_version_history_tab()

    with tab4:
        render_version_comparison_tab()


def render_export_tab():
    """Render the export/download tab."""
    st.markdown("Generate and download your optimized resume in multiple formats.")

    # Get optimization result from session state
    if 'optimization_result' not in st.session_state or st.session_state.optimization_result is None:
        st.warning("⚠️ No optimized resume found. Please complete Step 3 first.")
        if st.button("← Back to Step 3"):
            set_current_step(3)
            st.rerun()
        return

    optimization_result: ResumeOptimizationResult = st.session_state.optimization_result
    optimized_resume = optimization_result.optimized_resume

    # Display summary
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Changes", optimization_result.get_total_changes())
    with col2:
        st.metric("Optimization Style", optimization_result.style_used.title())
    with col3:
        timestamp = datetime.fromisoformat(optimization_result.optimization_timestamp)
        st.metric("Generated", timestamp.strftime("%Y-%m-%d %H:%M"))

    st.markdown("---")

    # Preview Section
    st.subheader("📋 Resume Preview")

    preview_format = st.radio(
        "Preview Format",
        ["Markdown", "HTML"],
        horizontal=True
    )

    if preview_format == "Markdown":
        with st.expander("📝 Markdown Preview", expanded=True):
            markdown_content = optimized_resume.to_markdown()
            st.markdown(markdown_content)
    else:
        with st.expander("🌐 HTML Preview", expanded=True):
            html_content = generate_html(optimized_resume)
            st.components.v1.html(html_content, height=800, scrolling=True)

    st.markdown("---")

    # Download Section
    st.subheader("⬇️ Download Resume")

    # Get inputs for filename
    inputs = get_all_inputs()
    company_name = inputs.get('company_name', 'Company')
    job_title = inputs.get('job_title', 'Position')

    # Create default filename
    safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_company = safe_company.replace(' ', '_')
    default_filename = f"resume_{safe_company}_{datetime.now().strftime('%Y%m%d')}"

    # Filename input
    col1, col2 = st.columns([3, 1])
    with col1:
        filename_base = st.text_input(
            "Filename (without extension)",
            value=default_filename,
            help="Enter the base filename. Extensions will be added automatically."
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        include_pdf = st.checkbox("Include PDF", value=True, help="Requires weasyprint")

    # Generate files for download
    st.markdown("### Available Formats")

    col1, col2, col3, col4 = st.columns(4)

    # Generate DOCX
    with col1:
        try:
            docx_bytes = generate_docx(optimized_resume)
            st.download_button(
                label="📄 Download DOCX",
                data=docx_bytes,
                file_name=f"{filename_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"DOCX Error: {str(e)}")

    # Generate PDF
    with col2:
        if include_pdf:
            try:
                pdf_bytes = generate_pdf(optimized_resume)
                st.download_button(
                    label="📕 Download PDF",
                    data=pdf_bytes,
                    file_name=f"{filename_base}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except ImportError:
                st.warning("⚠️ PDF generation requires weasyprint. Install with: `pip install weasyprint`")
            except Exception as e:
                st.error(f"PDF Error: {str(e)}")
        else:
            st.info("PDF disabled")

    # Generate HTML
    with col3:
        try:
            html_content = generate_html(optimized_resume)
            st.download_button(
                label="🌐 Download HTML",
                data=html_content.encode('utf-8'),
                file_name=f"{filename_base}.html",
                mime="text/html",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"HTML Error: {str(e)}")

    # Generate Markdown
    with col4:
        try:
            markdown_content = optimized_resume.to_markdown()
            st.download_button(
                label="📝 Download MD",
                data=markdown_content.encode('utf-8'),
                file_name=f"{filename_base}.md",
                mime="text/markdown",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Markdown Error: {str(e)}")

    st.markdown("---")

    # Save to Output Folder Section
    st.subheader("💾 Save to Output Folder")

    output_folder = inputs.get('output_folder')

    if output_folder:
        st.info(f"📁 Output folder: `{output_folder}`")

        if st.button("💾 Save All Formats to Output Folder", type="primary"):
            try:
                output_path = Path(output_folder)

                # Save all formats
                saved_files = save_resume_files(
                    optimized_resume,
                    output_path,
                    base_filename=filename_base
                )

                # Display success message with file paths
                st.success("✅ Files saved successfully!")

                with st.expander("📂 Saved Files", expanded=True):
                    for format_type, file_path in saved_files.items():
                        if file_path:
                            st.markdown(f"- **{format_type.upper()}**: `{file_path}`")
                        elif format_type == 'pdf':
                            st.markdown(f"- **{format_type.upper()}**: ⚠️ Skipped (weasyprint not available)")

            except Exception as e:
                st.error(f"❌ Error saving files: {str(e)}")
    else:
        st.warning("⚠️ No output folder specified. Files can only be downloaded.")

    st.markdown("---")

    # Additional Actions
    st.subheader("🎯 Next Steps")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Start New Resume", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            set_current_step(1)
            st.rerun()

    with col2:
        if st.button("← Back to Optimization", use_container_width=True):
            set_current_step(3)
            st.rerun()

    with col3:
        if st.button("✅ Mark Complete", type="primary", use_container_width=True):
            mark_step_complete(4)
            st.balloons()
            st.success("🎉 Resume tailoring complete! Your optimized resume is ready.")

    # Tips Section
    with st.expander("💡 Tips for Using Your Resume"):
        st.markdown("""
        **Best Practices:**

        1. **Review Before Sending**
           - Carefully review all changes made by the AI
           - Verify all information is accurate and truthful
           - Check for any formatting issues

        2. **File Format Selection**
           - **DOCX**: Best for further editing and ATS compatibility
           - **PDF**: Best for final submission (preserves formatting)
           - **HTML**: Good for web portfolios or email
           - **Markdown**: Easy to version control and edit in plain text

        3. **ATS (Applicant Tracking System) Tips**
           - Use the DOCX format for ATS submissions
           - Avoid headers/footers with important info
           - Keep formatting simple and clean
           - Use standard section headings

        4. **Customization**
           - Tailor the resume for each specific job
           - Update the summary/headline per application
           - Highlight most relevant experiences first

        5. **Version Control**
           - Keep track of different versions
           - Note which company/position each version targets
           - Save original resume for reference
        """)

    # Display warnings if any risky changes detected
    authenticity_report = optimization_result.get_authenticity_report()

    if not authenticity_report.get('is_safe', True):
        with st.expander("⚠️ Authenticity Warnings", expanded=True):
            # Check if LLM-based report is available
            has_llm_report = optimization_result.has_llm_authenticity_report()

            if has_llm_report:
                # Display LLM-based report with rich details
                st.warning(
                    f"**AI-Powered Verification Found {authenticity_report['flagged_changes']} Issue(s)**\n\n"
                    f"Risk Level: **{authenticity_report.get('overall_risk_level', 'unknown').upper()}** | "
                    f"Total Changes Analyzed: {authenticity_report['total_changes']}"
                )

                st.info(f"📋 **Summary:** {authenticity_report.get('summary', 'Review required')}")

                # Display recommendations
                if authenticity_report.get('recommendations'):
                    st.markdown("**⚠️ Important Recommendations:**")
                    for recommendation in authenticity_report['recommendations']:
                        st.markdown(f"- {recommendation}")

                # Display detailed issues
                issues = authenticity_report.get('issues_found', [])
                if issues:
                    st.markdown("---")
                    st.markdown("### 🔍 Detected Issues")

                    # Group by severity
                    high_issues = [i for i in issues if i.get('severity') == 'high']
                    medium_issues = [i for i in issues if i.get('severity') == 'medium']
                    low_issues = [i for i in issues if i.get('severity') == 'low']

                    # Display high severity first
                    if high_issues:
                        st.markdown("#### 🚨 High Severity Issues")
                        for issue in high_issues:
                            with st.container():
                                issue_type = issue.get('type', 'unknown').title()
                                location = issue.get('location', 'unknown')

                                st.markdown(f"**{issue_type}** at `{location}`")
                                st.markdown(f"*{issue.get('explanation', 'No explanation provided')}*")

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.text_area(
                                        "Original:",
                                        value=issue.get('original_text', '')[:200],
                                        height=100,
                                        disabled=True,
                                        key=f"orig_{issue.get('location', 'unknown')}"
                                    )
                                with col2:
                                    st.text_area(
                                        "Modified:",
                                        value=issue.get('modified_text', '')[:200],
                                        height=100,
                                        disabled=True,
                                        key=f"mod_{issue.get('location', 'unknown')}"
                                    )

                                st.success(f"💡 **Recommendation:** {issue.get('recommendation', 'Review carefully')}")
                                st.markdown("---")

                    # Display medium severity
                    if medium_issues:
                        st.markdown("#### ⚠️ Medium Severity Issues")
                        for issue in medium_issues:
                            issue_type = issue.get('type', 'unknown').title()
                            location = issue.get('location', 'unknown')
                            st.markdown(f"- **{issue_type}** at `{location}`: {issue.get('explanation', 'No explanation')}")
                            st.markdown(f"  💡 {issue.get('recommendation', 'Review carefully')}")

                    # Display low severity (collapsed)
                    if low_issues:
                        with st.expander(f"ℹ️ Low Severity Issues ({len(low_issues)})"):
                            for issue in low_issues:
                                issue_type = issue.get('type', 'unknown').title()
                                location = issue.get('location', 'unknown')
                                st.markdown(f"- **{issue_type}** at `{location}`: {issue.get('explanation', 'No explanation')}")

            else:
                # Fall back to heuristic-based display
                st.warning(
                    f"**{authenticity_report['flagged_changes']} of {authenticity_report['total_changes']} "
                    f"changes were flagged for review ({authenticity_report['flag_rate']:.1f}%)**"
                )

                st.markdown("**Please review the following before using this resume:**")

                for recommendation in authenticity_report.get('recommendations', []):
                    st.markdown(f"- {recommendation}")

                if authenticity_report.get('risky_changes'):
                    st.markdown("**Flagged Changes:**")
                    for change, warnings in authenticity_report['risky_changes']:
                        st.markdown(f"- **{change.location}**: {', '.join(warnings)}")

    # Save version dialog (if triggered from change review)
    if st.session_state.get('show_save_version_dialog', False):
        render_save_version_section()


def render_save_version_section():
    """Render the save version section."""
    from modules.version_manager_ui import render_version_save_dialog

    # Get required data from session
    optimization_result = st.session_state.get('optimization_result')
    final_resume = st.session_state.get('final_resume') or optimization_result.optimized_resume
    inputs = get_all_inputs()

    # Check if optimization tier is available
    optimization_tier = st.session_state.get('optimization_tier', 'standard')
    optimization_style = optimization_result.style_used if optimization_result else "balanced"

    st.markdown("---")

    saved = render_version_save_dialog(
        optimization_result=optimization_result,
        final_resume=final_resume,
        job_title=inputs.get('job_title', 'Unknown Position'),
        company_name=inputs.get('company_name', 'Unknown Company'),
        job_description=inputs.get('job_description', ''),
        original_resume_text=inputs.get('resume_text', ''),
        optimization_style=optimization_style,
        optimization_tier=optimization_tier
    )

    if saved:
        # Clear the dialog flag
        st.session_state['show_save_version_dialog'] = False
        st.rerun()


def render_editor_tab():
    """Render the resume editor tab."""
    from modules.resume_editor import render_resume_editor

    render_resume_editor()


def render_version_history_tab():
    """Render the version history tab."""
    from modules.version_manager_ui import render_version_history, render_version_editor

    # Check if editing a specific version
    if 'edit_version_id' in st.session_state:
        from services.version_manager import VersionManager
        version_manager = VersionManager()
        render_version_editor(st.session_state['edit_version_id'], version_manager)
    else:
        render_version_history()


def render_version_comparison_tab():
    """Render the version comparison tab."""
    from modules.version_manager_ui import render_version_comparison

    render_version_comparison()
