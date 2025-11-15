"""Output management utilities for saving analysis results."""

import json
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime

from modules.models import JobModel, ResumeModel, GapAnalysis


class OutputManager:
    """Manages saving and loading of analysis outputs."""

    def __init__(self, output_folder: str):
        """
        Initialize output manager.

        Args:
            output_folder: Path to output folder
        """
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def save_job_model(self, job: JobModel, filename: str = "job_analysis.json") -> Tuple[bool, str]:
        """
        Save JobModel to JSON file.

        Args:
            job: JobModel to save
            filename: Output filename

        Returns:
            Tuple of (success, file_path or error_message)
        """
        try:
            file_path = self.output_folder / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(job.to_json())
            return True, str(file_path)
        except Exception as e:
            return False, f"Error saving job model: {str(e)}"

    def save_resume_model(self, resume: ResumeModel, filename: str = "resume_analysis.json") -> Tuple[bool, str]:
        """
        Save ResumeModel to JSON file.

        Args:
            resume: ResumeModel to save
            filename: Output filename

        Returns:
            Tuple of (success, file_path or error_message)
        """
        try:
            file_path = self.output_folder / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(resume.to_json())
            return True, str(file_path)
        except Exception as e:
            return False, f"Error saving resume model: {str(e)}"

    def save_gap_analysis(self, gap: GapAnalysis, filename: str = "gap_analysis.json") -> Tuple[bool, str]:
        """
        Save GapAnalysis to JSON file.

        Args:
            gap: GapAnalysis to save
            filename: Output filename

        Returns:
            Tuple of (success, file_path or error_message)
        """
        try:
            file_path = self.output_folder / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(gap.to_json())
            return True, str(file_path)
        except Exception as e:
            return False, f"Error saving gap analysis: {str(e)}"

    def save_all(
        self,
        job: JobModel,
        resume: ResumeModel,
        gap: GapAnalysis,
        prefix: str = ""
    ) -> Tuple[bool, list, list]:
        """
        Save all analysis outputs.

        Args:
            job: JobModel to save
            resume: ResumeModel to save
            gap: GapAnalysis to save
            prefix: Optional prefix for filenames

        Returns:
            Tuple of (all_success, saved_files, errors)
        """
        saved_files = []
        errors = []

        # Save job model
        job_file = f"{prefix}job_analysis.json" if prefix else "job_analysis.json"
        success, result = self.save_job_model(job, job_file)
        if success:
            saved_files.append(result)
        else:
            errors.append(result)

        # Save resume model
        resume_file = f"{prefix}resume_analysis.json" if prefix else "resume_analysis.json"
        success, result = self.save_resume_model(resume, resume_file)
        if success:
            saved_files.append(result)
        else:
            errors.append(result)

        # Save gap analysis
        gap_file = f"{prefix}gap_analysis.json" if prefix else "gap_analysis.json"
        success, result = self.save_gap_analysis(gap, gap_file)
        if success:
            saved_files.append(result)
        else:
            errors.append(result)

        return len(errors) == 0, saved_files, errors

    def save_summary_report(
        self,
        job: JobModel,
        resume: ResumeModel,
        gap: GapAnalysis,
        filename: str = "analysis_summary.txt"
    ) -> Tuple[bool, str]:
        """
        Save human-readable summary report.

        Args:
            job: JobModel
            resume: ResumeModel
            gap: GapAnalysis
            filename: Output filename

        Returns:
            Tuple of (success, file_path or error_message)
        """
        try:
            file_path = self.output_folder / filename

            # Generate report
            report = self._generate_summary_report(job, resume, gap)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)

            return True, str(file_path)
        except Exception as e:
            return False, f"Error saving summary report: {str(e)}"

    def _generate_summary_report(
        self, job: JobModel, resume: ResumeModel, gap: GapAnalysis
    ) -> str:
        """Generate human-readable summary report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""
═══════════════════════════════════════════════════════════════
RESUME TAILOR - ANALYSIS SUMMARY REPORT
═══════════════════════════════════════════════════════════════
Generated: {timestamp}

───────────────────────────────────────────────────────────────
JOB POSTING
───────────────────────────────────────────────────────────────
Title:    {job.title}
Company:  {job.company or 'N/A'}
Location: {job.location or 'N/A'}
Level:    {job.experience_level or 'N/A'}

───────────────────────────────────────────────────────────────
CANDIDATE
───────────────────────────────────────────────────────────────
Name:       {resume.name or 'N/A'}
Email:      {resume.email or 'N/A'}
Experience: {resume.total_years_experience or 'N/A'} years

───────────────────────────────────────────────────────────────
OVERALL MATCH
───────────────────────────────────────────────────────────────
Requirements Coverage: {gap.coverage_percentage}%
Requirements Met:      {gap.met_requirements}/{gap.total_requirements}
Relevant Experience:   {gap.relevant_experience_count} positions

"""

        # Strengths
        if gap.strengths:
            report += "\n✅ STRENGTHS\n" + "─" * 60 + "\n"
            for i, strength in enumerate(gap.strengths, 1):
                report += f"{i}. {strength}\n"

        # Weaknesses
        if gap.weaknesses:
            report += "\n⚠️  WEAKNESSES\n" + "─" * 60 + "\n"
            for i, weakness in enumerate(gap.weaknesses, 1):
                report += f"{i}. {weakness}\n"

        # Skill Analysis
        report += "\n📊 SKILL ANALYSIS\n" + "─" * 60 + "\n"

        # Matched skills
        strong_matches = [s for s in gap.matched_skills if s.strength == "strong"]
        if strong_matches:
            report += f"\nStrong Matches ({len(strong_matches)}):\n"
            for skill in strong_matches[:10]:  # Top 10
                report += f"  ✓ {skill.skill}\n"

        # Missing required
        if gap.missing_required_skills:
            report += f"\nMissing Required Skills ({len(gap.missing_required_skills)}):\n"
            for skill in gap.missing_required_skills:
                report += f"  ✗ {skill}\n"

        # Weakly covered
        if gap.weakly_covered_skills:
            report += f"\nWeakly Covered Skills ({len(gap.weakly_covered_skills)}):\n"
            for skill_match in gap.weakly_covered_skills[:5]:
                report += f"  ⚡ {skill_match.skill}\n"

        # Suggestions
        if gap.suggestions:
            report += "\n💡 RECOMMENDATIONS\n" + "─" * 60 + "\n"
            for i, suggestion in enumerate(gap.suggestions, 1):
                report += f"{i}. {suggestion}\n"

        report += "\n" + "═" * 60 + "\n"
        report += "End of Report\n"
        report += "═" * 60 + "\n"

        return report

    def load_job_model(self, filename: str = "job_analysis.json") -> Tuple[bool, Optional[JobModel], str]:
        """
        Load JobModel from JSON file.

        Args:
            filename: Input filename

        Returns:
            Tuple of (success, JobModel or None, error_message)
        """
        try:
            file_path = self.output_folder / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            job = JobModel.from_dict(data)
            return True, job, ""
        except Exception as e:
            return False, None, f"Error loading job model: {str(e)}"

    def load_resume_model(self, filename: str = "resume_analysis.json") -> Tuple[bool, Optional[ResumeModel], str]:
        """
        Load ResumeModel from JSON file.

        Args:
            filename: Input filename

        Returns:
            Tuple of (success, ResumeModel or None, error_message)
        """
        try:
            file_path = self.output_folder / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            resume = ResumeModel.from_dict(data)
            return True, resume, ""
        except Exception as e:
            return False, None, f"Error loading resume model: {str(e)}"

    def load_gap_analysis(self, filename: str = "gap_analysis.json") -> Tuple[bool, Optional[GapAnalysis], str]:
        """
        Load GapAnalysis from JSON file.

        Args:
            filename: Input filename

        Returns:
            Tuple of (success, GapAnalysis or None, error_message)
        """
        try:
            file_path = self.output_folder / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            gap = GapAnalysis.from_dict(data)
            return True, gap, ""
        except Exception as e:
            return False, None, f"Error loading gap analysis: {str(e)}"

    def save_optimization_result(
        self,
        result,  # ResumeOptimizationResult
        filename: str = "optimization_result.json"
    ) -> Tuple[bool, str]:
        """
        Save ResumeOptimizationResult to JSON file.

        Args:
            result: ResumeOptimizationResult to save
            filename: Output filename

        Returns:
            Tuple of (success, file_path or error_message)
        """
        try:
            file_path = self.output_folder / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result.to_json())
            return True, str(file_path)
        except Exception as e:
            return False, f"Error saving optimization result: {str(e)}"

    def load_optimization_result(
        self,
        filename: str = "optimization_result.json"
    ) -> Tuple[bool, Optional[any], str]:
        """
        Load ResumeOptimizationResult from JSON file.

        Args:
            filename: Input filename

        Returns:
            Tuple of (success, ResumeOptimizationResult or None, error_message)
        """
        try:
            from modules.models import ResumeOptimizationResult
            file_path = self.output_folder / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            result = ResumeOptimizationResult.from_dict(data)
            return True, result, ""
        except Exception as e:
            return False, None, f"Error loading optimization result: {str(e)}"
