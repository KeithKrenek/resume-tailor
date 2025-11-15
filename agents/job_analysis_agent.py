"""AI agent for analyzing job postings and extracting structured data."""

import os
import json
from typing import Tuple, Optional
from utils.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available")

from modules.models import JobModel, JobRequirement
from config.settings import ANTHROPIC_API_KEY, DEFAULT_MODEL


class JobAnalysisAgent:
    """Agent for analyzing job postings and extracting structured information."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the job analysis agent.

        Args:
            api_key: Anthropic API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or ANTHROPIC_API_KEY or os.getenv('ANTHROPIC_API_KEY')
        self.client = None

        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Could not initialize Anthropic client: {e}")
                self.client = None

    def analyze_job(
        self,
        job_description: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> Tuple[bool, Optional[JobModel], str]:
        """
        Analyze job description and extract structured data.

        Args:
            job_description: Raw job description text
            job_title: Pre-extracted job title (optional)
            company_name: Pre-extracted company name (optional)

        Returns:
            Tuple of (success, JobModel or None, error_message)
        """
        if not self.client:
            error_msg = "Anthropic API client not available. Please set ANTHROPIC_API_KEY."
            logger.error(error_msg)
            return False, None, error_msg

        try:
            logger.info(f"Starting job analysis (title={job_title}, company={company_name})")

            # Construct the analysis prompt
            prompt = self._build_analysis_prompt(job_description, job_title, company_name)
            logger.debug(f"Built analysis prompt ({len(prompt)} chars)")

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
            logger.debug(f"Received API response ({len(response_text)} chars)")

            # Extract JSON from response
            job_data = self._parse_json_response(response_text)

            if not job_data:
                logger.error("Failed to parse job analysis response - no valid JSON found")
                logger.debug(f"Response preview: {response_text[:200]}...")
                return False, None, "Failed to parse job analysis response"

            # Create JobModel from parsed data
            job_model = self._create_job_model(job_data, job_description)
            logger.info(f"Job analysis complete: {job_model.title} at {job_model.company or 'Unknown'}")

            return True, job_model, ""

        except Exception as e:
            logger.exception("Error analyzing job")
            return False, None, f"Error analyzing job: {str(e)}"

    def _get_system_prompt(self) -> str:
        """Get the system prompt for job analysis."""
        return """You are an expert job posting analyzer. Your task is to extract structured information from job descriptions.

Analyze the job posting carefully and extract:
1. Job title and basic information
2. Responsibilities and duties
3. Requirements (both required and preferred)
4. Skills (technical and soft skills)
5. Experience level requirements
6. Any other relevant information

Return your analysis as a valid JSON object with the following structure:
{
  "title": "Job title",
  "company": "Company name or null",
  "location": "Location or null",
  "job_type": "Full-time/Part-time/Contract/etc or null",
  "experience_level": "Entry/Mid/Senior/etc or null",
  "salary_range": "Salary range or null",
  "description": "Brief job description",
  "responsibilities": ["List of responsibilities"],
  "requirements": [
    {
      "description": "Requirement description",
      "category": "Required Skill|Preferred Skill|Responsibility|Qualification|Education|Experience",
      "is_must_have": true/false,
      "keywords": ["relevant", "keywords"]
    }
  ],
  "nice_to_haves": ["List of preferred but not required items"],
  "required_skills": ["List of must-have skills"],
  "preferred_skills": ["List of nice-to-have skills"],
  "benefits": ["List of benefits if mentioned"],
  "company_description": "Company description if provided"
}

Be thorough and accurate. Extract all relevant information."""

    def _build_analysis_prompt(
        self,
        job_description: str,
        job_title: Optional[str],
        company_name: Optional[str]
    ) -> str:
        """Build the analysis prompt."""
        prompt = "Analyze the following job posting and return structured JSON:\n\n"

        if job_title:
            prompt += f"Job Title: {job_title}\n"
        if company_name:
            prompt += f"Company: {company_name}\n"

        prompt += f"\nJob Description:\n{job_description}\n\n"
        prompt += "Return only the JSON object, no additional text."

        return prompt

    def _parse_json_response(self, response_text: str) -> Optional[dict]:
        """Parse JSON from response text."""
        from utils.json_utils import extract_json_object
        return extract_json_object(response_text)

    def _create_job_model(self, data: dict, raw_text: str) -> JobModel:
        """Create JobModel from parsed data."""
        # Parse requirements
        requirements = []
        for req in data.get('requirements', []):
            requirements.append(JobRequirement(
                description=req.get('description', ''),
                category=req.get('category', 'Requirement'),
                is_must_have=req.get('is_must_have', True),
                keywords=req.get('keywords', [])
            ))

        return JobModel(
            title=data.get('title', 'Unknown Position'),
            company=data.get('company'),
            location=data.get('location'),
            job_type=data.get('job_type'),
            experience_level=data.get('experience_level'),
            salary_range=data.get('salary_range'),
            description=data.get('description'),
            responsibilities=data.get('responsibilities', []),
            requirements=requirements,
            nice_to_haves=data.get('nice_to_haves', []),
            required_skills=data.get('required_skills', []),
            preferred_skills=data.get('preferred_skills', []),
            benefits=data.get('benefits', []),
            company_description=data.get('company_description'),
            raw_text=raw_text
        )


# Convenience function
def analyze_job_posting(
    job_description: str,
    job_title: Optional[str] = None,
    company_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> Tuple[bool, Optional[JobModel], str]:
    """
    Analyze a job posting and extract structured data.

    Args:
        job_description: Raw job description text
        job_title: Pre-extracted job title (optional)
        company_name: Pre-extracted company name (optional)
        api_key: Anthropic API key (optional)

    Returns:
        Tuple of (success, JobModel or None, error_message)
    """
    agent = JobAnalysisAgent(api_key=api_key)
    return agent.analyze_job(job_description, job_title, company_name)
