"""Input collection module for Step 1 of the Resume Tailor workflow."""

import streamlit as st
from pathlib import Path
from typing import Optional

from modules.validators import (
    validate_job_description,
    validate_resume_text,
    validate_url,
    validate_folder_path,
    extract_basic_info,
    get_text_statistics
)
from utils.file_handlers import extract_text_from_file
from utils.scraper import scrape_job_posting
from utils.session_manager import (
    save_job_inputs,
    save_resume_inputs,
    save_output_folder,
    get_all_inputs,
    SESSION_KEYS
)
from config.settings import (
    SUPPORTED_RESUME_EXTENSIONS,
    DEFAULT_OUTPUT_FOLDER,
    TOTAL_STEPS,
    STEP_NAMES
)


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


def render_job_description_input() -> tuple[str, bool]:
    """
    Render job description input section.

    Returns:
        Tuple of (job_description_text, is_valid)
    """
    st.markdown("### 📄 Job Description")

    # Get current value from session state
    current_inputs = get_all_inputs()
    current_job_desc = current_inputs.get('job_description', '')
    current_job_url = current_inputs.get('job_url', '')

    # Job URL input with scrape button
    col1, col2 = st.columns([3, 1])

    with col1:
        job_url = st.text_input(
            "Job Posting URL (optional)",
            value=current_job_url,
            placeholder="https://example.com/jobs/position",
            help="Paste the URL of the job posting to automatically scrape the description"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacer for alignment
        scrape_button = st.button("🔍 Scrape URL", use_container_width=True)

    # Handle URL scraping
    scraped_description = ""
    if scrape_button and job_url:
        with st.spinner("Scraping job posting..."):
            url_valid, url_error = validate_url(job_url)
            if not url_valid:
                st.error(f"❌ {url_error}")
            else:
                success, job_data, error = scrape_job_posting(job_url)
                if success:
                    scraped_description = job_data.get('description', '')
                    if scraped_description:
                        st.success("✅ Job description scraped successfully!")

                        # Show preview in expander
                        with st.expander("📋 Preview Scraped Content", expanded=True):
                            if job_data.get('title'):
                                st.markdown(f"**Title:** {job_data['title']}")
                            if job_data.get('company'):
                                st.markdown(f"**Company:** {job_data['company']}")
                            if job_data.get('location'):
                                st.markdown(f"**Location:** {job_data['location']}")
                            st.markdown("**Description:**")
                            st.text_area(
                                "Scraped Description",
                                value=scraped_description,
                                height=200,
                                label_visibility="collapsed"
                            )

                        # Save scraped data
                        save_job_inputs(
                            job_description=scraped_description,
                            job_url=job_url,
                            scraped_data=job_data
                        )
                        current_job_desc = scraped_description
                    else:
                        st.warning("⚠️ Scraped content but no description found. Please paste manually below.")
                else:
                    st.error(f"❌ Failed to scrape URL: {error}")

    # Manual text input
    job_description = st.text_area(
        "Or paste the job description below:",
        value=current_job_desc if not scraped_description else scraped_description,
        height=300,
        placeholder="Paste the complete job description here...",
        help="Include all relevant information: responsibilities, requirements, qualifications, etc."
    )

    # Statistics and validation
    stats = get_text_statistics(job_description)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Characters", stats['chars'])
    with col2:
        st.metric("Words", stats['words'])
    with col3:
        st.metric("Lines", stats['lines'])

    # Validate
    is_valid = False
    if job_description.strip():
        valid, error = validate_job_description(job_description)
        if valid:
            st.success("✅ Job description is valid")
            is_valid = True
        else:
            st.warning(f"⚠️ {error}")

    return job_description, is_valid


def render_company_url_input() -> str:
    """
    Render company URL input section.

    Returns:
        Company URL string
    """
    st.markdown("### 🏢 Company Information (Optional)")

    current_inputs = get_all_inputs()
    current_company_url = current_inputs.get('company_url', '')

    company_url = st.text_input(
        "Company Website URL",
        value=current_company_url,
        placeholder="https://company.com",
        help="Optional: Company website for additional context"
    )

    # Validate if provided
    if company_url.strip():
        valid, error = validate_url(company_url)
        if not valid:
            st.warning(f"⚠️ {error}")

    return company_url


def render_resume_input() -> tuple[str, dict, bool]:
    """
    Render resume input section.

    Returns:
        Tuple of (resume_text, metadata, is_valid)
    """
    st.markdown("### 📝 Your Resume")

    current_inputs = get_all_inputs()
    current_resume_text = current_inputs.get('resume_text', '')
    current_metadata = current_inputs.get('resume_metadata', {})

    # File upload
    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=SUPPORTED_RESUME_EXTENSIONS,
        help=f"Supported formats: {', '.join(SUPPORTED_RESUME_EXTENSIONS)}"
    )

    resume_text = current_resume_text
    metadata = current_metadata

    if uploaded_file is not None:
        with st.spinner("Processing resume..."):
            success, extracted_text, error = extract_text_from_file(uploaded_file)

            if success:
                resume_text = extracted_text
                st.success(f"✅ Resume uploaded successfully: {uploaded_file.name}")

                # Extract metadata
                metadata = extract_basic_info(extracted_text)
                metadata['filename'] = uploaded_file.name
                metadata['file_type'] = uploaded_file.type

                # Show preview
                with st.expander("📄 Preview Extracted Text", expanded=False):
                    st.text_area(
                        "Extracted Resume Text",
                        value=resume_text[:2000] + ("..." if len(resume_text) > 2000 else ""),
                        height=200,
                        label_visibility="collapsed"
                    )
            else:
                st.error(f"❌ {error}")

    # Divider
    st.markdown("---")
    st.markdown("**OR paste your resume text:**")

    # Manual text input
    manual_resume = st.text_area(
        "Resume Text",
        value=resume_text,
        height=300,
        placeholder="Paste your resume text here...",
        label_visibility="collapsed"
    )

    # Use manual input if provided and different from uploaded
    if manual_resume.strip() and manual_resume != resume_text:
        resume_text = manual_resume
        metadata = extract_basic_info(manual_resume)

    # Statistics and validation
    if resume_text.strip():
        stats = get_text_statistics(resume_text)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Characters", stats['chars'])
        with col2:
            st.metric("Words", stats['words'])

        # Show extracted info if available
        if metadata:
            with st.expander("📊 Detected Information"):
                if metadata.get('email'):
                    st.markdown(f"**Email:** {metadata['email']}")
                if metadata.get('phone'):
                    st.markdown(f"**Phone:** {metadata['phone']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Education:** {'✅' if metadata.get('has_education') else '❌'}")
                with col2:
                    st.markdown(f"**Experience:** {'✅' if metadata.get('has_experience') else '❌'}")
                with col3:
                    st.markdown(f"**Skills:** {'✅' if metadata.get('has_skills') else '❌'}")

    # Validate
    is_valid = False
    if resume_text.strip():
        valid, error = validate_resume_text(resume_text)
        if valid:
            st.success("✅ Resume is valid")
            is_valid = True
        else:
            st.warning(f"⚠️ {error}")

    return resume_text, metadata, is_valid


