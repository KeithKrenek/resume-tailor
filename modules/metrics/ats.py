"""
ATS Optimization Metric
Evaluates resume compatibility with Applicant Tracking Systems.

IMPROVED VERSION: Uses comprehensive stopwords for accurate keyword extraction.
"""

import re
from typing import Set
from .base import MetricCalculator, MetricScore
from modules.llm_keyword_extractor import COMPREHENSIVE_STOPWORDS


class ATSScorer(MetricCalculator):
    """Calculates ATS optimization score based on formatting and keywords."""

    def __init__(self, threshold: float = 0.80):
        self.threshold = threshold

    def calculate(self, original_resume: str, optimized_resume: str, job_description: str) -> MetricScore:
        """Calculate ATS optimization score."""

        # Component scores
        keyword_density_score = self._calculate_keyword_density(optimized_resume, job_description)
        format_score = self._calculate_format_score(optimized_resume)
        structure_score = self._calculate_structure_score(optimized_resume)
        readability_score = self._calculate_readability_score(optimized_resume)

        # Weighted overall score
        # Keyword density: 40%, Format: 25%, Structure: 20%, Readability: 15%
        overall_score = (
            keyword_density_score * 0.40 +
            format_score * 0.25 +
            structure_score * 0.20 +
            readability_score * 0.15
        )

        # Generate recommendations
        recommendations = []
        if keyword_density_score < 0.7:
            recommendations.append("Increase keyword density from job description (target: 2-8%)")
        if format_score < 0.7:
            recommendations.append("Simplify formatting - avoid tables, excessive tabs, and special characters")
        if structure_score < 0.7:
            recommendations.append("Ensure resume includes standard sections: Experience, Education, Skills")
        if readability_score < 0.7:
            recommendations.append("Improve readability - aim for 15-20 words per sentence")

        return MetricScore(
            name="ATS Optimization",
            score=overall_score,
            passed=overall_score >= self.threshold,
            threshold=self.threshold,
            details={
                "keyword_density_score": keyword_density_score,
                "format_score": format_score,
                "structure_score": structure_score,
                "readability_score": readability_score,
                "keyword_density_pct": self._get_keyword_density_pct(optimized_resume, job_description),
                "avg_sentence_length": self._get_avg_sentence_length(optimized_resume),
                "has_standard_sections": self._has_standard_sections(optimized_resume)
            },
            recommendations=recommendations
        )

    def get_threshold(self) -> float:
        return self.threshold

    def _calculate_keyword_density(self, resume: str, job_description: str) -> float:
        """
        Calculate keyword density score.
        Optimal range: 2-8% of resume words should be JD keywords.
        """
        # Extract keywords from job description
        jd_keywords = self._extract_keywords(job_description)

        # Count keyword occurrences in resume
        resume_lower = resume.lower()
        keyword_count = 0
        for keyword in jd_keywords:
            keyword_count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', resume_lower))

        # Total words in resume
        total_words = len(re.findall(r'\b\w+\b', resume))

        if total_words == 0:
            return 0.0

        density_pct = (keyword_count / total_words) * 100

        # Score based on optimal range (2-8%)
        if 2 <= density_pct <= 8:
            return 1.0
        elif density_pct < 2:
            # Penalize low density (linear from 0 to 2%)
            return max(0.0, density_pct / 2.0)
        else:
            # Penalize high density (linear decay from 8% to 15%, then 0)
            if density_pct > 15:
                return 0.0
            return max(0.0, 1.0 - ((density_pct - 8) / 7.0))

    def _get_keyword_density_pct(self, resume: str, job_description: str) -> float:
        """Get actual keyword density percentage for display."""
        jd_keywords = self._extract_keywords(job_description)
        resume_lower = resume.lower()
        keyword_count = 0
        for keyword in jd_keywords:
            keyword_count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', resume_lower))

        total_words = len(re.findall(r'\b\w+\b', resume))
        if total_words == 0:
            return 0.0

        return round((keyword_count / total_words) * 100, 2)

    def _calculate_format_score(self, resume: str) -> float:
        """
        Calculate format simplicity score.
        Penalize: tables, excessive tabs, non-ASCII characters, special formatting.
        """
        score = 1.0

        # Penalize table-like structures (multiple consecutive tabs)
        table_patterns = len(re.findall(r'\t{2,}', resume))
        score -= min(0.3, table_patterns * 0.05)

        # Penalize excessive special characters (except common punctuation)
        special_chars = len(re.findall(r'[^\w\s\.,\-:;()\'"!?]', resume))
        score -= min(0.2, special_chars * 0.001)

        # Penalize non-ASCII characters
        non_ascii = len([c for c in resume if ord(c) > 127])
        score -= min(0.2, non_ascii * 0.001)

        # Penalize very long lines (> 100 chars) - may indicate formatting issues
        long_lines = len([line for line in resume.split('\n') if len(line) > 100])
        score -= min(0.15, long_lines * 0.01)

        # Penalize multiple consecutive blank lines
        blank_line_groups = len(re.findall(r'\n\s*\n\s*\n', resume))
        score -= min(0.15, blank_line_groups * 0.02)

        return max(0.0, score)

    def _calculate_structure_score(self, resume: str) -> float:
        """
        Calculate structure score.
        Check for standard resume sections.
        """
        resume_lower = resume.lower()

        # Standard sections to look for
        sections = {
            'experience': r'\b(experience|work history|employment)\b',
            'education': r'\b(education|academic|degrees?)\b',
            'skills': r'\b(skills|technical skills|competencies)\b',
            'summary': r'\b(summary|profile|objective)\b',
        }

        found_sections = 0
        for section_name, pattern in sections.items():
            if re.search(pattern, resume_lower):
                found_sections += 1

        # At minimum should have: Experience, Education, Skills (3 out of 4)
        # Full score for all 4, partial for 3, lower for 2 or fewer
        if found_sections >= 4:
            return 1.0
        elif found_sections == 3:
            return 0.85
        elif found_sections == 2:
            return 0.60
        elif found_sections == 1:
            return 0.30
        else:
            return 0.0

    def _has_standard_sections(self, resume: str) -> dict:
        """Return which standard sections are present."""
        resume_lower = resume.lower()

        return {
            'experience': bool(re.search(r'\b(experience|work history|employment)\b', resume_lower)),
            'education': bool(re.search(r'\b(education|academic|degrees?)\b', resume_lower)),
            'skills': bool(re.search(r'\b(skills|technical skills|competencies)\b', resume_lower)),
            'summary': bool(re.search(r'\b(summary|profile|objective)\b', resume_lower))
        }

    def _calculate_readability_score(self, resume: str) -> float:
        """
        Calculate readability score.
        Optimal: 15-20 words per sentence.
        """
        avg_length = self._get_avg_sentence_length(resume)

        # Optimal range: 15-20 words per sentence
        if 15 <= avg_length <= 20:
            return 1.0
        elif avg_length < 15:
            # Too short - penalize slightly (may be too choppy)
            return max(0.6, avg_length / 15.0)
        else:
            # Too long - penalize (harder for ATS to parse)
            if avg_length > 30:
                return 0.3
            return max(0.3, 1.0 - ((avg_length - 20) / 10.0) * 0.7)

    def _get_avg_sentence_length(self, resume: str) -> float:
        """Get average sentence length in words."""
        # Split by common sentence terminators
        sentences = re.split(r'[.!?]+', resume)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        total_words = sum(len(re.findall(r'\b\w+\b', s)) for s in sentences)
        return round(total_words / len(sentences), 1)

    def _extract_keywords(self, text: str) -> Set[str]:
        """
        Extract keywords (4+ character words, filtered).

        IMPROVED: Now uses comprehensive stopword list (400+ words)
        instead of the inadequate 30-word list.
        """
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

        # Use comprehensive stopword list (400+ words)
        keywords = {w for w in words if w not in COMPREHENSIVE_STOPWORDS}

        return keywords
