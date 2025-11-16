# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2025-01-16

### Added

#### Smart Resume Editor with Inline Optimization (HIGH)
- **Interactive inline editing** - Edit any resume section with AI assistance
  - Click-to-edit interface for all resume sections
  - Manual text editing with live updates
  - AI-powered "Improve This" button for each section
  - "Get Suggestions" for actionable improvement tips
  - Real-time preview of changes
  - Edit history tracking with undo capability

- **Section-Level AI Improvements**:
  - Improve professional summary - enhance impact and clarity
  - Improve headline - optimize for role and keywords
  - Improve experience bullets - add metrics, strengthen verbs
  - Improve skills section - organize and prioritize
  - Context-aware improvements using job description
  - Focused improvements (no full re-optimization needed)

- **AI Assistance Features**:
  - Smart prompts tailored to section type
  - Rationale provided for each AI improvement
  - Suggestions without rewriting (guidance mode)
  - Maintains truthfulness - no fabrication
  - Preserves existing facts and achievements
  - Professional resume writing best practices

- **User Control**:
  - Manual editing always available
  - Save, Revert, or Cancel for each section
  - Edit history panel showing all changes
  - Undo last edit capability
  - Reset to optimized version option
  - Clear edit history

- **Seamless Integration**:
  - New "Edit Resume" tab in Step 4
  - Works with optimized or final resume
  - Changes persist across session
  - Export edited version in all formats

#### New Services & Agents
- **Section Improvement Agent** (`agents/section_improvement_agent.py`):
  - improve_section() - AI-powered section improvements
  - suggest_improvements() - Get actionable suggestions
  - Context-aware prompts by section type
  - Maintains truthfulness and authenticity
  - Uses Claude Sonnet 4 for high-quality improvements

#### UI Components
- **Resume Editor Module** (`modules/resume_editor.py`):
  - render_resume_editor() - Main editor interface
  - render_editable_summary() - Edit professional summary
  - render_editable_headline() - Edit headline
  - render_editable_experience() - Edit experience bullets
  - render_editable_skills() - Edit skills list
  - render_edit_interface() - Unified edit UI with AI assistance
  - render_edit_history() - Track and display changes
  - render_editor_actions() - Save/reset/clear actions

### Enhanced

#### Workflow Integration
- Added fourth tab "Edit Resume" in Step 4
- Tab order: Export, Edit, Version History, Compare
- Live editing with immediate visual feedback
- Edit history persistence across session

#### User Experience
- Fine-tune resume without full re-optimization
- Iterate quickly on specific sections
- Get AI assistance for individual improvements
- Maintain full control with manual editing
- See before/after for each change

### Technical Details

**Files Added:**
- `agents/section_improvement_agent.py` - AI agent for section improvements
- `modules/resume_editor.py` - Interactive editor UI

**Files Modified:**
- `modules/output.py` - Add editor tab to Step 4

**Features:**
- Click-to-edit inline interface
- AI improvement with rationale
- AI suggestions without rewriting
- Edit history with undo
- Session persistence
- Full export integration

**Impact:**
- ✅ Fine-tune resume without full re-optimization
- ✅ Iterate quickly on specific sections
- ✅ Get targeted AI assistance
- ✅ Maintain control with manual editing
- ✅ Track all changes with edit history
- ✅ Faster workflow for minor tweaks

**Backward Compatibility:**
- All changes maintain backward compatibility
- Editor is optional (doesn't affect normal workflow)
- Works with existing resumes

## [2.3.0] - 2025-01-16

### Added

#### Resume Version Management & Comparison System (HIGH)
- **Complete version history tracking** - Save, manage, and compare resume optimization attempts
  - Automatic version numbering and metadata tracking
  - Track company, job title, optimization style, tier, and statistics
  - Optional notes and tags for organization
  - Submission tracking (date submitted, response received status)
  - Storage statistics (total versions, disk usage, last updated)

- **Version History Browser**:
  - List all saved versions with smart filtering
  - Filter by company name, tags, or submission status
  - View detailed metrics for each version
  - Edit metadata, notes, and submission status
  - Delete old versions
  - Quick actions: View, Use, Edit, Delete

- **Version Comparison Tool**:
  - Side-by-side comparison of any two versions
  - Metrics delta visualization (overall score, authenticity, role alignment, ATS)
  - Content comparison (summary, headline, skills)
  - Before/after text comparison with highlighting

- **Seamless Workflow Integration**:
  - Automatic save dialog after change review completion
  - Three tabs in Step 4: Export Resume, Version History, Compare Versions
  - "Use This" button to load any version as current
  - Version saved with full optimization result and final resume

#### New Models & Data Structures
- **VersionMetadata model** - Track version details:
  - version_id, version_number, timestamp
  - job_title, company_name
  - optimization_style, optimization_tier
  - total_changes, accepted_changes, rejected_changes
  - notes, tags (for organization)
  - is_submitted, submitted_date, response_received (application tracking)

- **ResumeVersion model** - Complete version snapshot:
  - metadata, optimization_result, final_resume
  - job_description, original_resume_text
  - Helper methods: get_metrics_summary()

- **VersionComparison model** - Compare two versions:
  - get_metrics_delta() - Compute metric differences
  - get_text_diff() - Extract content differences

#### New Services
- **VersionManager Service** (`services/version_manager.py`):
  - save_version() - Save version to disk with metadata
  - load_version() - Load specific version by ID
  - list_versions() - List all versions with filtering
  - delete_version() - Remove version from storage
  - update_version_metadata() - Update notes, tags, submission status
  - compare_versions() - Create version comparison
  - get_storage_stats() - Storage usage analytics
  - JSON-based storage in ~/resume_tailor_versions
  - Version index for fast lookups

#### UI Components
- **Version Manager UI** (`modules/version_manager_ui.py`):
  - render_version_save_dialog() - Save current version with metadata
  - render_version_history() - Browse all saved versions
  - render_version_card() - Display individual version with actions
  - render_version_comparison() - Compare two versions side-by-side
  - render_comparison_results() - Visualize comparison metrics and content
  - render_version_editor() - Edit version metadata and tracking

### Enhanced

#### Workflow Integration
- Added version save dialog after completing change review (Step 3.5)
- Integrated version management into Step 4 with tabbed interface
- Export, History, and Compare tabs for complete version control
- "Use This" feature to load any saved version

#### User Experience
- Track application history (which versions were submitted, responses)
- Organize versions with custom tags and notes
- Filter and search through version history
- Compare optimization approaches across versions
- Informed decision-making with metrics comparison

### Technical Details

**Files Added:**
- `modules/version_models.py` - Data models for version management
- `services/version_manager.py` - Version storage and retrieval service
- `modules/version_manager_ui.py` - UI components for version management

**Files Modified:**
- `modules/optimization.py` - Trigger save dialog after change review
- `modules/output.py` - Add version management tabs

**Storage:**
- Versions stored in `~/resume_tailor_versions/`
- JSON format for easy portability
- Index file for fast lookups
- Incremental version numbering

**Impact:**
- ✅ Never lose optimization work
- ✅ Compare different approaches for same job
- ✅ Track application history and responses
- ✅ Organize versions by company and role
- ✅ Make data-driven decisions on resume versions
- ✅ Export any previous version at any time

**Backward Compatibility:**
- All changes maintain backward compatibility
- No breaking changes to existing features
- Version management is optional (doesn't interfere with normal workflow)

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
