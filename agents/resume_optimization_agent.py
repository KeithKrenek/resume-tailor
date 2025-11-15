"""AI agent for optimizing resumes based on job requirements and gap analysis."""

import os
import json
import uuid
from typing import Tuple, Optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from modules.models import (
    JobModel, ResumeModel, GapAnalysis,
    ResumeOptimizationResult, ResumeChange, ChangeType
)
from config.settings import ANTHROPIC_API_KEY, DEFAULT_MODEL


class ResumeOptimizationAgent:
    """Agent for optimizing resumes based on job requirements."""

    # Style configurations
    STYLES = {
        'conservative': {
            'temperature': 0.3,
            'description': 'Minimal changes, only obvious improvements',
            'aggressiveness': 'low'
        },
        'balanced': {
            'temperature': 0.5,
            'description': 'Moderate improvements, keyword optimization',
            'aggressiveness': 'medium'
        },
        'aggressive': {
            'temperature': 0.7,
            'description': 'Comprehensive rewrite for maximum match',
            'aggressiveness': 'high'
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the optimization agent.

        Args:
            api_key: Anthropic API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or ANTHROPIC_API_KEY or os.getenv('ANTHROPIC_API_KEY')
        self.client = None

        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")

    def optimize_resume(
        self,
        job: JobModel,
        resume: ResumeModel,
        gap: GapAnalysis,
        style: str = "balanced"
    ) -> Tuple[bool, Optional[ResumeOptimizationResult], str]:
        """
        Optimize resume based on job requirements and gap analysis.

        Args:
            job: JobModel with job requirements
            resume: Current ResumeModel to optimize
            gap: GapAnalysis showing what's missing
            style: Optimization style ("conservative", "balanced", "aggressive")

        Returns:
            Tuple of (success, ResumeOptimizationResult or None, error_message)
        """
        if not self.client:
            return False, None, "Anthropic API client not available. Please set ANTHROPIC_API_KEY."

        if style not in self.STYLES:
            return False, None, f"Invalid style: {style}. Choose from: {list(self.STYLES.keys())}"

        try:
            # Get style configuration
            style_config = self.STYLES[style]

            # Build optimization prompt
            prompt = self._build_optimization_prompt(job, resume, gap, style_config)

            # Call Claude API
            response = self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=6000,
                temperature=style_config['temperature'],
                system=self._get_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = response.content[0].text

            # Extract JSON from response
            optimization_data = self._parse_json_response(response_text)

            if not optimization_data:
                return False, None, "Failed to parse optimization response"

            # Create ResumeOptimizationResult
            result = self._create_optimization_result(
                original_resume=resume,
                optimization_data=optimization_data,
                style=style
            )

            return True, result, ""

        except Exception as e:
            return False, None, f"Error optimizing resume: {str(e)}"

    def _get_system_prompt(self) -> str:
        """Get the system prompt for resume optimization."""
        return """You are an expert resume optimization specialist. Your task is to improve resumes to better match job requirements while maintaining truthfulness and ATS compatibility.

CRITICAL RULES:
1. NEVER invent experience, skills, or qualifications the candidate doesn't have
2. ONLY rephrase, clarify, and emphasize what's already present in the resume
3. Add quantification ONLY where plausible given existing context
4. Keep language simple, clear, and keyword-rich for ATS systems
5. Maintain the original structure and order of experiences

Your optimization should:
- Align the summary/headline with the target job
- Rewrite experience bullets to highlight relevant skills
- Incorporate missing keywords naturally where they truly apply
- Add quantification to achievements where appropriate
- Use action verbs and concrete language
- Optimize for both human readers and ATS systems

Return a JSON object with:
{
  "optimized_resume": {
    // Complete ResumeModel with improved text
    "name": "...",
    "email": "...",
    "summary": "IMPROVED professional summary",
    "headline": "IMPROVED headline",
    "experiences": [
      {
        "title": "...",
        "company": "...",
        "bullets": ["IMPROVED bullet 1", "IMPROVED bullet 2"],
        "skills": ["skill1", "skill2"]  // Add missing skills if truly applicable
      }
    ],
    "skills": ["updated", "skills", "list"],
    // ... rest of resume fields
  },
  "changes": [
    {
      "id": "uuid",
      "change_type": "summary|headline|experience_bullet|skills_section|education|other",
      "location": "summary" or "experiences[0].bullets[1]",
      "before": "original text",
      "after": "optimized text",
      "rationale": "Why this change improves the resume"
    }
  ],
  "summary_of_improvements": [
    "High-level improvement 1",
    "High-level improvement 2"
  ]
}"""

    def _build_optimization_prompt(
        self,
        job: JobModel,
        resume: ResumeModel,
        gap: GapAnalysis,
        style_config: dict
    ) -> str:
        """Build the optimization prompt."""
        prompt = f"""Optimize this resume for the target job.

OPTIMIZATION STYLE: {style_config['description']}
AGGRESSIVENESS: {style_config['aggressiveness']}

TARGET JOB:
-----------
Title: {job.title}
Company: {job.company or 'N/A'}
Level: {job.experience_level or 'N/A'}

Required Skills: {', '.join(job.required_skills[:10])}
Preferred Skills: {', '.join(job.preferred_skills[:5])}

Key Requirements:
"""
        # Add top requirements
        for req in job.requirements[:8]:
            prompt += f"- {req.description}\n"

        prompt += f"\nGAP ANALYSIS:\n-----------\n"
        prompt += f"Coverage: {gap.coverage_percentage}%\n"
        prompt += f"Missing Required Skills: {', '.join(gap.missing_required_skills[:5])}\n"
        prompt += f"Weakly Covered Skills: {', '.join([s.skill for s in gap.weakly_covered_skills[:5]])}\n"

        if gap.suggestions:
            prompt += f"\nTop Suggestions:\n"
            for suggestion in gap.suggestions[:3]:
                prompt += f"- {suggestion}\n"

        prompt += f"\nCURRENT RESUME:\n-----------\n"
        prompt += f"Name: {resume.name}\n"
        prompt += f"Current Summary: {resume.summary or 'None'}\n"
        prompt += f"Current Headline: {resume.headline or 'None'}\n\n"

        prompt += "Experiences:\n"
        for i, exp in enumerate(resume.experiences[:3]):  # Top 3 experiences
            prompt += f"\n{i+1}. {exp.title} at {exp.company}\n"
            for bullet in exp.bullets[:5]:  # Top 5 bullets
                prompt += f"   - {bullet}\n"
            if exp.skills:
                prompt += f"   Skills: {', '.join(exp.skills[:8])}\n"

        prompt += f"\nCurrent Skills: {', '.join(resume.skills[:15])}\n"

        if resume.education:
            prompt += f"\nEducation:\n"
            for edu in resume.education[:2]:
                prompt += f"- {edu.degree} from {edu.institution}\n"

        prompt += "\n\nINSTRUCTIONS:\n"
        prompt += "Optimize this resume to better match the target job. Return ONLY the JSON object with no additional text."

        return prompt

    def _parse_json_response(self, response_text: str) -> Optional[dict]:
        """Parse JSON from response text."""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                return None

            json_text = response_text[start_idx:end_idx]
            return json.loads(json_text)

        except json.JSONDecodeError:
            return None

    def _create_optimization_result(
        self,
        original_resume: ResumeModel,
        optimization_data: dict,
        style: str
    ) -> ResumeOptimizationResult:
        """Create ResumeOptimizationResult from parsed data."""
        # Parse optimized resume
        optimized_resume = ResumeModel.from_dict(optimization_data['optimized_resume'])

        # Parse changes
        changes = []
        for change_data in optimization_data.get('changes', []):
            # Ensure id exists
            if 'id' not in change_data:
                change_data['id'] = str(uuid.uuid4())

            changes.append(ResumeChange(
                id=change_data['id'],
                change_type=ChangeType(change_data['change_type']),
                location=change_data['location'],
                before=change_data['before'],
                after=change_data['after'],
                rationale=change_data['rationale']
            ))

        return ResumeOptimizationResult(
            original_resume=original_resume,
            optimized_resume=optimized_resume,
            changes=changes,
            summary_of_improvements=optimization_data.get('summary_of_improvements', []),
            style_used=style
        )


# Convenience function
def optimize_resume(
    job: JobModel,
    resume: ResumeModel,
    gap: GapAnalysis,
    style: str = "balanced",
    api_key: Optional[str] = None
) -> Tuple[bool, Optional[ResumeOptimizationResult], str]:
    """
    Optimize a resume for a specific job.

    Args:
        job: JobModel with job requirements
        resume: Current ResumeModel to optimize
        gap: GapAnalysis showing what's missing
        style: Optimization style ("conservative", "balanced", "aggressive")
        api_key: Anthropic API key (optional)

    Returns:
        Tuple of (success, ResumeOptimizationResult or None, error_message)
    """
    agent = ResumeOptimizationAgent(api_key=api_key)
    return agent.optimize_resume(job, resume, gap, style)
