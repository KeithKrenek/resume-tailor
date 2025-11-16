# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2025-01-16

### Fixed

#### Critical Bug Fixes
- **Fixed workflow progression bug**: Steps 2 and 3 were never marked as complete, preventing proper workflow tracking
  - Added initialization for `step_2_complete` and `step_3_complete` in session manager
  - Extended `mark_step_complete()` to handle all steps
  - Extended `is_step_complete()` to check all steps
  - Updated `clear_session_state()` to properly reset all completion flags

- **Fixed configuration mismatch**: TOTAL_STEPS was set to 6 but only 4 steps are implemented
  - Changed `TOTAL_STEPS` from 6 to 4 in `config/settings.py`
  - Removed undefined steps 5 and 6 from `STEP_NAMES`
  - Progress indicators now show correct percentages (Step 1 = 25% instead of 16.67%)

#### Type Safety & Compatibility
- **Fixed type annotation inconsistencies** for Python 3.8+ compatibility
  - Changed lowercase `tuple[...]` to `Tuple[...]` from typing module (5 files)
  - Fixed `any` to `Any` from typing module (2 files)
  - Added proper imports for `Tuple`, `Optional`, `Any` where missing
  - Added missing `Optional[float]` return type annotation

#### Code Organization
- **Improved import organization**
  - Moved inline `import re` to top of module in `gap_analyzer.py`
  - Added proper typing imports where they were missing
  - Ensures better IDE support and type checking

#### Validation Consistency
- **Fixed validation inconsistencies** across the application
  - Replaced hardcoded validation values in `analysis_service.py`
  - Now uses `MIN_JOB_DESC_LENGTH` and `MIN_RESUME_LENGTH` from config
  - Ensures consistent validation throughout the application

### Technical Details

**Files Modified:**
- `config/settings.py` - Fixed TOTAL_STEPS and STEP_NAMES
- `modules/gap_analyzer.py` - Type annotations, imports, return types
- `modules/input_collector.py` - Type annotations
- `modules/validators.py` - Type annotations
- `services/analysis_service.py` - Validation consistency
- `utils/json_utils.py` - Type annotations
- `utils/session_manager.py` - Step tracking logic

**Impact:**
- ✅ Workflow progression now works correctly for all 4 steps
- ✅ Progress indicators show accurate percentages
- ✅ Type checking works with Python 3.8+
- ✅ Consistent validation throughout the app
- ✅ Better IDE support and code quality

**Backward Compatibility:**
- All changes maintain backward compatibility
- No changes to user-facing functionality
- Only bug fixes and code quality improvements

## [2.1.0] - 2025-01-15

### Added
- Resume Score Dashboard with comprehensive 0-100 scoring
- Smart Warnings System with 4 severity levels
- Company & Industry Research capabilities
- Multi-Model Support (Claude, GPT-4, Gemini)
- Version history tracking in iterative optimization
- Three optimization tiers (Basic, Standard, Premium)

### Enhanced
- Improved metrics calculation with role alignment
- Better ATS compatibility checking
- Enhanced keyword optimization analysis
- More detailed authenticity verification

## [2.0.0] - 2025-01-10

### Added
- **Hallucination Guard**: LLM-based authenticity verification
- Advanced authenticity checking with severity levels
- Detailed issue reporting with recommendations
- Heuristic-based fallback checks

### Enhanced
- Complete Step 4 implementation with multi-format output
- PDF generation via weasyprint
- DOCX generation with proper formatting
- HTML generation with embedded CSS
- Interactive preview modes

## [1.0.0] - 2025-01-05

### Added
- Initial release with 4-step workflow
- Step 1: Input Collection
  - Job description input and URL scraping
  - Resume upload with multiple format support
  - AI-powered company and job title extraction

- Step 2: Analysis
  - Job requirements analysis
  - Resume parsing and structure extraction
  - Gap analysis with coverage metrics

- Step 3: Optimization
  - Three optimization styles (Conservative, Balanced, Aggressive)
  - Change tracking with before/after comparison
  - Detailed rationale for each modification

- Step 4: Output Generation
  - Multi-format document generation
  - Interactive preview
  - Batch export functionality

### Infrastructure
- Streamlit-based web interface
- Anthropic Claude integration (Sonnet 4)
- Comprehensive test suite
- Environment configuration management
- Error handling and validation
