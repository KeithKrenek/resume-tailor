"""Agent for simulating ATS (Applicant Tracking System) parsing and analysis."""

import os
import re
from typing import Tuple, Optional, Dict, Any, List
from anthropic import Anthropic
from utils.logging_config import get_logger

logger = get_logger(__name__)


def simulate_ats_parsing(
    resume_text: str,
    job_description: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514"
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Simulate how an ATS system would parse and analyze a resume.

    Args:
        resume_text: Resume text to analyze
        job_description: Optional job description for keyword matching
        api_key: Anthropic API key
        model: Model to use for simulation

    Returns:
        Tuple of (success, ats_report, error_message)
    """
    try:
        # Get API key
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            return False, None, "No API key available"

        # Initialize client
        client = Anthropic(api_key=key)

        # Build prompt
        prompt = build_ats_simulation_prompt(resume_text, job_description)

        # Call API
        logger.info(f"Running ATS simulation via {model}")
        message = client.messages.create(
            model=model,
            max_tokens=3000,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract response
        if message.content and len(message.content) > 0:
            response_text = message.content[0].text.strip()

            # Parse JSON response
            import json
            try:
                ats_report = json.loads(response_text)

                # Add basic keyword analysis
                if job_description:
                    keyword_analysis = analyze_keyword_matching(resume_text, job_description)
                    ats_report['keyword_analysis'] = keyword_analysis

                logger.info("ATS simulation successful")
                return True, ats_report, ""
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse ATS response: {e}")
                return False, None, f"Failed to parse response: {str(e)}"
        else:
            logger.error("Empty response from API")
            return False, None, "Empty response from API"

    except Exception as e:
        logger.error(f"ATS simulation failed: {str(e)}", exc_info=True)
        return False, None, str(e)


def build_ats_simulation_prompt(resume_text: str, job_description: Optional[str] = None) -> str:
    """Build prompt for ATS simulation."""

    prompt = f"""You are simulating an Applicant Tracking System (ATS) that parses and analyzes resumes.

**Resume Text:**
{resume_text}

{"**Job Description:**\n" + job_description[:1000] + "..." if job_description else ""}

**Your Task:**
Analyze this resume as an ATS system would, and provide a comprehensive report in JSON format.

**Analysis Areas:**

1. **Parsing Quality** (0-100):
   - How well-structured is the resume for ATS parsing?
   - Are sections clearly identifiable?
   - Is formatting simple and clean?

2. **Contact Information Extraction** (0-100):
   - Can you easily extract name, email, phone, location?
   - Is contact info at the top and clearly formatted?

3. **Section Identification** (0-100):
   - Can you identify: Experience, Education, Skills, Summary?
   - Are section headers clear and standard?

4. **Keyword Density** (0-100):
   - Does the resume contain relevant keywords?
   - Are keywords naturally integrated?
   - Appropriate keyword frequency?

5. **Format Compatibility** (0-100):
   - Simple formatting (no tables, columns, headers/footers)?
   - Standard fonts and text?
   - No images or graphics?

6. **Experience Parsing** (0-100):
   - Can you extract job titles, companies, dates?
   - Are responsibilities clearly listed?
   - Consistent date formats?

**Response Format (JSON):**
```json
{{
  "overall_score": 85,
  "overall_grade": "B+",
  "parsing_quality": 90,
  "contact_extraction": 95,
  "section_identification": 85,
  "keyword_density": 80,
  "format_compatibility": 90,
  "experience_parsing": 85,
  "passed_ats": true,
  "critical_issues": [
    "No phone number detected",
    "Skills section header not standard"
  ],
  "warnings": [
    "Summary could include more keywords",
    "Some dates are inconsistent format"
  ],
  "recommendations": [
    "Add phone number to contact information",
    "Use standard section header 'Skills' instead of 'Core Competencies'",
    "Include more industry keywords in experience descriptions",
    "Ensure all dates follow MM/YYYY format"
  ],
  "extracted_data": {{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": null,
    "location": "San Francisco, CA",
    "sections_found": ["Summary", "Experience", "Education", "Skills"],
    "years_of_experience": 8,
    "education_level": "Bachelor's Degree"
  }},
  "ats_view": "Brief summary of what the ATS 'sees' - clean text extraction"
}}
```

**Important:**
- Be realistic about ATS limitations
- Identify issues that would cause parsing failures
- Provide actionable recommendations
- Consider standard ATS behavior

Return ONLY the JSON, no other text."""

    return prompt


def analyze_keyword_matching(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Analyze keyword matching between resume and job description.

    Args:
        resume_text: Resume text
        job_description: Job description text

    Returns:
        Keyword analysis dictionary
    """
    # Extract keywords from job description
    job_keywords = extract_keywords(job_description)

    # Extract keywords from resume
    resume_keywords = extract_keywords(resume_text)

    # Find matches
    matched_keywords = set(job_keywords) & set(resume_keywords)
    missing_keywords = set(job_keywords) - set(resume_keywords)

    # Calculate match rate
    match_rate = len(matched_keywords) / len(job_keywords) * 100 if job_keywords else 0

    return {
        'total_job_keywords': len(job_keywords),
        'matched_keywords': len(matched_keywords),
        'missing_keywords': len(missing_keywords),
        'match_rate': round(match_rate, 1),
        'matched_list': sorted(list(matched_keywords))[:20],  # Top 20
        'missing_list': sorted(list(missing_keywords))[:20],  # Top 20
        'grade': get_keyword_grade(match_rate)
    }


def extract_keywords(text: str) -> List[str]:
    """
    Extract important keywords from text.

    Args:
        text: Text to extract keywords from

    Returns:
        List of keywords
    """
    # Convert to lowercase
    text = text.lower()

    # Remove special characters
    text = re.sub(r'[^a-z0-9\s\+\#\.]', ' ', text)

    # Common stop words to ignore
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }

    # Split into words
    words = text.split()

    # Filter and deduplicate
    keywords = []
    seen = set()

    for word in words:
        word = word.strip()
        if (len(word) >= 3 and
            word not in stop_words and
            word not in seen and
            not word.isdigit()):
            keywords.append(word)
            seen.add(word)

    # Also extract common multi-word phrases
    phrases = extract_phrases(text)
    keywords.extend(phrases)

    return keywords


