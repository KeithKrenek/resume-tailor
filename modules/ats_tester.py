"""ATS Testing and Simulation UI."""

import streamlit as st
from typing import Optional, Dict, Any

from agents.ats_simulation_agent import simulate_ats_parsing, check_format_issues
from modules.models import ResumeModel


def render_ats_tester() -> None:
    """
    Render the ATS testing interface.

    Allows users to simulate how ATS systems will parse their resume.
    """
    st.markdown("## 🤖 ATS Simulation & Testing")

    st.info(
        "📊 **Test how ATS systems will parse your resume!** "
        "Get a detailed analysis of parsing quality, keyword matching, and formatting compatibility. "
        "Identify issues before submitting to real ATS systems."
    )

    # Get resume from session
    resume = get_testable_resume()

    if not resume:
        st.warning("No resume available to test. Please complete optimization first.")
        return

    # Get job description for keyword analysis
    job_description = st.session_state.get('job_description', '')

    # Run ATS simulation button
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("### 🚀 Run ATS Simulation")
        st.markdown("Click the button below to simulate how an ATS would parse your resume.")

    with col2:
        run_test = st.button(
            "▶️ Run ATS Test",
            type="primary",
            use_container_width=True,
            help="Simulate ATS parsing and analysis"
        )

    # Run simulation if requested or if results already exist
    if run_test or 'ats_test_result' in st.session_state:
        if run_test:
            # Run new simulation
            with st.spinner("🤖 Simulating ATS parsing... This may take a moment."):
                resume_text = resume.to_markdown()

                success, ats_report, error = simulate_ats_parsing(
                    resume_text=resume_text,
                    job_description=job_description if job_description else None
                )

                if success and ats_report:
                    st.session_state.ats_test_result = ats_report
                    st.balloons()
                    st.success("✅ ATS simulation complete!")
                else:
                    st.error(f"❌ ATS simulation failed: {error}")
                    return

        # Display results
        ats_report = st.session_state.ats_test_result
        render_ats_results(ats_report, job_description)


def get_testable_resume() -> Optional[ResumeModel]:
    """Get the resume that should be tested."""
    # Priority: edited_resume > final_resume > optimized_resume
    if 'edited_resume' in st.session_state:
        return st.session_state.edited_resume
    elif 'final_resume' in st.session_state:
        return st.session_state.final_resume
    elif 'optimization_result' in st.session_state:
        return st.session_state.optimization_result.optimized_resume
    return None


def render_ats_results(ats_report: Dict[str, Any], job_description: str) -> None:
    """
    Render ATS simulation results.

    Args:
        ats_report: ATS analysis report
        job_description: Job description used for analysis
    """
    st.markdown("---")
    st.markdown("## 📊 ATS Test Results")

    # Overall score and grade
    render_overall_score(ats_report)

    st.markdown("---")

    # Detailed scores by category
    render_category_scores(ats_report)

    st.markdown("---")

    # Keyword analysis (if available)
    if 'keyword_analysis' in ats_report and job_description:
        render_keyword_analysis(ats_report['keyword_analysis'])
        st.markdown("---")

    # Issues and recommendations
    render_issues_and_recommendations(ats_report)

    st.markdown("---")

    # Extracted data
    render_extracted_data(ats_report)

    st.markdown("---")

    # ATS view
    if 'ats_view' in ats_report:
        render_ats_view(ats_report['ats_view'])


def render_overall_score(ats_report: Dict[str, Any]) -> None:
    """Render overall ATS score."""
    overall_score = ats_report.get('overall_score', 0)
    overall_grade = ats_report.get('overall_grade', 'N/A')
    passed_ats = ats_report.get('passed_ats', False)

    st.markdown("### 🎯 Overall ATS Score")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Score with color coding
        score_color = get_score_color(overall_score)
        st.markdown(
            f"<h1 style='text-align: center; color: {score_color};'>{overall_score}</h1>",
            unsafe_allow_html=True
        )
        st.markdown("<p style='text-align: center;'>out of 100</p>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"<h1 style='text-align: center;'>{overall_grade}</h1>",
            unsafe_allow_html=True
        )
        st.markdown("<p style='text-align: center;'>Letter Grade</p>", unsafe_allow_html=True)

    with col3:
        if passed_ats:
            st.success("### ✅ PASSED")
            st.markdown("Your resume is likely to pass ATS screening")
        else:
            st.error("### ❌ NEEDS WORK")
            st.markdown("Your resume may have issues with ATS parsing")

    # Score interpretation
    st.markdown(get_score_interpretation(overall_score))


def render_category_scores(ats_report: Dict[str, Any]) -> None:
    """Render detailed category scores."""
    st.markdown("### 📈 Detailed Category Scores")

    categories = [
        ('parsing_quality', '🔍 Parsing Quality', 'How well-structured for ATS parsing'),
        ('contact_extraction', '📇 Contact Extraction', 'Ease of extracting contact information'),
        ('section_identification', '📑 Section Identification', 'Clarity of section headers'),
        ('keyword_density', '🔤 Keyword Density', 'Presence of relevant keywords'),
        ('format_compatibility', '📄 Format Compatibility', 'ATS-friendly formatting'),
        ('experience_parsing', '💼 Experience Parsing', 'Extractability of work history')
    ]

    for key, label, description in categories:
        score = ats_report.get(key, 0)
        render_score_bar(label, score, description)


