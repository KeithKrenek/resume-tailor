# 🧪 Testing Guide - Resume Tailor Step 1

## Quick Test Checklist

### Pre-Flight Check
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Port 8501 available
- [ ] Internet connection (for URL scraping)

### Installation Test

```bash
# Clone and setup
cd resume-tailor
pip install -r requirements.txt

# Verify installation
python -c "import streamlit; import anthropic; print('✅ Dependencies OK')"
```

### Unit Tests

```bash
# Run all tests
pytest tests/test_validators.py -v

# Run with coverage
pytest tests/test_validators.py --cov=modules --cov=utils --cov-report=term-missing

# Expected: All tests should pass
```

### Application Launch Test

```bash
# Start the app
streamlit run app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

## Manual Testing Scenarios

### Test 1: Basic Job Description Input

**Steps:**
1. Launch app
2. Paste this job description:
   ```
   Senior Software Engineer

   We are seeking a Senior Software Engineer with 5+ years of experience.

   Responsibilities:
   - Design and develop web applications
   - Lead code reviews
   - Mentor junior developers

   Requirements:
   - BS in Computer Science
   - 5+ years Python/JavaScript experience
   - Cloud platform experience (AWS/GCP)

   Qualifications:
   - Strong problem-solving skills
   - Excellent communication
   - Agile methodology experience
   ```
3. Verify statistics appear (chars, words)
4. Check for ✅ green validation

**Expected Result:** ✅ Valid job description

### Test 2: Resume Upload (PDF)

**Prerequisite:** Have a PDF resume ready

**Steps:**
1. Click "Browse files"
2. Select a PDF resume
3. Wait for extraction
4. Check preview

**Expected Result:**
- ✅ Resume uploaded successfully
- Text appears in preview
- Metadata extracted (email, phone if present)

### Test 3: Resume Upload (DOCX)

**Steps:**
1. Click "Browse files"
2. Select a DOCX resume
3. Wait for extraction

**Expected Result:**
- ✅ Resume uploaded successfully
- Text extracted with formatting

### Test 4: Manual Resume Paste

**Steps:**
1. Skip file upload
2. Paste this resume text:
   ```
   John Doe
   john.doe@email.com
   (555) 123-4567

   EXPERIENCE
   Senior Software Engineer | Tech Co | 2020-Present
   - Led development of microservices architecture
   - Managed team of 5 developers
   - Implemented CI/CD pipeline

   Software Engineer | Startup | 2018-2020
   - Built RESTful APIs with Python
   - Designed PostgreSQL schemas

   EDUCATION
   BS Computer Science | University | 2018

   SKILLS
   Python, JavaScript, React, Node.js, AWS, Docker
   ```
3. Check validation

**Expected Result:**
- ✅ Resume is valid
- Email and phone detected
- Experience, Education, Skills sections detected

### Test 5: URL Scraping

**Steps:**
1. Find a public job posting URL (LinkedIn, Indeed, etc.)
2. Paste URL in "Job Posting URL" field
3. Click "🔍 Scrape URL"
4. Wait for scraping

**Expected Results:**
- Success: ✅ Job description scraped successfully
- OR: ⚠️ Clear error message if scraping fails
- Preview shows scraped content
- Description auto-populates

**Test URLs (public examples):**
- LinkedIn: Any public job posting
- Indeed: Search for jobs and copy URL
- Company career pages with Greenhouse/Lever

### Test 6: Company URL Input

**Steps:**
1. Enter company URL: `https://google.com`
2. Check validation

**Expected Result:** ✅ or no error

### Test 7: Output Folder Selection

**Steps:**
1. Enter folder path: `/tmp/resume_test`
2. Check validation

**Expected Result:**
- ✅ Output folder: /tmp/resume_test
- Folder created automatically

### Test 8: Validation Errors

**Test 8a: Short Job Description**
1. Enter: "Short text"
2. Check error message

**Expected:** ⚠️ Job description is too short

