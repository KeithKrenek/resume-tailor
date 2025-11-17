"""
LLM-Based Intelligent Keyword Extraction

Uses Claude AI to extract meaningful, context-aware keywords from job descriptions
and resumes, filtering out noise and focusing on professionally relevant terms.
"""

import os
import json
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
from utils.logging_config import get_logger

logger = get_logger(__name__)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available - LLM keyword extraction disabled")

from config.settings import ANTHROPIC_API_KEY, DEFAULT_MODEL


# Comprehensive industry-standard stopword list (400+ words)
COMPREHENSIVE_STOPWORDS = {
    # Articles & Determiners
    'a', 'an', 'the', 'this', 'that', 'these', 'those',

    # Pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their', 'theirs',
    'my', 'your', 'his', 'her', 'its', 'our', 'yours', 'mine', 'ours',
    'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves',
    'who', 'whom', 'whose', 'which', 'what', 'whatever', 'whichever',

    # Prepositions
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among',
    'under', 'over', 'about', 'against', 'along', 'around', 'across', 'behind',
    'beside', 'besides', 'beyond', 'down', 'inside', 'near', 'off', 'outside',
    'toward', 'towards', 'upon', 'within', 'without', 'throughout',

    # Conjunctions
    'and', 'or', 'but', 'nor', 'so', 'yet', 'because', 'although', 'though',
    'while', 'whereas', 'if', 'unless', 'until', 'since', 'when', 'whenever',
    'where', 'wherever', 'whether', 'than',

    # Auxiliary & Modal Verbs
    'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'done',
    'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could',

    # Common Verbs (Too Generic)
    'get', 'got', 'getting', 'give', 'given', 'giving', 'take', 'took', 'taken',
    'make', 'made', 'making', 'go', 'went', 'gone', 'going', 'come', 'came',
    'become', 'became', 'becoming', 'seem', 'seemed', 'seeming', 'appears',
    'appear', 'appeared', 'appearing', 'look', 'looked', 'looking', 'looks',

    # Generic Adverbs
    'very', 'too', 'quite', 'rather', 'somewhat', 'somehow', 'somewhere',
    'anywhere', 'everywhere', 'nowhere', 'always', 'never', 'often', 'sometimes',
    'usually', 'frequently', 'rarely', 'seldom', 'already', 'just', 'only',
    'also', 'even', 'still', 'almost', 'nearly', 'hardly', 'barely', 'really',
    'actually', 'especially', 'particularly', 'generally', 'specifically',

    # Quantifiers & Numbers (generic)
    'all', 'any', 'some', 'many', 'much', 'few', 'little', 'more', 'most',
    'less', 'least', 'several', 'every', 'each', 'both', 'either', 'neither',
    'none', 'no', 'not', 'nor', 'other', 'another', 'such', 'same', 'different',

    # Generic Adjectives (Too Common)
    'good', 'better', 'best', 'bad', 'worse', 'worst', 'great', 'big', 'small',
    'large', 'little', 'long', 'short', 'high', 'low', 'new', 'old', 'young',
    'early', 'late', 'right', 'wrong', 'true', 'false', 'real', 'actual',
    'possible', 'impossible', 'easy', 'hard', 'difficult', 'simple', 'complex',
    'important', 'main', 'major', 'minor', 'primary', 'secondary', 'first',
    'last', 'next', 'previous', 'following', 'own', 'same', 'similar', 'different',
    'certain', 'sure', 'clear', 'full', 'complete', 'total', 'whole', 'entire',
    'single', 'double', 'few', 'several', 'various', 'available', 'current',

    # Generic Nouns (Too Vague for Keyword Matching)
    'able', 'ability', 'access', 'action', 'active', 'activity', 'actual',
    'adapt', 'addition', 'address', 'advantage', 'age', 'agent', 'agree',
    'agreement', 'ahead', 'allow', 'amount', 'answer', 'anyone', 'anything',
    'apply', 'applicant', 'approach', 'area', 'around', 'article', 'ask',
    'aspect', 'assume', 'attempt', 'attention', 'available', 'average', 'avoid',
    'away', 'back', 'base', 'basic', 'basis', 'become', 'begin', 'beginning',
    'behind', 'believe', 'benefit', 'better', 'beyond', 'body', 'book', 'bring',
    'build', 'business', 'call', 'candidate', 'care', 'carry', 'case', 'cause',
    'center', 'central', 'century', 'certain', 'certainly', 'challenge', 'change',
    'character', 'check', 'choice', 'choose', 'class', 'clear', 'close', 'cold',
    'collect', 'come', 'comment', 'common', 'community', 'company', 'compare',
    'complete', 'concern', 'condition', 'consider', 'contain', 'continue',
    'control', 'cost', 'count', 'country', 'course', 'cover', 'create', 'current',
    'customer', 'date', 'deal', 'decide', 'decision', 'deep', 'degree', 'describe',
    'design', 'detail', 'determine', 'develop', 'difference', 'direct', 'discover',
    'discuss', 'discussion', 'doctor', 'door', 'drive', 'drop', 'during', 'each',
    'early', 'east', 'easy', 'economic', 'economy', 'edge', 'education', 'effect',
    'effort', 'eight', 'either', 'else', 'encourage', 'end', 'energy', 'enough',
    'ensure', 'enter', 'entire', 'environment', 'equal', 'especially', 'establish',
    'evening', 'event', 'ever', 'every', 'everyone', 'everything', 'evidence',
    'exactly', 'example', 'exist', 'expect', 'experience', 'explain', 'face',
    'fact', 'factor', 'fall', 'family', 'fast', 'father', 'feel', 'feeling',
    'field', 'figure', 'fill', 'final', 'finally', 'find', 'fine', 'finger',
    'finish', 'fire', 'firm', 'five', 'floor', 'focus', 'follow', 'food',
    'foot', 'force', 'foreign', 'forget', 'form', 'former', 'forward', 'four',
    'free', 'friend', 'front', 'full', 'function', 'fund', 'future', 'gain',
    'general', 'glass', 'goal', 'going', 'gone', 'ground', 'group', 'grow',
    'growth', 'guess', 'guide', 'hand', 'handle', 'hang', 'happen', 'happy',
    'hard', 'head', 'health', 'hear', 'heart', 'heat', 'heavy', 'help', 'here',
    'herself', 'high', 'himself', 'history', 'hit', 'hold', 'home', 'hope',
    'hot', 'hotel', 'hour', 'house', 'however', 'huge', 'human', 'hundred',
    'idea', 'identify', 'image', 'imagine', 'impact', 'include', 'including',
    'increase', 'indeed', 'indicate', 'individual', 'industry', 'information',
    'inside', 'instead', 'interest', 'international', 'interview', 'involve',
    'issue', 'item', 'itself', 'join', 'keep', 'kind', 'king', 'kitchen',
    'know', 'knowledge', 'land', 'language', 'large', 'later', 'laugh', 'law',
    'lay', 'lead', 'learn', 'least', 'leave', 'left', 'legal', 'less', 'let',
    'letter', 'level', 'life', 'light', 'like', 'likely', 'line', 'list',
    'listen', 'little', 'live', 'local', 'long', 'lose', 'loss', 'love',
    'machine', 'magazine', 'main', 'maintain', 'major', 'majority', 'make',
    'manage', 'manager', 'manner', 'many', 'market', 'marriage', 'material',
    'matter', 'maybe', 'mean', 'meaning', 'measure', 'media', 'medical',
    'meet', 'meeting', 'member', 'memory', 'mention', 'message', 'method',
    'middle', 'might', 'military', 'million', 'mind', 'minute', 'miss',
    'mission', 'model', 'modern', 'moment', 'money', 'month', 'more', 'morning',
    'most', 'mother', 'mouth', 'move', 'movement', 'movie', 'much', 'music',
    'myself', 'name', 'nation', 'national', 'natural', 'nature', 'near',
    'nearly', 'necessary', 'neck', 'need', 'network', 'never', 'news',
    'newspaper', 'next', 'night', 'nine', 'nobody', 'none', 'north', 'note',
    'nothing', 'notice', 'number', 'occur', 'offer', 'office', 'officer',
    'official', 'often', 'once', 'one', 'only', 'onto', 'open', 'operation',
    'opportunity', 'option', 'order', 'organization', 'other', 'others',
    'otherwise', 'ought', 'outside', 'over', 'overall', 'owner', 'page',
    'pain', 'painting', 'paper', 'parent', 'part', 'participant', 'particular',
    'particularly', 'partner', 'party', 'pass', 'past', 'patient', 'pattern',
    'pay', 'peace', 'people', 'per', 'perform', 'performance', 'perhaps',
    'period', 'person', 'personal', 'phone', 'physical', 'pick', 'picture',
    'piece', 'place', 'plan', 'plant', 'play', 'player', 'point', 'police',
    'policy', 'political', 'politics', 'poor', 'popular', 'population',
    'position', 'positive', 'possible', 'power', 'practice', 'prepare',
    'present', 'president', 'pressure', 'pretty', 'prevent', 'price', 'private',
    'probably', 'problem', 'process', 'produce', 'product', 'production',
    'professional', 'professor', 'program', 'project', 'property', 'protect',
    'prove', 'provide', 'public', 'pull', 'purpose', 'push', 'quality',
    'question', 'quickly', 'quite', 'race', 'radio', 'raise', 'range', 'rate',
    'rather', 'reach', 'read', 'ready', 'real', 'reality', 'realize', 'really',
    'reason', 'receive', 'recent', 'recently', 'recognize', 'record', 'reduce',
    'reflect', 'region', 'relate', 'relationship', 'remain', 'remember',
    'remove', 'report', 'represent', 'require', 'required', 'research',
    'resource', 'respond', 'response', 'responsibility', 'rest', 'result',
    'return', 'reveal', 'rich', 'right', 'rise', 'risk', 'road', 'rock',
    'role', 'room', 'rule', 'safe', 'same', 'save', 'saying', 'scene',
    'school', 'science', 'scientist', 'score', 'sea', 'season', 'seat',
    'second', 'section', 'security', 'seek', 'seem', 'sell', 'send', 'senior',
    'sense', 'series', 'serious', 'serve', 'service', 'seven', 'several',
    'shake', 'share', 'sheet', 'shoot', 'short', 'shot', 'shoulder', 'show',
    'side', 'sign', 'significant', 'similar', 'simple', 'simply', 'since',
    'sing', 'single', 'sister', 'site', 'situation', 'size', 'skill',
    'skin', 'small', 'smile', 'social', 'society', 'soldier', 'some',
    'somebody', 'someone', 'something', 'sometimes', 'song', 'soon', 'sort',
    'sound', 'source', 'south', 'southern', 'space', 'speak', 'special',
    'specific', 'speech', 'spend', 'sport', 'spring', 'staff', 'stage',
    'stand', 'standard', 'star', 'start', 'state', 'statement', 'station',
    'stay', 'step', 'still', 'stock', 'stop', 'store', 'story', 'strategy',
    'street', 'strong', 'structure', 'student', 'study', 'stuff', 'style',
    'subject', 'success', 'successful', 'such', 'suddenly', 'suffer', 'suggest',
    'summer', 'support', 'sure', 'surface', 'system', 'table', 'take', 'talk',
    'task', 'teach', 'teacher', 'team', 'technology', 'television', 'tell',
    'tend', 'term', 'test', 'text', 'than', 'thank', 'their', 'them',
    'themselves', 'then', 'theory', 'there', 'these', 'they', 'thing', 'think',
    'third', 'though', 'thought', 'thousand', 'threat', 'three', 'through',
    'throughout', 'throw', 'thus', 'time', 'today', 'together', 'tonight',
    'total', 'tough', 'toward', 'town', 'trade', 'traditional', 'training',
    'travel', 'treat', 'treatment', 'tree', 'trial', 'trip', 'trouble', 'true',
    'truth', 'turn', 'type', 'under', 'understand', 'unit', 'until', 'upon',
    'usual', 'value', 'various', 'very', 'victim', 'view', 'violence', 'visit',
    'voice', 'vote', 'wait', 'walk', 'wall', 'want', 'watch', 'water', 'way',
    'weapon', 'wear', 'week', 'weight', 'well', 'west', 'western', 'what',
    'whatever', 'when', 'where', 'whether', 'which', 'while', 'white', 'whole',
    'whom', 'whose', 'wide', 'wife', 'will', 'wind', 'window', 'wish', 'with',
    'within', 'without', 'woman', 'wonder', 'word', 'work', 'worker', 'working',
    'world', 'worry', 'worth', 'would', 'write', 'writer', 'wrong', 'yard',
    'yeah', 'year', 'yes', 'yesterday', 'young',

    # Job Description Specific (Too Generic)
    'excellent', 'preferred', 'plus', 'candidate', 'applicant', 'apply',
    'application', 'hiring', 'seeking', 'looking', 'equal', 'employer',
    'employment', 'diverse', 'diversity', 'inclusion', 'location', 'remote',
    'office', 'hybrid', 'fulltime', 'parttime', 'contract', 'permanent',
    'temporary', 'compensation', 'salary', 'benefits', 'bonus', 'equity',
    'package', 'perks', 'culture', 'values', 'mission', 'vision',
}


