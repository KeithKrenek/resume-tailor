"""Agent for improving individual resume sections."""

import os
from typing import Tuple, Optional
from anthropic import Anthropic
from utils.logging_config import get_logger

logger = get_logger(__name__)


def improve_section(
    section_type: str,
    current_text: str,
    job_context: Optional[str] = None,
    improvement_focus: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514"
) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    Improve a specific resume section with AI assistance.

    Args:
        section_type: Type of section (e.g., "summary", "bullet", "headline", "skills")
        current_text: Current text to improve
        job_context: Optional job description for context
        improvement_focus: Optional specific improvement focus (e.g., "make more quantitative", "add keywords")
        api_key: Anthropic API key (optional)
        model: Model to use for improvement

    Returns:
        Tuple of (success, improved_text, rationale, error_message)
    """
    try:
        # Get API key
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            return False, None, None, "No API key available"

        # Initialize client
        client = Anthropic(api_key=key)

        # Build prompt based on section type
        prompt = build_improvement_prompt(
            section_type=section_type,
            current_text=current_text,
            job_context=job_context,
            improvement_focus=improvement_focus
        )

        # Call API
        logger.info(f"Requesting improvement for {section_type} section via {model}")
        message = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract response
        if message.content and len(message.content) > 0:
            response_text = message.content[0].text.strip()

            # Parse response (expected format: IMPROVED_TEXT\n---RATIONALE---\nrationale)
            if "---RATIONALE---" in response_text:
                parts = response_text.split("---RATIONALE---")
                improved_text = parts[0].strip()
                rationale = parts[1].strip() if len(parts) > 1 else "Improved for clarity and impact"
            else:
                improved_text = response_text
                rationale = "Improved based on best practices"

            logger.info(f"Section improvement successful for {section_type}")
            return True, improved_text, rationale, ""
        else:
            logger.error("Empty response from API")
            return False, None, None, "Empty response from API"

    except Exception as e:
        logger.error(f"Section improvement failed: {str(e)}", exc_info=True)
        return False, None, None, str(e)


def build_improvement_prompt(
    section_type: str,
    current_text: str,
    job_context: Optional[str] = None,
    improvement_focus: Optional[str] = None
) -> str:
    """
    Build a prompt for improving a specific section.

    Args:
        section_type: Type of section
        current_text: Current text
        job_context: Optional job context
        improvement_focus: Optional improvement focus

    Returns:
        Formatted prompt string
    """
    # Base instructions by section type
    section_instructions = {
        "summary": """Improve this professional summary to be:
- Concise and impactful (2-3 sentences)
- Highlight key strengths and value proposition
- Use strong action words
- Include relevant keywords""",

        "headline": """Improve this professional headline to be:
- Clear and specific about role/expertise
- Compelling and memorable
- Include key skills or achievements
- Brief (one line)""",

        "bullet": """Improve this experience bullet point to be:
- Start with a strong action verb
- Include quantifiable results/metrics where possible
- Show impact and value delivered
- Be specific and concrete
- Use professional resume language""",

        "skills": """Improve this skills section to be:
- Organized and well-structured
- Include both technical and soft skills
- Prioritize most relevant skills first
- Use industry-standard terminology
- Remove redundant or outdated skills""",

        "education": """Improve this education entry to be:
- Clear and professionally formatted
- Highlight relevant coursework or achievements
- Include GPA if impressive (>3.5)
- Mention honors or distinctions"""
    }

    instructions = section_instructions.get(section_type, "Improve this text to be more professional and impactful")

    prompt = f"""You are a professional resume writer helping improve a specific section of a resume.

**Section Type:** {section_type}

**Current Text:**
{current_text}
"""

    if job_context:
        prompt += f"""
**Job Context (for relevance):**
{job_context[:500]}...
"""

    if improvement_focus:
        prompt += f"""
**Specific Focus:**
{improvement_focus}
"""

    prompt += f"""

**Your Task:**
{instructions}

**Important Guidelines:**
1. DO NOT fabricate new information, metrics, or accomplishments
2. Only enhance clarity, impact, and professionalism of EXISTING information
3. Maintain truthfulness - improve presentation, not facts
4. Keep the same basic meaning and substance
5. Ensure the improvement is realistic and believable

**Response Format:**
Provide your improved version, then on a new line write "---RATIONALE---" and explain briefly (1-2 sentences) what you improved and why.

**Example:**
Led cross-functional team of 8 engineers to deliver cloud migration project 2 weeks ahead of schedule, reducing infrastructure costs by 30%
---RATIONALE---
Added quantitative metrics (team size, timeline, cost reduction) and strengthened action verb from "managed" to "led" for greater impact.

Now improve the text:"""

    return prompt


def suggest_improvements(
    section_type: str,
    current_text: str,
    job_context: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514"
) -> Tuple[bool, Optional[list], str]:
    """
    Get AI suggestions for improving a section without actually rewriting it.

    Args:
        section_type: Type of section
        current_text: Current text
        job_context: Optional job context
        api_key: Anthropic API key
        model: Model to use

    Returns:
        Tuple of (success, suggestions_list, error_message)
    """
    try:
        # Get API key
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            return False, None, "No API key available"

        # Initialize client
        client = Anthropic(api_key=key)

        # Build prompt
        prompt = f"""You are a professional resume writer providing suggestions for improvement.

**Section Type:** {section_type}
**Current Text:**
{current_text}

{"**Job Context:** " + job_context[:300] + "..." if job_context else ""}

**Your Task:**
Provide 3-5 specific, actionable suggestions for improving this text. Focus on:
- Adding quantifiable metrics
- Strengthening action verbs
- Improving clarity and impact
- Aligning with job requirements (if context provided)
- Professional language and formatting

**Response Format:**
Return ONLY a JSON array of suggestions, each as a string. Example:
["Add specific metrics (e.g., team size, timeline, cost savings)", "Start with a stronger action verb like 'spearheaded' or 'orchestrated'", "Mention specific technologies or tools used"]

Suggestions:"""

        # Call API
        message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        if message.content and len(message.content) > 0:
            response_text = message.content[0].text.strip()

            # Try to parse as JSON
            import json
            try:
                suggestions = json.loads(response_text)
                return True, suggestions, ""
            except json.JSONDecodeError:
                # Fallback: split by newlines
                suggestions = [s.strip('- ').strip() for s in response_text.split('\n') if s.strip()]
                return True, suggestions, ""
        else:
            return False, None, "Empty response from API"

    except Exception as e:
        logger.error(f"Suggestion generation failed: {str(e)}", exc_info=True)
        return False, None, str(e)
