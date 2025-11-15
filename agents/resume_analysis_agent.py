"""AI agent for analyzing resumes and extracting structured data."""

import os
import json
from typing import Tuple, Optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from modules.models import ResumeModel, ExperienceItem, EducationItem
from config.settings import ANTHROPIC_API_KEY, DEFAULT_MODEL


class ResumeAnalysisAgent:
    """Agent for analyzing resumes and extracting structured information."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the resume analysis agent.

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

    def analyze_resume(
        self,
        resume_text: str,
        metadata: Optional[dict] = None
    ) -> Tuple[bool, Optional[ResumeModel], str]:
        """
        Analyze resume and extract structured data.

        Args:
            resume_text: Raw resume text
            metadata: Pre-extracted metadata (email, phone, etc.) (optional)

        Returns:
            Tuple of (success, ResumeModel or None, error_message)
        """
        if not self.client:
            return False, None, "Anthropic API client not available. Please set ANTHROPIC_API_KEY."

        try:
            # Construct the analysis prompt
            prompt = self._build_analysis_prompt(resume_text, metadata)

            # Call Claude API
            response = self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=4000,
                temperature=0,
                system=self._get_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = response.content[0].text

            # Extract JSON from response
            resume_data = self._parse_json_response(response_text)

            if not resume_data:
                return False, None, "Failed to parse resume analysis response"

            # Create ResumeModel from parsed data
            resume_model = self._create_resume_model(resume_data, resume_text, metadata)

            return True, resume_model, ""

        except Exception as e:
            return False, None, f"Error analyzing resume: {str(e)}"

    def _get_system_prompt(self) -> str:
        """Get the system prompt for resume analysis."""
        return """You are an expert resume analyzer. Your task is to extract structured information from resumes.

Analyze the resume carefully and extract:
1. Contact information
2. Professional summary/headline
3. Work experience (with detailed bullet points and skills)
4. Education
5. Skills (technical and soft skills)
6. Certifications, projects, awards, languages if present
7. Estimate total years of experience

Return your analysis as a valid JSON object with the following structure:
{
  "name": "Full name or null",
  "email": "Email or null",
  "phone": "Phone or null",
  "location": "Location or null",
  "linkedin": "LinkedIn URL or null",
  "github": "GitHub URL or null",
  "portfolio": "Portfolio URL or null",
  "headline": "Professional headline/title or null",
  "summary": "Professional summary or null",
  "experiences": [
    {
      "title": "Job title",
      "company": "Company name",
      "start_date": "Start date (e.g., 'Jan 2020')",
      "end_date": "End date or 'Present'",
      "location": "Location or null",
      "bullets": ["Achievement/responsibility bullet points"],
      "skills": ["Skills mentioned or implied in this role"],
      "is_current": true/false
    }
  ],
  "skills": ["List of all technical and relevant skills"],
  "education": [
    {
      "degree": "Degree name",
      "institution": "School name",
      "field_of_study": "Major/field or null",
      "graduation_date": "Graduation date or null",
      "gpa": "GPA or null",
      "honors": ["Honors/awards"],
      "relevant_coursework": ["Relevant courses"]
    }
  ],
  "certifications": ["List of certifications"],
  "projects": [
    {
      "name": "Project name",
      "description": "Description",
      "technologies": ["Tech stack"],
      "url": "Project URL or null"
    }
  ],
  "awards": ["List of awards/recognitions"],
  "languages": ["Languages spoken"],
  "total_years_experience": 5.5
}

Be thorough and accurate. Extract all skills mentioned or implied in experience bullets."""

    def _build_analysis_prompt(
        self,
        resume_text: str,
        metadata: Optional[dict]
    ) -> str:
        """Build the analysis prompt."""
        prompt = "Analyze the following resume and return structured JSON:\n\n"

        if metadata:
            if metadata.get('email'):
                prompt += f"Email (pre-extracted): {metadata['email']}\n"
            if metadata.get('phone'):
                prompt += f"Phone (pre-extracted): {metadata['phone']}\n"

        prompt += f"\nResume Text:\n{resume_text}\n\n"
        prompt += "Return only the JSON object, no additional text."

        return prompt

    def _parse_json_response(self, response_text: str) -> Optional[dict]:
        """Parse JSON from response text."""
        from utils.json_utils import extract_json_object
        return extract_json_object(response_text)

    def _create_resume_model(
        self,
        data: dict,
        raw_text: str,
        metadata: Optional[dict]
    ) -> ResumeModel:
        """Create ResumeModel from parsed data."""
        # Parse experiences
        experiences = []
        for exp in data.get('experiences', []):
            experiences.append(ExperienceItem(
                title=exp.get('title', ''),
                company=exp.get('company', ''),
                start_date=exp.get('start_date'),
                end_date=exp.get('end_date'),
                location=exp.get('location'),
                bullets=exp.get('bullets', []),
                skills=exp.get('skills', []),
                is_current=exp.get('is_current', False)
            ))

        # Parse education
        education = []
        for edu in data.get('education', []):
            education.append(EducationItem(
                degree=edu.get('degree', ''),
                institution=edu.get('institution', ''),
                field_of_study=edu.get('field_of_study'),
                graduation_date=edu.get('graduation_date'),
                gpa=edu.get('gpa'),
                honors=edu.get('honors', []),
                relevant_coursework=edu.get('relevant_coursework', [])
            ))

        # Use metadata as fallback for contact info
        email = data.get('email')
        phone = data.get('phone')
        if metadata:
            email = email or metadata.get('email')
            phone = phone or metadata.get('phone')

        return ResumeModel(
            name=data.get('name'),
            email=email,
            phone=phone,
            location=data.get('location'),
            linkedin=data.get('linkedin'),
            github=data.get('github'),
            portfolio=data.get('portfolio'),
            headline=data.get('headline'),
            summary=data.get('summary'),
            experiences=experiences,
            skills=data.get('skills', []),
            education=education,
            certifications=data.get('certifications', []),
            projects=data.get('projects', []),
            awards=data.get('awards', []),
            languages=data.get('languages', []),
            total_years_experience=data.get('total_years_experience'),
            raw_text=raw_text
        )


# Convenience function
def analyze_resume(
    resume_text: str,
    metadata: Optional[dict] = None,
    api_key: Optional[str] = None
) -> Tuple[bool, Optional[ResumeModel], str]:
    """
    Analyze a resume and extract structured data.

    Args:
        resume_text: Raw resume text
        metadata: Pre-extracted metadata (optional)
        api_key: Anthropic API key (optional)

    Returns:
        Tuple of (success, ResumeModel or None, error_message)
    """
    agent = ResumeAnalysisAgent(api_key=api_key)
    return agent.analyze_resume(resume_text, metadata)