@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction."""
    # Core keywords by category
    hard_skills: List[str] = field(default_factory=list)  # Technical skills
    soft_skills: List[str] = field(default_factory=list)  # Soft skills
    tools_technologies: List[str] = field(default_factory=list)  # Tools, frameworks, languages
    certifications: List[str] = field(default_factory=list)  # Certs and qualifications
    domain_terms: List[str] = field(default_factory=list)  # Industry-specific terminology

    # Metadata
    all_keywords: List[str] = field(default_factory=list)  # All keywords combined
    keyword_frequencies: Dict[str, int] = field(default_factory=dict)  # Frequency counts
    is_llm_extracted: bool = False  # Whether LLM was used

    def get_weighted_keywords(self) -> Dict[str, int]:
        """Get keywords with importance weights."""
        weighted = Counter()

        # Hard skills and tools are most important (weight: 3)
        for keyword in self.hard_skills + self.tools_technologies:
            weighted[keyword.lower()] += 3

        # Certifications (weight: 2)
        for keyword in self.certifications:
            weighted[keyword.lower()] += 2

        # Domain terms and soft skills (weight: 1)
        for keyword in self.domain_terms + self.soft_skills:
            weighted[keyword.lower()] += 1

        return dict(weighted)

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary."""
        return {
            'hard_skills': self.hard_skills,
            'soft_skills': self.soft_skills,
            'tools_technologies': self.tools_technologies,
            'certifications': self.certifications,
            'domain_terms': self.domain_terms,
            'all_keywords': self.all_keywords,
            'keyword_frequencies': self.keyword_frequencies,
            'is_llm_extracted': self.is_llm_extracted,
        }


