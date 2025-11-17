"""Agent for revising resume changes based on user feedback."""

import os
from typing import Tuple, Optional
from anthropic import Anthropic
from utils.logging_config import get_logger

logger = get_logger(__name__)


def revise_change(
    original_text: str,
    ai_suggested_text: str,
    user_guidance: str,
    change_type: str,
    rationale: str,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514"
) -> Tuple[bool, Optional[str], str]:
    """
    Revise a resume change based on user guidance.

    Args:
        original_text: The original text before AI optimization
        ai_suggested_text: The text suggested by AI optimization
        user_guidance: User's guidance for how to revise
        change_type: Type of change (e.g., "experience_bullet", "summary")
        rationale: Original rationale for the change
        api_key: Anthropic API key (optional)
        model: Model to use for revision

    Returns:
        Tuple of (success, revised_text, error_message)
    """
    try:
        # Get API key
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            return False, None, "No API key available"

        # Initialize client
        client = Anthropic(api_key=key)

        # Build prompt
        prompt = f"""You are helping revise a resume change based on user feedback.

**Context:**
- Change Type: {change_type}
- Original Rationale: {rationale}

**Original Text (before optimization):**
{original_text}

**AI-Suggested Text (after optimization):**
{ai_suggested_text}

**User's Revision Request:**
{user_guidance}

**Your Task:**
Based on the user's feedback, create a revised version that:
1. Incorporates the user's specific requests
2. Maintains the intent of the original optimization (improving job match)
3. Stays truthful to the original resume content
4. Uses professional resume language

**Important:**
- Do NOT fabricate new information not present in the original text
- Keep the same basic facts and timeline
- Adjust tone, emphasis, and keywords based on user guidance
- Return ONLY the revised text, nothing else

Revised text:"""

        # Call API
        logger.info(f"Requesting change revision via {model}")
        message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract response
        if message.content and len(message.content) > 0:
            revised_text = message.content[0].text.strip()
            logger.info("Change revision successful")
            return True, revised_text, ""
        else:
            logger.error("Empty response from API")
            return False, None, "Empty response from API"

    except Exception as e:
        logger.error(f"Change revision failed: {str(e)}", exc_info=True)
        return False, None, str(e)
