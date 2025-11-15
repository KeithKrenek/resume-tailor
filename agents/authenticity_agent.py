"""
AI agent for verifying authenticity of resume optimizations.

This agent uses LLM-based analysis to detect fabrications and exaggerations
in optimized resume content compared to the original resume.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from utils.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available")

from modules.models import ResumeModel, ResumeChange
from config.settings import ANTHROPIC_API_KEY


@dataclass
class AuthenticityIssue:
    """Represents a detected authenticity issue."""
    type: str  # "fabrication" or "exaggeration"
    severity: str  # "high", "medium", "low"
    location: str  # e.g., "experience[0].bullets[2]"
    original_text: str
    modified_text: str
    explanation: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthenticityIssue':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class AuthenticityReport:
    """Complete authenticity verification report."""
    total_changes_analyzed: int
    issues_found: List[AuthenticityIssue]
    is_safe: bool
    overall_risk_level: str  # "low", "medium", "high"
    summary: str
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_changes_analyzed': self.total_changes_analyzed,
            'issues_found': [issue.to_dict() for issue in self.issues_found],
            'is_safe': self.is_safe,
            'overall_risk_level': self.overall_risk_level,
            'summary': self.summary,
            'recommendations': self.recommendations
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthenticityReport':
        """Create from dictionary."""
        issues = [AuthenticityIssue.from_dict(issue) for issue in data.get('issues_found', [])]
        return cls(
            total_changes_analyzed=data['total_changes_analyzed'],
            issues_found=issues,
            is_safe=data['is_safe'],
            overall_risk_level=data['overall_risk_level'],
            summary=data['summary'],
            recommendations=data['recommendations']
        )

    def get_fabrications(self) -> List[AuthenticityIssue]:
        """Get all fabrication issues."""
        return [issue for issue in self.issues_found if issue.type == "fabrication"]

    def get_exaggerations(self) -> List[AuthenticityIssue]:
        """Get all exaggeration issues."""
        return [issue for issue in self.issues_found if issue.type == "exaggeration"]

    def get_high_severity_issues(self) -> List[AuthenticityIssue]:
        """Get all high severity issues."""
        return [issue for issue in self.issues_found if issue.severity == "high"]


class AuthenticityAgent:
    """
    Agent for verifying the authenticity of resume optimizations.

    Uses LLM-based analysis to detect:
    - Fabrications: Completely new claims not supported by original
    - Exaggerations: Claims that overstate original achievements
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        """
        Initialize the authenticity agent.

        Args:
            api_key: Anthropic API key (uses env var if not provided)
            model: Model to use for verification (default: Haiku for speed)
        """
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model = model

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic library is required for AuthenticityAgent")

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"AuthenticityAgent initialized with model: {self.model}")

    def _build_verification_prompt(
        self,
        original_resume_text: str,
        optimized_resume: ResumeModel,
        changes: List[ResumeChange]
    ) -> str:
        """
        Build the prompt for authenticity verification.

        Args:
            original_resume_text: Original resume as plain text
            optimized_resume: Optimized resume model
            changes: List of changes made during optimization

        Returns:
            Formatted prompt string
        """
        # Build a summary of changes for context
        changes_summary = []
        for change in changes[:20]:  # Limit to first 20 for token efficiency
            changes_summary.append(f"""
Location: {change.location}
Before: {change.before[:200]}
After: {change.after[:200]}
---""")

        changes_text = "\n".join(changes_summary)

        prompt = f"""You are an expert resume authenticity verifier. Your task is to analyze changes made to a resume during optimization and identify any fabrications or exaggerations.

**ORIGINAL RESUME:**
```
{original_resume_text[:4000]}
```

**CHANGES MADE DURING OPTIMIZATION:**
{changes_text}

**YOUR TASK:**
Analyze each change and identify:

1. **FABRICATIONS**: Completely new claims, metrics, technologies, or achievements that have NO BASIS in the original resume
   - New numbers/metrics not present before (e.g., "increased by 50%" when no metric existed)
   - New technologies/tools never mentioned
   - New companies, projects, or achievements invented
   - New responsibilities that weren't implied

2. **EXAGGERATIONS**: Claims that overstate or significantly embellish what was in the original
   - Inflating metrics (e.g., "10%" became "40%")
   - Upgrading scope (e.g., "contributed to" became "led")
   - Adding superlatives not supported (e.g., "worked on project" became "architected award-winning project")

**IMPORTANT GUIDELINES:**
- Minor rephrasing for clarity is ACCEPTABLE
- Using industry-standard terminology is ACCEPTABLE
- Quantifying vague claims with reasonable estimates is ACCEPTABLE if clearly based on original content
- Adding keywords that align with existing skills is ACCEPTABLE
- Only flag clear fabrications or significant exaggerations

**OUTPUT FORMAT:**
Return a JSON object with this structure:

{{
  "issues": [
    {{
      "type": "fabrication" | "exaggeration",
      "severity": "high" | "medium" | "low",
      "location": "experience[0].bullets[2]",
      "original_text": "original text here",
      "modified_text": "new text here",
      "explanation": "Clear explanation of the issue",
      "recommendation": "Suggested fix"
    }}
  ],
  "summary": "Brief overall assessment",
  "overall_risk_level": "low" | "medium" | "high"
}}

**SEVERITY LEVELS:**
- **high**: Clear fabrication or major exaggeration that could damage credibility
- **medium**: Noticeable exaggeration that should be reviewed
- **low**: Minor concern, likely acceptable but worth noting

Analyze the changes now and return ONLY the JSON object, no other text."""

        return prompt

    def verify_updates(
        self,
        original_resume_text: str,
        optimized_resume: ResumeModel,
        changes: List[ResumeChange]
    ) -> Tuple[bool, AuthenticityReport]:
        """
        Verify the authenticity of resume updates.

        Args:
            original_resume_text: Original resume as plain text
            optimized_resume: Optimized resume model
            changes: List of changes made during optimization

        Returns:
            Tuple of (success: bool, report: AuthenticityReport)
        """
        logger.info(f"Starting authenticity verification for {len(changes)} changes")

        try:
            # Build verification prompt
            prompt = self._build_verification_prompt(
                original_resume_text,
                optimized_resume,
                changes
            )

            # Call LLM for verification
            logger.info(f"Calling {self.model} for verification")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.1,  # Low temperature for consistent analysis
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract response text
            response_text = response.content[0].text.strip()
            logger.debug(f"LLM response: {response_text[:500]}")

            # Parse JSON response
            # Handle potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            result = json.loads(response_text)

            # Build authenticity issues from response
            issues = []
            for issue_data in result.get('issues', []):
                issue = AuthenticityIssue(
                    type=issue_data['type'],
                    severity=issue_data['severity'],
                    location=issue_data['location'],
                    original_text=issue_data['original_text'],
                    modified_text=issue_data['modified_text'],
                    explanation=issue_data['explanation'],
                    recommendation=issue_data['recommendation']
                )
                issues.append(issue)

            # Determine overall safety
            high_severity_count = len([i for i in issues if i.severity == "high"])
            fabrication_count = len([i for i in issues if i.type == "fabrication"])

            is_safe = (high_severity_count == 0 and fabrication_count < 2)

            # Build recommendations
            recommendations = []
            if high_severity_count > 0:
                recommendations.append(
                    f"Found {high_severity_count} high-severity issue(s). "
                    "Review and correct these before using the resume."
                )
            if fabrication_count > 0:
                recommendations.append(
                    f"Found {fabrication_count} fabrication(s). "
                    "Ensure all claims are truthful and based on your experience."
                )

            if not is_safe:
                recommendations.append(
                    "Consider re-running optimization with 'conservative' style to reduce risk."
                )

            # Create report
            report = AuthenticityReport(
                total_changes_analyzed=len(changes),
                issues_found=issues,
                is_safe=is_safe,
                overall_risk_level=result.get('overall_risk_level', 'medium'),
                summary=result.get('summary', 'Verification completed'),
                recommendations=recommendations
            )

            logger.info(
                f"Verification complete: {len(issues)} issues found, "
                f"risk level: {report.overall_risk_level}, safe: {is_safe}"
            )

            return True, report

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {response_text}")

            # Return a fallback report
            fallback_report = AuthenticityReport(
                total_changes_analyzed=len(changes),
                issues_found=[],
                is_safe=False,
                overall_risk_level="unknown",
                summary="Verification failed due to parsing error",
                recommendations=["Manual review recommended due to verification failure"]
            )
            return False, fallback_report

        except Exception as e:
            logger.error(f"Authenticity verification failed: {e}", exc_info=True)

            # Return a fallback report
            fallback_report = AuthenticityReport(
                total_changes_analyzed=len(changes),
                issues_found=[],
                is_safe=False,
                overall_risk_level="unknown",
                summary=f"Verification failed: {str(e)}",
                recommendations=["Manual review required due to verification failure"]
            )
            return False, fallback_report

    def verify_single_change(
        self,
        original_context: str,
        modified_text: str,
        change_location: str
    ) -> Optional[AuthenticityIssue]:
        """
        Verify a single change in isolation.

        Args:
            original_context: Original text/context
            modified_text: Modified text
            change_location: Location identifier

        Returns:
            AuthenticityIssue if issue found, None otherwise
        """
        prompt = f"""Compare the original and modified text. Identify if the modification is a fabrication or exaggeration.

Original: {original_context}
Modified: {modified_text}

Return JSON:
{{
  "has_issue": true/false,
  "type": "fabrication" | "exaggeration" | null,
  "severity": "high" | "medium" | "low" | null,
  "explanation": "...",
  "recommendation": "..."
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()

            # Parse response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            result = json.loads(response_text)

            if result.get('has_issue'):
                return AuthenticityIssue(
                    type=result['type'],
                    severity=result['severity'],
                    location=change_location,
                    original_text=original_context,
                    modified_text=modified_text,
                    explanation=result['explanation'],
                    recommendation=result['recommendation']
                )

            return None

        except Exception as e:
            logger.error(f"Single change verification failed: {e}")
            return None


def create_authenticity_agent(api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307") -> AuthenticityAgent:
    """
    Factory function to create an AuthenticityAgent.

    Args:
        api_key: Anthropic API key (uses env var if not provided)
        model: Model to use for verification

    Returns:
        Configured AuthenticityAgent instance
    """
    return AuthenticityAgent(api_key=api_key, model=model)
