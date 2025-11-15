"""
Authenticity Metric
Ensures optimized resume claims are grounded in original resume.
"""

import re
from typing import List, Set, Tuple
from .base import MetricCalculator, MetricScore


class AuthenticityScorer(MetricCalculator):
    """
    Calculates authenticity score by comparing optimized resume claims
    against original resume content.

    Uses heuristic approach to detect potential exaggerations or fabrications.
    For more sophisticated checking, use the AuthenticityAgent from agents/ module.
    """

    def __init__(self, threshold: float = 0.90):
        """
        Initialize Authenticity Scorer.

        Args:
            threshold: Minimum acceptable score (default: 0.90)
        """
        self.threshold = threshold

    def calculate(self, original_resume: str, optimized_resume: str, job_description: str) -> MetricScore:
        """Calculate authenticity score."""

        # Extract claims from optimized resume
        optimized_claims = self._extract_claims(optimized_resume)

        # Extract facts from original resume
        original_facts = self._extract_facts(original_resume)

        # Check for unsupported claims
        unsupported_claims = []
        supported_count = 0

        for claim in optimized_claims:
            if self._is_claim_supported(claim, original_facts, original_resume):
                supported_count += 1
            else:
                unsupported_claims.append(claim)

        # Calculate score
        if len(optimized_claims) > 0:
            score = supported_count / len(optimized_claims)
        else:
            score = 1.0  # No claims to verify

        # Detect specific red flags
        red_flags = self._detect_red_flags(original_resume, optimized_resume)

        # Penalize for red flags
        if red_flags:
            penalty = min(0.3, len(red_flags) * 0.1)
            score = max(0.0, score - penalty)

        # Generate recommendations
        recommendations = []
        if score < self.threshold:
            if unsupported_claims:
                recommendations.append(
                    f"Found {len(unsupported_claims)} potentially unsupported claims. "
                    "Ensure all quantitative achievements have basis in original resume."
                )
            if red_flags:
                recommendations.append(
                    f"Detected {len(red_flags)} red flags: {', '.join(red_flags[:3])}"
                )
            recommendations.append(
                "Consider using the Hallucination Guard (AuthenticityAgent) for detailed verification"
            )

        return MetricScore(
            name="Authenticity",
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            details={
                "total_claims": len(optimized_claims),
                "supported_claims": supported_count,
                "unsupported_claims": len(unsupported_claims),
                "red_flags_count": len(red_flags),
                "red_flags": red_flags[:5],  # Top 5 red flags
                "sample_unsupported": unsupported_claims[:3]  # Sample unsupported claims
            },
            recommendations=recommendations
        )

    def get_threshold(self) -> float:
        return self.threshold

    def _extract_claims(self, resume: str) -> List[str]:
        """
        Extract claims from resume (bullet points, quantifiable statements).

        Focus on:
        - Bullet points
        - Sentences with numbers/percentages
        - Achievement statements
        """
        claims = []

        # Extract bullet points
        bullet_patterns = [
            r'^\s*[-•*]\s+(.+)$',  # Standard bullets
            r'^\s*\d+\.\s+(.+)$',   # Numbered lists
        ]

        for line in resume.split('\n'):
            for pattern in bullet_patterns:
                match = re.match(pattern, line)
                if match:
                    claim = match.group(1).strip()
                    if claim:
                        claims.append(claim)

        # Also extract sentences with quantifiable metrics
        sentences = re.split(r'[.!?]+', resume)
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for numbers, percentages, metrics
            if re.search(r'\d+[%$]?|\b(increased|decreased|improved|reduced|grew|managed|led)\b', sentence, re.IGNORECASE):
                if sentence and sentence not in claims:
                    claims.append(sentence)

        return claims

    def _extract_facts(self, resume: str) -> Set[str]:
        """
        Extract facts from original resume.

        This includes:
        - Numbers and metrics
        - Company names
        - Technologies/tools
        - Skills
        - Role titles
        """
        facts = set()

        # Extract numbers/percentages
        numbers = re.findall(r'\b\d+(?:\.\d+)?[%$]?\b', resume)
        facts.update(numbers)

        # Extract capitalized terms (likely proper nouns, technologies, companies)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', resume)
        facts.update(capitalized)

        # Extract technical terms
        tech_terms = re.findall(
            r'\b(?:Python|Java|JavaScript|React|AWS|Docker|Kubernetes|SQL|'
            r'Machine Learning|AI|API|Cloud|Agile|Scrum)\b',
            resume,
            re.IGNORECASE
        )
        facts.update([t.lower() for t in tech_terms])

        # Extract role-related terms
        role_terms = re.findall(
            r'\b(?:Engineer|Developer|Manager|Lead|Director|Analyst|Architect|'
            r'Designer|Scientist|Specialist|Consultant)\b',
            resume,
            re.IGNORECASE
        )
        facts.update([r.lower() for r in role_terms])

        return facts

    def _is_claim_supported(self, claim: str, facts: Set[str], original_resume: str) -> bool:
        """
        Check if a claim is supported by facts in original resume.

        A claim is considered supported if:
        1. Key numbers/metrics appear in original
        2. Technologies/tools mentioned exist in original
        3. General claim structure is similar to original content
        """
        claim_lower = claim.lower()

        # Extract numbers from claim
        claim_numbers = set(re.findall(r'\b\d+(?:\.\d+)?[%$]?\b', claim))

        # Check if numbers exist in facts
        if claim_numbers:
            # At least one number should be in facts
            if not claim_numbers.intersection(facts):
                return False

        # Extract key terms from claim
        claim_terms = set(re.findall(r'\b[A-Z][a-z]+\b', claim))
        claim_terms.update(re.findall(
            r'\b(?:Python|Java|JavaScript|React|AWS|Docker|SQL|API)\b',
            claim,
            re.IGNORECASE
        ))

        # Check if key terms exist in original
        if claim_terms:
            matching_terms = sum(1 for term in claim_terms if term.lower() in original_resume.lower())
            if matching_terms / len(claim_terms) < 0.5:
                # Less than 50% of terms match
                return False

        # If we got here, claim seems reasonably supported
        return True

    def _detect_red_flags(self, original: str, optimized: str) -> List[str]:
        """
        Detect red flags that might indicate fabrication.

        Red flags:
        - New numbers not in original
        - Inflated percentages (>50% increase)
        - New company names
        - New roles/titles not in original
        """
        red_flags = []

        # Extract numbers from both
        original_numbers = set(re.findall(r'\b\d+(?:\.\d+)?\b', original))
        optimized_numbers = set(re.findall(r'\b\d+(?:\.\d+)?\b', optimized))

        # Check for new numbers
        new_numbers = optimized_numbers - original_numbers
        if len(new_numbers) > 5:
            red_flags.append(f"{len(new_numbers)} new numbers not found in original")

        # Check for percentage inflation
        original_percentages = [float(x) for x in re.findall(r'\b(\d+(?:\.\d+)?)%', original)]
        optimized_percentages = [float(x) for x in re.findall(r'\b(\d+(?:\.\d+)?)%', optimized)]

        if optimized_percentages and original_percentages:
            max_opt = max(optimized_percentages)
            max_orig = max(original_percentages) if original_percentages else 0
            if max_opt > max_orig * 1.5:
                red_flags.append(f"Percentage inflation detected: {max_opt}% vs {max_orig}%")

        # Check for new capitalized terms (potential new companies/technologies)
        original_caps = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', original))
        optimized_caps = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', optimized))

        new_caps = optimized_caps - original_caps
        # Filter out common words
        common_words = {'The', 'This', 'That', 'These', 'Those', 'From', 'With', 'When', 'Where'}
        new_caps = new_caps - common_words

        if len(new_caps) > 10:
            red_flags.append(f"{len(new_caps)} new capitalized terms (potential new companies/products)")

        # Check for completely new roles
        role_keywords = ['Engineer', 'Developer', 'Manager', 'Lead', 'Director', 'Architect', 'Designer']
        original_roles = set()
        optimized_roles = set()

        for keyword in role_keywords:
            if keyword in original:
                original_roles.add(keyword)
            if keyword in optimized:
                optimized_roles.add(keyword)

        new_roles = optimized_roles - original_roles
        if len(new_roles) > 2:
            red_flags.append(f"New role titles added: {', '.join(new_roles)}")

        return red_flags
