# 🧪 Step 2 Testing Guide - Job & Resume Analysis

## Quick Test (5 minutes)

### Prerequisites
1. Anthropic API key set in `.env`:
   ```bash
   echo "ANTHROPIC_API_KEY=your_actual_api_key" > .env
   ```

2. Install any missing dependencies:
   ```bash
   pip install pandas anthropic
   ```

3. Verify tests pass:
   ```bash
   pytest tests/ -v
   # Should show: 52 passed
   ```

### Run the App

```bash
streamlit run app.py
```

### Test Workflow

#### 1. Complete Step 1 (2 minutes)
- **Job Description**: Paste this sample or find a real one:
  ```
  Senior Software Engineer

  We are seeking a Senior Software Engineer with 5+ years of experience.

  Responsibilities:
  - Design and develop scalable web applications
  - Lead technical discussions and code reviews
  - Mentor junior developers
  - Collaborate with product team

  Requirements:
  - BS in Computer Science or equivalent
  - 5+ years of professional software development
  - Strong proficiency in Python and JavaScript
  - Experience with cloud platforms (AWS, GCP, or Azure)
  - Experience with SQL and NoSQL databases
  - Strong problem-solving skills
  - Excellent communication skills

  Preferred Skills:
  - Docker and Kubernetes
  - CI/CD pipelines
  - GraphQL
  - React or Vue.js
  - Agile methodologies
  ```

- **Resume**: Upload a PDF/DOCX or paste text like:
  ```
  John Doe
  john.doe@email.com | (555) 123-4567 | San Francisco, CA

  PROFESSIONAL SUMMARY
  Senior Software Engineer with 7 years of experience building scalable web applications.
  Expertise in Python, JavaScript, and cloud technologies.

  WORK EXPERIENCE

  Senior Software Engineer | TechCorp | 2020 - Present
  - Designed and implemented microservices architecture serving 1M+ users
  - Led team of 5 developers using Agile methodologies
  - Reduced deployment time by 50% through CI/CD automation
  - Technologies: Python, JavaScript, AWS, Docker, PostgreSQL

  Software Engineer | StartupCo | 2018 - 2020
  - Built RESTful APIs using Python and FastAPI
  - Developed frontend components with React
  - Implemented automated testing with 90% coverage
  - Technologies: Python, React, MongoDB, Redis

  EDUCATION
  BS Computer Science | University of Technology | 2018
  GPA: 3.8/4.0

  SKILLS
  Languages: Python, JavaScript, TypeScript, SQL
  Frameworks: Django, FastAPI, React, Node.js
  Cloud: AWS (EC2, S3, Lambda), Docker
  Databases: PostgreSQL, MongoDB, Redis
  Tools: Git, Jenkins, JIRA
  ```

- Click **"Continue to Analysis →"**

#### 2. Watch Step 2 Analysis (30-45 seconds)

You should see:
1. ✅ **Status Panel 1**: "Analyzing job posting..." → "✅ Job posting analyzed"
2. ✅ **Status Panel 2**: "Analyzing resume..." → "✅ Resume analyzed"
3. ✅ **Status Panel 3**: "Performing gap analysis..." → "✅ Gap analysis complete"
4. ✅ **Status Panel 4**: "Saving analysis results..." → "✅ Results saved"
5. 🎈 **Balloons** animation
6. ✅ **Success message**: "Analysis complete!"

#### 3. Review Results

**Summary Metrics** (top of page):
- Overall Match: ~75-85%
- Matched Skills: ~8-10
- Missing Required: ~2-4

**Tab 1: Job Analysis**
- Expand "📄 Job Details" - see title, company, level
- Expand "📝 Requirements Breakdown" - see table of all requirements
- Expand "🔴 Required Skills" - see list of must-have skills
- Expand "🟡 Preferred Skills" - see nice-to-have skills

**Tab 2: Resume Analysis**
- See metrics: 7 years experience, 2 positions, 12 skills
- Expand "👤 Contact Information" - see name, email, phone
- Expand "💼 Work Experience" - see detailed positions with bullets
- Expand "🛠️ Skills" - see full skills list
- Expand "🎓 Education" - see degree details

**Tab 3: Gap Analysis**
- See coverage percentage and metrics
- Read "✅ Strengths" section (should show 4-5 items)
- Read "⚠️ Gaps to Address" section (should show 1-2 items)
- Expand "📊 Detailed Skill Analysis":
  - **✅ Matched tab**: See skills with evidence (e.g., "Python - Listed in skills section; Used in TechCorp role")
  - **❌ Missing tab**: See missing required skills (e.g., "Kubernetes", "GraphQL")
  - **⚡ Weak Coverage tab**: See weakly covered skills
