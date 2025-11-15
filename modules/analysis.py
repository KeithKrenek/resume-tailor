"""Step 2: Job and Resume Analysis module."""

import streamlit as st
from typing import Optional, Tuple
import pandas as pd

from modules.models import JobModel, ResumeModel, GapAnalysis
from agents.job_analysis_agent import analyze_job_posting
from agents.resume_analysis_agent import analyze_resume
from modules.gap_analyzer import perform_gap_analysis
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


def perform_analysis() -> Tuple[Optional[JobModel], Optional[ResumeModel], Optional[GapAnalysis], list]:
    """
    Perform job and resume analysis.

    Returns:
        Tuple of (JobModel, ResumeModel, GapAnalysis, errors)
    """
    errors = []
    inputs = get_all_inputs()

    # Analyze job posting
    job_model = None
    with st.status("🔍 Analyzing job posting...", expanded=True) as status:
        st.write("Extracting job requirements and skills...")
        success, job_model, error = analyze_job_posting(
            job_description=inputs['job_description'],
            job_title=inputs.get('job_title'),
            company_name=inputs.get('company_name')
        )

        if success and job_model:
            st.write("✅ Job analysis complete")
            status.update(label="✅ Job posting analyzed", state="complete")
        else:
            st.error(f"❌ {error}")
            errors.append(f"Job analysis: {error}")
            status.update(label="❌ Job analysis failed", state="error")
            return None, None, None, errors

    # Analyze resume
    resume_model = None
    with st.status("📝 Analyzing resume...", expanded=True) as status:
        st.write("Extracting experience, education, and skills...")
        success, resume_model, error = analyze_resume(
            resume_text=inputs['resume_text'],
            metadata=inputs.get('resume_metadata', {})
        )

        if success and resume_model:
            st.write("✅ Resume analysis complete")
            status.update(label="✅ Resume analyzed", state="complete")
        else:
            st.error(f"❌ {error}")
            errors.append(f"Resume analysis: {error}")
            status.update(label="❌ Resume analysis failed", state="error")
            return job_model, None, None, errors

    # Perform gap analysis
    gap_analysis = None
    with st.status("🔬 Performing gap analysis...", expanded=True) as status:
        st.write("Comparing job requirements with resume...")
        try:
            gap_analysis = perform_gap_analysis(job_model, resume_model)
            st.write("✅ Gap analysis complete")
            status.update(label="✅ Gap analysis complete", state="complete")
        except Exception as e:
            st.error(f"❌ {str(e)}")
            errors.append(f"Gap analysis: {str(e)}")
            status.update(label="❌ Gap analysis failed", state="error")
            return job_model, resume_model, None, errors

    # Save outputs
    with st.status("💾 Saving analysis results...", expanded=False) as status:
        try:
            output_manager = OutputManager(inputs['output_folder'])
            all_success, saved_files, save_errors = output_manager.save_all(
                job_model, resume_model, gap_analysis
            )

            # Also save summary report
            success, result = output_manager.save_summary_report(
                job_model, resume_model, gap_analysis
            )
            if success:
                saved_files.append(result)

            if all_success and success:
                st.write(f"✅ Saved {len(saved_files)} files")
                status.update(label="✅ Results saved", state="complete")
            else:
                for err in save_errors:
                    st.warning(f"⚠️ {err}")
                status.update(label="⚠️ Some files not saved", state="error")
        except Exception as e:
            st.error(f"❌ {str(e)}")
            errors.append(f"Save error: {str(e)}")

    return job_model, resume_model, gap_analysis, errors


