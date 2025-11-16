"""
Prompt Customization System

Provides customizable prompt templates for different industries, roles,
and optimization scenarios. Users can select pre-built templates or
create custom prompts.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class IndustryType(Enum):
    """Industry categories for prompt templates."""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    CONSULTING = "consulting"
    MARKETING = "marketing"
    SALES = "sales"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"
    GENERAL = "general"


class RoleLevel(Enum):
    """Role level categories."""
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


@dataclass
class PromptTemplate:
    """
    Customizable prompt template for resume optimization.
    """

    name: str
    description: str
    industry: IndustryType = IndustryType.GENERAL
    role_level: RoleLevel = RoleLevel.MID_LEVEL

    # Core prompt components
    system_prompt: str = ""
    optimization_instructions: str = ""
    safety_rules: str = ""
    output_format_instructions: str = ""

    # Emphasis areas
    emphasize_keywords: List[str] = field(default_factory=list)
    avoid_keywords: List[str] = field(default_factory=list)

    # Custom rules
    custom_rules: List[str] = field(default_factory=list)

    def build_system_prompt(self) -> str:
        """Build complete system prompt from components."""
        components = []

        # Base system prompt
        if self.system_prompt:
            components.append(self.system_prompt)
        else:
            components.append(self._get_default_system_prompt())

        # Safety rules
        if self.safety_rules:
            components.append("\n\nSAFETY RULES:")
            components.append(self.safety_rules)
        else:
            components.append(self._get_default_safety_rules())

        # Optimization instructions
        if self.optimization_instructions:
            components.append("\n\nOPTIMIZATION INSTRUCTIONS:")
            components.append(self.optimization_instructions)

        # Industry-specific guidance
        industry_guidance = self._get_industry_guidance()
        if industry_guidance:
            components.append("\n\nINDUSTRY-SPECIFIC GUIDANCE:")
            components.append(industry_guidance)

        # Role-level guidance
        role_guidance = self._get_role_level_guidance()
        if role_guidance:
            components.append("\n\nROLE-LEVEL GUIDANCE:")
            components.append(role_guidance)

        # Keyword emphasis
        if self.emphasize_keywords:
            components.append("\n\nKEYWORDS TO EMPHASIZE:")
            components.append(f"- Prioritize: {', '.join(self.emphasize_keywords)}")

        if self.avoid_keywords:
            components.append(f"- Avoid: {', '.join(self.avoid_keywords)}")

        # Custom rules
        if self.custom_rules:
            components.append("\n\nCUSTOM RULES:")
            for rule in self.custom_rules:
                components.append(f"- {rule}")

        # Output format
        if self.output_format_instructions:
            components.append("\n\nOUTPUT FORMAT:")
            components.append(self.output_format_instructions)
        else:
            components.append(self._get_default_output_format())

        return "\n".join(components)

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt."""
        return """You are an expert resume optimization specialist with deep knowledge of ATS systems, recruitment best practices, and industry-specific requirements.

Your task is to improve resumes to better match job requirements while maintaining absolute truthfulness and authenticity."""

    def _get_default_safety_rules(self) -> str:
        """Get default safety rules."""
        return """CRITICAL - YOU MUST NOT:
- Invent employers, job titles, or employment dates
- Add technologies, tools, or frameworks not in the original resume
- Create new specific metrics (percentages, dollar amounts) not already present
- Fabricate projects, products, or initiatives
- Add educational credentials, degrees, or certifications not earned
- Invent achievements or awards

YOU MAY:
- Rephrase existing content for clarity and impact
- Surface skills clearly implied by existing experience
- Reorder information for better presentation
- Adjust grammar, tense, and formatting
- Align language with job posting keywords where truthful"""

    def _get_default_output_format(self) -> str:
        """Get default output format instructions."""
        return """Return a JSON object with:
{
  "optimized_resume": { /* Complete ResumeModel with improved text */ },
  "changes": [ /* Array of changes made with rationale */ ],
  "summary_of_improvements": [ /* High-level improvements */ ]
}"""

    def _get_industry_guidance(self) -> str:
        """Get industry-specific guidance."""
        guidance = {
            IndustryType.TECHNOLOGY: """
- Emphasize technical skills, programming languages, and frameworks
- Include specific technologies, tools, and methodologies
- Quantify impact (users served, performance improvements, code quality)
- Highlight open source contributions, side projects
- Use technical terminology appropriately
- Focus on innovation, scalability, and efficiency""",

            IndustryType.HEALTHCARE: """
- Emphasize patient outcomes, safety, and quality of care
- Include certifications, licenses, and continuing education
- Use proper medical terminology and abbreviations
- Highlight compliance with regulations (HIPAA, etc.)
- Focus on compassionate care and clinical excellence
- Quantify patient volume, satisfaction scores, outcomes""",

            IndustryType.FINANCE: """
- Emphasize financial acumen, risk management, and compliance
- Include relevant certifications (CFA, CPA, Series 7, etc.)
- Quantify financial impact (revenue, cost savings, ROI)
- Highlight regulatory knowledge and adherence
- Use industry-specific terminology (P&L, EBITDA, etc.)
- Focus on analytical skills and data-driven decision making""",

            IndustryType.CONSULTING: """
- Emphasize problem-solving, strategic thinking, and client impact
- Quantify business outcomes and value delivered
- Highlight diverse industry experience and project types
- Include methodologies and frameworks used
- Focus on stakeholder management and communication
- Showcase thought leadership and expertise""",

            IndustryType.MARKETING: """
- Emphasize campaign performance and ROI
- Quantify metrics (conversion rates, engagement, reach)
- Highlight digital marketing skills and platforms
- Include creative achievements and brand building
- Focus on data-driven strategy and A/B testing
- Showcase cross-channel expertise""",

            IndustryType.SALES: """
- Emphasize revenue generation and quota attainment
- Quantify sales metrics (%, quota, revenue, deals closed)
- Highlight relationship building and account management
- Include CRM tools and sales methodologies
- Focus on client acquisition and retention
- Showcase negotiation and closing skills"""
        }

        return guidance.get(self.industry, "")

    def _get_role_level_guidance(self) -> str:
        """Get role-level specific guidance."""
        guidance = {
            RoleLevel.ENTRY_LEVEL: """
- Emphasize education, internships, and relevant coursework
- Highlight transferable skills and eagerness to learn
- Include academic projects and extracurricular activities
- Focus on potential and growth mindset
- Quantify achievements even if from academic/volunteer work""",

            RoleLevel.MID_LEVEL: """
- Emphasize proven track record and growing expertise
- Balance technical skills with soft skills
- Highlight progression and increasing responsibility
- Quantify individual contributions and impact
- Include mentorship and collaboration""",

            RoleLevel.SENIOR: """
- Emphasize deep expertise and thought leadership
- Highlight complex problem-solving and innovation
- Quantify significant business impact
- Include mentorship, training, and knowledge sharing
- Focus on strategic contributions""",

            RoleLevel.LEAD: """
- Emphasize technical leadership and architecture
- Highlight team guidance and best practices
- Quantify project success and team productivity
- Include cross-functional collaboration
- Focus on setting technical direction""",

            RoleLevel.MANAGER: """
- Emphasize team leadership and development
- Highlight resource management and planning
- Quantify team performance and outcomes
- Include hiring, coaching, and performance management
- Focus on operational excellence""",

            RoleLevel.DIRECTOR: """
- Emphasize strategic leadership and org-wide impact
- Highlight department growth and transformation
- Quantify business outcomes at scale
- Include cross-functional leadership
- Focus on vision, strategy, and execution""",

            RoleLevel.EXECUTIVE: """
- Emphasize C-level strategic leadership
- Highlight organizational transformation and vision
- Quantify company-wide impact and growth
- Include board interactions and stakeholder management
- Focus on P&L responsibility, culture building, industry leadership"""
        }

        return guidance.get(self.role_level, "")

    @classmethod
    def default(cls) -> 'PromptTemplate':
        """Default general-purpose template."""
        return cls(
            name="Default",
            description="General-purpose template suitable for most roles",
            industry=IndustryType.GENERAL,
            role_level=RoleLevel.MID_LEVEL
        )

    @classmethod
    def software_engineer(cls, level: RoleLevel = RoleLevel.MID_LEVEL) -> 'PromptTemplate':
        """Template for software engineering roles."""
        return cls(
            name=f"Software Engineer ({level.value})",
            description=f"Optimized for {level.value} software engineering positions",
            industry=IndustryType.TECHNOLOGY,
            role_level=level,
            emphasize_keywords=[
                'programming languages', 'frameworks', 'architecture',
                'scalability', 'performance', 'testing', 'CI/CD'
            ],
            avoid_keywords=['synergy', 'rockstar', 'ninja'],
            custom_rules=[
                "Emphasize concrete technical achievements over buzzwords",
                "Quantify performance improvements and scale",
                "Highlight open source contributions and side projects"
            ]
        )

    @classmethod
    def data_scientist(cls, level: RoleLevel = RoleLevel.MID_LEVEL) -> 'PromptTemplate':
        """Template for data science roles."""
        return cls(
            name=f"Data Scientist ({level.value})",
            description=f"Optimized for {level.value} data science positions",
            industry=IndustryType.TECHNOLOGY,
            role_level=level,
            emphasize_keywords=[
                'machine learning', 'statistical analysis', 'data visualization',
                'Python', 'R', 'SQL', 'model development', 'A/B testing'
            ],
            custom_rules=[
                "Emphasize model performance metrics and business impact",
                "Highlight experience with ML frameworks and tools",
                "Quantify data scale and processing efficiency"
            ]
        )

    @classmethod
    def product_manager(cls, level: RoleLevel = RoleLevel.MID_LEVEL) -> 'PromptTemplate':
        """Template for product management roles."""
        return cls(
            name=f"Product Manager ({level.value})",
            description=f"Optimized for {level.value} product management positions",
            industry=IndustryType.TECHNOLOGY,
            role_level=level,
            emphasize_keywords=[
                'product strategy', 'roadmap', 'user research',
                'stakeholder management', 'agile', 'metrics', 'KPIs'
            ],
            custom_rules=[
                "Emphasize product launches and feature adoption",
                "Highlight cross-functional leadership",
                "Quantify user growth, engagement, and revenue impact"
            ]
        )

    @classmethod
    def healthcare_professional(cls, level: RoleLevel = RoleLevel.MID_LEVEL) -> 'PromptTemplate':
        """Template for healthcare roles."""
        return cls(
            name=f"Healthcare Professional ({level.value})",
            description=f"Optimized for {level.value} healthcare positions",
            industry=IndustryType.HEALTHCARE,
            role_level=level,
            emphasize_keywords=[
                'patient care', 'clinical excellence', 'safety',
                'compliance', 'certifications', 'outcomes'
            ],
            custom_rules=[
                "Emphasize patient outcomes and quality of care",
                "Highlight certifications and continuing education",
                "Use appropriate medical terminology"
            ]
        )


