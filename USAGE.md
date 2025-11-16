# 📖 Resume Tailor - Usage Guide

## Getting Started in 5 Minutes

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) Set up API key for AI extraction
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 2. Launch Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Step-by-Step Walkthrough

### Step 1: Input Collection

#### A. Enter Job Description

**Method 1: Scrape from URL** (Recommended)
1. Paste the job posting URL in the "Job Posting URL" field
2. Click "🔍 Scrape URL"
3. Preview the scraped content
4. The description will automatically populate

**Method 2: Manual Paste**
1. Copy the job description from the posting
2. Paste it in the text area below
3. The app will show character/word count

#### B. Upload Resume

**Method 1: File Upload** (Recommended)
1. Click "Browse files"
2. Select your resume (PDF, DOCX, TXT, MD, or JSON)
3. Wait for extraction
4. Preview the extracted text

**Method 2: Manual Paste**
1. Skip the file upload
2. Paste your resume text in the text area below
3. The app will validate the content

#### C. Configure Settings

**Company URL** (Optional)
- Enter the company website for additional context
- Example: `https://company.com`

**Output Folder**
- Choose where to save generated files
- Default: `~/resume_tailor_output`
- The folder will be created automatically

#### D. Continue

1. Ensure all inputs show ✅ green checkmarks
2. Click "Continue to Analysis →"
3. The app will extract company name and job title
4. You'll move to Step 2 automatically

## Tips & Best Practices

### For Best Results

**Job Description**
- ✅ Use complete job postings (not just a title)
- ✅ Include all sections (responsibilities, requirements, qualifications)
- ✅ Minimum 100 characters recommended
- ❌ Avoid partial or incomplete descriptions

**Resume**
- ✅ Include contact information (email/phone)
- ✅ Have clear sections (Experience, Education, Skills)
- ✅ Use standard formatting
- ❌ Avoid image-based PDFs (use text-based)

**Output**
- ✅ Choose a dedicated folder for each application
- ✅ Use descriptive folder names (e.g., `Company_Position_Date`)
- ✅ Keep original files as backup

### Keyboard Shortcuts

- `R` - Refresh/Reload page
- `Ctrl/Cmd + K` - Clear cache
- `Esc` - Close sidebar

## Common Workflows

### Workflow 1: Quick Application

```
1. Paste job URL → Scrape
2. Upload resume PDF
3. Continue
4. Review AI suggestions
5. Generate tailored resume
6. Download and apply
```

**Time:** ~2-3 minutes

### Workflow 2: Multiple Applications

```
1. Upload your master resume once
2. For each job:
   a. Paste job URL
   b. Set output folder (Company_Position)
   c. Generate tailored version
3. Compare results
4. Choose best version
```

**Time:** ~5 minutes per job

### Workflow 3: Career Change

```
1. Paste job in target industry
2. Upload current resume
3. Review gap analysis (Step 2)
4. Identify missing skills
5. Optimize resume with new focus (Step 3)
6. Generate tailored version (Step 4)
```

**Time:** ~10-15 minutes

## Troubleshooting

### Common Issues

**Issue: PDF won't upload**
- Solution: Ensure it's a text-based PDF (not scanned)
- Workaround: Copy text and paste manually
- Alternative: Convert to DOCX or TXT

**Issue: URL scraping fails**
- Solution: Check internet connection
- Workaround: Copy job description manually
- Note: Some sites block automated scraping

**Issue: Validation errors**
- Check minimum length requirements
- Ensure contact info is present
- Verify job-related keywords exist

**Issue: AI extraction not working**
- Verify `ANTHROPIC_API_KEY` is set in `.env`
- Check API key is valid
- Note: Rule-based extraction will work as fallback

### Getting Help

1. Check the console for error messages
2. Review the sidebar "Session Info" panel
3. Try "Clear All" to reset
4. Restart the application

## Examples

### Example Job Description Input

```
Senior Software Engineer

We are seeking a talented Senior Software Engineer to join our team.

Responsibilities:
- Design and develop scalable web applications
- Lead technical discussions and code reviews
- Mentor junior developers

Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- Experience with cloud platforms (AWS/GCP/Azure)

Qualifications:
- Bachelor's degree in Computer Science or related field
- Excellent problem-solving and communication skills
- Experience with agile development methodologies
```

**Result:** ✅ Valid (contains responsibilities, requirements, qualifications)

### Example Resume Input

```
John Doe
Email: john.doe@email.com
Phone: (555) 123-4567

PROFESSIONAL EXPERIENCE

Senior Software Engineer | Tech Company | 2020-Present
- Developed microservices architecture serving 1M+ users
- Led team of 5 developers in agile environment
- Implemented CI/CD pipeline reducing deployment time by 50%

Software Engineer | Startup Inc | 2018-2020
- Built RESTful APIs using Python and FastAPI
- Designed database schemas in PostgreSQL
- Collaborated with product team on feature development

EDUCATION

Bachelor of Science in Computer Science
University of Technology, 2018

SKILLS

Languages: Python, JavaScript, TypeScript, Java
Frameworks: React, Node.js, Django, FastAPI
Cloud: AWS, Docker, Kubernetes
Tools: Git, Jenkins, JIRA
```

**Result:** ✅ Valid (has email, phone, experience, education, skills)

## Advanced Features

### JSON Resume Format

Upload a JSON resume following the [JSON Resume](https://jsonresume.org/) schema:

```json
{
  "basics": {
    "name": "John Doe",
    "email": "john@email.com",
    "phone": "(555) 123-4567"
  },
  "work": [
    {
      "company": "Tech Company",
      "position": "Senior Engineer",
      "summary": "Led development of scalable applications"
    }
  ],
  "education": [...],
  "skills": [...]
}
```

### Markdown Resume

Upload a markdown resume with proper formatting:

```markdown
# John Doe

**Email:** john@email.com | **Phone:** (555) 123-4567

## Experience

### Senior Software Engineer - Tech Company
*2020 - Present*

- Achievement 1
- Achievement 2

## Education

**BS Computer Science** - University, 2018
```

## Next Steps

After completing Step 1, the app will:

1. **Step 2: Analysis**
   - Extract job requirements and skills
   - Parse your resume structure
   - Perform gap analysis
   - Calculate coverage percentage
   - Provide detailed metrics and recommendations

2. **Step 3: Optimization**
   - Choose optimization style (Conservative/Balanced/Aggressive)
   - AI-powered resume rewriting
   - Keyword optimization for ATS
   - Track all changes with rationales
   - Authenticity verification (Hallucination Guard)

3. **Step 4: Output Generation**
   - Preview optimized resume
   - Download in multiple formats (PDF, DOCX, HTML, Markdown)
   - Save to output folder
   - Review authenticity report
   - Start new resume or go back to edit

---

**Questions?** Check the README.md for more details.
