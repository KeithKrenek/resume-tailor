"""
Company and Industry Research Agent

Uses LLM with web search capabilities to gather intelligence about
companies and industries to enhance resume optimization.
"""

import os
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass, field
from utils.logging_config import get_logger

logger = get_logger(__name__)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available")

from config.settings import ANTHROPIC_API_KEY


@dataclass
class CompanyResearch:
    """Company research results."""
    company_name: str
    industry: str = ""
    company_size: str = ""
    headquarters: str = ""

    # Culture and values
    mission_statement: str = ""
    core_values: List[str] = field(default_factory=list)
    company_culture: str = ""

    # Recent news and initiatives
    recent_news: List[str] = field(default_factory=list)
    key_initiatives: List[str] = field(default_factory=list)
    products_services: List[str] = field(default_factory=list)

    # Keywords and terminology
    company_keywords: List[str] = field(default_factory=list)
    industry_keywords: List[str] = field(default_factory=list)

    # Leadership
    key_executives: List[Dict[str, str]] = field(default_factory=list)

    # Optimization insights
    optimization_insights: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        """Get a text summary of the research."""
        parts = []

        if self.industry:
            parts.append(f"Industry: {self.industry}")

        if self.company_culture:
            parts.append(f"Culture: {self.company_culture}")

        if self.core_values:
            parts.append(f"Values: {', '.join(self.core_values[:3])}")

        if self.recent_news:
            parts.append(f"Recent Focus: {self.recent_news[0][:100]}...")

        return " | ".join(parts) if parts else "No research available"


@dataclass
class IndustryResearch:
    """Industry research results."""
    industry_name: str

    # Industry overview
    description: str = ""
    market_size: str = ""
    growth_rate: str = ""

    # Trends and technologies
    key_trends: List[str] = field(default_factory=list)
    emerging_technologies: List[str] = field(default_factory=list)
    hot_skills: List[str] = field(default_factory=list)

    # Industry challenges
    challenges: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)

    # Career insights
    common_roles: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)

    # Keywords
    industry_keywords: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        """Get a text summary of the research."""
        parts = []

        if self.description:
            parts.append(self.description[:150])

        if self.key_trends:
            parts.append(f"Trends: {', '.join(self.key_trends[:3])}")

        if self.hot_skills:
            parts.append(f"In-Demand Skills: {', '.join(self.hot_skills[:3])}")

        return " | ".join(parts) if parts else "No research available"


