# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-01-16

### Added

#### Interactive Change Review & Approval System (CRITICAL)
- **Step 3.5: Change Review** - New interactive step between optimization and output generation
  - Individual change approval with Accept/Reject/Edit/Ask AI to Revise options
  - Side-by-side before/after comparison for each change
  - Automatic flagging of potentially risky changes (new metrics, organizations, technologies)
  - Real-time progress tracking showing reviewed vs pending changes
  - Bulk actions: Accept/Reject all visible, Accept all non-flagged, Reset to pending
  - Smart filters: Filter by status (pending/accepted/rejected), flagged only, or change type
  - Inline editing with rich text areas for custom modifications
  - AI-powered revision based on user feedback

#### New Models & Enums
- **ChangeStatus enum** - Track review status: PENDING, ACCEPTED, REJECTED, EDITED
  - All changes start as PENDING after optimization
  - Users must review and approve before proceeding to output
  - Edited changes store both AI-suggested and user-edited versions

- **Enhanced ResumeChange model**:
  - Added `status: ChangeStatus` field (default: PENDING)
  - Added `is_flagged: bool` field for risky change detection
  - Added `edited_value: Optional[str]` for user edits
  - Helper methods: `get_final_value()`, `is_accepted()`, `is_rejected()`, `is_pending()`

- **Enhanced ResumeOptimizationResult model**:
  - New methods: `get_accepted_changes()`, `get_rejected_changes()`, `get_pending_changes()`
  - New methods: `get_flagged_changes()`, `get_change_stats()`, `all_changes_reviewed()`
  - New method: `has_any_accepted_changes()` - Validates at least one change is accepted

#### New Services & Agents
- **Resume Builder Service** (`services/resume_builder.py`):
  - `apply_accepted_changes()` - Generates final resume from only accepted changes
  - Smart change application by type (headline, summary, experience bullets, skills, education)
  - Location parsing for precise change application (e.g., "experience[0].bullets[2]")
  - `get_change_summary()` - Statistics on accepted vs rejected changes
  - `validate_final_resume()` - Ensures final resume meets quality standards

- **Change Revision Agent** (`agents/change_revision_agent.py`):
  - AI-powered revision based on user feedback
  - Uses Claude Sonnet 4 for high-quality revisions
  - Maintains truthfulness while incorporating user guidance
  - Preserves original facts and timeline

#### UI Components
- **Change Review Module** (`modules/change_review.py`):
  - `render_change_statistics()` - Progress dashboard with metrics
  - `render_change_filters()` - Smart filtering controls
  - `render_change_card()` - Individual change display with action buttons
  - `render_bulk_actions()` - Batch operations on filtered changes
  - `auto_flag_risky_changes()` - Automatic risk detection
  - Edit dialog with inline text editing
  - AI revision dialog with custom guidance input

#### Session Management
- Added `change_review_complete` to SESSION_KEYS
- Session state initialization for change review tracking
- Proper cleanup in `clear_session_state()`
- Integration with existing workflow progression

### Enhanced

#### Workflow Integration
- Seamless integration between Step 3 (Optimization) and Step 4 (Output)
- "Review Changes →" button replaces "Continue to Output →" until review is complete
- Re-optimization clears change review state for fresh review
- Back navigation preserves change review progress

#### User Experience
- Users maintain full control over resume changes
- Transparent view of all AI modifications
- Confidence in resume authenticity before submission
- Prevents accidental acceptance of fabricated information

### Technical Details

**Files Added:**
- `modules/change_review.py` - Interactive change review UI
- `agents/change_revision_agent.py` - AI-powered change revision
- `services/resume_builder.py` - Final resume generation from accepted changes

**Files Modified:**
- `modules/models.py` - Added ChangeStatus enum, enhanced ResumeChange and ResumeOptimizationResult
- `modules/optimization.py` - Integrated change review workflow
- `config/settings.py` - Added change_review_complete session key
- `utils/session_manager.py` - Initialize and manage change review state

**Impact:**
- ✅ Users have full control over every resume change
- ✅ Reduces risk of fabricated content in final resume
- ✅ Increases user confidence and resume authenticity
- ✅ Enables fine-tuning of AI suggestions
- ✅ Provides transparency into optimization process
- ✅ Maintains workflow continuity

**Backward Compatibility:**
- All changes maintain backward compatibility
- Existing optimization results can be upgraded seamlessly
- No breaking changes to public APIs
- Default values ensure old data works with new code

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