def extract_phrases(text: str) -> List[str]:
    """Extract common technical phrases."""
    common_phrases = [
        'machine learning', 'data science', 'project management',
        'software development', 'web development', 'full stack',
        'front end', 'back end', 'cloud computing', 'devops',
        'agile', 'scrum', 'ci/cd', 'rest api', 'graphql',
        'react', 'angular', 'vue', 'node.js', 'python',
        'java', 'javascript', 'typescript', 'c++', 'c#',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes',
        'customer service', 'sales', 'marketing', 'business development'
    ]

    found_phrases = []
    text_lower = text.lower()

    for phrase in common_phrases:
        if phrase in text_lower:
            found_phrases.append(phrase)

    return found_phrases


def get_keyword_grade(match_rate: float) -> str:
    """Get letter grade for keyword match rate."""
    if match_rate >= 90:
        return "A+"
    elif match_rate >= 85:
        return "A"
    elif match_rate >= 80:
        return "A-"
    elif match_rate >= 75:
        return "B+"
    elif match_rate >= 70:
        return "B"
    elif match_rate >= 65:
        return "B-"
    elif match_rate >= 60:
        return "C+"
    elif match_rate >= 55:
        return "C"
    elif match_rate >= 50:
        return "C-"
    else:
        return "D"


def check_format_issues(resume_text: str) -> List[str]:
    """
    Check for common formatting issues that ATS might struggle with.

    Args:
        resume_text: Resume text

    Returns:
        List of formatting issues
    """
    issues = []

    # Check for special characters that might cause parsing issues
    if re.search(r'[│─┌┐└┘├┤┬┴┼]', resume_text):
        issues.append("Contains box-drawing characters that ATS may not parse correctly")

    # Check for excessive special formatting
    if resume_text.count('*') > 50:
        issues.append("Excessive use of asterisks may indicate complex formatting")

    # Check for common header/footer indicators
    if re.search(r'Page \d+ of \d+', resume_text, re.IGNORECASE):
        issues.append("Contains page numbers - may be in header/footer (problematic for ATS)")

    # Check for tables (indicated by multiple tabs or aligned columns)
    if resume_text.count('\t') > 20:
        issues.append("May contain tables (excessive tabs detected)")

    # Check for standard section headers
    standard_headers = ['experience', 'education', 'skills', 'summary']
    found_headers = 0
    for header in standard_headers:
        if re.search(rf'\b{header}\b', resume_text, re.IGNORECASE):
            found_headers += 1

    if found_headers < 3:
        issues.append("Missing standard section headers (Experience, Education, Skills)")

    return issues