# Template registry
PROMPT_TEMPLATES: Dict[str, PromptTemplate] = {
    'default': PromptTemplate.default(),

    # Software Engineering
    'software_engineer_mid': PromptTemplate.software_engineer(RoleLevel.MID_LEVEL),
    'software_engineer_senior': PromptTemplate.software_engineer(RoleLevel.SENIOR),
    'software_engineer_lead': PromptTemplate.software_engineer(RoleLevel.LEAD),

    # Data Science
    'data_scientist_mid': PromptTemplate.data_scientist(RoleLevel.MID_LEVEL),
    'data_scientist_senior': PromptTemplate.data_scientist(RoleLevel.SENIOR),

    # Product Management
    'product_manager_mid': PromptTemplate.product_manager(RoleLevel.MID_LEVEL),
    'product_manager_senior': PromptTemplate.product_manager(RoleLevel.SENIOR),

    # Healthcare
    'healthcare_mid': PromptTemplate.healthcare_professional(RoleLevel.MID_LEVEL),
    'healthcare_senior': PromptTemplate.healthcare_professional(RoleLevel.SENIOR),
}


def get_template(template_name: str) -> PromptTemplate:
    """Get a prompt template by name."""
    return PROMPT_TEMPLATES.get(template_name, PromptTemplate.default())


def list_templates() -> List[str]:
    """Get list of available template names."""
    return list(PROMPT_TEMPLATES.keys())


def get_templates_by_industry(industry: IndustryType) -> List[PromptTemplate]:
    """Get all templates for a specific industry."""
    return [
        template for template in PROMPT_TEMPLATES.values()
        if template.industry == industry
    ]


def create_custom_template(
    name: str,
    description: str,
    industry: str = "general",
    role_level: str = "mid_level",
    **kwargs
) -> PromptTemplate:
    """
    Create a custom prompt template.

    Args:
        name: Template name
        description: Template description
        industry: Industry type
        role_level: Role level
        **kwargs: Additional template parameters

    Returns:
        PromptTemplate instance
    """
    try:
        industry_enum = IndustryType(industry.lower())
    except ValueError:
        industry_enum = IndustryType.GENERAL

    try:
        level_enum = RoleLevel(role_level.lower())
    except ValueError:
        level_enum = RoleLevel.MID_LEVEL

    return PromptTemplate(
        name=name,
        description=description,
        industry=industry_enum,
        role_level=level_enum,
        **kwargs
    )
