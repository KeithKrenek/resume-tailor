"""Configuration settings for Resume Tailor application."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Find the project root (where .env should be located)
_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent  # Go up two levels from config/settings.py
_env_file = _project_root / '.env'

# Load .env file if it exists
if _env_file.exists():
    load_dotenv(dotenv_path=_env_file)
else:
    # Try loading from default location (current working directory)
    load_dotenv()

# Application Settings
APP_NAME = "Resume Tailor"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-Powered Resume Optimization"

# File Upload Settings
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SUPPORTED_RESUME_FORMATS = ['.pdf', '.docx', '.txt', '.md', '.json']
SUPPORTED_RESUME_EXTENSIONS = ['pdf', 'docx', 'txt', 'md', 'json']

# Validation Settings
MIN_JOB_DESC_LENGTH = 100
MAX_JOB_DESC_LENGTH = 50000
MIN_RESUME_LENGTH = 200
MAX_RESUME_LENGTH = 100000
MIN_WORDS_IN_RESUME = 10

# Job Description Keywords (at least 3 should be present)
JOB_DESC_KEYWORDS = [
    'responsibilities', 'requirements', 'qualifications',
    'skills', 'experience', 'about', 'role', 'position',
    'duties', 'candidate', 'seeking', 'looking for'
]
MIN_JOB_KEYWORDS_MATCH = 3

# Resume Keywords (at least one should be present)
RESUME_KEYWORDS = [
    'experience', 'education', 'skills', 'projects',
    'work', 'employment', 'university', 'degree'
]

# Scraper Settings
REQUEST_TIMEOUT = 10  # seconds
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Session State Keys
SESSION_KEYS = {
    # Step 1: Input Collection
    'job_description': 'job_description',
    'job_url': 'job_url',
    'company_url': 'company_url',
    'resume_text': 'resume_text',
    'resume_metadata': 'resume_metadata',
    'output_folder': 'output_folder',
    'company_name': 'company_name',
    'job_title': 'job_title',
    'scraped_job_data': 'scraped_job_data',

    # Step 2: Analysis
    'job_model': 'job_model',
    'resume_model': 'resume_model',
    'gap_analysis': 'gap_analysis',

    # Step 3: Optimization
    'optimization_result': 'optimization_result',

    # Step tracking
    'step_1_complete': 'step_1_complete',
    'step_2_complete': 'step_2_complete',
    'step_3_complete': 'step_3_complete',
    'current_step': 'current_step'
}

# UI Settings
TOTAL_STEPS = 4
STEP_NAMES = {
    1: "Input Collection",
    2: "Job & Resume Analysis",
    3: "Resume Optimization",
    4: "Output Generation"
}

# Default Output Folder
# Load from environment variable or use default
_default_folder = os.getenv('DEFAULT_OUTPUT_FOLDER', '')
if _default_folder and Path(_default_folder).is_absolute():
    DEFAULT_OUTPUT_FOLDER = _default_folder
else:
    DEFAULT_OUTPUT_FOLDER = str(Path.home() / "resume_tailor_output")

# API Settings
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
DEFAULT_MODEL = "claude-sonnet-4-20250514"

# Export project root for other modules that might need it
PROJECT_ROOT = _project_root