class ResearchAgent:
    """Agent for conducting company and industry research using LLM with web search."""

    def __init__(self, api_key: Optional[str] = None, enable_web_search: bool = True):
        """
        Initialize the research agent.

        Args:
            api_key: Anthropic API key
            enable_web_search: Whether to enable web search (requires compatible environment)
        """
        self.api_key = api_key or ANTHROPIC_API_KEY or os.getenv('ANTHROPIC_API_KEY')
        self.enable_web_search = enable_web_search
        self.client = None

        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("Research agent initialized successfully")
            except Exception as e:
                logger.error(f"Could not initialize Anthropic client: {e}")
                self.client = None

    def research_company(
        self,
        company_name: str,
        company_url: Optional[str] = None,
        use_web_search: bool = True
    ) -> Tuple[bool, Optional[CompanyResearch], str]:
        """
        Research a company using LLM with optional web search.

        Args:
            company_name: Name of the company
            company_url: Optional company website URL
            use_web_search: Whether to use web search (if available)

        Returns:
            Tuple of (success, CompanyResearch or None, error_message)
        """
        if not self.client:
            error_msg = "Anthropic API client not available"
            logger.error(error_msg)
            return False, None, error_msg

        try:
            logger.info(f"Researching company: {company_name}")

            # Build research prompt
            prompt = self._build_company_research_prompt(company_name, company_url)

            # Note: In the current implementation, we're using the LLM's knowledge base
            # In a production environment with web search tools enabled, you would
            # use the web search functionality here

            # For now, we'll use the LLM's existing knowledge
            # Future enhancement: Integrate with Claude's web search tools when available

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,
                system=self._get_company_research_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text
            logger.debug(f"Received company research ({len(response_text)} chars)")

            # Parse the response
            research = self._parse_company_research(company_name, response_text)

            logger.info(f"Company research complete for {company_name}")
            return True, research, ""

        except Exception as e:
            logger.exception("Error researching company")
            return False, None, f"Error researching company: {str(e)}"

    def research_industry(
        self,
        industry_name: str,
        use_web_search: bool = True
    ) -> Tuple[bool, Optional[IndustryResearch], str]:
        """
        Research an industry using LLM with optional web search.

        Args:
            industry_name: Name of the industry
            use_web_search: Whether to use web search (if available)

        Returns:
            Tuple of (success, IndustryResearch or None, error_message)
        """
        if not self.client:
            error_msg = "Anthropic API client not available"
            logger.error(error_msg)
            return False, None, error_msg

        try:
            logger.info(f"Researching industry: {industry_name}")

            prompt = self._build_industry_research_prompt(industry_name)

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,
                system=self._get_industry_research_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text
            logger.debug(f"Received industry research ({len(response_text)} chars)")

            # Parse the response
            research = self._parse_industry_research(industry_name, response_text)

            logger.info(f"Industry research complete for {industry_name}")
            return True, research, ""

        except Exception as e:
            logger.exception("Error researching industry")
            return False, None, f"Error researching industry: {str(e)}"

    def _build_company_research_prompt(
        self,
        company_name: str,
        company_url: Optional[str]
    ) -> str:
        """Build the company research prompt."""
        prompt = f"""Research the following company and provide comprehensive intelligence for resume optimization:

Company Name: {company_name}
"""

        if company_url:
            prompt += f"Company Website: {company_url}\n"

        prompt += """
Please provide:

1. **Company Overview**
   - Industry and sector
   - Company size and scale
   - Headquarters location

2. **Culture and Values**
   - Mission statement
   - Core values (list up to 5)
   - Company culture description

3. **Recent News and Initiatives**
   - Recent news or press releases (last 6 months)
   - Key initiatives or projects
   - Main products or services

4. **Keywords and Terminology**
   - Company-specific keywords for resume optimization
   - Industry-specific terminology they use

5. **Leadership**
   - Key executives (if publicly known)

6. **Optimization Insights**
   - How should a candidate tailor their resume for this company?
   - What values or qualities does this company emphasize?
   - What keywords should be incorporated?

Provide detailed, actionable information that would help a job candidate optimize their resume.
"""

        return prompt

    def _build_industry_research_prompt(self, industry_name: str) -> str:
        """Build the industry research prompt."""
        return f"""Research the following industry and provide comprehensive intelligence:

Industry: {industry_name}

Please provide:

1. **Industry Overview**
   - Brief description
   - Market size (if known)
   - Growth rate and trends

2. **Key Trends and Technologies**
   - Current trends shaping the industry
   - Emerging technologies
   - Hot skills in demand

3. **Challenges and Opportunities**
   - Main challenges facing the industry
   - Growth opportunities

4. **Career Insights**
   - Common job roles in this industry
   - Valuable certifications or credentials
   - Typical career progression

5. **Industry Keywords**
   - Important terminology and keywords
   - Buzzwords commonly used in this field

Provide actionable insights for someone applying to jobs in this industry.
"""

    def _get_company_research_system_prompt(self) -> str:
        """Get system prompt for company research."""
        return """You are an expert business researcher specializing in company intelligence for job seekers.

Your role is to provide comprehensive, accurate information about companies that will help candidates optimize their resumes and prepare for applications.

Guidelines:
- Provide factual, verifiable information
- Focus on publicly available information
- Highlight aspects relevant to job applications
- Include keywords that candidates should use
- Be concise but thorough
- If you're not certain about specific facts, indicate this

Return information in a clear, structured format that's easy to parse and use."""

    def _get_industry_research_system_prompt(self) -> str:
        """Get system prompt for industry research."""
        return """You are an expert industry analyst specializing in career development and job market trends.

Your role is to provide comprehensive information about industries that will help job seekers understand the landscape and optimize their applications.

Guidelines:
- Provide current, relevant information
- Focus on practical career insights
- Highlight in-demand skills and trends
- Include industry-specific terminology
- Be actionable and specific
- Indicate when information may be rapidly changing

Return information in a clear, structured format."""

    def _parse_company_research(self, company_name: str, response: str) -> CompanyResearch:
        """
        Parse company research response into structured format.

        This is a basic implementation that extracts key information.
        In production, you might use more sophisticated parsing or structured outputs.
        """
        research = CompanyResearch(company_name=company_name)

        # Extract sections using simple text processing
        # This is a simplified version - in production, you'd use more robust parsing

        # Look for industry
        if "industry:" in response.lower():
            lines = response.split('\n')
            for line in lines:
                if "industry:" in line.lower():
                    research.industry = line.split(':', 1)[1].strip()
                    break

        # Extract values (look for bullet points or lists)
        values = []
        in_values_section = False
        lines = response.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Detect values section
            if 'core values' in line_lower or 'values:' in line_lower:
                in_values_section = True
                continue

            # Detect end of values section
            if in_values_section and (line_lower.startswith('##') or line_lower.startswith('**')):
                in_values_section = False

            # Extract values
            if in_values_section:
                # Look for bullet points or numbered lists
                if line.strip().startswith(('-', '*', '•')) or (len(line) > 2 and line.strip()[0].isdigit() and line.strip()[1] == '.'):
                    value = line.strip().lstrip('-*•0123456789. ').strip()
                    if value and len(value) > 2:
                        values.append(value)

        research.core_values = values[:5]  # Limit to 5

        # Extract keywords
        keywords = []
        if "keywords" in response.lower():
            # Simple extraction - look for comma-separated lists
            keyword_section = False
            for line in lines:
                if "keywords" in line.lower() and ":" in line:
                    keyword_section = True
                    # Try to extract from same line
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        potential_keywords = [k.strip() for k in parts[1].split(',')]
                        keywords.extend([k for k in potential_keywords if k and len(k) > 2])
                elif keyword_section:
                    if line.strip() and not line.strip().startswith(('##', '**', '#')):
                        potential_keywords = [k.strip() for k in line.split(',')]
                        keywords.extend([k for k in potential_keywords if k and len(k) > 2])
                    else:
                        keyword_section = False

        research.company_keywords = keywords[:10]  # Limit to 10

        # Store the full response as culture description (simplified)
        research.company_culture = response[:500]  # First 500 chars as summary

        # Generate optimization insights from the response
        if "optimization" in response.lower() or "resume" in response.lower():
            insights = []
            for line in lines:
                if any(keyword in line.lower() for keyword in ['should', 'focus', 'emphasize', 'include', 'highlight']):
                    clean_line = line.strip().lstrip('-*•0123456789. ')
                    if clean_line and len(clean_line) > 10:
                        insights.append(clean_line)
            research.optimization_insights = insights[:5]

        return research

    def _parse_industry_research(self, industry_name: str, response: str) -> IndustryResearch:
        """Parse industry research response into structured format."""
        research = IndustryResearch(industry_name=industry_name)

        lines = response.split('\n')

        # Extract description (usually in first paragraph)
        paragraphs = response.split('\n\n')
        if paragraphs:
            research.description = paragraphs[0].strip()[:300]

        # Extract trends
        trends = []
        in_trends = False

        for line in lines:
            line_lower = line.lower()

            if 'trends' in line_lower or 'emerging' in line_lower:
                in_trends = True
                continue

            if in_trends:
                if line.strip().startswith(('##', '**', '#')) and 'trends' not in line_lower:
                    in_trends = False
                elif line.strip().startswith(('-', '*', '•')) or (len(line.strip()) > 2 and line.strip()[0].isdigit()):
                    trend = line.strip().lstrip('-*•0123456789. ').strip()
                    if trend and len(trend) > 5:
                        trends.append(trend)

        research.key_trends = trends[:5]

        # Extract hot skills
        skills = []
        in_skills = False

        for line in lines:
            line_lower = line.lower()

            if 'skills' in line_lower or 'technologies' in line_lower:
                in_skills = True
                continue

            if in_skills:
                if line.strip().startswith(('##', '**', '#')) and 'skill' not in line_lower:
                    in_skills = False
                elif line.strip().startswith(('-', '*', '•')) or (len(line.strip()) > 2 and line.strip()[0].isdigit()):
                    skill = line.strip().lstrip('-*•0123456789. ').strip()
                    if skill and len(skill) > 2:
                        skills.append(skill)

        research.hot_skills = skills[:10]

        # Extract keywords (similar to company research)
        keywords = []
        for line in lines:
            if "keywords" in line.lower() or "terminology" in line.lower():
                # Extract comma-separated values
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        potential_keywords = [k.strip() for k in parts[1].split(',')]
                        keywords.extend([k for k in potential_keywords if k and len(k) > 2])

        research.industry_keywords = keywords[:15]

        return research


# Convenience functions
def research_company(
    company_name: str,
    company_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> Tuple[bool, Optional[CompanyResearch], str]:
    """Research a company."""
    agent = ResearchAgent(api_key=api_key)
    return agent.research_company(company_name, company_url)


def research_industry(
    industry_name: str,
    api_key: Optional[str] = None
) -> Tuple[bool, Optional[IndustryResearch], str]:
    """Research an industry."""
    agent = ResearchAgent(api_key=api_key)
    return agent.research_industry(industry_name)