def render_output_folder_input() -> str:
    """
    Render output folder selection.

    Returns:
        Output folder path
    """
    st.markdown("### 📁 Output Folder")

    current_inputs = get_all_inputs()
    current_folder = current_inputs.get('output_folder', DEFAULT_OUTPUT_FOLDER)

    output_folder = st.text_input(
        "Select folder to save all materials",
        value=current_folder,
        help="All generated files will be saved to this folder"
    )

    # Validate
    if output_folder.strip():
        valid, error = validate_folder_path(output_folder)
        if valid:
            # Try to create folder to verify permissions
            try:
                Path(output_folder).mkdir(parents=True, exist_ok=True)
                st.success(f"✅ Output folder: {output_folder}")
            except Exception as e:
                st.error(f"❌ Cannot create folder: {str(e)}")
        else:
            st.warning(f"⚠️ {error}")

    return output_folder


def render_action_buttons(all_valid: bool) -> tuple[bool, bool]:
    """
    Render action buttons (Clear, Continue).

    Args:
        all_valid: Whether all inputs are valid

    Returns:
        Tuple of (clear_clicked, continue_clicked)
    """
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        clear_clicked = st.button("🗑️ Clear All", use_container_width=True)

    with col3:
        if all_valid:
            continue_clicked = st.button(
                "Continue to Analysis →",
                type="primary",
                use_container_width=True
            )
        else:
            continue_clicked = st.button(
                "Continue to Analysis →",
                disabled=True,
                use_container_width=True,
                help="Please complete all required inputs"
            )

    return clear_clicked, continue_clicked


def render_input_collection_page() -> bool:
    """
    Render the complete input collection page (Step 1).

    Returns:
        True if step is complete and user clicked Continue
    """
    # Progress bar
    render_progress_bar(1)

    # Header
    st.title("🎯 Resume Tailor - Input Collection")
    st.markdown("""
    Welcome! Let's start by collecting the job description and your resume.
    This information will be used to tailor your resume to the specific job posting.
    """)
    st.markdown("---")

    # Job Description Section
    job_description, job_valid = render_job_description_input()
    st.markdown("---")

    # Company URL Section
    company_url = render_company_url_input()
    st.markdown("---")

    # Resume Section
    resume_text, metadata, resume_valid = render_resume_input()
    st.markdown("---")

    # Output Folder Section
    output_folder = render_output_folder_input()
    folder_valid = bool(output_folder.strip())

    # Check if all inputs are valid
    all_valid = job_valid and resume_valid and folder_valid

    # Action Buttons
    clear_clicked, continue_clicked = render_action_buttons(all_valid)

    # Handle clear button
    if clear_clicked:
        from utils.session_manager import clear_session_state
        clear_session_state()
        st.rerun()

    # Handle continue button
    if continue_clicked and all_valid:
        # Save all inputs
        job_url = st.session_state.get(SESSION_KEYS['job_url'], '')
        scraped_data = st.session_state.get(SESSION_KEYS['scraped_job_data'], None)

        save_job_inputs(job_description, job_url, company_url, scraped_data)
        save_resume_inputs(resume_text, metadata)
        save_output_folder(output_folder)

        return True

    return False