def render_score_bar(label: str, score: int, description: str) -> None:
    """Render a single score bar."""
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown(f"**{label}**")
        st.caption(description)

    with col2:
        # Progress bar with color
        progress_color = get_score_color(score)

        # Use columns for score and bar
        score_col, bar_col = st.columns([1, 5])

        with score_col:
            st.markdown(f"<h3 style='color: {progress_color}; margin: 0;'>{score}</h3>", unsafe_allow_html=True)

        with bar_col:
            st.progress(score / 100)


def render_keyword_analysis(keyword_data: Dict[str, Any]) -> None:
    """Render keyword matching analysis."""
    st.markdown("### 🔤 Keyword Matching Analysis")

    match_rate = keyword_data.get('match_rate', 0)
    grade = keyword_data.get('grade', 'N/A')

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Job Keywords",
            keyword_data.get('total_job_keywords', 0),
            help="Total important keywords in job description"
        )

    with col2:
        st.metric(
            "Matched",
            keyword_data.get('matched_keywords', 0),
            help="Keywords from job description found in your resume"
        )

    with col3:
        st.metric(
            "Missing",
            keyword_data.get('missing_keywords', 0),
            delta=f"-{keyword_data.get('missing_keywords', 0)}",
            delta_color="inverse",
            help="Keywords from job description NOT in your resume"
        )

    with col4:
        match_color = get_score_color(match_rate)
        st.markdown(
            f"<h3 style='text-align: center; color: {match_color};'>{match_rate}%</h3>",
            unsafe_allow_html=True
        )
        st.markdown(f"<p style='text-align: center;'>Match Rate ({grade})</p>", unsafe_allow_html=True)

    # Show matched and missing keywords
    col1, col2 = st.columns(2)

    with col1:
        matched_list = keyword_data.get('matched_list', [])
        if matched_list:
            st.markdown("**✅ Matched Keywords:**")
            keywords_str = ", ".join([f"`{kw}`" for kw in matched_list[:15]])
            st.markdown(keywords_str)
            if len(matched_list) > 15:
                st.caption(f"...and {len(matched_list) - 15} more")

    with col2:
        missing_list = keyword_data.get('missing_list', [])
        if missing_list:
            st.markdown("**❌ Missing Keywords:**")
            keywords_str = ", ".join([f"`{kw}`" for kw in missing_list[:15]])
            st.markdown(keywords_str)
            if len(missing_list) > 15:
                st.caption(f"...and {len(missing_list) - 15} more")


def render_issues_and_recommendations(ats_report: Dict[str, Any]) -> None:
    """Render issues and recommendations."""
    critical_issues = ats_report.get('critical_issues', [])
    warnings = ats_report.get('warnings', [])
    recommendations = ats_report.get('recommendations', [])

    st.markdown("### 🔧 Issues & Recommendations")

    # Critical issues
    if critical_issues:
        st.markdown("#### 🚨 Critical Issues")
        st.error("These issues may prevent ATS from parsing your resume correctly:")
        for issue in critical_issues:
            st.markdown(f"- {issue}")

    # Warnings
    if warnings:
        st.markdown("#### ⚠️ Warnings")
        st.warning("These issues may reduce ATS effectiveness:")
        for warning in warnings:
            st.markdown(f"- {warning}")

    # Recommendations
    if recommendations:
        st.markdown("#### 💡 Recommendations")
        st.info("Actionable steps to improve ATS compatibility:")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.success("✅ No recommendations - your resume is well-optimized for ATS!")


def render_extracted_data(ats_report: Dict[str, Any]) -> None:
    """Render data extracted by ATS simulation."""
    extracted = ats_report.get('extracted_data', {})

    if not extracted:
        return

    st.markdown("### 📋 Data Extracted by ATS")

    st.info(
        "This is what an ATS system was able to extract from your resume. "
        "Verify that all information is correct."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Contact Information:**")
        st.markdown(f"- Name: {extracted.get('name', 'Not detected')}")
        st.markdown(f"- Email: {extracted.get('email', 'Not detected')}")
        st.markdown(f"- Phone: {extracted.get('phone', 'Not detected')}")
        st.markdown(f"- Location: {extracted.get('location', 'Not detected')}")

    with col2:
        st.markdown("**Professional Information:**")
        sections = extracted.get('sections_found', [])
        st.markdown(f"- Sections Found: {', '.join(sections) if sections else 'None'}")
        st.markdown(f"- Years of Experience: {extracted.get('years_of_experience', 'Not detected')}")
        st.markdown(f"- Education Level: {extracted.get('education_level', 'Not detected')}")


def render_ats_view(ats_view: str) -> None:
    """Render what ATS 'sees'."""
    with st.expander("👁️ What the ATS 'Sees'", expanded=False):
        st.markdown("**This is a simplified view of how an ATS parses your resume:**")
        st.text_area(
            "ATS Text View",
            value=ats_view,
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )


def get_score_color(score: int) -> str:
    """Get color for score visualization."""
    if score >= 85:
        return "#28a745"  # Green
    elif score >= 70:
        return "#ffc107"  # Yellow
    elif score >= 50:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red


def get_score_interpretation(score: int) -> str:
    """Get interpretation text for overall score."""
    if score >= 90:
        return "🌟 **Excellent!** Your resume is highly optimized for ATS systems."
    elif score >= 80:
        return "✅ **Great!** Your resume should pass most ATS systems with minor improvements."
    elif score >= 70:
        return "👍 **Good!** Your resume is ATS-compatible but could be improved."
    elif score >= 60:
        return "⚠️ **Fair** - Your resume may have difficulty with some ATS systems."
    else:
        return "❌ **Needs Improvement** - Significant ATS compatibility issues detected."
