"""Tests for environment variable loading."""

import os
import tempfile
from pathlib import Path
import sys
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestEnvLoading:
    """Test environment variable loading from .env file."""

    def test_dotenv_module_available(self):
        """Test that python-dotenv is available."""
        try:
            import dotenv
            assert True
        except ImportError:
            pytest.fail("python-dotenv not installed")

    def test_settings_import(self):
        """Test that settings module can be imported."""
        from config import settings
        assert settings.APP_NAME == "Resume Tailor"

    def test_anthropic_api_key_loaded(self):
        """Test that ANTHROPIC_API_KEY is accessible (may be empty)."""
        from config.settings import ANTHROPIC_API_KEY
        # Should be a string (even if empty)
        assert isinstance(ANTHROPIC_API_KEY, str)

    def test_default_output_folder_loaded(self):
        """Test that DEFAULT_OUTPUT_FOLDER is set."""
        from config.settings import DEFAULT_OUTPUT_FOLDER
        assert isinstance(DEFAULT_OUTPUT_FOLDER, str)
        assert len(DEFAULT_OUTPUT_FOLDER) > 0

    def test_project_root_exported(self):
        """Test that PROJECT_ROOT is exported."""
        from config.settings import PROJECT_ROOT
        assert isinstance(PROJECT_ROOT, Path)
        assert PROJECT_ROOT.exists()
        assert (PROJECT_ROOT / 'config').exists()

    def test_env_file_location(self):
        """Test that .env file is looked for in the right location."""
        from config.settings import _project_root, _env_file

        # Should be looking in project root
        assert _env_file == _project_root / '.env'
        # Project root should contain config directory
        assert (_project_root / 'config').exists()

    def test_agents_can_access_api_key(self):
        """Test that all agents can access ANTHROPIC_API_KEY."""
        from agents.extraction_agent import ExtractionAgent
        from agents.job_analysis_agent import JobAnalysisAgent
        from agents.resume_analysis_agent import ResumeAnalysisAgent
        from agents.resume_optimization_agent import ResumeOptimizationAgent

        # All agents should initialize without error
        # (they may not have a valid API key, but should handle that gracefully)
        agent1 = ExtractionAgent()
        agent2 = JobAnalysisAgent()
        agent3 = ResumeAnalysisAgent()
        agent4 = ResumeOptimizationAgent()

        # All should have api_key attribute
        assert hasattr(agent1, 'api_key')
        assert hasattr(agent2, 'api_key')
        assert hasattr(agent3, 'api_key')
        assert hasattr(agent4, 'api_key')

    def test_env_example_exists(self):
        """Test that .env.example exists as a template."""
        from config.settings import PROJECT_ROOT
        env_example = PROJECT_ROOT / '.env.example'
        assert env_example.exists()

        # Should contain expected variables
        content = env_example.read_text()
        assert 'ANTHROPIC_API_KEY' in content
        assert 'DEFAULT_OUTPUT_FOLDER' in content


class TestEnvVariablePriority:
    """Test that environment variables are loaded in correct priority."""

    def test_actual_env_var_takes_precedence(self):
        """Test that actual environment variable takes precedence over .env file."""
        # Set an actual environment variable
        test_key = "TEST_ANTHROPIC_KEY_123"
        os.environ['ANTHROPIC_API_KEY'] = test_key

        # Reload the settings module to pick up the change
        import importlib
        from config import settings
        importlib.reload(settings)

        # Should use the environment variable
        assert settings.ANTHROPIC_API_KEY == test_key

        # Clean up
        del os.environ['ANTHROPIC_API_KEY']
        importlib.reload(settings)

    def test_default_model_is_set(self):
        """Test that DEFAULT_MODEL is set to expected value."""
        from config.settings import DEFAULT_MODEL
        assert DEFAULT_MODEL == "claude-sonnet-4-20250514"
