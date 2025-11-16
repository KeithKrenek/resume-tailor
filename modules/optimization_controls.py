"""
Section-Level Optimization Controls

Provides granular control over resume optimization on a per-section basis,
allowing users to customize intensity, focus, and constraints for each section.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class OptimizationIntensity(Enum):
    """Optimization intensity levels."""
    NONE = "none"  # Don't optimize this section
    MINIMAL = "minimal"  # Only fix obvious issues
    MODERATE = "moderate"  # Standard optimization
    AGGRESSIVE = "aggressive"  # Maximum optimization


class SectionType(Enum):
    """Resume section types."""
    SUMMARY = "summary"
    HEADLINE = "headline"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    PROJECTS = "projects"
    AWARDS = "awards"


@dataclass
class SectionOptimizationSettings:
    """Optimization settings for a specific section."""

    section: SectionType
    intensity: OptimizationIntensity = OptimizationIntensity.MODERATE

    # Section-specific constraints
    max_length: Optional[int] = None  # Max characters
    max_bullets_per_item: Optional[int] = None  # For experience
    required_keywords: List[str] = field(default_factory=list)
    forbidden_keywords: List[str] = field(default_factory=list)

    # Focus areas
    emphasize_achievements: bool = True
    emphasize_metrics: bool = True
    emphasize_keywords: bool = True

    # Voice and tone
    preserve_original_voice: bool = False
    use_first_person: bool = False  # "I led" vs "Led"

    # Special instructions
    custom_instructions: str = ""

    @property
    def is_enabled(self) -> bool:
        """Check if optimization is enabled for this section."""
        return self.intensity != OptimizationIntensity.NONE

    def to_prompt_instructions(self) -> str:
        """Convert settings to LLM prompt instructions."""
        if not self.is_enabled:
            return f"Do NOT modify the {self.section.value} section."

        instructions = [f"For the {self.section.value} section:"]

        # Intensity
        if self.intensity == OptimizationIntensity.MINIMAL:
            instructions.append("- Make only minimal, essential changes")
        elif self.intensity == OptimizationIntensity.MODERATE:
            instructions.append("- Apply standard optimization techniques")
        elif self.intensity == OptimizationIntensity.AGGRESSIVE:
            instructions.append("- Maximize keyword density and ATS optimization")

        # Length constraints
        if self.max_length:
            instructions.append(f"- Keep total length under {self.max_length} characters")

        if self.max_bullets_per_item:
            instructions.append(f"- Maximum {self.max_bullets_per_item} bullet points per position")

        # Keywords
        if self.required_keywords:
            instructions.append(f"- MUST include: {', '.join(self.required_keywords)}")

        if self.forbidden_keywords:
            instructions.append(f"- MUST NOT include: {', '.join(self.forbidden_keywords)}")

        # Focus areas
        if self.emphasize_achievements:
            instructions.append("- Emphasize concrete achievements and results")

        if self.emphasize_metrics:
            instructions.append("- Include specific metrics and quantifiable results")

        if self.emphasize_keywords:
            instructions.append("- Optimize for relevant keywords")

        # Voice
        if self.preserve_original_voice:
            instructions.append("- Preserve the original writing voice and style")

        if self.use_first_person:
            instructions.append("- Use first-person perspective (I, my)")
        else:
            instructions.append("- Use third-person perspective (no I, me, my)")

        # Custom
        if self.custom_instructions:
            instructions.append(f"- Special: {self.custom_instructions}")

        return "\n".join(instructions)


@dataclass
class OptimizationProfile:
    """
    Complete optimization profile with settings for all sections.

    Profiles can be saved and reused for different optimization styles.
    """

    name: str
    description: str
    section_settings: Dict[SectionType, SectionOptimizationSettings] = field(default_factory=dict)

    # Global constraints
    max_total_length: Optional[int] = None  # Max characters for entire resume
    target_page_count: Optional[int] = 2  # Target pages (1 or 2)

    # Global preferences
    overall_tone: str = "professional"  # professional, enthusiastic, technical
    prioritize_recent_experience: bool = True

    def __post_init__(self):
        """Initialize default settings for all sections if not provided."""
        for section_type in SectionType:
            if section_type not in self.section_settings:
                self.section_settings[section_type] = SectionOptimizationSettings(
                    section=section_type
                )

    def get_settings(self, section: SectionType) -> SectionOptimizationSettings:
        """Get settings for a specific section."""
        return self.section_settings.get(section, SectionOptimizationSettings(section=section))

    def set_settings(self, section: SectionType, settings: SectionOptimizationSettings):
        """Set settings for a specific section."""
        self.section_settings[section] = settings

    def set_intensity_all(self, intensity: OptimizationIntensity):
        """Set the same intensity for all sections."""
        for section_type in SectionType:
            self.section_settings[section_type].intensity = intensity

    def enable_section(self, section: SectionType, intensity: OptimizationIntensity = OptimizationIntensity.MODERATE):
        """Enable optimization for a section."""
        self.section_settings[section].intensity = intensity

    def disable_section(self, section: SectionType):
        """Disable optimization for a section."""
        self.section_settings[section].intensity = OptimizationIntensity.NONE

    def to_llm_instructions(self) -> str:
        """
        Convert profile to comprehensive LLM instructions.

        Returns:
            Formatted prompt instructions for the LLM
        """
        instructions = [
            f"OPTIMIZATION PROFILE: {self.name}",
            f"{self.description}",
            "",
            "GLOBAL CONSTRAINTS:"
        ]

        if self.max_total_length:
            instructions.append(f"- Total resume length: maximum {self.max_total_length} characters")

        if self.target_page_count:
            instructions.append(f"- Target page count: {self.target_page_count} page(s)")

        instructions.append(f"- Overall tone: {self.overall_tone}")

        if self.prioritize_recent_experience:
            instructions.append("- Prioritize recent experience (last 5 years)")

        instructions.append("")
        instructions.append("SECTION-SPECIFIC INSTRUCTIONS:")
        instructions.append("")

        # Add section-specific instructions
        for section_type in SectionType:
            settings = self.get_settings(section_type)
            instructions.append(settings.to_prompt_instructions())
            instructions.append("")

        return "\n".join(instructions)

    @classmethod
    def conservative(cls) -> 'OptimizationProfile':
        """
        Conservative profile: minimal changes, preserve voice.

        Best for: Established professionals, sensitive industries
        """
        profile = cls(
            name="Conservative",
            description="Minimal changes with strong voice preservation",
            target_page_count=2
        )

        profile.set_intensity_all(OptimizationIntensity.MINIMAL)

        # Preserve voice for all sections
        for section_type in SectionType:
            profile.get_settings(section_type).preserve_original_voice = True

        # Only optimize summary and skills moderately
        profile.get_settings(SectionType.SUMMARY).intensity = OptimizationIntensity.MODERATE
        profile.get_settings(SectionType.SKILLS).intensity = OptimizationIntensity.MODERATE

        return profile

    @classmethod
    def balanced(cls) -> 'OptimizationProfile':
        """
        Balanced profile: standard optimization across all sections.

        Best for: General use, most applications
        """
        profile = cls(
            name="Balanced",
            description="Standard optimization with keyword focus",
            target_page_count=2
        )

        profile.set_intensity_all(OptimizationIntensity.MODERATE)

        # Emphasize achievements and metrics
        for section_type in SectionType:
            settings = profile.get_settings(section_type)
            settings.emphasize_achievements = True
            settings.emphasize_metrics = True
            settings.emphasize_keywords = True

        # Limit experience bullets
        profile.get_settings(SectionType.EXPERIENCE).max_bullets_per_item = 5

        return profile

    @classmethod
    def aggressive(cls) -> 'OptimizationProfile':
        """
        Aggressive profile: maximum optimization for ATS.

        Best for: Competitive roles, career changers, ATS-heavy companies
        """
        profile = cls(
            name="Aggressive",
            description="Maximum keyword density and ATS optimization",
            target_page_count=2,
            overall_tone="professional"
        )

        # Aggressive optimization for all content sections
        profile.set_intensity_all(OptimizationIntensity.AGGRESSIVE)

        # Keep education minimal (usually not the focus)
        profile.get_settings(SectionType.EDUCATION).intensity = OptimizationIntensity.MINIMAL

        # Maximum emphasis on keywords and metrics
        for section_type in SectionType:
            settings = profile.get_settings(section_type)
            settings.emphasize_achievements = True
            settings.emphasize_metrics = True
            settings.emphasize_keywords = True

        return profile

    @classmethod
    def technical_focus(cls) -> 'OptimizationProfile':
        """
        Technical focus profile: emphasize technical skills and projects.

        Best for: Software engineers, data scientists, technical roles
        """
        profile = cls(
            name="Technical Focus",
            description="Emphasis on technical skills, projects, and technologies",
            target_page_count=2,
            overall_tone="technical"
        )

        profile.set_intensity_all(OptimizationIntensity.MODERATE)

        # Aggressive optimization for technical sections
        profile.get_settings(SectionType.SKILLS).intensity = OptimizationIntensity.AGGRESSIVE
        profile.get_settings(SectionType.PROJECTS).intensity = OptimizationIntensity.AGGRESSIVE

        # Add technical keywords emphasis
        for section in [SectionType.EXPERIENCE, SectionType.PROJECTS]:
            settings = profile.get_settings(section)
            settings.emphasize_metrics = True
            settings.custom_instructions = "Focus on technical challenges, technologies used, and measurable outcomes"

        # De-emphasize education (unless entry-level)
        profile.get_settings(SectionType.EDUCATION).intensity = OptimizationIntensity.MINIMAL

        return profile

    @classmethod
    def leadership_focus(cls) -> 'OptimizationProfile':
        """
        Leadership focus profile: emphasize team management and strategic impact.

        Best for: Managers, directors, executives
        """
        profile = cls(
            name="Leadership Focus",
            description="Emphasis on leadership, team management, and business impact",
            target_page_count=2,
            overall_tone="professional"
        )

        profile.set_intensity_all(OptimizationIntensity.MODERATE)

        # Aggressive for summary and experience
        profile.get_settings(SectionType.SUMMARY).intensity = OptimizationIntensity.AGGRESSIVE
        profile.get_settings(SectionType.EXPERIENCE).intensity = OptimizationIntensity.AGGRESSIVE

        # Customize instructions for leadership
        exp_settings = profile.get_settings(SectionType.EXPERIENCE)
        exp_settings.custom_instructions = (
            "Emphasize team size, budget managed, strategic initiatives, "
            "cross-functional collaboration, and business outcomes"
        )
        exp_settings.max_bullets_per_item = 6  # More bullets for leadership roles

        summary_settings = profile.get_settings(SectionType.SUMMARY)
        summary_settings.custom_instructions = "Highlight leadership philosophy and strategic impact"

        return profile

    @classmethod
    def career_changer(cls) -> 'OptimizationProfile':
        """
        Career changer profile: reframe experience for new industry.

        Best for: Industry transitions, role changes
        """
        profile = cls(
            name="Career Changer",
            description="Reframe transferable skills and relevant experience",
            target_page_count=2
        )

        # Aggressive reframing of summary and skills
        profile.get_settings(SectionType.SUMMARY).intensity = OptimizationIntensity.AGGRESSIVE
        profile.get_settings(SectionType.SKILLS).intensity = OptimizationIntensity.AGGRESSIVE

        # Moderate for experience (reframe but stay truthful)
        profile.get_settings(SectionType.EXPERIENCE).intensity = OptimizationIntensity.MODERATE

        # Customize instructions
        summary_settings = profile.get_settings(SectionType.SUMMARY)
        summary_settings.custom_instructions = "Focus on transferable skills and how past experience applies to new role"

        exp_settings = profile.get_settings(SectionType.EXPERIENCE)
        exp_settings.custom_instructions = "Emphasize transferable skills and relevant achievements"

        return profile

    def to_dict(self) -> Dict:
        """Convert profile to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'max_total_length': self.max_total_length,
            'target_page_count': self.target_page_count,
            'overall_tone': self.overall_tone,
            'prioritize_recent_experience': self.prioritize_recent_experience,
            'section_settings': {
                section.value: {
                    'intensity': settings.intensity.value,
                    'max_length': settings.max_length,
                    'max_bullets_per_item': settings.max_bullets_per_item,
                    'required_keywords': settings.required_keywords,
                    'forbidden_keywords': settings.forbidden_keywords,
                    'emphasize_achievements': settings.emphasize_achievements,
                    'emphasize_metrics': settings.emphasize_metrics,
                    'emphasize_keywords': settings.emphasize_keywords,
                    'preserve_original_voice': settings.preserve_original_voice,
                    'use_first_person': settings.use_first_person,
                    'custom_instructions': settings.custom_instructions
                }
                for section, settings in self.section_settings.items()
            }
        }


# Predefined profiles
OPTIMIZATION_PROFILES = {
    'conservative': OptimizationProfile.conservative(),
    'balanced': OptimizationProfile.balanced(),
    'aggressive': OptimizationProfile.aggressive(),
    'technical': OptimizationProfile.technical_focus(),
    'leadership': OptimizationProfile.leadership_focus(),
    'career_changer': OptimizationProfile.career_changer()
}


def get_profile(profile_name: str) -> OptimizationProfile:
    """Get a predefined optimization profile by name."""
    return OPTIMIZATION_PROFILES.get(
        profile_name.lower(),
        OptimizationProfile.balanced()
    )


def list_profiles() -> List[str]:
    """Get list of available profile names."""
    return list(OPTIMIZATION_PROFILES.keys())
