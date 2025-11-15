"""
Resume Tailor - AI-Powered Resume Optimization Application

Main Streamlit application entry point.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import APP_NAME, APP_VERSION, APP_DESCRIPTION
from utils.session_manager import (
    initialize_session_state,
    get_current_step,
    set_current_step,
    mark_step_complete,
    save_extracted_info,
    get_all_inputs
)
from modules.input_collector import render_input_collection_page
from modules.analysis import render_analysis_page
from modules.optimization import render_optimization_page
from modules.output import render_output_generation_page
from agents.extraction_agent import extract_job_info


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title=f"{APP_NAME} v{APP_VERSION}",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_sidebar():
    """Render application sidebar with info and navigation."""
    with st.sidebar:
        st.title(f"🎯 {APP_NAME}")
        st.markdown(f"**Version:** {APP_VERSION}")
        st.markdown(f"*{APP_DESCRIPTION}*")
        st.markdown("---")

        # Current step indicator
        current_step = get_current_step()
        st.markdown(f"### 📍 Current Step: {current_step}")

        st.markdown("---")

        # Workflow steps
        st.markdown("### 📋 Workflow Steps")
        steps = [
            "1️⃣ Input Collection",
            "2️⃣ Analysis",
            "3️⃣ Optimization",
            "4️⃣ Output Generation"
        ]

        for i, step in enumerate(steps, 1):
            if i == current_step:
                st.markdown(f"**{step}** ⬅️")
            elif i < current_step:
                st.markdown(f"~~{step}~~ ✅")
            else:
                st.markdown(f"{step}")

        st.markdown("---")

        # Session info
        inputs = get_all_inputs()
        with st.expander("📊 Session Info"):
            if inputs['job_description']:
                st.markdown(f"✅ Job Description ({len(inputs['job_description'])} chars)")
            if inputs['resume_text']:
                st.markdown(f"✅ Resume ({len(inputs['resume_text'])} chars)")
            if inputs['company_name']:
                st.markdown(f"🏢 Company: {inputs['company_name']}")
            if inputs['job_title']:
                st.markdown(f"💼 Title: {inputs['job_title']}")
            if inputs['output_folder']:
                st.markdown(f"📁 Output: {Path(inputs['output_folder']).name}")

        st.markdown("---")

        # Help section
        with st.expander("ℹ️ Help & Info"):
            st.markdown("""
            **How to use:**
            1. Enter job description and resume
            2. The app will analyze both documents
            3. Identify gaps and opportunities
            4. Generate optimized resume
            5. Download tailored materials

            **Tips:**
            - Use complete job descriptions
            - Ensure resume has all sections
            - Review AI suggestions carefully
            """)

        st.markdown("---")
        st.markdown("Made with ❤️ using Streamlit & Claude")


def step_1_input_collection():
    """Handle Step 1: Input Collection."""
    step_complete = render_input_collection_page()

    if step_complete:
        with st.spinner("Extracting company and job title..."):
            # Get inputs
            inputs = get_all_inputs()

            # Extract company and job title using AI agent
            success, company, title, error = extract_job_info(
                job_description=inputs['job_description'],
                job_url=inputs.get('job_url', ''),
                scraped_data=inputs.get('scraped_job_data')
            )

            if success:
                save_extracted_info(company_name=company, job_title=title)
                st.success(f"✅ Extracted: **{title}** at **{company}**")

        # Mark step as complete
        mark_step_complete(1)
        set_current_step(2)
        st.success("✅ Step 1 completed! Moving to next step...")
        st.balloons()

        # Wait a moment then rerun to show next step
        import time
        time.sleep(1)
        st.rerun()


def step_2_analysis():
    """Handle Step 2: Job and Resume Analysis."""
    render_analysis_page()


def step_3_optimization():
    """Handle Step 3: Resume Optimization."""
    render_optimization_page()


def step_4_output_generation():
    """Handle Step 4: Output Generation."""
    render_output_generation_page()


def main():
    """Main application entry point."""
    # Configure page
    configure_page()

    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Get current step
    current_step = get_current_step()

    # Route to appropriate step
    if current_step == 1:
        step_1_input_collection()
    elif current_step == 2:
        step_2_analysis()
    elif current_step == 3:
        step_3_optimization()
    elif current_step == 4:
        step_4_output_generation()
    elif current_step >= 5:
        st.title("🎉 All Steps Complete!")
        st.success("Your resume has been optimized and generated successfully!")
        st.info("You can now start a new resume or return to previous steps.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Start New Resume"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                set_current_step(1)
                st.rerun()
        with col2:
            if st.button("← Back to Output Generation"):
                set_current_step(4)
                st.rerun()
    else:
        st.error(f"Invalid step: {current_step}")


if __name__ == "__main__":
    main()
