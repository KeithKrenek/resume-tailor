# 🎯 Resume Tailor

**AI-Powered Resume Optimization with Hallucination Guard**

Resume Tailor is a production-grade Streamlit application that uses AI agents to automatically optimize your resume for specific job descriptions. Built with Claude AI and featuring advanced authenticity verification, it provides an end-to-end workflow for creating truthful, ATS-compatible, tailored resumes.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Anthropic](https://img.shields.io/badge/anthropic-claude-purple.svg)](https://www.anthropic.com/)

## 🆕 Latest Enhancements (v2.4.0)

### What's New
- ✏️ **Smart Resume Editor with Inline Optimization** (HIGH) - Fine-tune any section with AI assistance
  - Click-to-edit interface for all resume sections
  - "Improve This" button for AI-powered enhancements
  - "Get Suggestions" for actionable improvement tips
  - Edit history tracking with undo capability
  - Manual editing with real-time updates
- 📚 **Resume Version Management & Comparison** (HIGH) - Track, compare, and manage all resume versions
  - Save unlimited versions with automatic numbering and metadata
  - Side-by-side version comparison with metrics delta
  - Track which versions were submitted and responses received
  - Filter and organize with custom tags and notes
  - "Use This" feature to load any previous version
- 🎯 **Interactive Change Review & Approval System** (CRITICAL) - Full control over every AI-suggested change
  - Accept, reject, edit, or ask AI to revise individual changes
  - Automatic flagging of risky changes (new metrics, organizations, technologies)
  - Side-by-side before/after comparison with inline editing
  - Bulk actions and smart filtering by status or change type
- ✨ **Resume Score Dashboard** - Get a comprehensive 0-100 score across 6 key metrics (ATS, Keywords, Impact, etc.)
- ⚠️ **Smart Warnings System** - Proactive issue detection with 4 severity levels and actionable fixes
- 🔍 **Company & Industry Research** - AI-powered intelligence gathering for better optimization
- 🤖 **Multi-Model Support** - Choose between Claude Sonnet/Opus, GPT-4, or Gemini

**[📖 Read the detailed New Features Guide →](NEW_FEATURES_GUIDE.md)**

---

## ✨ Core Features

### 🎯 Complete 4-Step Workflow (All Implemented!)

#### Step 1: Input Collection ✅
- **Job Description Input**
  - Paste job description manually or scrape from URLs
  - Supports LinkedIn, Indeed, Greenhouse, Lever, and more
  - Real-time validation and statistics
  - Preview scraped content before proceeding

- **Resume Upload**
  - Multiple formats: PDF, DOCX, TXT, MD, JSON
  - Automatic text extraction with intelligent parsing
  - Resume metadata extraction (email, phone, sections)
  - Manual text paste as fallback

- **AI-Powered Extraction**
  - Automatically extract company name and job title
  - Uses Claude AI with rule-based fallback

#### Step 2: Intelligent Analysis ✅
- **Job Analysis**
  - Extract required and preferred skills
  - Identify key responsibilities and qualifications
  - Categorize requirements by importance
  - Extract experience level and job type

- **Resume Analysis**
  - Parse work experience with dates and locations
  - Extract skills, education, and certifications
  - Calculate total years of experience
  - Identify projects, awards, and languages

- **Gap Analysis**
  - Compare job requirements vs resume content
  - Identify missing required skills
  - Calculate coverage percentage
  - Provide actionable suggestions

#### Step 3: AI-Powered Optimization ✅
- **Intelligent Rewriting**
  - Three optimization styles: Conservative, Balanced, Aggressive
  - Keyword optimization for ATS systems
  - Achievement-focused bullet points
  - Professional summary enhancement

- **Change Tracking**
  - Detailed changelog for every modification
  - Before/after comparison
  - Rationale for each change
  - Categorized by change type

- **Interactive Change Review** 🎯
  - Review and approve each change individually
  - Accept, reject, edit, or ask AI to revise
  - Automatic flagging of risky changes
  - Bulk actions for efficient review
  - Smart filtering by status and type
  - Final resume generated only from accepted changes

- **Hallucination Guard** 🛡️
  - LLM-based authenticity verification
  - Detects fabrications and exaggerations
  - Severity-based issue categorization
  - Actionable recommendations

#### Step 4: Multi-Format Output Generation ✅
- **Professional Document Generation**
  - PDF (via weasyprint)
  - DOCX (ATS-compatible)
  - HTML (web-ready)
  - Markdown (version control friendly)

- **Interactive Preview**
  - Toggle between Markdown and HTML views
  - Embedded preview with scrolling
  - Download individual formats

- **Batch Export**
  - Save all formats at once
  - Customizable filenames
  - Output folder integration

- **Smart Resume Editor** ✏️
  - Click-to-edit any resume section
  - AI-powered "Improve This" button
  - Get actionable improvement suggestions
  - Manual editing with live updates
  - Edit history with undo capability
  - Reset to optimized version
  - Context-aware AI improvements

- **Version Management** 📚
  - Save versions with automatic numbering
  - Track company, job, style, and statistics
  - Add notes and tags for organization
  - Mark versions as submitted
  - Browse version history with filtering
  - Compare any two versions side-by-side
  - Load any previous version
  - Application tracking (submitted date, response status)

### 🛡️ Hallucination Guard (Phase 2)

Our advanced authenticity verification system ensures your optimized resume remains truthful:

- **AI-Powered Detection**
  - Uses Claude Haiku for fast, accurate analysis
  - Detects fabrications (completely new claims)
  - Identifies exaggerations (overstated achievements)
  - Contextual understanding of acceptable changes

- **Structured Reporting**
  - Severity levels: High, Medium, Low
  - Clear explanations for each issue
  - Specific fix recommendations
  - Side-by-side original vs modified comparison

- **Seamless Integration**
  - Automatic verification after optimization
  - Non-blocking (doesn't fail optimization)
  - Falls back to heuristic checks if needed
  - Rich UI display in Step 4

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resume-tailor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your API key
   nano .env  # or use your preferred editor
   ```

   Add your Anthropic API key:
   ```bash
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

4. **Verify setup**
   ```bash
   python check_env.py
   ```

   This checks:
   - ✓ .env file loaded correctly
   - ✓ API key is valid
   - ✓ All agents initialize
   - ✓ Output folder configuration

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - Automatically opens at `http://localhost:8501`

## 📖 Usage Guide

### Complete Workflow

1. **Input Collection (Step 1)**
   - Enter job description (paste text or scrape URL)
   - Upload resume (multiple formats supported)
   - Optional: Add company URL
   - Choose output folder
   - Click "Continue to Analysis"

2. **Analysis (Step 2)**
   - AI analyzes job requirements
   - AI parses your resume structure
   - Gap analysis identifies missing skills
   - View detailed metrics and recommendations
   - Click "Continue to Optimization"

3. **Optimization (Step 3)**
   - Choose optimization style:
     - **Conservative**: Minimal changes, safe
     - **Balanced**: Moderate optimization (recommended)
     - **Aggressive**: Maximum keyword density
   - AI rewrites resume content
   - Review side-by-side comparison
   - Check authenticity warnings
   - Examine all changes and rationales
   - Click "Continue to Output"

4. **Output Generation (Step 4)**
   - Preview optimized resume
   - Download individual formats (PDF, DOCX, HTML, MD)
   - Save all formats to output folder
   - Review authenticity report
   - Start new resume or go back to edit

### Hallucination Guard

When optimization completes, the Hallucination Guard automatically:

1. **Analyzes Changes**
   - Compares original vs optimized content
   - Uses Claude Haiku for verification
   - Generates structured report

2. **Categorizes Issues**
   - **High Severity**: Clear fabrications requiring immediate attention
   - **Medium Severity**: Noticeable exaggerations to review
   - **Low Severity**: Minor concerns worth noting

3. **Provides Recommendations**
   - Specific fixes for each issue
   - Explanation of what's wrong
   - Guidance on maintaining truthfulness

4. **Displays Results**
   - Rich UI with severity-based grouping
   - Side-by-side original vs modified text
   - Expandable sections for detailed review

## 📁 Project Structure

```
resume-tailor/
├── app.py                          # Main Streamlit application
├── check_env.py                    # Environment verification script
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
│
├── config/
│   └── settings.py                 # Application configuration
│
├── modules/
│   ├── input_collector.py          # Step 1: Input collection UI
│   ├── analysis.py                 # Step 2: Analysis UI
│   ├── optimization.py             # Step 3: Optimization UI
│   ├── output.py                   # Step 4: Output generation UI
│   ├── models.py                   # Data models and schemas
│   ├── validators.py               # Input validation logic
│   └── gap_analyzer.py             # Gap analysis logic
│
├── agents/
│   ├── extraction_agent.py         # AI: Company/title extraction
│   ├── job_analysis_agent.py       # AI: Job requirements analysis
│   ├── resume_analysis_agent.py    # AI: Resume parsing
│   ├── resume_optimization_agent.py # AI: Resume rewriting
│   └── authenticity_agent.py       # AI: Hallucination detection
│
├── services/
│   ├── analysis_service.py         # Analysis orchestration
│   └── optimization_service.py     # Optimization orchestration
│
├── utils/
│   ├── file_handlers.py            # Resume file processing
│   ├── scraper.py                  # Job URL scraping
│   ├── session_manager.py          # Streamlit session state
│   ├── output_manager.py           # File output management
│   ├── document_generator.py       # PDF/DOCX generation
│   ├── authenticity_checks.py      # Heuristic checks
│   ├── json_utils.py               # JSON parsing utilities
│   └── logging_config.py           # Logging configuration
│
└── tests/
    ├── test_validators.py          # Validation tests
    ├── test_models.py              # Model tests
    ├── test_gap_analyzer.py        # Gap analysis tests
    ├── test_document_generator.py  # Document generation tests
    ├── test_authenticity_agent.py  # Authenticity tests
    └── ...                         # Additional test files
```

## 🎮 Detailed Usage

### Optimization Styles

**Conservative** 🛡️
- Minimal changes to preserve your voice
- Only obvious improvements
- Safe for sensitive industries
- Lower keyword density

**Balanced** ⚖️ (Recommended)
- Moderate keyword optimization
- Achievement-focused rewriting
- Good ATS compatibility
- Maintains authenticity

**Aggressive** 🚀
- Maximum keyword density
- Comprehensive rewriting
- Highest ATS score potential
- May trigger more authenticity warnings

### Authenticity Report Interpretation

**High Severity Issues** 🚨
- Fabricated metrics or achievements
- Invented technologies or projects
- False claims about scope or impact
- **Action**: Must correct before using resume

**Medium Severity Issues** ⚠️
- Noticeable exaggerations
- Overstated responsibilities
- Inflated team sizes or budgets
- **Action**: Review and consider revising

**Low Severity Issues** ℹ️
- Minor wording concerns
- Borderline acceptable changes
- Potential ATS optimization
- **Action**: Verify accuracy

### File Format Recommendations

| Format | Best For | ATS Compatible | Editable |
|--------|----------|----------------|----------|
| **DOCX** | ATS submissions, further editing | ✅ Yes | ✅ Yes |
| **PDF** | Final submissions, printing | ✅ Yes | ❌ No |
| **HTML** | Web portfolios, email | ❌ No | ✅ Yes |
| **Markdown** | Version control, plain text | ❌ No | ✅ Yes |

## 🔧 Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional
DEFAULT_OUTPUT_FOLDER=/path/to/output  # Default: ~/resume_tailor_output
```

### Application Settings

Edit `config/settings.py` to customize:

```python
# File upload limits
MAX_FILE_SIZE_MB = 5

# Validation rules
MIN_JOB_DESC_LENGTH = 100
MIN_RESUME_LENGTH = 200

# Supported formats
SUPPORTED_RESUME_FORMATS = ['.pdf', '.docx', '.txt', '.md', '.json']

# Model selection
DEFAULT_MODEL = "claude-sonnet-4-20250514"  # For optimization
# Haiku used automatically for authenticity verification
```

### Optimization Configuration

In the UI, you can control:
- **Optimization Style**: Conservative, Balanced, Aggressive
- **Authenticity Checking**: Enabled by default
- **Output Formats**: Select which formats to generate

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Tests
```bash
# Validation tests
pytest tests/test_validators.py

# Model tests
pytest tests/test_models.py

# Document generation tests
pytest tests/test_document_generator.py

# Authenticity agent tests
pytest tests/test_authenticity_agent.py
```

### Integration Tests
```bash
# Test output generation
python test_output_generation.py

# Test hallucination guard
python test_hallucination_guard.py
```

## 📊 Supported Features

### Resume File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based PDFs only (not scanned images) |
| Word | `.docx` | Microsoft Word documents |
| Text | `.txt` | Plain text files |
| Markdown | `.md` | Markdown formatted resumes |
| JSON | `.json` | JSON Resume format |

### Job Board Support

Optimized scraping for:
- ✅ LinkedIn
- ✅ Indeed
- ✅ Greenhouse
- ✅ Lever.co
- ✅ Generic job boards (fallback)

### Output Formats

Generated documents:
- 📕 **PDF**: Professional, print-ready (requires weasyprint)
- 📄 **DOCX**: ATS-compatible, editable
- 🌐 **HTML**: Web-ready with embedded CSS
- 📝 **Markdown**: Version control friendly

## 🏗️ Architecture

### Design Principles

1. **Modularity**: Each component is self-contained and testable
2. **Separation of Concerns**: UI, business logic, and utilities separated
3. **Error Handling**: Graceful degradation with helpful messages
4. **AI Safety**: Hallucination Guard ensures authenticity
5. **Testability**: Comprehensive test coverage

### AI Agent Pipeline

```
Input Collection
    ↓
[ExtractionAgent] → Extract company & job title
    ↓
Analysis
    ↓
[JobAnalysisAgent] → Parse job requirements
[ResumeAnalysisAgent] → Parse resume structure
[GapAnalyzer] → Compare and identify gaps
    ↓
Optimization
    ↓
[ResumeOptimizationAgent] → Rewrite resume content
    ↓
[AuthenticityAgent] → Verify changes (Hallucination Guard)
    ↓
Output Generation
    ↓
[DocumentGenerator] → Generate PDF, DOCX, HTML, MD
```

### Data Models

**Core Models:**
- `ResumeModel`: Structured resume data
- `JobModel`: Structured job posting data
- `GapAnalysis`: Comparison results
- `ResumeOptimizationResult`: Optimization results + authenticity report
- `AuthenticityReport`: LLM-based verification results

**Supporting Models:**
- `ExperienceItem`: Work experience entry
- `EducationItem`: Education entry
- `JobRequirement`: Job requirement entry
- `ResumeChange`: Single modification record
- `AuthenticityIssue`: Single detected issue

## 🐛 Troubleshooting

### PDF Generation Issues

**Problem**: PDF generation fails
**Solution**:
```bash
# Install weasyprint system dependencies (Ubuntu/Debian)
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0

# Then reinstall weasyprint
pip install weasyprint
```

**Workaround**: Use DOCX, HTML, or Markdown formats instead

### Authenticity Verification Fails

**Problem**: Hallucination Guard doesn't run
**Causes**:
- Missing or invalid API key
- Network issues
- Rate limiting

**Solution**:
- Run `python check_env.py` to verify setup
- Check API key validity and credits
- Optimization will still complete; review changes manually

### API Key Issues

**Problem**: "ANTHROPIC_API_KEY must be set" error
**Solution**:
1. Ensure `.env` file exists in project root
2. Verify API key format: `ANTHROPIC_API_KEY=sk-ant-...`
3. Restart the application after setting `.env`
4. Run `python check_env.py` to verify

### Session State Issues

**Problem**: App shows old data or unexpected state
**Solution**:
- Click "🔄 Start New Resume" button
- Press `R` to refresh the page
- Press `Ctrl/Cmd + K` to clear Streamlit cache

### Memory Issues

**Problem**: Large resumes cause slowdowns
**Solution**:
- Keep resumes under 100KB
- Use text formats instead of PDF when possible
- Clear session state between resumes

## 📚 Documentation

Detailed documentation available:

- **[ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md)** - Environment configuration
- **[USAGE.md](USAGE.md)** - Detailed usage instructions
- **[TESTING.md](TESTING.md)** - Testing guide
- **[STEP_4_SUMMARY.md](STEP_4_SUMMARY.md)** - Output generation details
- **[HALLUCINATION_GUARD_SUMMARY.md](HALLUCINATION_GUARD_SUMMARY.md)** - Authenticity verification details
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## 🔒 Security & Privacy

### Data Handling

- **API Usage**: Resume and job data sent to Anthropic API for processing
- **No Storage**: Anthropic doesn't store your data (per their policy)
- **Local Processing**: All validation and file processing done locally
- **Session Only**: Data stored in Streamlit session state only

### Best Practices

1. **Review AI Changes**: Always review optimized content before using
2. **Verify Authenticity**: Check Hallucination Guard warnings
3. **Protect PII**: Be cautious with sensitive personal information
4. **API Key Security**: Never commit `.env` file to version control

## 🚀 Performance

### Speed Benchmarks

| Operation | Average Time | Model Used |
|-----------|-------------|------------|
| Job Analysis | 3-5 seconds | Sonnet 4 |
| Resume Analysis | 3-5 seconds | Sonnet 4 |
| Optimization | 10-15 seconds | Sonnet 4 |
| Authenticity Check | 2-5 seconds | Haiku |
| PDF Generation | 1-2 seconds | Local |
| DOCX Generation | <1 second | Local |

### Cost Estimates

Per resume optimization (approximate):
- **Job Analysis**: ~$0.01-0.02
- **Resume Analysis**: ~$0.01-0.02
- **Optimization**: ~$0.05-0.10
- **Authenticity Check**: ~$0.001-0.003
- **Total per resume**: ~$0.07-0.15

## 🤝 Contributing

This project uses:
- **Code Style**: Black formatter
- **Type Hints**: For better IDE support
- **Testing**: pytest with coverage
- **Documentation**: Comprehensive inline comments

## 📝 License

This project is proprietary and confidential.

## 🙏 Acknowledgments

**Frameworks & Libraries:**
- [Streamlit](https://streamlit.io/) - Web application framework
- [Anthropic Claude](https://www.anthropic.com/) - AI models (Sonnet 4, Haiku)
- [python-docx](https://python-docx.readthedocs.io/) - DOCX generation
- [weasyprint](https://weasyprint.org/) - PDF generation
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF parsing
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping

**AI Models:**
- **Claude Sonnet 4**: Job analysis, resume analysis, optimization
- **Claude Haiku**: Fast authenticity verification

## 📧 Support

For questions or issues:
1. Check the documentation in this repository
2. Run `python check_env.py` for environment diagnostics
3. Review error messages in the UI
4. Contact the development team

## 🗺️ Roadmap

### Completed ✅
- ✅ Input collection with file upload and URL scraping
- ✅ AI-powered job and resume analysis
- ✅ Gap analysis with coverage metrics
- ✅ Resume optimization with three styles
- ✅ Multi-format output generation (PDF, DOCX, HTML, MD)
- ✅ Hallucination Guard with LLM-based verification

### Future Enhancements 🔮
- [ ] Cover letter generation
- [ ] Multiple resume versions for different jobs
- [ ] Browser extension for one-click job scraping
- [ ] Historical tracking of applications
- [ ] A/B testing different optimization styles
- [ ] Industry-specific optimization profiles
- [ ] LinkedIn profile integration
- [ ] Email integration for sending applications
- [ ] Custom templates for different industries

---

**Version:** 2.0.0
**Last Updated:** November 2025
**Status:** ✅ Production Ready - All 4 Steps Complete + Hallucination Guard

**Made with ❤️ using Streamlit & Claude AI**
