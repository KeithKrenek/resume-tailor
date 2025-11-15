#!/usr/bin/env python3
"""
Utility script to check environment variable configuration.
Run this to verify your .env file is properly configured.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import (
    ANTHROPIC_API_KEY,
    DEFAULT_OUTPUT_FOLDER,
    PROJECT_ROOT,
    _env_file
)


def check_env_setup():
    """Check environment variable setup and provide feedback."""
    print("=" * 60)
    print("Resume Tailor - Environment Configuration Check")
    print("=" * 60)
    print()

    # Check project root
    print(f"✓ Project Root: {PROJECT_ROOT}")
    print()

    # Check .env file
    print("Environment File:")
    if _env_file.exists():
        print(f"  ✓ .env file found at: {_env_file}")
    else:
        print(f"  ✗ .env file NOT found at: {_env_file}")
        print(f"  → Copy .env.example to .env and configure it:")
        print(f"     cp {PROJECT_ROOT}/.env.example {PROJECT_ROOT}/.env")
    print()

    # Check ANTHROPIC_API_KEY
    print("API Configuration:")
    if ANTHROPIC_API_KEY:
        # Don't print the full key for security
        masked_key = f"{ANTHROPIC_API_KEY[:8]}...{ANTHROPIC_API_KEY[-4:]}" if len(ANTHROPIC_API_KEY) > 12 else "***"
        print(f"  ✓ ANTHROPIC_API_KEY is set: {masked_key}")

        # Basic validation
        if ANTHROPIC_API_KEY == "your_api_key_here":
            print(f"  ⚠ WARNING: API key looks like the example value")
            print(f"     Please update it with your actual API key")
        elif len(ANTHROPIC_API_KEY) < 20:
            print(f"  ⚠ WARNING: API key seems too short (may be invalid)")
    else:
        print(f"  ✗ ANTHROPIC_API_KEY is NOT set")
        print(f"  → Add your API key to .env file:")
        print(f"     ANTHROPIC_API_KEY=your_actual_api_key_here")
        print(f"  → Get your API key from: https://console.anthropic.com/")
    print()

    # Check DEFAULT_OUTPUT_FOLDER
    print("Output Configuration:")
    print(f"  ✓ Output folder: {DEFAULT_OUTPUT_FOLDER}")
    output_path = Path(DEFAULT_OUTPUT_FOLDER)
    if output_path.exists():
        print(f"    → Folder exists and is ready")
    else:
        print(f"    → Folder will be created when needed")
    print()

    # Test AI agent initialization
    print("Agent Initialization Test:")
    try:
        from agents.extraction_agent import ExtractionAgent
        from agents.job_analysis_agent import JobAnalysisAgent
        from agents.resume_analysis_agent import ResumeAnalysisAgent
        from agents.resume_optimization_agent import ResumeOptimizationAgent

        extraction_agent = ExtractionAgent()
        job_agent = JobAnalysisAgent()
        resume_agent = ResumeAnalysisAgent()
        optimization_agent = ResumeOptimizationAgent()

        print(f"  ✓ All agents initialized successfully")

        if extraction_agent.client:
            print(f"  ✓ Anthropic API client is ready")
        else:
            print(f"  ⚠ Anthropic API client not initialized")
            print(f"    → This usually means ANTHROPIC_API_KEY is missing or invalid")
            print(f"    → AI features will not work without a valid API key")
    except Exception as e:
        print(f"  ✗ Error initializing agents: {e}")
    print()

    # Summary
    print("=" * 60)
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your_api_key_here":
        print("✓ Configuration looks good! You're ready to run the app.")
        print()
        print("Start the application with:")
        print("  streamlit run app.py")
    else:
        print("⚠ Configuration incomplete. Please set up your .env file.")
        print()
        print("Steps to complete setup:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your ANTHROPIC_API_KEY to .env")
        print("  3. Run this script again to verify")
    print("=" * 60)


if __name__ == "__main__":
    check_env_setup()
