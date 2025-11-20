"""
Role Alignment Metric
Measures how well the resume matches job requirements.

IMPROVED VERSION: Uses LLM-based keyword extraction and comprehensive stopwords.
"""

import re
from typing import List, Set, Dict
from .base import MetricCalculator, MetricScore
from modules.llm_keyword_extractor import (
    LLMKeywordExtractor,
    COMPREHENSIVE_STOPWORDS
)
from utils.logging_config import get_logger

logger = get_logger(__name__)


class RoleAlignmentScorer(MetricCalculator):
    """
    Calculates role alignment score based on intelligent keyword matching.

    IMPROVED: Uses LLM-based extraction, comprehensive stopwords,
    and focuses on technical skills rather than noisy general keywords.
    """

    def __init__(self, threshold: float = 0.70, api_key: str = None):
        """
        Initialize scorer.

        Args:
            threshold: Minimum score to pass (default: 0.70, lowered from 0.85
                      because we now use proper filtering)
            api_key: Anthropic API key for LLM extraction (optional)
        """
        self.threshold = threshold
        self.llm_extractor = LLMKeywordExtractor(api_key=api_key)
        logger.info(f"RoleAlignmentScorer initialized (threshold={threshold})")

    def calculate(self, original_resume: str, optimized_resume: str, job_description: str) -> MetricScore:
        """
        Calculate role alignment score using intelligent LLM-based extraction.

        IMPROVED: Focuses on meaningful keywords only, uses comprehensive stopwords,
        and weights technical skills appropriately.
        """
        logger.info("Calculating role alignment score with LLM extraction")

        # Extract keywords from job description using LLM
        try:
            jd_extraction = self.llm_extractor.extract_from_job_description(
                job_text=job_description,
                required_skills=[],
                preferred_skills=[]
            )
            logger.info(f"Extracted {len(jd_extraction.all_keywords)} keywords from job description")
        except Exception as e:
            logger.error(f"LLM extraction failed for job description: {e}")
            # Fallback to technical terms only
            jd_technical = self._extract_technical_terms(job_description)
            jd_extraction = None

        # Extract keywords from optimized resume using LLM
        try:
            resume_extraction = self.llm_extractor.extract_from_resume(
                resume_text=optimized_resume,
                structured_skills=[]
            )
            logger.info(f"Extracted {len(resume_extraction.all_keywords)} keywords from resume")
        except Exception as e:
            logger.error(f"LLM extraction failed for resume: {e}")
            # Fallback to technical terms only
            resume_technical = self._extract_technical_terms(optimized_resume)
            resume_extraction = None

        # If LLM extraction succeeded, use categorized keyword matching
        if jd_extraction and resume_extraction:
            matched, missing, overall_score = self._calculate_llm_based_score(
                jd_extraction,
                resume_extraction
            )
        else:
            # Fallback to technical-only matching
            logger.warning("Using fallback technical-only matching")
            if not jd_extraction:
                jd_technical = self._extract_technical_terms(job_description)
            else:
                jd_technical = set([k.lower() for k in jd_extraction.tools_technologies])

            if not resume_extraction:
                resume_technical = self._extract_technical_terms(optimized_resume)
            else:
                resume_technical = set([k.lower() for k in resume_extraction.tools_technologies])

            matched = jd_technical.intersection(resume_technical)
            missing = jd_technical - resume_technical
            overall_score = len(matched) / len(jd_technical) if jd_technical else 1.0

        # Generate recommendations
        recommendations = []
        if overall_score < self.threshold:
            if missing:
                # Show most important missing keywords (limit to 5)
                top_missing = sorted(list(missing))[:5]
                recommendations.append(f"Add these missing keywords: {', '.join(top_missing)}")
            if overall_score < 0.5:
                recommendations.append("Focus on incorporating more technical terms from the job description")

        return MetricScore(
            name="Role Alignment",
            score=overall_score,
            passed=overall_score >= self.threshold,
            threshold=self.threshold,
            details={
                "total_jd_keywords": len(jd_extraction.all_keywords) if jd_extraction else len(jd_technical) if 'jd_technical' in locals() else 0,
                "matched_keywords": len(matched),
                "missing_keywords": len(missing),
                "matched_list": sorted(list(matched))[:20],  # Top 20 matched
                "missing_list": sorted(list(missing))[:10],  # Top 10 missing
                "extraction_method": "LLM" if (jd_extraction and resume_extraction) else "Technical-Only"
            },
            recommendations=recommendations
        )

    def _calculate_llm_based_score(
        self,
        jd_extraction,
        resume_extraction
    ) -> tuple:
        """
        Calculate score using LLM-extracted categorized keywords.

        Weights:
        - Hard skills: 40%
        - Tools/Technologies: 40%
        - Certifications: 15%
        - Domain terms: 5%
        """
        # Convert to sets for comparison (case-insensitive)
        jd_hard = set([k.lower() for k in jd_extraction.hard_skills])
        jd_tools = set([k.lower() for k in jd_extraction.tools_technologies])
        jd_certs = set([k.lower() for k in jd_extraction.certifications])
        jd_domain = set([k.lower() for k in jd_extraction.domain_terms])

        resume_hard = set([k.lower() for k in resume_extraction.hard_skills])
        resume_tools = set([k.lower() for k in resume_extraction.tools_technologies])
        resume_certs = set([k.lower() for k in resume_extraction.certifications])
        resume_domain = set([k.lower() for k in resume_extraction.domain_terms])

        # Calculate match rates for each category
        hard_match_rate = len(jd_hard & resume_hard) / len(jd_hard) if jd_hard else 1.0
        tools_match_rate = len(jd_tools & resume_tools) / len(jd_tools) if jd_tools else 1.0
        certs_match_rate = len(jd_certs & resume_certs) / len(jd_certs) if jd_certs else 1.0
        domain_match_rate = len(jd_domain & resume_domain) / len(jd_domain) if jd_domain else 1.0

        # Weighted overall score (focus on what matters for ATS)
        overall_score = (
            hard_match_rate * 0.40 +
            tools_match_rate * 0.40 +
            certs_match_rate * 0.15 +
            domain_match_rate * 0.05
        )

        # Calculate overall matched and missing
        jd_all = jd_hard | jd_tools | jd_certs | jd_domain
        resume_all = resume_hard | resume_tools | resume_certs | resume_domain
        matched = jd_all & resume_all
        missing = jd_all - resume_all

        logger.info(f"LLM-based score: {overall_score:.2f} (hard={hard_match_rate:.2f}, tools={tools_match_rate:.2f})")

        return matched, missing, overall_score

    def get_threshold(self) -> float:
        return self.threshold

    def _extract_keywords(self, text: str) -> Set[str]:
        """
        Extract general keywords (DEPRECATED - use LLM extraction instead).

        This fallback method now uses comprehensive stopwords.
        """
        # Extract words 4+ characters, lowercase, alphanumeric
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

        # Use comprehensive stopword list (400+ words)
        keywords = {w for w in words if w not in COMPREHENSIVE_STOPWORDS}

        logger.debug(f"Extracted {len(keywords)} keywords using fallback method")
        return keywords

    def _extract_technical_terms(self, text: str) -> Set[str]:
        """Extract technical terms (programming languages, frameworks, tools)."""

        # Common technical terms (expand this list)
        technical_patterns = [
            # Programming languages
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\btypescript\b',
            r'\bc\+\+\b', r'\bc#\b', r'\bruby\b', r'\bgo\b', r'\brust\b',
            r'\bswift\b', r'\bkotlin\b', r'\bphp\b', r'\bscala\b', r'\bc\b',

            # Frameworks
            r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bdjango\b',
            r'\bflask\b', r'\bspring\b', r'\bexpress\b', r'\bnode\.?js\b',
            r'\bnext\.?js\b', r'\btensorflow\b', r'\bpytorch\b', r'\bjquery\b',
            r'\bbootstrap\b', r'\btailwind\b', r'\b\.net\b', r'\basp\.net\b',

            # Databases
            r'\bpostgresql\b', r'\bpostgres\b', r'\bmysql\b', r'\bmongodb\b',
            r'\bredis\b', r'\belasticsearch\b', r'\bcassandra\b', r'\bsql\b',
            r'\bnosql\b', r'\bsqlite\b', r'\boracle\b', r'\bdynamodb\b',

            # Cloud/DevOps
            r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bdocker\b',
            r'\bkubernetes\b', r'\bk8s\b', r'\bterraform\b', r'\bjenkins\b',
            r'\bgithub actions\b', r'\bci/cd\b', r'\bansible\b', r'\bhelm\b',

            # Tools & Methodologies
            r'\bgit\b', r'\blinux\b', r'\bapi\b', r'\brest\b', r'\bgraphql\b',
            r'\bmicroservices\b', r'\bagile\b', r'\bscrum\b', r'\bkanban\b',
            r'\bjira\b', r'\bconfluence\b', r'\bslack\b', r'\btrello\b',

            # Data & ML
            r'\bmachine learning\b', r'\bdeep learning\b', r'\bnlp\b',
            r'\bdata science\b', r'\bpandas\b', r'\bnumpy\b', r'\bscikit-learn\b',
            r'\bspark\b', r'\bhadoop\b', r'\bairflow\b', r'\btableauб\b',

            # Testing
            r'\bpytest\b', r'\bjest\b', r'\bmocha\b', r'\bjunit\b',
            r'\bselenium\b', r'\bcypress\b', r'\bunit test\b',

            # Other
            r'\bhtml\b', r'\bcss\b', r'\bsass\b', r'\bwebpack\b',
            r'\bbabel\b', r'\bnpm\b', r'\byarn\b', r'\bvscode\b'
        ]

        technical_terms = set()
        text_lower = text.lower()

        for pattern in technical_patterns:
            matches = re.findall(pattern, text_lower)
            technical_terms.update(matches)

        return technical_terms
