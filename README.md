# 🎯 Resume Tailor

**AI-Powered Resume Optimization Application**

Resume Tailor is a Streamlit-based application that uses AI agents to automatically optimize your resume for specific job descriptions. Built with production-quality code and a modular architecture, it provides an end-to-end workflow for tailoring resumes to maximize your chances of landing interviews.

## ✨ Features

### Step 1: Input Collection (✅ Implemented)

- **Job Description Input**
  - Paste job description manually
  - Scrape job postings from URLs (supports LinkedIn, Indeed, Greenhouse, Lever, and more)
  - Real-time validation and statistics
  - Preview scraped content before proceeding

- **Resume Upload**
  - Support for multiple formats: PDF, DOCX, TXT, MD, JSON
  - Automatic text extraction with intelligent parsing
  - Resume metadata extraction (email, phone, sections)
  - Manual text paste as fallback

- **Company Information**
  - Optional company URL input
  - Automatic company name extraction

- **AI-Powered Extraction**
  - Automatically extract company name and job title
  - Uses Claude AI with rule-based fallback
  - No API key required for basic extraction

- **Output Management**
  - Configurable output folder
  - Automatic folder creation
  - Session state persistence

### Coming Soon

- **Step 2:** Job Analysis - Extract requirements, skills, and qualifications
- **Step 3:** Resume Analysis - Analyze current resume content
- **Step 4:** Gap Identification - Identify missing skills and opportunities
- **Step 5:** Resume Optimization - AI-powered resume rewriting
- **Step 6:** Output Generation - Generate tailored resume and cover letter

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Anthropic API key for AI-powered extraction

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

3. **Set up environment variables (optional)**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY if using AI extraction
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   - The app will automatically open at `http://localhost:8501`

## 📁 Project Structure

```
resume-tailor/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── config/
│   └── settings.py            # Application configuration
│
├── modules/
│   ├── input_collector.py     # Step 1: Input collection UI
│   └── validators.py          # Input validation logic
│
├── utils/
│   ├── file_handlers.py       # Resume file processing
│   ├── scraper.py             # Job URL scraping
│   └── session_manager.py     # Streamlit session state
│
├── agents/
│   └── extraction_agent.py    # AI agent for info extraction
│
└── tests/
    └── test_*.py              # Unit tests
```

## 🎮 Usage Guide

### Step 1: Input Collection

1. **Enter Job Description**
   - Option A: Paste the URL of a job posting and click "Scrape URL"
   - Option B: Manually paste the job description text
   - The app will validate the description and show statistics

2. **Upload Your Resume**
   - Option A: Upload a file (PDF, DOCX, TXT, MD, or JSON)
   - Option B: Paste your resume text directly
   - The app will extract and validate the content

3. **Configure Output** (Optional)
   - Enter company website URL for additional context
   - Choose where to save generated files (default: ~/resume_tailor_output)

4. **Continue**
   - Click "Continue to Analysis" when all inputs are valid
   - The app will automatically extract company name and job title
   - Move to the next step of the workflow

### Keyboard Shortcuts

- `R` - Refresh the page
- `Ctrl/Cmd + K` - Clear app cache

## 🛠️ Configuration

Edit `config/settings.py` to customize:

- File size limits
- Validation rules
- Supported file formats
- Scraper timeouts
- UI settings

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_validators.py
```

## 📊 Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Supports text-based PDFs (not scanned images) |
| Word | `.docx` | Microsoft Word documents |
| Text | `.txt` | Plain text files |
| Markdown | `.md` | Markdown formatted resumes |
| JSON | `.json` | JSON Resume format and others |

## 🌐 Supported Job Boards

The scraper has optimized support for:

- LinkedIn
- Indeed
- Greenhouse
- Lever.co
- Generic job boards (fallback)

## 🔑 Environment Variables

Create a `.env` file with the following (optional):

```bash
# Anthropic API Key (for AI-powered extraction)
ANTHROPIC_API_KEY=your_api_key_here

# Default output folder
DEFAULT_OUTPUT_FOLDER=/path/to/output
```

## 🐛 Troubleshooting

### PDF extraction fails
- Ensure the PDF is text-based (not a scanned image)
- Try converting to DOCX or TXT format
- Use the manual text paste option

### URL scraping doesn't work
- Check your internet connection
- Some sites may block automated scraping
- Use the manual paste option as fallback

### AI extraction not working
- Ensure you have set the `ANTHROPIC_API_KEY` environment variable
- The app will fall back to rule-based extraction if API is unavailable
- Check your API key is valid and has credits

### Session state issues
- Click "Clear All" to reset the session
- Refresh the page (press R)
- Clear Streamlit cache (Ctrl/Cmd + K)

## 🏗️ Architecture

### Design Principles

- **Modularity**: Each component is self-contained and testable
- **Separation of Concerns**: UI, business logic, and utilities are separate
- **Error Handling**: Graceful degradation with helpful error messages
- **Session Management**: Persistent state across page interactions
- **Validation**: Multi-layer validation for data quality

### Key Components

1. **Input Collector** (`modules/input_collector.py`)
   - Handles all UI rendering for Step 1
   - Integrates validation and file processing
   - Manages user interactions

2. **File Handlers** (`utils/file_handlers.py`)
   - Format-agnostic file processing
   - Robust error handling
   - Support for multiple formats

3. **Validators** (`modules/validators.py`)
   - Multi-level validation rules
   - Helpful error messages
   - Metadata extraction

4. **Scraper** (`utils/scraper.py`)
   - Job board-specific extraction
   - Generic fallback
   - Request management

5. **Extraction Agent** (`agents/extraction_agent.py`)
   - AI-powered information extraction
   - Rule-based fallback
   - Structured output

## 🤝 Contributing

This is a work in progress. Future contributions will be welcome!

## 📝 License

This project is proprietary and confidential.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- PDF processing by [pdfplumber](https://github.com/jsvine/pdfplumber)
- Web scraping with [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)

## 📧 Support

For questions or issues, please contact the development team.

---

**Version:** 1.0.0
**Last Updated:** November 2024
**Status:** Step 1 Complete - MVP in Progress
