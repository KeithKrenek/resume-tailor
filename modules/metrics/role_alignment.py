"""
Role Alignment Metric
Measures how well the resume matches job requirements.
"""

import re
from typing import List, Set
from .base import MetricCalculator, MetricScore


class RoleAlignmentScorer(MetricCalculator):
    """Calculates role alignment score based on keyword matching."""

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def calculate(self, original_resume: str, optimized_resume: str, job_description: str) -> MetricScore:
        """Calculate role alignment score."""

        # Extract keywords from job description
        jd_keywords = self._extract_keywords(job_description)
        jd_technical = self._extract_technical_terms(job_description)
        jd_all = jd_keywords.union(jd_technical)

        # Extract keywords from optimized resume
        resume_keywords = self._extract_keywords(optimized_resume)
        resume_technical = self._extract_technical_terms(optimized_resume)
        resume_all = resume_keywords.union(resume_technical)

        # Calculate matches
        matched = jd_all.intersection(resume_all)
        missing = jd_all - resume_all

        # Calculate score (weighted by importance)
        technical_match_rate = len(jd_technical.intersection(resume_technical)) / len(jd_technical) if jd_technical else 1.0
        keyword_match_rate = len(jd_keywords.intersection(resume_keywords)) / len(jd_keywords) if jd_keywords else 1.0

        # Technical terms weighted higher (70% technical, 30% general keywords)
        overall_score = (technical_match_rate * 0.7) + (keyword_match_rate * 0.3)

        # Generate recommendations
        recommendations = []
        if overall_score < self.threshold:
            if missing:
                top_missing = sorted(list(missing))[:5]
                recommendations.append(f"Add these missing keywords: {', '.join(top_missing)}")
            if technical_match_rate < 0.7:
                recommendations.append("Focus on incorporating more technical terms from the job description")

        return MetricScore(
            name="Role Alignment",
            score=overall_score,
            passed=overall_score >= self.threshold,
            threshold=self.threshold,
            details={
                "total_jd_keywords": len(jd_all),
                "matched_keywords": len(matched),
                "missing_keywords": len(missing),
                "technical_match_rate": technical_match_rate,
                "keyword_match_rate": keyword_match_rate,
                "matched_list": sorted(list(matched)),
                "missing_list": sorted(list(missing))[:10]  # Top 10 missing
            },
            recommendations=recommendations
        )

    def get_threshold(self) -> float:
        return self.threshold

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract general keywords (nouns, verbs, adjectives)."""
        # Simple approach: extract words 4+ characters, lowercase, alphanumeric
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

        # Filter out common stop words
        stop_words = {
            'about', 'after', 'before', 'during', 'from', 'into', 'through',
            'that', 'this', 'these', 'those', 'with', 'will', 'would', 'should',
            'could', 'have', 'been', 'being', 'their', 'there', 'where', 'when',
            'what', 'which', 'while', 'work', 'working', 'experience', 'ability',
            'apply', 'applicant', 'candidate', 'position', 'role', 'company',
            'team', 'strong', 'good', 'great', 'excellent', 'required', 'preferred'
        }

        keywords = {w for w in words if w not in stop_words}
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