class LLMKeywordExtractor:
    """
    Production-grade LLM-based keyword extractor.

    Uses Claude AI to intelligently extract meaningful keywords from text,
    with fallback to rule-based extraction when LLM is unavailable.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the keyword extractor.

        Args:
            api_key: Anthropic API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or ANTHROPIC_API_KEY or os.getenv('ANTHROPIC_API_KEY')
        self.client = None

        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("LLM Keyword Extractor initialized with Claude API")
            except Exception as e:
                logger.error(f"Could not initialize Anthropic client: {e}")
                self.client = None
        else:
            logger.warning("LLM Keyword Extractor initialized in fallback mode (no API)")

    def extract_from_job_description(
        self,
        job_text: str,
        required_skills: Optional[List[str]] = None,
        preferred_skills: Optional[List[str]] = None
    ) -> KeywordExtractionResult:
        """
        Extract keywords from job description.

        Args:
            job_text: Raw job description text
            required_skills: Pre-extracted required skills (optional)
            preferred_skills: Pre-extracted preferred skills (optional)

        Returns:
            KeywordExtractionResult with categorized keywords
        """
        if self.client:
            try:
                return self._extract_with_llm(
                    text=job_text,
                    context="job_description",
                    structured_skills={
                        'required': required_skills or [],
                        'preferred': preferred_skills or []
                    }
                )
            except Exception as e:
                logger.error(f"LLM extraction failed, falling back to rule-based: {e}")
                return self._extract_with_rules(job_text, required_skills, preferred_skills)
        else:
            logger.info("Using rule-based extraction (LLM unavailable)")
            return self._extract_with_rules(job_text, required_skills, preferred_skills)

    def extract_from_resume(
        self,
        resume_text: str,
        structured_skills: Optional[List[str]] = None
    ) -> KeywordExtractionResult:
        """
        Extract keywords from resume.

        Args:
            resume_text: Raw resume text
            structured_skills: Pre-extracted skills from resume parser (optional)

        Returns:
            KeywordExtractionResult with categorized keywords
        """
        if self.client:
            try:
                return self._extract_with_llm(
                    text=resume_text,
                    context="resume",
                    structured_skills={'existing': structured_skills or []}
                )
            except Exception as e:
                logger.error(f"LLM extraction failed, falling back to rule-based: {e}")
                return self._extract_with_rules(resume_text, structured_skills, [])
        else:
            logger.info("Using rule-based extraction (LLM unavailable)")
            return self._extract_with_rules(resume_text, structured_skills, [])

    def _extract_with_llm(
        self,
        text: str,
        context: str,
        structured_skills: Dict[str, List[str]]
    ) -> KeywordExtractionResult:
        """Extract keywords using Claude AI."""
        logger.info(f"Extracting keywords with LLM (context: {context})")

        # Build prompt based on context
        if context == "job_description":
            prompt = self._build_job_extraction_prompt(text, structured_skills)
        else:  # resume
            prompt = self._build_resume_extraction_prompt(text, structured_skills)

        # Call Claude API
        response = self.client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=2000,
            temperature=0,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = response.content[0].text
        logger.debug(f"LLM response: {response_text[:200]}...")

        # Extract JSON from response
        result_data = self._parse_json_response(response_text)

        if not result_data:
            logger.error("Failed to parse LLM response, falling back to rules")
            return self._extract_with_rules(
                text,
                structured_skills.get('required', []) + structured_skills.get('existing', []),
                structured_skills.get('preferred', [])
            )

        # Create result object
        result = KeywordExtractionResult(
            hard_skills=result_data.get('hard_skills', []),
            soft_skills=result_data.get('soft_skills', []),
            tools_technologies=result_data.get('tools_technologies', []),
            certifications=result_data.get('certifications', []),
            domain_terms=result_data.get('domain_terms', []),
            is_llm_extracted=True
        )

        # Combine all keywords
        result.all_keywords = (
            result.hard_skills +
            result.soft_skills +
            result.tools_technologies +
            result.certifications +
            result.domain_terms
        )

        # Calculate frequencies
        result.keyword_frequencies = Counter([kw.lower() for kw in result.all_keywords])

        logger.info(f"LLM extracted {len(result.all_keywords)} keywords")
        return result

    def _extract_with_rules(
        self,
        text: str,
        required_skills: Optional[List[str]],
        preferred_skills: Optional[List[str]]
    ) -> KeywordExtractionResult:
        """
        Fallback rule-based extraction.

        Uses technical term patterns and filters out stopwords.
        More sophisticated than the original implementation.
        """
        logger.info("Extracting keywords with rule-based approach")

        import re

        # Technical term patterns (expanded)
        technical_patterns = [
            # Programming languages
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\btypescript\b',
            r'\bc\+\+\b', r'\bc#\b', r'\bruby\b', r'\bgo\b', r'\brust\b',
            r'\bswift\b', r'\bkotlin\b', r'\bphp\b', r'\bscala\b', r'\bc\b',
            r'\bperl\b', r'\br\b', r'\bmatlab\b', r'\bvba\b', r'\bsql\b',

            # Frameworks & Libraries
            r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bdjango\b',
            r'\bflask\b', r'\bspring\b', r'\bexpress\b', r'\bnode\.?js\b',
            r'\bnext\.?js\b', r'\bnuxt\.?js\b', r'\btensorflow\b', r'\bpytorch\b',
            r'\bjquery\b', r'\bbootstrap\b', r'\btailwind\b', r'\b\.net\b',
            r'\basp\.net\b', r'\blaravel\b', r'\brails\b', r'\bfastapi\b',

            # Databases
            r'\bpostgresql\b', r'\bpostgres\b', r'\bmysql\b', r'\bmongodb\b',
            r'\bredis\b', r'\belasticsearch\b', r'\bcassandra\b', r'\bnosql\b',
            r'\bsqlite\b', r'\boracle\b', r'\bdynamodb\b', r'\bmariadb\b',
            r'\bcouchdb\b', r'\bneo4j\b', r'\bmssql\b',

            # Cloud & Infrastructure
            r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bgoogle cloud\b',
            r'\bdocker\b', r'\bkubernetes\b', r'\bk8s\b', r'\bterraform\b',
            r'\bjenkins\b', r'\bgithub actions\b', r'\bgitlab ci\b', r'\bci/cd\b',
            r'\bansible\b', r'\bhelm\b', r'\bvagrant\b', r'\bchef\b', r'\bpuppet\b',

            # Tools & Platforms
            r'\bgit\b', r'\bgithub\b', r'\bgitlab\b', r'\bbitbucket\b',
            r'\blinux\b', r'\bunix\b', r'\bwindows\b', r'\bmacos\b',
            r'\bjira\b', r'\bconfluence\b', r'\bslack\b', r'\btrello\b',
            r'\basana\b', r'\bnotion\b', r'\bmiro\b', r'\bfigma\b',

            # APIs & Protocols
            r'\brest\b', r'\brestful\b', r'\bgraphql\b', r'\bgrpc\b',
            r'\bsoap\b', r'\bhttp\b', r'\bhttps\b', r'\bwebsocket\b',
            r'\bapi\b', r'\bmicroservices\b', r'\bserverless\b',

            # Methodologies
            r'\bagile\b', r'\bscrum\b', r'\bkanban\b', r'\bdevops\b',
            r'\btdd\b', r'\bbdd\b', r'\bci/cd\b', r'\btest-driven\b',

            # Data & ML
            r'\bmachine learning\b', r'\bdeep learning\b', r'\bnlp\b',
            r'\bnatural language processing\b', r'\bdata science\b',
            r'\bpandas\b', r'\bnumpy\b', r'\bscikit-learn\b', r'\bspark\b',
            r'\bhadoop\b', r'\bairflow\b', r'\btableau\b', r'\bpower bi\b',
            r'\bkafka\b', r'\bflink\b',

            # Testing
            r'\bpytest\b', r'\bjest\b', r'\bmocha\b', r'\bjunit\b',
            r'\bselenium\b', r'\bcypress\b', r'\bunit test\b', r'\bintegration test\b',

            # Web Technologies
            r'\bhtml\b', r'\bhtml5\b', r'\bcss\b', r'\bcss3\b', r'\bsass\b',
            r'\bscss\b', r'\bless\b', r'\bwebpack\b', r'\bbabel\b', r'\bnpm\b',
            r'\byarn\b', r'\bpnpm\b', r'\bvite\b', r'\brollup\b',

            # Certifications
            r'\baws certified\b', r'\bazure certified\b', r'\bgcp certified\b',
            r'\bpmp\b', r'\bcism\b', r'\bcissp\b', r'\bccna\b', r'\bceh\b',
        ]

        # Extract technical terms
        text_lower = text.lower()
        technical_terms = set()

        for pattern in technical_patterns:
            matches = re.findall(pattern, text_lower)
            technical_terms.update(matches)

        # Extract other meaningful words (4+ chars, not stopwords)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text_lower)
        meaningful_words = {
            w for w in words
            if w not in COMPREHENSIVE_STOPWORDS
        }

        # Combine with structured skills
        all_keywords = list(technical_terms | meaningful_words)

        if required_skills:
            all_keywords.extend([s.lower() for s in required_skills])
        if preferred_skills:
            all_keywords.extend([s.lower() for s in preferred_skills])

        # Remove duplicates
        all_keywords = list(set(all_keywords))

        # Create result (can't categorize without LLM, so put most in tools_technologies)
        result = KeywordExtractionResult(
            hard_skills=list(required_skills or []),
            soft_skills=[],
            tools_technologies=list(technical_terms),
            certifications=[],
            domain_terms=list(meaningful_words - technical_terms)[:50],  # Limit domain terms
            is_llm_extracted=False
        )

        result.all_keywords = all_keywords
        result.keyword_frequencies = Counter(all_keywords)

        logger.info(f"Rule-based extracted {len(all_keywords)} keywords")
        return result

    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM extraction."""
        return """You are an expert ATS (Applicant Tracking System) keyword extraction specialist.

Your task is to extract MEANINGFUL, PROFESSIONALLY RELEVANT keywords from text.

IMPORTANT: Exclude common English words, generic business terms, and vague descriptors.

Focus on extracting:
1. **Hard Skills**: Specific technical abilities, domain expertise
2. **Soft Skills**: Leadership, communication, teamwork, problem-solving
3. **Tools & Technologies**: Programming languages, frameworks, software, platforms
4. **Certifications**: Professional certifications, licenses, qualifications
5. **Domain Terms**: Industry-specific terminology, specialized vocabulary

DO NOT include:
- Common words (able, access, active, above, etc.)
- Generic verbs (make, do, have, get, etc.)
- Generic adjectives (good, great, excellent, strong, etc.)
- Generic nouns (company, team, role, position, etc.)
- Articles, prepositions, conjunctions

Return your analysis as a JSON object with this structure:
{
  "hard_skills": ["skill1", "skill2", ...],
  "soft_skills": ["skill1", "skill2", ...],
  "tools_technologies": ["tool1", "tool2", ...],
  "certifications": ["cert1", "cert2", ...],
  "domain_terms": ["term1", "term2", ...]
}

Be thorough but discriminating. Quality over quantity."""

    def _build_job_extraction_prompt(
        self,
        job_text: str,
        structured_skills: Dict[str, List[str]]
    ) -> str:
        """Build prompt for job description extraction."""
        prompt = "Extract meaningful keywords from this job description.\n\n"

        if structured_skills.get('required'):
            prompt += f"Pre-identified Required Skills: {', '.join(structured_skills['required'])}\n"
        if structured_skills.get('preferred'):
            prompt += f"Pre-identified Preferred Skills: {', '.join(structured_skills['preferred'])}\n"

        prompt += f"\nJob Description:\n{job_text}\n\n"
        prompt += "Return only the JSON object, no additional text."

        return prompt

    def _build_resume_extraction_prompt(
        self,
        resume_text: str,
        structured_skills: Dict[str, List[str]]
    ) -> str:
        """Build prompt for resume extraction."""
        prompt = "Extract meaningful keywords from this resume.\n\n"

        if structured_skills.get('existing'):
            prompt += f"Pre-identified Skills: {', '.join(structured_skills['existing'])}\n\n"

        prompt += f"Resume:\n{resume_text}\n\n"
        prompt += "Return only the JSON object, no additional text."

        return prompt

    def _parse_json_response(self, response_text: str) -> Optional[Dict]:
        """Parse JSON from LLM response."""
        from utils.json_utils import extract_json_object
        return extract_json_object(response_text)


# Convenience functions
def extract_job_keywords(
    job_text: str,
    required_skills: Optional[List[str]] = None,
    preferred_skills: Optional[List[str]] = None,
    api_key: Optional[str] = None
) -> KeywordExtractionResult:
    """
    Extract keywords from job description.

    Args:
        job_text: Raw job description text
        required_skills: Pre-extracted required skills (optional)
        preferred_skills: Pre-extracted preferred skills (optional)
        api_key: Anthropic API key (optional)

    Returns:
        KeywordExtractionResult
    """
    extractor = LLMKeywordExtractor(api_key=api_key)
    return extractor.extract_from_job_description(job_text, required_skills, preferred_skills)


def extract_resume_keywords(
    resume_text: str,
    structured_skills: Optional[List[str]] = None,
    api_key: Optional[str] = None
) -> KeywordExtractionResult:
    """
    Extract keywords from resume.

    Args:
        resume_text: Raw resume text
        structured_skills: Pre-extracted skills (optional)
        api_key: Anthropic API key (optional)

    Returns:
        KeywordExtractionResult
    """
    extractor = LLMKeywordExtractor(api_key=api_key)
    return extractor.extract_from_resume(resume_text, structured_skills)
