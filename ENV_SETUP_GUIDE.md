# Environment Variables Setup Guide

This guide explains how to configure environment variables for the Resume Tailor application.

## Overview

Resume Tailor uses environment variables to configure sensitive information like API keys and user preferences. These variables are loaded from a `.env` file in the project root.

## Quick Start

### 1. Create Your .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

### 2. Configure Required Variables

At minimum, you need to set:

```bash
ANTHROPIC_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Verify Configuration

Run the environment check script:

```bash
python3 check_env.py
```

This will verify that your environment variables are loaded correctly.

## Environment Variables

### ANTHROPIC_API_KEY (Required)

**Purpose:** API key for Claude AI model (powers all AI features)

**Required:** Yes, for AI features to work

**Format:** String (provided by Anthropic)

**Example:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Security Notes:**
- Never commit your `.env` file to git (it's in `.gitignore`)
- Keep your API key confidential
- Rotate keys regularly for security

### DEFAULT_OUTPUT_FOLDER (Optional)

**Purpose:** Default location where resume outputs are saved

**Required:** No (defaults to `~/resume_tailor_output`)

**Format:** Absolute file path

**Examples:**
```bash
# macOS/Linux
DEFAULT_OUTPUT_FOLDER=/Users/yourname/Documents/resumes

# Windows (in WSL or Git Bash)
DEFAULT_OUTPUT_FOLDER=/mnt/c/Users/yourname/Documents/resumes
```

**Notes:**
- Must be an absolute path (not relative)
- Folder will be created automatically if it doesn't exist
- Can be overridden in the UI when running the app

## How .env Loading Works

### Loading Priority

Environment variables are loaded in this order (later overwrites earlier):

1. System environment variables (from your shell)
2. `.env` file in project root
3. Explicitly set values in code

### Implementation Details

The `.env` file is loaded automatically when you import any module from the `config` package:

```python
from config.settings import ANTHROPIC_API_KEY
# .env is already loaded at this point
```

**Location:** Environment loading happens in `config/settings.py`

**Library:** Uses `python-dotenv` package

**Project Root Detection:** Automatically finds the project root (where `.env` should be)

### Code Example

```python
# config/settings.py
from dotenv import load_dotenv
from pathlib import Path

# Automatically find and load .env from project root
project_root = Path(__file__).parent.parent
env_file = project_root / '.env'

if env_file.exists():
    load_dotenv(dotenv_path=env_file)

# Now environment variables are available
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
```

## Verification and Troubleshooting

### Check Environment Setup

Use the included check script:

```bash
python3 check_env.py
```

**Expected Output (Configured):**
```
✓ .env file found
✓ ANTHROPIC_API_KEY is set: sk-ant-a...xxx
✓ All agents initialized successfully
✓ Anthropic API client is ready
```

**Expected Output (Not Configured):**
```
✗ .env file NOT found
✗ ANTHROPIC_API_KEY is NOT set
→ Steps to complete setup: ...
```

### Common Issues

#### Issue: "ANTHROPIC_API_KEY is NOT set"

**Solution:**
1. Verify `.env` file exists in project root: `ls -la .env`
2. Check the file contains your API key: `cat .env`
3. Ensure no typos in variable name (case-sensitive)
4. Reload your shell or restart your application

#### Issue: "API key seems too short"

**Solution:**
- Anthropic API keys should be 100+ characters
- Verify you copied the complete key from the console
- Check for accidental spaces or line breaks

#### Issue: ".env file NOT found"

**Solution:**
```bash
# Verify you're in the project root
pwd
# Should show: /path/to/resume-tailor

# Check if .env.example exists
ls -la .env.example

# Copy it to .env
cp .env.example .env

# Edit with your values
nano .env
```

#### Issue: "Folder will be created when needed" Warning

**This is normal!** The output folder doesn't need to exist beforehand. It will be created automatically when saving results.

To create it manually:
```bash
mkdir -p ~/resume_tailor_output
```

### Testing Environment Loading

Run the automated tests:

```bash
# Test just environment loading
python3 -m pytest tests/test_env_loading.py -v

# Test all functionality
python3 -m pytest tests/ -v
```

All tests should pass whether or not you have a `.env` file configured.

## Security Best Practices

### DO ✓

- ✓ Keep `.env` file in project root (already in `.gitignore`)
- ✓ Use different API keys for development/production
- ✓ Rotate API keys regularly
- ✓ Set file permissions: `chmod 600 .env` (owner read/write only)
- ✓ Use environment check script to verify setup

### DON'T ✗

- ✗ Commit `.env` to version control
- ✗ Share your `.env` file or API keys
- ✗ Hardcode API keys in source code
- ✗ Use production keys in public demos
- ✗ Post screenshots showing your API keys

## Advanced Usage

### Using System Environment Variables

Instead of a `.env` file, you can set system environment variables:

```bash
# Bash/Zsh
export ANTHROPIC_API_KEY="your_key_here"
streamlit run app.py

# Or inline
ANTHROPIC_API_KEY="your_key_here" streamlit run app.py
```

### Multiple Environments

For different environments (dev/staging/prod):

```bash
# .env.development
ANTHROPIC_API_KEY=dev_key_here

# .env.production
ANTHROPIC_API_KEY=prod_key_here

# Load specific env file
cp .env.production .env
python3 check_env.py
```

### CI/CD Integration

For automated deployments, use secret management:

```yaml
# GitHub Actions example
- name: Run tests
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: pytest tests/
```

## Reference

### File Structure

```
resume-tailor/
├── .env                 # Your actual config (gitignored, you create this)
├── .env.example         # Template (committed to git)
├── check_env.py         # Verification script
├── config/
│   └── settings.py      # Loads .env and exports variables
└── agents/
    └── *.py             # Import variables from config.settings
```

### Related Files

- `.env.example` - Template for environment variables
- `config/settings.py` - Environment loading implementation
- `check_env.py` - Verification and diagnostic script
- `tests/test_env_loading.py` - Automated tests for .env loading

### Environment Loading Tests

The test suite includes 10 tests that verify:

✓ python-dotenv is installed and available
✓ Settings module imports correctly
✓ ANTHROPIC_API_KEY is accessible
✓ DEFAULT_OUTPUT_FOLDER is set
✓ PROJECT_ROOT is exported correctly
✓ .env file location is correct
✓ All agents can access API key
✓ .env.example exists as template
✓ Actual env vars take precedence over .env file
✓ DEFAULT_MODEL is set correctly

Run these tests:
```bash
python3 -m pytest tests/test_env_loading.py -v
```

## Getting Help

If you encounter issues:

1. Run `python3 check_env.py` for diagnostic information
2. Check the troubleshooting section above
3. Review test output: `pytest tests/test_env_loading.py -v`
4. Verify `.env.example` for correct variable names
5. Check that `python-dotenv` is installed: `pip list | grep dotenv`

## Summary

The Resume Tailor application uses a robust environment variable loading system:

- **Automatic loading** from `.env` file in project root
- **Security-first** design (never commit `.env` to git)
- **Verification tools** included (`check_env.py`)
- **Comprehensive tests** ensure reliability
- **Flexible** - supports .env file or system environment variables
- **Well-documented** with examples and troubleshooting

Follow this guide to ensure your environment is properly configured!