- Read "💡 Recommendations" section (should show 3-5 suggestions)

#### 4. Check Output Files

Navigate to your output folder (default: `~/resume_tailor_output`):

```bash
ls -lh ~/resume_tailor_output/
```

You should see:
```
job_analysis.json         # ~2-5 KB
resume_analysis.json      # ~5-10 KB
gap_analysis.json         # ~3-8 KB
analysis_summary.txt      # ~2-4 KB (human-readable)
```

Open `analysis_summary.txt` and verify it's formatted correctly.

#### 5. Test Controls

- **🔄 Re-analyze button**: Click it → should re-run analysis with fresh API calls
- **← Back to Step 1**: Click it → should return to input page (data persists)
- **Continue to Optimization →**: Click it → should show "Step 3: Coming Soon"

---

## Expected Results

### Job Analysis Output

Should extract:
- ✅ Title: "Senior Software Engineer"
- ✅ Experience Level: "Senior"
- ✅ 6-10 requirements with categories
- ✅ 5-7 required skills
- ✅ 3-5 preferred skills
- ✅ 3-5 responsibilities

### Resume Analysis Output

Should extract:
- ✅ Name: "John Doe"
- ✅ Email and phone
- ✅ 2 work experiences with bullets
- ✅ Skills list: 10-15 items
- ✅ Education: BS degree
- ✅ Total years: 7

### Gap Analysis Output

Should identify:
- ✅ **Matched**: Python, JavaScript, AWS, Docker, PostgreSQL, React, CI/CD
- ✅ **Missing Required**: Kubernetes, NoSQL (maybe), Vue.js (maybe)
- ✅ **Missing Preferred**: GraphQL, (maybe others)
- ✅ **Coverage**: 70-85%
- ✅ **Strengths**: Experience level, technical skills, relevant positions
- ✅ **Suggestions**: Add Kubernetes, strengthen certain skills

---

## Troubleshooting

### Issue: "Anthropic API client not available"
**Fix**: Ensure `.env` file exists with valid `ANTHROPIC_API_KEY`

### Issue: Analysis takes >2 minutes
**Fix**: Check internet connection, API may be slow. Re-analyze.

### Issue: "Failed to parse response"
**Fix**: Claude response may be malformed. Click "Re-analyze".

### Issue: Coverage shows 0%
**Fix**: Job may have no requirements. Try different job description.

### Issue: Missing files in output folder
**Fix**: Check folder permissions. Try different output folder.

---

## Test Cases

### Test Case 1: Perfect Match
- Use job description with Python, AWS
- Use resume with Python, AWS prominently featured
- **Expected**: Coverage >80%, few missing skills

### Test Case 2: Junior Position
- Use entry-level job description
- Use junior resume (1-2 years experience)
- **Expected**: Should detect experience level match

### Test Case 3: Career Change
- Use job in different field (e.g., Data Science)
- Use resume from different field (e.g., Web Development)
- **Expected**: Lower coverage, many missing skills, clear suggestions

### Test Case 4: Multiple Formats
- Test with PDF resume
- Test with DOCX resume
- Test with pasted text resume
- **Expected**: All should work, extract similar data

### Test Case 5: Re-analyze
- Complete analysis once
- Click "Re-analyze"
- **Expected**: Should run again with fresh results

---

## Success Checklist

- [ ] Analysis completes in 30-60 seconds
- [ ] All 4 status panels show ✅
- [ ] Summary metrics displayed
- [ ] All 3 tabs render without errors
- [ ] Skills show evidence/context
- [ ] Suggestions are actionable
- [ ] Output files created in folder
- [ ] Summary report is readable
- [ ] Re-analyze works
- [ ] Navigation works (back/forward)
- [ ] No Python errors in console

---

## Performance Benchmarks

**Acceptable**:
- Job analysis: 10-25 seconds
- Resume analysis: 10-25 seconds
- Gap analysis: <2 seconds
- Total: 25-60 seconds

**Problematic** (investigate if you see these):
- >40 seconds per API call
- >2 minutes total
- Timeouts or connection errors

---

## Next Steps After Testing

If all tests pass:
1. ✅ Document any issues found
2. ✅ Test with your own resume and real job postings
3. ✅ Review analysis accuracy and suggestions quality
4. ✅ Check API costs (each run = 2 API calls)
5. ✅ Provide feedback for improvements
6. ✅ Ready to proceed to Step 3: Resume Optimization

If issues found:
1. ❌ Document specific error messages
2. ❌ Check browser console for JavaScript errors
3. ❌ Check terminal for Python errors
4. ❌ Verify API key is valid
5. ❌ Try with different inputs
6. ❌ Report issues before proceeding

---

Happy Testing! 🚀