def render_job_analysis(job: JobModel) -> None:
    """Render job analysis results."""
    st.markdown("### 📋 Job Analysis")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Required Skills", len(job.required_skills))
    with col2:
        st.metric("Preferred Skills", len(job.preferred_skills))
    with col3:
        st.metric("Total Requirements", len(job.requirements))

    # Job details
    with st.expander("📄 Job Details", expanded=False):
        st.markdown(f"**Title:** {job.title}")
        if job.company:
            st.markdown(f"**Company:** {job.company}")
        if job.location:
            st.markdown(f"**Location:** {job.location}")
        if job.experience_level:
            st.markdown(f"**Experience Level:** {job.experience_level}")

    # Requirements table
    if job.requirements:
        with st.expander("📝 Requirements Breakdown", expanded=True):
            req_data = []
            for req in job.requirements:
                req_data.append({
                    "Requirement": req.description[:80] + "..." if len(req.description) > 80 else req.description,
                    "Category": req.category,
                    "Must-Have": "✅" if req.is_must_have else "➖"
                })

            df = pd.DataFrame(req_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # Skills
    col1, col2 = st.columns(2)
    with col1:
        if job.required_skills:
            with st.expander(f"🔴 Required Skills ({len(job.required_skills)})", expanded=False):
                for skill in job.required_skills:
                    st.markdown(f"- {skill}")

    with col2:
        if job.preferred_skills:
            with st.expander(f"🟡 Preferred Skills ({len(job.preferred_skills)})", expanded=False):
                for skill in job.preferred_skills:
                    st.markdown(f"- {skill}")


def render_resume_analysis(resume: ResumeModel) -> None:
    """Render resume analysis results."""
    st.markdown("### 📝 Resume Analysis")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Experience", f"{resume.total_years_experience or 0} yrs")
    with col2:
        st.metric("Positions", len(resume.experiences))
    with col3:
        st.metric("Skills", len(resume.skills))
    with col4:
        st.metric("Education", len(resume.education))

    # Contact info
    with st.expander("👤 Contact Information", expanded=False):
        if resume.name:
            st.markdown(f"**Name:** {resume.name}")
        if resume.email:
            st.markdown(f"**Email:** {resume.email}")
        if resume.phone:
            st.markdown(f"**Phone:** {resume.phone}")
        if resume.location:
            st.markdown(f"**Location:** {resume.location}")

    # Experience
    if resume.experiences:
        with st.expander(f"💼 Work Experience ({len(resume.experiences)} positions)", expanded=True):
            for i, exp in enumerate(resume.experiences, 1):
                st.markdown(f"**{i}. {exp.title}** at **{exp.company}**")
                if exp.start_date or exp.end_date:
                    period = f"{exp.start_date or '?'} - {exp.end_date or 'Present'}"
                    st.markdown(f"*{period}*")

                if exp.bullets:
                    st.markdown("**Key Achievements:**")
                    for bullet in exp.bullets[:3]:  # Show first 3 bullets
                        st.markdown(f"- {bullet}")

                if exp.skills:
                    st.markdown(f"**Skills:** {', '.join(exp.skills[:5])}")

                if i < len(resume.experiences):
                    st.markdown("---")

    # Skills
    if resume.skills:
        with st.expander(f"🛠️ Skills ({len(resume.skills)})", expanded=False):
            # Group skills (simple grouping by first letter or show all)
            skills_text = ", ".join(resume.skills)
            st.markdown(skills_text)

    # Education
    if resume.education:
        with st.expander(f"🎓 Education ({len(resume.education)})", expanded=False):
            for edu in resume.education:
                st.markdown(f"**{edu.degree}**")
                st.markdown(f"*{edu.institution}*")
                if edu.graduation_date:
                    st.markdown(f"Graduated: {edu.graduation_date}")
                if edu.gpa:
                    st.markdown(f"GPA: {edu.gpa}")
                st.markdown("")


def render_gap_analysis(gap: GapAnalysis) -> None:
    """Render gap analysis results."""
    st.markdown("### 🔬 Gap Analysis")

    # Overall metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        coverage_color = "🟢" if gap.coverage_percentage >= 70 else "🟡" if gap.coverage_percentage >= 50 else "🔴"
        st.metric(
            "Coverage",
            f"{gap.coverage_percentage}%",
            delta=f"{coverage_color} {gap.met_requirements}/{gap.total_requirements} requirements"
        )
    with col2:
        st.metric("Matched Skills", len(gap.matched_skills))
    with col3:
        st.metric("Missing Skills", len(gap.missing_required_skills))

    # Strengths
    if gap.strengths:
        st.markdown("#### ✅ Strengths")
        for strength in gap.strengths:
            st.success(f"✓ {strength}")

    # Weaknesses
    if gap.weaknesses:
        st.markdown("#### ⚠️ Gaps to Address")
        for weakness in gap.weaknesses:
            st.warning(f"⚡ {weakness}")

    # Skill Match Details
    with st.expander("📊 Detailed Skill Analysis", expanded=True):
        # Tabs for different skill categories
        tab1, tab2, tab3 = st.tabs(["✅ Matched", "❌ Missing", "⚡ Weak Coverage"])

        with tab1:
            if gap.matched_skills:
                match_data = []
                for skill in gap.matched_skills:
                    match_data.append({
                        "Skill": skill.skill,
                        "Required": "✅" if skill.is_required else "➖",
                        "Strength": skill.strength.upper(),
                        "Evidence": "; ".join(skill.evidence[:2])  # First 2 pieces of evidence
                    })
                df = pd.DataFrame(match_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No matched skills found")

        with tab2:
            if gap.missing_required_skills:
                st.markdown("**Missing Required Skills:**")
                for skill in gap.missing_required_skills:
                    st.markdown(f"- ❌ {skill}")
            else:
                st.success("All required skills are present!")

            if gap.missing_preferred_skills:
                st.markdown("\n**Missing Preferred Skills:**")
                for skill in gap.missing_preferred_skills:
                    st.markdown(f"- ➖ {skill}")

        with tab3:
            if gap.weakly_covered_skills:
                weak_data = []
                for skill in gap.weakly_covered_skills:
                    weak_data.append({
                        "Skill": skill.skill,
                        "Required": "✅" if skill.is_required else "➖",
                        "Evidence": "; ".join(skill.evidence)
                    })
                df = pd.DataFrame(weak_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.info("💡 These skills are mentioned but could be strengthened with more specific examples")
            else:
                st.success("No weakly covered skills")

    # Recommendations
    if gap.suggestions:
        st.markdown("#### 💡 Recommendations")
        for i, suggestion in enumerate(gap.suggestions, 1):
            st.info(f"{i}. {suggestion}")


def render_analysis_page() -> bool:
    """
    Render the complete analysis page (Step 2).

    Returns:
        True if step is complete and user clicked Continue
    """
    # Progress bar
    render_progress_bar(2)

    # Header
    st.title("🔍 Step 2: Job & Resume Analysis")
    st.markdown("""
    Analyzing the job posting and your resume to identify strengths, gaps, and opportunities.
    This will help tailor your resume for maximum impact.
    """)
    st.markdown("---")

    # Check if analysis already done (stored in session)
    if 'job_model' in st.session_state and 'resume_model' in st.session_state and 'gap_analysis' in st.session_state:
        job_model = st.session_state['job_model']
        resume_model = st.session_state['resume_model']
        gap_analysis = st.session_state['gap_analysis']

        st.success("✅ Analysis already completed. Showing cached results.")

    else:
        # Run analysis
        st.info("🚀 Starting analysis... This may take 30-60 seconds.")

        job_model, resume_model, gap_analysis, errors = perform_analysis()

        if errors:
            st.error("❌ Analysis failed. Please check the errors above and try again.")
            if st.button("← Back to Step 1"):
                set_current_step(1)
                st.rerun()
            return False

        # Store in session
        st.session_state['job_model'] = job_model
        st.session_state['resume_model'] = resume_model
        st.session_state['gap_analysis'] = gap_analysis

        st.balloons()
        st.success("✅ Analysis complete!")

    # Display results
    st.markdown("---")

    # Summary card
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Overall Match",
            f"{gap_analysis.coverage_percentage}%",
            delta="Requirements Coverage"
        )
    with col2:
        st.metric("Matched Skills", len(gap_analysis.matched_skills))
    with col3:
        st.metric("Missing Required", len(gap_analysis.missing_required_skills))

    st.markdown("---")

    # Detailed results
    tab1, tab2, tab3 = st.tabs(["📋 Job Analysis", "📝 Resume Analysis", "🔬 Gap Analysis"])

    with tab1:
        render_job_analysis(job_model)

    with tab2:
        render_resume_analysis(resume_model)

    with tab3:
        render_gap_analysis(gap_analysis)

    st.markdown("---")

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back to Step 1"):
            set_current_step(1)
            st.rerun()

    with col2:
        if st.button("🔄 Re-analyze"):
            # Clear cached results
            if 'job_model' in st.session_state:
                del st.session_state['job_model']
            if 'resume_model' in st.session_state:
                del st.session_state['resume_model']
            if 'gap_analysis' in st.session_state:
                del st.session_state['gap_analysis']
            st.rerun()

    with col3:
        if st.button("Continue to Optimization →", type="primary"):
            mark_step_complete(2)
            set_current_step(3)
            st.success("✅ Step 2 completed! Moving to optimization...")
            import time
            time.sleep(1)
            st.rerun()
            return True

    return False