**Test 8b: Short Resume**
1. Enter: "Short resume"
2. Check error message

**Expected:** ⚠️ Resume is too short

**Test 8c: Invalid URL**
1. Enter: "not a url"
2. Check error message

**Expected:** ⚠️ Invalid URL format

### Test 9: Complete Workflow

**Steps:**
1. Enter valid job description (paste or scrape)
2. Upload valid resume (file or paste)
3. Enter company URL (optional)
4. Set output folder
5. Verify all inputs show ✅
6. Click "Continue to Analysis →"
7. Wait for extraction

**Expected Result:**
- ✅ Extracted: [Job Title] at [Company Name]
- ✅ Step 1 completed!
- 🎈 Balloons animation
- Automatically moves to Step 2 placeholder

### Test 10: Clear All Function

**Steps:**
1. Enter job description and resume
2. Click "🗑️ Clear All"

**Expected Result:**
- All fields cleared
- Page resets
- Session state cleared

### Test 11: Session Persistence

**Steps:**
1. Enter job description
2. Enter resume
3. Refresh page (press R)

**Expected Result:**
- Data persists in session
- Inputs remain filled

### Test 12: AI Extraction (with API key)

**Prerequisite:** Set `ANTHROPIC_API_KEY` in `.env`

**Steps:**
1. Complete valid job description
2. Complete valid resume
3. Click "Continue to Analysis"
4. Observe extraction

**Expected Result:**
- Uses AI to extract company and title
- More accurate than rule-based

### Test 13: AI Extraction Fallback (without API key)

**Prerequisite:** No API key set

**Steps:**
1. Complete workflow
2. Click "Continue"

**Expected Result:**
- Uses rule-based extraction
- Still extracts company/title (may be less accurate)
- No errors

## Performance Tests

### Test P1: Large Resume (100KB)
- Upload large resume
- Check extraction speed
- Expected: < 5 seconds

### Test P2: Long Job Description (10K chars)
- Paste very long job description
- Check validation speed
- Expected: Instant validation

### Test P3: Multiple File Formats
- Test PDF, DOCX, TXT, MD, JSON
- All should extract correctly

## Error Handling Tests

### Test E1: Corrupted PDF
- Upload corrupted/image-based PDF
- Expected: Clear error message, suggest alternatives

### Test E2: Network Timeout (URL Scraping)
- Scrape URL with timeout
- Expected: Error message, suggest manual paste

### Test E3: Invalid File Type
- Try to upload .exe or .zip
- Expected: File type not accepted

### Test E4: File Too Large
- Upload file > 5MB
- Expected: File size error message

## Browser Compatibility

Test in:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (macOS)
- [ ] Mobile browser (responsive design)

## Test Results Template

```markdown
## Test Session: [Date]

**Tester:** [Name]
**Environment:** [OS, Python version, Browser]

| Test | Status | Notes |
|------|--------|-------|
| Installation | ✅/❌ | |
| Unit Tests | ✅/❌ | |
| Job Description Input | ✅/❌ | |
| Resume Upload PDF | ✅/❌ | |
| Resume Upload DOCX | ✅/❌ | |
| Manual Resume Paste | ✅/❌ | |
| URL Scraping | ✅/❌ | |
| Complete Workflow | ✅/❌ | |
| AI Extraction | ✅/❌ | |
| Error Handling | ✅/❌ | |

**Issues Found:**
1. [Issue description]
2. [Issue description]

**Overall Assessment:** [Pass/Fail]
```

## Known Limitations

1. **Image-based PDFs:** Cannot extract text from scanned documents
2. **Some job boards:** May block automated scraping
3. **Very large files:** May be slow to process (>1MB)
4. **Non-English text:** Validation keywords are English-only

## Next Steps After Testing

If all tests pass:
1. Document any bugs found
2. Create issues for enhancements
3. Plan Step 2 implementation
4. Get user feedback

If tests fail:
1. Document failing tests
2. Debug and fix issues
3. Re-run test suite
4. Update code as needed
