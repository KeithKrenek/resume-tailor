"""AI agent for extracting company name and job title from job descriptions."""

import os
from typing import Tuple, Dict, Optional
import re

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from config.settings import ANTHROPIC_API_KEY, DEFAULT_MODEL


class ExtractionAgent:
    """Agent for extracting structured information from job postings."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the extraction agent.

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

    def extract_company_and_title(
        self,
        job_description: str,
        job_url: str = "",
        scraped_data: Optional[Dict] = None
    ) -> Tuple[bool, str, str, str]:
        """
        Extract company name and job title from job description.

        Args:
            job_description: Job description text
            job_url: Job posting URL (optional)
            scraped_data: Previously scraped data (optional)

        Returns:
            Tuple of (success, company_name, job_title, error_message)
        """
        # First try to get from scraped data if available
        if scraped_data:
            company = scraped_data.get('company', '').strip()
            title = scraped_data.get('title', '').strip()
            if company and title:
                return True, company, title, ""

        # Try rule-based extraction first (faster, no API needed)
        company, title = self._rule_based_extraction(job_description, job_url)

        if company and title:
            return True, company, title, ""

        # Fall back to AI extraction if available
        if self.client:
            return self._ai_extraction(job_description, job_url)
        else:
            # If no AI available, return what we have or empty
            return True, company or "Unknown Company", title or "Unknown Position", ""

    def _rule_based_extraction(self, job_description: str, job_url: str = "") -> Tuple[str, str]:
        """
        Extract company and title using regex patterns.

        Args:
            job_description: Job description text
            job_url: Job posting URL

        Returns:
            Tuple of (company_name, job_title)
        """
        company = ""
        title = ""

        # Common patterns for job titles at the start of description
        title_patterns = [
            r'^([A-Z][A-Za-z\s&,\-/]+(?:Engineer|Developer|Manager|Analyst|Specialist|Director|Lead|Architect|Designer|Consultant|Coordinator))',
            r'(?:Job Title|Position|Role):\s*([A-Z][A-Za-z\s&,\-/]+)',
            r'(?:We are looking for|Seeking|Hiring)\s+an?\s+([A-Z][A-Za-z\s&,\-/]+?)(?:\s+to|\s+who|\s+with)',
        ]

        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.MULTILINE | re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                break

        # Common patterns for company names
        company_patterns = [
            r'(?:Company|Organization|About Us):\s*([A-Z][A-Za-z\s&,\.]+?)(?:\n|\s{2,})',
            r'([A-Z][A-Za-z\s&,\.]+?)\s+is (?:seeking|looking for|hiring)',
            r'^([A-Z][A-Za-z\s&,\.]+?)\s+(?:Job Description|Position|Role)',
        ]

        for pattern in company_patterns:
            match = re.search(pattern, job_description, re.MULTILINE)
            if match:
                company = match.group(1).strip()
                # Clean up common false positives
                if len(company) > 50 or company.lower() in ['the', 'we', 'our']:
                    company = ""
                    continue
                break

        # Try to extract from URL if company not found
        if not company and job_url:
            company = self._extract_company_from_url(job_url)

        return company, title

    def _extract_company_from_url(self, url: str) -> str:
        """
        Extract company name from URL.

        Args:
            url: Job posting URL

        Returns:
            Company name or empty string
        """
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            domain = domain.replace('www.', '')

            # Skip job boards
            job_boards = ['linkedin', 'indeed', 'glassdoor', 'monster', 'ziprecruiter', 'greenhouse', 'lever']
            if any(board in domain.lower() for board in job_boards):
                return ""

            # Get company name from domain
            company = domain.split('.')[0]
            return company.capitalize()
        except:
            return ""

    def _ai_extraction(self, job_description: str, job_url: str = "") -> Tuple[bool, str, str, str]:
        """
        Extract company and title using AI.

        Args:
            job_description: Job description text
            job_url: Job posting URL

        Returns:
            Tuple of (success, company_name, job_title, error_message)
        """
        try:
            # Truncate description if too long (keep first 3000 chars)
            truncated_desc = job_description[:3000]

            prompt = f"""Extract the company name and job title from the following job posting.

Job URL: {job_url if job_url else 'Not provided'}

Job Description:
{truncated_desc}

Please respond in the following format EXACTLY:
COMPANY: [company name]
TITLE: [job title]

If you cannot find the information, use "Unknown Company" or "Unknown Position"."""

            response = self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=200,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = response.content[0].text

            company_match = re.search(r'COMPANY:\s*(.+)', response_text)
            title_match = re.search(r'TITLE:\s*(.+)', response_text)

            company = company_match.group(1).strip() if company_match else "Unknown Company"
            title = title_match.group(1).strip() if title_match else "Unknown Position"

            return True, company, title, ""

        except Exception as e:
            return False, "", "", f"AI extraction error: {str(e)}"


# Convenience function
def extract_job_info(
    job_description: str,
    job_url: str = "",
    scraped_data: Optional[Dict] = None,
    api_key: Optional[str] = None
) -> Tuple[bool, str, str, str]:
    """
    Extract company name and job title from job posting.

    Args:
        job_description: Job description text
        job_url: Job posting URL (optional)
        scraped_data: Previously scraped data (optional)
        api_key: Anthropic API key (optional)

    Returns:
        Tuple of (success, company_name, job_title, error_message)
    """
    agent = ExtractionAgent(api_key=api_key)
    return agent.extract_company_and_title(job_description, job_url, scraped_data)
