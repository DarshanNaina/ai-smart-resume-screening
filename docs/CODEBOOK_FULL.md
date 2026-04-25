# Smart Resume Screening — Full Python Source Codebook

Auto-generated bundle of all `.py` files (excluding `.venv`, `__pycache__`, etc.).

---

## `app.py`

```python
import streamlit as st
from resume_parser import extract_info, extract_text_from_file
from job_description import clean_job_description
from nlp_processing import preprocess_text
from skill_matching import match_skills
from matching_algorithm import score_resumes
from candidate_ranking import rank_candidates

st.title("AI-Based Smart Resume Screening System")

# Upload resumes
uploaded_files = st.file_uploader("Upload Resumes", accept_multiple_files=True, type=["pdf", "docx"])

# Job Description Input
job_description = st.text_area("Job Description")

if st.button("Evaluate"):
    resumes = {}
    for uploaded_file in uploaded_files:
        text = extract_text_from_file(uploaded_file)
        resume_info = extract_info(text)
        resumes[resume_info['name']] = {
            'email': resume_info['email'],
            'skills': resume_info['skills'],
            'text': text
        }
    
    job_skills = ["python", "communication", "teamwork"]  # For demonstration, hardcoded
    resume_scores = score_resumes([resume['text'] for resume in resumes.values()], job_description)
    
    ranked_candidates = rank_candidates(dict(zip(resumes.keys(), resume_scores)))
    
    for candidate in ranked_candidates:
        st.write(f"Candidate: {candidate[0]}, Score: {candidate[1]:.2f}%")
```

## `candidate_ranking.py`

```python
"""
candidate_ranking.py
====================
PURPOSE: Rank multiple candidates based on their match scores and generate detailed reports.

HOW IT WORKS:
- Takes a list of candidates with their scores
- Sorts them from highest to lowest score (best candidate first)
- Generates a detailed human-readable report for each candidate
- Produces a summary ranking table

REAL WORLD ANALOGY:
Think of this as the "scoreboard" system at an exam.
After everyone submits their test, this module:
1. Ranks all candidates from highest to lowest score
2. Tells each candidate which skills they matched and which they're missing
3. Gives HR a clear prioritized list of who to call first

"""

# --- IMPORTS ---
from datetime import datetime  # For adding timestamp to reports


def rank_candidates(candidates_data):
    """
    Sorts candidates from highest to lowest final_score.

    PARAMETER:
        candidates_data (list): List of candidate dictionaries
                                Each dict must have at minimum:
                                {'name': ..., 'final_score': ...}

    RETURNS:
        list: Same list but sorted by final_score (highest first)
    """

    # sorted() creates a new sorted list (doesn't modify original)
    # key=lambda x: x['final_score'] → sort by this field
    # reverse=True → highest score first (descending order)
    ranked = sorted(candidates_data, key=lambda x: x['final_score'], reverse=True)

    # Add rank numbers (1 = best, 2 = second best, etc.)
    for position, candidate in enumerate(ranked):
        # enumerate gives index starting from 0, so we add 1 for human-readable rank
        candidate['rank'] = position + 1

    return ranked


def generate_candidate_report(candidate):
    """
    Creates a detailed text report for a single candidate.

    PARAMETER:
        candidate (dict): Candidate data with all scores and skill info

    RETURNS:
        str: Formatted text report
    """

    # Start building the report as a string
    # We use a list and join at end (faster than string concatenation)
    report_lines = []

    # Header separator
    report_lines.append("=" * 60)
    report_lines.append(f"  RANK #{candidate.get('rank', '?')} — {candidate.get('name', 'Unknown')}")
    report_lines.append("=" * 60)

    # Score Summary section
    report_lines.append("\n📊 SCORE SUMMARY:")
    report_lines.append(f"   Overall Match Score : {candidate.get('final_score', 0):.2f}%")
    report_lines.append(f"   TF-IDF Similarity   : {candidate.get('tfidf_percent', 0):.2f}%")
    report_lines.append(f"   Skill Match Score   : {candidate.get('skill_score', 0):.2f}%")

    # Interpretation
    report_lines.append(f"\n🔍 VERDICT: {candidate.get('interpretation', 'N/A')}")

    # Matching Skills section
    matching = candidate.get('matching_skills', set())
    if matching:
        report_lines.append(f"\n✅ MATCHING SKILLS ({len(matching)} found):")
        # Sort for consistent, readable output
        skill_list = sorted(list(matching))
        # Group skills in rows of 4 for readability
        for i in range(0, len(skill_list), 4):
            row = skill_list[i:i+4]  # Get up to 4 skills
            report_lines.append("   • " + "   • ".join(row))
    else:
        report_lines.append("\n✅ MATCHING SKILLS: None found")

    # Missing Skills section
    missing = candidate.get('missing_skills', set())
    if missing:
        report_lines.append(f"\n❌ MISSING SKILLS ({len(missing)} missing):")
        skill_list = sorted(list(missing))
        for i in range(0, len(skill_list), 4):
            row = skill_list[i:i+4]
            report_lines.append("   ✗ " + "   ✗ ".join(row))
    else:
        report_lines.append("\n❌ MISSING SKILLS: None! Candidate meets all requirements.")

    # Recommendation section
    score = candidate.get('final_score', 0)
    report_lines.append("\n💡 RECOMMENDATION:")
    if score >= 80:
        report_lines.append("   → SHORTLIST IMMEDIATELY. Excellent candidate.")
    elif score >= 65:
        report_lines.append("   → Schedule for first-round interview.")
    elif score >= 50:
        report_lines.append("   → Review manually before deciding.")
    elif score >= 35:
        report_lines.append("   → Consider only if shortage of candidates.")
    else:
        report_lines.append("   → Not recommended for this role.")

    report_lines.append("")  # Empty line at end

    # Join all lines with newline character
    return "\n".join(report_lines)


def generate_ranking_summary(ranked_candidates, role_name=""):
    """
    Creates a concise summary table showing all candidates ranked.

    This is the "at a glance" view for HR managers.

    PARAMETERS:
        ranked_candidates (list): Sorted list of candidate dicts
        role_name (str): Name of the job role (for display)

    RETURNS:
        str: Formatted ranking table as string
    """

    lines = []

    # Report header
    lines.append("\n" + "=" * 70)
    lines.append("           AI RESUME SCREENING SYSTEM — RANKING REPORT")
    lines.append("=" * 70)

    if role_name:
        lines.append(f"Role: {role_name}")

    # Add current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"Generated: {timestamp}")
    lines.append(f"Total Candidates Screened: {len(ranked_candidates)}")
    lines.append("-" * 70)

    # Table header row
    lines.append(f"\n{'Rank':<6} {'Candidate Name':<25} {'Final Score':<14} {'Verdict'}")
    lines.append("-" * 70)

    # Data rows — one per candidate
    for candidate in ranked_candidates:
        rank = candidate.get('rank', '?')
        name = candidate.get('name', 'Unknown')[:24]  # Truncate long names
        score = candidate.get('final_score', 0)
        verdict = candidate.get('interpretation', 'N/A')

        # Remove emoji from verdict for table (cleaner display)
        verdict_clean = verdict.split("—")[-1].strip() if "—" in verdict else verdict

        # f-string formatting: :<N means left-align in N characters
        lines.append(f"{rank:<6} {name:<25} {score:<14.2f} {verdict_clean}")

    lines.append("-" * 70)

    # Add shortlisted candidates summary
    shortlisted = [c for c in ranked_candidates if c.get('final_score', 0) >= 65]
    lines.append(f"\n📋 SHORTLISTED CANDIDATES ({len(shortlisted)} of {len(ranked_candidates)}):")
    if shortlisted:
        for c in shortlisted:
            lines.append(f"   #{c['rank']} {c['name']} — {c['final_score']:.2f}%")
    else:
        lines.append("   No candidates meet the shortlisting threshold (65%)")

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)


def generate_full_report(ranked_candidates, role_name=""):
    """
    MAIN FUNCTION: Generates the complete report for all candidates.

    Combines:
    1. Summary ranking table (all candidates at a glance)
    2. Detailed individual reports (for each candidate)

    PARAMETERS:
        ranked_candidates (list): Sorted list of candidates
        role_name (str): Job role name

    RETURNS:
        str: Complete report as formatted text
    """

    # Start with the summary table
    full_report = generate_ranking_summary(ranked_candidates, role_name)

    # Add detailed report for each candidate
    full_report += "\n\n" + "=" * 70
    full_report += "\n           DETAILED CANDIDATE REPORTS"
    full_report += "\n" + "=" * 70 + "\n"

    for candidate in ranked_candidates:
        full_report += generate_candidate_report(candidate)

    return full_report


def save_report(report_text, filename="screening_report.txt"):
    """
    Saves the report to a text file.

    PARAMETERS:
        report_text (str): The report content
        filename (str): Output filename

    RETURNS:
        str: Path where file was saved
    """
    try:
        # Open file in write mode, using UTF-8 encoding for special characters
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"[INFO] Report saved to: {filename}")
        return filename
    except Exception as e:
        print(f"[ERROR] Could not save report: {e}")
        return ""


# ---- TEST / DEMO ----
if __name__ == "__main__":
    print("=== Candidate Ranking Test ===\n")

    # Sample data simulating output from matching_algorithm.py
    sample_candidates = [
        {
            'name': 'Alice Johnson',
            'final_score': 82.5,
            'tfidf_percent': 78.0,
            'skill_score': 87.0,
            'interpretation': '🌟 Excellent Match — Highly Recommended',
            'matching_skills': {'python', 'machine learning', 'sql', 'pandas', 'tensorflow'},
            'missing_skills': {'pytorch', 'deep learning'}
        },
        {
            'name': 'Bob Smith',
            'final_score': 61.3,
            'tfidf_percent': 55.0,
            'skill_score': 67.6,
            'interpretation': '🟡 Moderate Match — Consider for Interview',
            'matching_skills': {'python', 'sql', 'pandas'},
            'missing_skills': {'machine learning', 'tensorflow', 'pytorch', 'deep learning'}
        },
        {
            'name': 'Carol White',
            'final_score': 74.8,
            'tfidf_percent': 70.2,
            'skill_score': 79.4,
            'interpretation': '✅ Good Match — Recommended for Interview',
            'matching_skills': {'python', 'machine learning', 'tensorflow', 'sql'},
            'missing_skills': {'pytorch', 'deep learning', 'pandas'}
        }
    ]

    # Rank the candidates
    ranked = rank_candidates(sample_candidates)

    # Generate and print the full report
    report = generate_full_report(ranked, "Data Scientist")
    print(report)
```

## `job_description.py`

```python

# --- IMPORTS ---
import os  # For file path operations (if loading from file)


# ============================================================
# BUILT-IN JOB DESCRIPTIONS DICTIONARY
# ============================================================
# This dictionary stores sample job descriptions for different roles.
# KEY   = Role name (what you type to select)
# VALUE = Full job description text

JOB_DESCRIPTIONS = {

    "data_scientist": """
        We are looking for an experienced Data Scientist to join our team.

        Required Skills:
        Python, Machine Learning, Deep Learning, TensorFlow, PyTorch,
        Data Analysis, Statistics, SQL, Data Visualization, Pandas, NumPy,
        Scikit-learn, Natural Language Processing, Computer Vision,
        Matplotlib, Seaborn, Jupyter Notebook, Git, GitHub,
        Communication Skills, Problem Solving, Critical Thinking.

        Responsibilities:
        - Build and deploy machine learning models
        - Analyze large datasets to extract insights
        - Collaborate with engineering and product teams
        - Present findings to stakeholders
        - Optimize existing models for better performance

        Experience: Minimum 2 years in data science or related field.
        Education: Bachelor's or Master's degree in Computer Science, Statistics, or related field.
    """,

    "software_engineer": """
        We are hiring a Software Engineer for our backend development team.

        Required Skills:
        Python, Java, JavaScript, REST API, Django, Flask, Spring Boot,
        SQL, PostgreSQL, MySQL, MongoDB, Git, GitHub, Docker, Kubernetes,
        AWS, Linux, Agile, Scrum, Problem Solving, Communication,
        Unit Testing, CI/CD, Microservices, System Design.

        Responsibilities:
        - Design and implement scalable backend services
        - Write clean, tested, maintainable code
        - Collaborate with frontend and DevOps teams
        - Participate in code reviews
        - Debug and resolve production issues

        Experience: 1-4 years of software development experience.
        Education: Bachelor's degree in Computer Science or equivalent.
    """,

    "web_developer": """
        Looking for a Front-End / Full Stack Web Developer.

        Required Skills:
        HTML, CSS, JavaScript, React, Angular, Vue.js, Node.js,
        Bootstrap, Tailwind CSS, REST API, JSON, Git, GitHub,
        Responsive Design, UI/UX, Figma, TypeScript, Next.js,
        MongoDB, MySQL, Redux, Problem Solving, Teamwork.

        Responsibilities:
        - Build responsive and interactive web applications
        - Convert UI/UX designs into working code
        - Ensure cross-browser compatibility
        - Optimize web performance
        - Work with backend APIs

        Experience: 1-3 years in web development.
        Education: Any degree in Computer Science or related field.
    """,

    "hr_manager": """
        We are looking for an HR Manager to lead our People & Culture team.

        Required Skills:
        Recruitment, Talent Acquisition, Employee Relations, Payroll,
        Performance Management, HR Policies, Communication, Leadership,
        Conflict Resolution, Onboarding, HRIS Systems, MS Excel,
        Labor Law, Training & Development, Team Management,
        Problem Solving, Emotional Intelligence, Negotiation.

        Responsibilities:
        - Manage end-to-end recruitment processes
        - Handle employee relations and grievances
        - Design and implement HR policies
        - Conduct performance appraisals
        - Manage payroll and benefits

        Experience: 4-6 years in HR or People Management.
        Education: MBA in HR or equivalent.
    """,

    "data_analyst": """
        Seeking a Data Analyst to help drive data-driven decisions.

        Required Skills:
        Python, SQL, Excel, Power BI, Tableau, Data Visualization,
        Statistics, Data Cleaning, Pandas, NumPy, Matplotlib,
        Google Analytics, A/B Testing, Reporting, Communication,
        Critical Thinking, Problem Solving, Attention to Detail.

        Responsibilities:
        - Collect, clean and analyze large datasets
        - Create dashboards and reports for business teams
        - Identify trends and actionable insights
        - Support business decisions with data evidence
        - Present findings to non-technical stakeholders

        Experience: 1-3 years in data analysis.
        Education: Bachelor's in Statistics, Mathematics, or Computer Science.
    """
}


def get_job_description(role_name):
    """
    Fetches the job description for a given role.

    PARAMETER:
        role_name (str): Name of the role (e.g., "data_scientist")

    RETURNS:
        str: Full job description text, or empty string if not found
    """

    # Convert to lowercase and replace spaces with underscores for matching
    # Example: "Data Scientist" -> "data_scientist"
    role_key = role_name.lower().replace(" ", "_")

    # Look up the role in our dictionary
    if role_key in JOB_DESCRIPTIONS:
        print(f"[INFO] Loaded job description for role: {role_name}")
        return JOB_DESCRIPTIONS[role_key]
    else:
        # Role not found in our database
        print(f"[WARNING] Role '{role_name}' not found. Available roles: {list(JOB_DESCRIPTIONS.keys())}")
        return ""


def load_jd_from_text(jd_text):
    """
    If user types/pastes a custom job description, just clean and return it.

    PARAMETER:
        jd_text (str): Raw job description text entered by user

    RETURNS:
        str: Cleaned JD text
    """
    return jd_text.strip()  # Remove leading/trailing whitespace


def list_available_roles():
    """
    Returns a list of all available job roles in our system.

    RETURNS:
        list: List of role name strings
    """
    return list(JOB_DESCRIPTIONS.keys())  # Get all keys from dictionary


# ---- TEST / DEMO ----
if __name__ == "__main__":
    print("=== Job Description Module Test ===\n")

    # Show available roles
    print("Available Roles:", list_available_roles())
    print()

    # Fetch and display a sample JD
    jd = get_job_description("data_scientist")
    print("Data Scientist JD (first 300 chars):\n", jd[:300], "...")
```

## `main.py`

```python
"""
main.py
=======
PURPOSE: The central control file that ties all modules together.

This is the file you run to use the system.
It orchestrates the entire pipeline:

PIPELINE FLOW:
    Resume Files / Text
          ↓
    resume_parser.py     → Extract raw text
          ↓
    nlp_processing.py    → Clean and preprocess text
          ↓
    skill_matching.py    → Find matching & missing skills
          ↓
    matching_algorithm.py → Calculate similarity scores (TF-IDF)
          ↓
    candidate_ranking.py  → Rank all candidates
          ↓
    Final Report         → Display results

HOW TO RUN:
    python main.py

MODES:
    1. Demo Mode: Uses built-in sample resumes (no files needed)
    2. File Mode: Reads real PDF/DOCX files from your computer
"""

# --- IMPORT ALL OUR MODULES ---
from resume_parser import parse_resume, parse_resume_from_text     # Parse resumes
from job_description import get_job_description, list_available_roles  # Get JD
from nlp_processing import preprocess_to_string                    # NLP preprocessing
from skill_matching import get_skill_analysis                      # Skill extraction
from matching_algorithm import match_resume_to_jd                  # Similarity scoring
from candidate_ranking import rank_candidates, generate_full_report, save_report  # Ranking


# ============================================================
# SAMPLE RESUMES FOR DEMO MODE
# ============================================================
# These are built-in sample resumes so you can test without needing real files.
# Each entry has a 'name' and 'text' key.

SAMPLE_RESUMES = [
    {
        "name": "Alice Johnson",
        "text": """
        Alice Johnson
        Email: alice.johnson@email.com | Phone: +1-234-567-8901
        LinkedIn: linkedin.com/in/alicejohnson

        PROFESSIONAL SUMMARY:
        Data Scientist with 4 years of experience in machine learning, deep learning,
        and natural language processing. Proven track record of delivering business insights.

        TECHNICAL SKILLS:
        Languages: Python, R, SQL
        ML/AI: Machine Learning, Deep Learning, Natural Language Processing, Computer Vision
        Frameworks: TensorFlow, PyTorch, Scikit-learn, Keras, Pandas, NumPy
        Visualization: Matplotlib, Seaborn, Tableau, Power BI
        Databases: MySQL, PostgreSQL, MongoDB
        Tools: Git, GitHub, Jupyter Notebook, Docker, AWS

        EXPERIENCE:
        Senior Data Scientist | TechCorp Solutions (2021 - Present)
        - Developed machine learning models increasing sales prediction accuracy by 35%
        - Built NLP pipeline for customer sentiment analysis using BERT (HuggingFace)
        - Created Power BI dashboards for executive reporting
        - Led team of 3 junior data scientists

        Data Analyst | DataDriven Inc (2019 - 2021)
        - Performed statistical analysis on customer datasets (2M+ records)
        - Built predictive models using Python and Scikit-learn
        - Developed automated reporting using SQL and Excel

        EDUCATION:
        M.Tech in Computer Science | IIT Delhi | 2019
        B.Tech in Electronics | Delhi University | 2017

        CERTIFICATIONS:
        - AWS Certified Machine Learning Specialty
        - Google Professional Data Engineer
        - TensorFlow Developer Certificate
        """
    },
    {
        "name": "Bob Smith",
        "text": """
        Bob Smith
        Email: bob.smith@email.com | Phone: +1-987-654-3210

        SUMMARY:
        Fresh graduate with knowledge of Python and basic data analysis.
        Completed several online courses in machine learning.
        Eager to learn and grow in a professional environment.

        SKILLS:
        Python (Intermediate), SQL (Basic), Excel, Pandas (Basic),
        Matplotlib, Git, Communication, Teamwork, Problem Solving

        PROJECTS:
        Student Grade Predictor (College Project):
        - Used Python and Scikit-learn to predict student grades
        - Applied linear regression on dataset of 500 students
        - Achieved 78% accuracy on test data

        Movie Recommendation System:
        - Built collaborative filtering system using Python
        - Used Pandas for data manipulation and Matplotlib for visualization

        EDUCATION:
        B.Tech in Computer Science | Mumbai University | 2024
        CGPA: 7.8 / 10.0

        CERTIFICATIONS:
        - Coursera: Machine Learning by Andrew Ng
        - Udemy: Python for Data Science
        - Google: Fundamentals of Digital Marketing
        """
    },
    {
        "name": "Carol White",
        "text": """
        Carol White
        Email: carol.white@email.com | GitHub: github.com/carolwhite

        PROFESSIONAL PROFILE:
        2.5 years experienced Data Scientist specializing in NLP and predictive analytics.
        Strong background in Python, machine learning, and data visualization.

        SKILLS:
        Programming: Python, SQL, R
        Machine Learning: Scikit-learn, Machine Learning, TensorFlow, XGBoost
        NLP: Natural Language Processing, NLTK, SpaCy, Text Classification
        Data: Pandas, NumPy, Data Analysis, Data Visualization
        Visualization: Matplotlib, Seaborn, Tableau
        Cloud: AWS, Google Cloud (GCP)
        Others: Git, GitHub, Docker, Agile, Communication, Leadership

        WORK EXPERIENCE:
        Data Scientist | Analytics Hub (2022 - Present)
        - Developed text classification model with 91% accuracy for support tickets
        - Built customer churn prediction model saving $2M annually
        - Deployed ML models to AWS SageMaker production environment
        - Conducted weekly data insights sessions for business stakeholders

        Junior Data Analyst | StartupXYZ (2021 - 2022)
        - Cleaned and analyzed datasets of 500K+ records using Python and SQL
        - Created automated Tableau dashboards reducing manual reporting by 60%

        EDUCATION:
        B.Sc. Statistics | University of Delhi | 2021

        SOFT SKILLS:
        Communication, Leadership, Teamwork, Problem Solving, Critical Thinking
        """
    },
    {
        "name": "David Lee",
        "text": """
        David Lee
        Email: david.lee@email.com

        OBJECTIVE:
        Seeking a position in data or IT domain. Background in web development
        and some exposure to data analytics.

        SKILLS:
        HTML, CSS, JavaScript, React, Node.js, Python (basic),
        MySQL, Excel, Git, Communication

        EXPERIENCE:
        Web Developer | Freelance (2022 - 2024)
        - Developed 10+ websites for local businesses using HTML, CSS, React
        - Managed MySQL databases for e-commerce clients
        - Integrated payment gateways and REST APIs

        EDUCATION:
        B.Sc. IT | Pune University | 2022

        INTERESTS:
        Learning machine learning, data analysis, Python programming
        """
    }
]


def run_screening(resumes, jd_text, jd_role="Job Role"):
    """
    CORE PIPELINE FUNCTION: Screens all resumes against a job description.

    STEP-BY-STEP:
        1. Preprocess JD text (NLP cleaning)
        2. For each resume:
           a. Preprocess resume text
           b. Extract and compare skills
           c. Calculate match score
        3. Rank all candidates
        4. Generate report

    PARAMETERS:
        resumes (list): List of {'name': ..., 'text': ...} dicts
        jd_text (str): Full job description text
        jd_role (str): Name of the role (for display)

    RETURNS:
        tuple: (ranked_candidates, full_report_string)
    """

    print(f"\n{'='*60}")
    print(f"   SCREENING {len(resumes)} CANDIDATES FOR: {jd_role.upper()}")
    print(f"{'='*60}\n")

    # STEP 1: Preprocess the Job Description
    # This converts the JD to clean, stemmed tokens as a string
    print("[STEP 1] Preprocessing Job Description...")
    processed_jd = preprocess_to_string(jd_text)
    print(f"         JD processed. Words extracted: {len(processed_jd.split())}")

    # List to collect all candidate data
    candidates_data = []

    # STEP 2: Process each resume
    for i, resume in enumerate(resumes, 1):
        name = resume['name']
        text = resume['text']

        print(f"\n[STEP 2.{i}] Processing Resume: {name}")
        print(f"            Resume length: {len(text)} characters")

        # A: Preprocess resume text (same cleaning as JD)
        processed_resume = preprocess_to_string(text)

        # B: Extract skills and calculate skill match
        print(f"            Extracting skills...")
        skill_analysis = get_skill_analysis(text, jd_text)

        # C: Calculate TF-IDF similarity + final score
        print(f"            Calculating match score...")
        match_result = match_resume_to_jd(processed_resume, processed_jd,
                                           skill_analysis['skill_score'])

        # D: Combine everything into one candidate record
        candidate_record = {
            'name': name,
            'tfidf_score': match_result['tfidf_score'],
            'tfidf_percent': match_result['tfidf_percent'],
            'skill_score': match_result['skill_score'],
            'final_score': match_result['final_score'],
            'interpretation': match_result['interpretation'],
            'matching_skills': skill_analysis['matching_skills'],
            'missing_skills': skill_analysis['missing_skills'],
            'resume_skills': skill_analysis['resume_skills'],
            'jd_skills': skill_analysis['jd_skills']
        }

        candidates_data.append(candidate_record)

        # Quick preview for each candidate
        print(f"            ✅ Score: {match_result['final_score']:.2f}% | {match_result['interpretation']}")

    # STEP 3: Rank all candidates
    print(f"\n[STEP 3] Ranking {len(candidates_data)} candidates...")
    ranked_candidates = rank_candidates(candidates_data)

    # STEP 4: Generate full report
    print("[STEP 4] Generating report...\n")
    full_report = generate_full_report(ranked_candidates, jd_role)

    return ranked_candidates, full_report


def main():
    """
    ENTRY POINT: Main function that runs when you execute: python main.py

    Provides a simple menu to:
    1. Run demo with built-in sample data
    2. Specify a job role from available options
    3. Enter a custom job description
    """

    # Print welcome banner
    print("\n" + "=" * 60)
    print("   🤖 AI-BASED SMART RESUME SCREENING SYSTEM")
    print("   Built with Python | NLP | TF-IDF | Cosine Similarity")
    print("=" * 60)

    # Show available roles
    available_roles = list_available_roles()
    print("\n📋 Available Job Roles:")
    for idx, role in enumerate(available_roles, 1):
        print(f"   {idx}. {role.replace('_', ' ').title()}")

    print("\n" + "-" * 60)
    print("Select a mode:")
    print("  [1] Demo Mode (use built-in sample resumes + select role)")
    print("  [2] Custom JD Mode (paste your own job description)")
    print("-" * 60)

    # Get user choice
    try:
        mode = input("\nEnter choice (1 or 2): ").strip()
    except (EOFError, KeyboardInterrupt):
        mode = "1"  # Default to demo mode if running non-interactively

    if mode == "1" or mode == "":
        # ---- DEMO MODE ----
        print("\n📌 DEMO MODE: Using built-in sample resumes")

        # Ask which role to screen for
        print("\nEnter role to screen for (e.g., data_scientist, software_engineer):")
        print(f"Options: {', '.join(available_roles)}")
        try:
            role_input = input("Role: ").strip()
        except (EOFError, KeyboardInterrupt):
            role_input = "data_scientist"

        if not role_input:
            role_input = "data_scientist"

        # Fetch the job description
        jd_text = get_job_description(role_input)
        if not jd_text:
            print("Invalid role. Using 'data_scientist' as default.")
            role_input = "data_scientist"
            jd_text = get_job_description(role_input)

        # Run the screening pipeline
        ranked_candidates, full_report = run_screening(
            SAMPLE_RESUMES,
            jd_text,
            role_input.replace("_", " ").title()
        )

    elif mode == "2":
        # ---- CUSTOM JD MODE ----
        print("\n📌 CUSTOM JD MODE")
        print("Paste your job description below.")
        print("Press ENTER twice when done:\n")
        jd_lines = []
        try:
            while True:
                line = input()
                if line == "":
                    if jd_lines and jd_lines[-1] == "":
                        break
                jd_lines.append(line)
        except EOFError:
            pass

        jd_text = "\n".join(jd_lines)

        if not jd_text.strip():
            print("No JD entered. Using default Data Scientist JD.")
            jd_text = get_job_description("data_scientist")
            role_input = "data_scientist"
        else:
            role_input = "custom_role"

        # Run screening
        ranked_candidates, full_report = run_screening(
            SAMPLE_RESUMES,
            jd_text,
            "Custom Role"
        )

    else:
        print("Invalid choice. Running demo mode.")
        jd_text = get_job_description("data_scientist")
        ranked_candidates, full_report = run_screening(
            SAMPLE_RESUMES, jd_text, "Data Scientist"
        )

    # ---- DISPLAY RESULTS ----
    print(full_report)

    # ---- SAVE REPORT ----
    save_path = "outputs/screening_report.txt"
    import os
    os.makedirs("outputs", exist_ok=True)
    save_report(full_report, save_path)

    print(f"\n✅ Screening complete! Report saved to: {save_path}")
    print("   You can open this file to view the full results.\n")


# This is Python's way of saying: "Only run main() if this file is run directly"
# When imported by another file (like streamlit_app.py), main() won't auto-run
if __name__ == "__main__":
    main()
```

## `manage.py`

```python
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resume_system.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django is not installed.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

## `matching_algorithm.py`

```python
"""
matching_algorithm.py
=====================
PURPOSE: Calculate how similar a resume is to a job description using TF-IDF + Cosine Similarity.

HOW IT WORKS:
1. TF-IDF converts text into numbers (a mathematical vector/array)
   - TF  = Term Frequency    → How often a word appears in THIS document
   - IDF = Inverse Document  → How rare/important the word is across all documents
   - TF-IDF = TF × IDF       → Words that appear often HERE but rarely elsewhere get HIGH score

2. Cosine Similarity measures the "angle" between two vectors
   - Score = 1.0  → Documents are identical
   - Score = 0.0  → Documents have nothing in common
   - Score = 0.7  → Documents are 70% similar

REAL WORLD ANALOGY:
Imagine two arrows pointing in directions. Cosine Similarity measures how closely
they point in the same direction. If resume and JD arrows point the same way,
they're highly similar (good candidate match).

EXAMPLE:
JD: "We need Python Machine Learning expert"
Resume: "I have 3 years Python Machine Learning experience"
→ High similarity because both talk about same topics!
"""

# --- IMPORTS ---
from sklearn.feature_extraction.text import TfidfVectorizer  # Converts text to TF-IDF vectors
from sklearn.metrics.pairwise import cosine_similarity        # Measures similarity between vectors
import numpy as np                                            # Numerical operations


def calculate_tfidf_cosine_similarity(text1, text2):
    """
    Calculates TF-IDF based Cosine Similarity between two texts.

    This is the CORE matching algorithm of our system.

    PARAMETERS:
        text1 (str): First preprocessed text (e.g., resume)
        text2 (str): Second preprocessed text (e.g., job description)

    RETURNS:
        float: Similarity score between 0.0 and 1.0
               (multiply by 100 to get percentage)

    STEP-BY-STEP:
        1. Put both texts in a list (TfidfVectorizer needs a collection)
        2. Create TF-IDF matrix: each row = a document, each column = a word
        3. Row 0 = resume vector, Row 1 = JD vector
        4. Calculate cosine similarity between the two rows
        5. Return the similarity score
    """

    # STEP 1: Create the corpus (collection of documents)
    # TfidfVectorizer needs a list of texts to process together
    corpus = [text1, text2]

    # STEP 2: Create TF-IDF Vectorizer
    # ngram_range=(1,2): consider single words AND two-word phrases
    #   - "machine" alone gets a score
    #   - "machine learning" as a phrase also gets its own score
    # min_df=1: include word even if it appears in just 1 document
    # max_features=5000: limit to 5000 most important words (for speed)
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),     # Use unigrams and bigrams
        min_df=1,               # Include rare words too
        max_features=5000       # Max vocabulary size
    )

    # STEP 3: Fit and transform the corpus
    # fit_transform(): learns vocabulary AND converts text to numbers
    # Result is a matrix: shape = (2 documents, N unique words)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # STEP 4: Calculate cosine similarity
    # tfidf_matrix[0]: vector for text1 (resume)
    # tfidf_matrix[1]: vector for text2 (JD)
    # cosine_similarity() returns a matrix — we get [0][0] for the score
    similarity_matrix = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

    # STEP 5: Extract the single similarity score
    # similarity_matrix is [[score]] so we take [0][0]
    similarity_score = similarity_matrix[0][0]

    # Round to 4 decimal places for precision
    return round(float(similarity_score), 4)


def calculate_weighted_score(tfidf_score, skill_score, tfidf_weight=0.5, skill_weight=0.5):
    """
    Combines TF-IDF score and Skill Match score into one final score.

    WHY COMBINE?
    - TF-IDF is good at measuring overall text similarity
    - Skill matching is good at finding specific required skills
    - Together they give a more accurate and fair score

    PARAMETERS:
        tfidf_score (float): TF-IDF cosine similarity (0 to 1)
        skill_score (float): Skill match percentage (0 to 100)
        tfidf_weight (float): Weight for TF-IDF score (default 0.5 = 50%)
        skill_weight (float): Weight for skill score (default 0.5 = 50%)

    RETURNS:
        float: Final combined score as percentage (0 to 100)

    FORMULA:
        Final = (tfidf_score × 100 × tfidf_weight) + (skill_score × skill_weight)
    """

    # Convert tfidf_score from 0-1 scale to 0-100 scale
    tfidf_percent = tfidf_score * 100  # e.g., 0.72 → 72%

    # Weighted combination
    # Example: tfidf=72%, skill=60%, both at 50% weight
    # Final = (72 × 0.5) + (60 × 0.5) = 36 + 30 = 66%
    final_score = (tfidf_percent * tfidf_weight) + (skill_score * skill_weight)

    # Ensure score doesn't exceed 100
    final_score = min(final_score, 100.0)

    # Round to 2 decimal places
    return round(final_score, 2)


def match_resume_to_jd(preprocessed_resume, preprocessed_jd, skill_score):
    """
    MAIN MATCHING FUNCTION: Combines all matching approaches.

    Takes preprocessed texts and skill score, returns comprehensive results.

    PARAMETERS:
        preprocessed_resume (str): Cleaned resume text (from nlp_processing.py)
        preprocessed_jd (str): Cleaned JD text (from nlp_processing.py)
        skill_score (float): Skill match percentage from skill_matching.py

    RETURNS:
        dict: {
            'tfidf_score': Raw TF-IDF similarity (0-1),
            'tfidf_percent': TF-IDF as percentage,
            'skill_score': Skill match percentage,
            'final_score': Combined weighted score,
            'interpretation': Text description of the match level
        }
    """

    # Calculate TF-IDF cosine similarity
    tfidf_score = calculate_tfidf_cosine_similarity(preprocessed_resume, preprocessed_jd)

    # Convert to percentage
    tfidf_percent = round(tfidf_score * 100, 2)

    # Calculate final weighted score
    final_score = calculate_weighted_score(tfidf_score, skill_score)

    # Interpret the final score with human-readable description
    interpretation = interpret_score(final_score)

    return {
        'tfidf_score': tfidf_score,
        'tfidf_percent': tfidf_percent,
        'skill_score': skill_score,
        'final_score': final_score,
        'interpretation': interpretation
    }


def interpret_score(score):
    """
    Converts a numeric score into a human-readable match level.

    PARAMETERS:
        score (float): Final match score (0 to 100)

    RETURNS:
        str: Text description of the match level
    """

    if score >= 80:
        return "🌟 Excellent Match — Highly Recommended"
    elif score >= 65:
        return "✅ Good Match — Recommended for Interview"
    elif score >= 50:
        return "🟡 Moderate Match — Consider for Interview"
    elif score >= 35:
        return "🟠 Weak Match — Needs Review"
    else:
        return "❌ Poor Match — Not Recommended"


# ---- TEST / DEMO ----
if __name__ == "__main__":
    print("=== Matching Algorithm Test ===\n")

    # Sample preprocessed texts (already cleaned/stemmed)
    resume_processed = "python machin learn tensor flow panda sql data analyt git communic"
    jd_processed = "python machin learn deep learn tensor flow pytorch sql data scienc communic teamwork"

    skill_score = 65.0  # Simulating 65% skill match

    result = match_resume_to_jd(resume_processed, jd_processed, skill_score)

    print("TF-IDF Raw Score:", result['tfidf_score'])
    print("TF-IDF Percentage:", result['tfidf_percent'], "%")
    print("Skill Score:", result['skill_score'], "%")
    print("FINAL SCORE:", result['final_score'], "%")
    print("Interpretation:", result['interpretation'])
```

## `nlp_processing.py`

```python
"""
nlp_processing.py
=================
PURPOSE: Clean and preprocess text using Natural Language Processing (NLP) techniques.

HOW IT WORKS:
1. Convert text to lowercase
2. Remove punctuation and special characters
3. Tokenize (split into individual words)
4. Remove stopwords (common words like "the", "is", "and" that don't add meaning)
5. Apply stemming (reduce words to base form using Porter Stemmer algorithm)

REAL WORLD ANALOGY:
Think of this as a "text cleaner". Before comparing two documents,
we remove all the noise (punctuation, filler words) so we compare
only the meaningful words. Like cleaning vegetables before cooking.

EXAMPLE:
Input:  "The candidate has experience in Python programming and Machine Learning."
Output: ['candidat', 'experi', 'python', 'program', 'machin', 'learn']

NOTE: This version works with built-in Python + scikit-learn (no NLTK required).
      Optionally uses NLTK if installed for enhanced processing.
"""

# --- IMPORTS ---
import re           # Regular Expressions - for pattern matching in text
import string       # Provides list of punctuation characters

# Try to import NLTK (optional, for enhanced NLP)
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords as nltk_stopwords
    from nltk.stem import PorterStemmer

    for resource, path in [('punkt', 'tokenizers/punkt'),
                            ('punkt_tab', 'tokenizers/punkt_tab'),
                            ('stopwords', 'corpora/stopwords')]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource, quiet=True)

    NLTK_AVAILABLE = True
    _stemmer = PorterStemmer()
    _stop_words_base = set(nltk_stopwords.words('english'))

except ImportError:
    NLTK_AVAILABLE = False


# ============================================================
# BUILT-IN PORTER STEMMER (No external dependency version)
# ============================================================

class SimplePorterStemmer:
    """
    A lightweight stemmer that handles common English word endings.
    Reduces words to approximate root form without needing NLTK.

    EXAMPLE:
        stem("programming") -> "program"
        stem("learning")    -> "learn"
        stem("databases")   -> "databas"
    """

    def stem(self, word):
        """Reduce word to its approximate root form."""
        if len(word) <= 3:
            return word  # Very short words: don't stem them

        # List of (suffix_to_remove, replacement) pairs
        # Ordered from most specific to most general
        suffixes = [
            ('ational', 'ate'), ('tional', 'tion'), ('enci', 'ence'),
            ('anci', 'ance'), ('izer', 'ize'), ('ization', 'ize'),
            ('isation', 'ise'), ('ising', 'ise'), ('izing', 'ize'),
            ('nesses', ''), ('fulness', 'ful'), ('ousness', 'ous'),
            ('iveness', 'ive'), ('ations', 'ate'), ('ation', 'ate'),
            ('alism', 'al'), ('ments', ''), ('ment', ''),
            ('ness', ''), ('ings', ''), ('ing', ''),
            ('tions', ''), ('tion', ''), ('sion', ''),
            ('edly', ''), ('ingly', ''), ('lly', 'l'),
            ('ally', 'al'), ('ful', ''), ('less', ''),
            ('ous', ''), ('ive', ''), ('al', ''),
            ('ers', ''), ('ied', 'y'), ('ies', 'y'),
            ('ses', 's'), ('ed', ''), ('er', ''),
            ('ly', ''), ('ry', ''), ('es', ''), ('s', '')
        ]

        for suffix, replacement in suffixes:
            # Only apply if: word ends with suffix AND remaining stem >= 3 chars
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                return word[:-len(suffix)] + replacement

        return word  # No suffix matched — return original word


# ============================================================
# STOPWORDS (Built-in English stopwords list)
# ============================================================

BUILT_IN_STOPWORDS = {
    # Articles
    'a', 'an', 'the', 'this', 'that', 'these', 'those',
    # Pronouns
    'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his',
    'she', 'her', 'it', 'its', 'they', 'them', 'their', 'who', 'whom',
    # Prepositions
    'at', 'by', 'for', 'in', 'of', 'on', 'to', 'up', 'as', 'from',
    'with', 'into', 'through', 'about', 'between', 'during', 'before',
    'after', 'above', 'below', 'over', 'under', 'per', 'via',
    # Conjunctions
    'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
    'neither', 'not', 'only', 'than', 'if', 'then', 'when',
    'where', 'while', 'how', 'although', 'though', 'because',
    # Common verbs
    'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'must', 'can',
    # Other filler words
    'also', 'just', 'more', 'most', 'other', 'some', 'such',
    'no', 'all', 'each', 'every', 'any', 'many', 'very',
    'however', 'therefore', 'thus', 'hence', 'including',
    'without', 'across', 'within', 'us', 'eg', 'ie',
    # Resume/JD specific filler words
    'experience', 'year', 'years', 'work', 'working', 'company',
    'role', 'position', 'responsibilities', 'job', 'candidate',
    'required', 'requirement', 'skill', 'skills', 'ability',
    'knowledge', 'understand', 'understanding', 'using', 'use',
    'good', 'strong', 'excellent', 'etc', 'please', 'well',
    'new', 'high', 'like', 'include', 'includes', 'including'
}

# Use NLTK stopwords if available (more comprehensive), else use built-in
if NLTK_AVAILABLE:
    STOP_WORDS = _stop_words_base.union(BUILT_IN_STOPWORDS)
    stemmer = _stemmer
else:
    STOP_WORDS = BUILT_IN_STOPWORDS
    stemmer = SimplePorterStemmer()


# ============================================================
# MAIN PREPROCESSING FUNCTIONS
# ============================================================

def clean_text(text):
    """
    STEP 1 & 2: Clean the text.

    REMOVES: URLs, emails, phone numbers, punctuation, extra spaces.
    CONVERTS: All text to lowercase.

    PARAMETER:
        text (str): Raw input text

    RETURNS:
        str: Cleaned text
    """

    # Convert to lowercase so "Python" == "python"
    text = text.lower()

    # Remove URLs (http://..., www....)
    # \S+ means "one or more non-whitespace characters"
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remove email addresses (word@word.word pattern)
    text = re.sub(r'\S+@\S+', '', text)

    # Remove phone numbers (various formats like +1-234-567-8901)
    text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', '', text)

    # Remove all punctuation characters
    # string.punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Replace multiple spaces with single space
    # \s+ matches one or more whitespace characters (spaces, tabs, newlines)
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def tokenize(text):
    """
    STEP 3: Split text into individual words.

    EXAMPLE:
        "python data science" → ["python", "data", "science"]

    PARAMETER:
        text (str): Cleaned text

    RETURNS:
        list: List of individual word strings
    """
    if NLTK_AVAILABLE:
        # NLTK's word_tokenize handles contractions etc. more intelligently
        tokens = word_tokenize(text)
    else:
        # Python's built-in split() — works well enough for our purpose
        tokens = text.split()

    # Keep ONLY pure alphabetic tokens (no numbers like "2024", no symbols)
    # token.isalpha() returns True only if ALL characters are letters
    tokens = [token for token in tokens if token.isalpha()]

    return tokens


def remove_stopwords(tokens):
    """
    STEP 4: Remove common filler words.

    EXAMPLE:
        ["the", "candidate", "has", "python", "skills"] → ["candidate", "python"]

    PARAMETER:
        tokens (list): List of word strings

    RETURNS:
        list: Filtered list without stopwords
    """
    # List comprehension: keep word ONLY IF it's not in stopwords AND length > 2
    filtered = [word for word in tokens
                if word not in STOP_WORDS and len(word) > 2]
    return filtered


def apply_stemming(tokens):
    """
    STEP 5: Reduce words to their root/base form.

    EXAMPLE:
        ["programming", "learning", "databases"] → ["program", "learn", "databas"]

    WHY STEM?
    So "programmer" and "programming" both match when searching for "program".

    PARAMETER:
        tokens (list): List of word strings

    RETURNS:
        list: List of stemmed words
    """
    # Apply stemmer to each word using a list comprehension
    stemmed = [stemmer.stem(word) for word in tokens]
    return stemmed


def preprocess(text, use_stemming=True):
    """
    MAIN FUNCTION: Run the complete 4-step preprocessing pipeline.

    Pipeline: Raw Text → Clean → Tokenize → Remove Stopwords → Stem

    PARAMETERS:
        text (str): Raw input text (resume or job description)
        use_stemming (bool): Whether to apply stemming (default: True)

    RETURNS:
        list: Fully processed list of word tokens
    """
    # STEP 1+2: Clean the text
    cleaned = clean_text(text)

    # STEP 3: Split into words
    tokens = tokenize(cleaned)

    # STEP 4: Remove stopwords
    filtered = remove_stopwords(tokens)

    # STEP 5: Apply stemming (if enabled)
    if use_stemming:
        result = apply_stemming(filtered)
    else:
        result = filtered

    return result


def preprocess_to_string(text, use_stemming=True):
    """
    Same as preprocess() but returns result as a STRING (not list).

    WHY: TF-IDF Vectorizer needs a string, not a list.

    EXAMPLE:
        Input:  "Python programming and Machine Learning"
        Output: "python program machin learn"

    RETURNS:
        str: Space-joined string of processed tokens
    """
    tokens = preprocess(text, use_stemming)
    # " ".join() connects list items with spaces
    # ["python", "program", "learn"] → "python program learn"
    return " ".join(tokens)


# ---- TEST / DEMO ----
if __name__ == "__main__":
    print("=== NLP Processing Test ===")
    print(f"Using NLTK: {NLTK_AVAILABLE}\n")

    sample_text = """
    The candidate has 3 years of experience in Python programming, Machine Learning,
    and Data Analysis. They have worked with TensorFlow, Scikit-learn, and Pandas.
    """

    print("Original Text:", sample_text.strip())
    print("\nAfter Cleaning:")
    print(clean_text(sample_text))

    print("\nAfter Tokenizing:")
    print(tokenize(clean_text(sample_text)))

    print("\nAfter Removing Stopwords:")
    tokens = tokenize(clean_text(sample_text))
    print(remove_stopwords(tokens))

    print("\nFinal Output (with stemming):")
    print(preprocess(sample_text))

    print("\nAs String (for TF-IDF):")
    print(preprocess_to_string(sample_text))
```

## `resume_parser.py`

```python
"""
resume_parser.py
================
PURPOSE: Extract raw text from resume files (PDF and DOCX formats).

HOW IT WORKS:
- Reads PDF resumes using PyPDF2
- Reads DOCX resumes using python-docx
- Returns plain text for further processing

REAL WORLD ANALOGY:
Think of this as a "scanner" that reads physical resumes and converts
them into plain text so the computer can understand them.
"""

# --- IMPORTS ---
import os                      # os: used to check if file exists and get file extension
# Try PyPDF2 first; fall back to pypdf (newer package name)
try:
    import PyPDF2 as _pdf_lib   # PyPDF2: library to read PDF files
    _PDF_LIB = "PyPDF2"
except ImportError:
    import pypdf as _pdf_lib    # pypdf: the updated successor to PyPDF2
    _PDF_LIB = "pypdf"
from docx import Document      # docx: library to read Word (.docx) files


def extract_text_from_pdf(pdf_path):
    """
    Reads a PDF file and returns all text from it.

    PARAMETER:
        pdf_path (str): Full path to the PDF file on your computer

    RETURNS:
        str: All text content found in the PDF
    """
    text = ""  # Start with empty string; we'll add text to this

    try:
        # Open the PDF file in binary read mode ("rb")
        # "rb" = read binary — needed for non-text files like PDFs
        with open(pdf_path, "rb") as pdf_file:

            # Create a PDF reader object — like "opening" the file
            # Uses whichever PDF library was successfully imported
            pdf_reader = _pdf_lib.PdfReader(pdf_file)

            # Loop through every page in the PDF
            # len(pdf_reader.pages) gives us total number of pages
            for page_number in range(len(pdf_reader.pages)):

                # Get the specific page object
                page = pdf_reader.pages[page_number]

                # Extract text from this page and add to our full text
                # The "\n" adds a new line between pages
                text += page.extract_text() + "\n"

    except Exception as e:
        # If something goes wrong (file not found, corrupted PDF, etc.)
        # Print the error and return empty string instead of crashing
        print(f"[ERROR] Could not read PDF: {pdf_path} | Reason: {e}")
        return ""

    return text  # Return all the text we collected


def extract_text_from_docx(docx_path):
    """
    Reads a Word (.docx) file and returns all text from it.

    PARAMETER:
        docx_path (str): Full path to the DOCX file

    RETURNS:
        str: All text content found in the DOCX file
    """
    text = ""  # Start with empty string

    try:
        # Open the DOCX file using python-docx's Document class
        doc = Document(docx_path)

        # A DOCX file contains "paragraphs" — each line/block of text
        # Loop through all paragraphs in the document
        for paragraph in doc.paragraphs:

            # paragraph.text gives us the text of one paragraph
            # Strip() removes extra spaces at start and end
            # "\n" adds a newline after each paragraph
            text += paragraph.text.strip() + "\n"

    except Exception as e:
        print(f"[ERROR] Could not read DOCX: {docx_path} | Reason: {e}")
        return ""

    return text  # Return all collected text


def parse_resume(file_path):
    """
    MAIN FUNCTION: Automatically detects file type and extracts text.

    This is the function you call from other files.
    It figures out if the file is PDF or DOCX and calls the right function.

    PARAMETER:
        file_path (str): Path to the resume file (PDF or DOCX)

    RETURNS:
        str: Extracted text from the resume
    """

    # First, check if the file actually exists on the computer
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return ""

    # Get the file extension (e.g., ".pdf" or ".docx")
    # os.path.splitext splits "resume.pdf" into ("resume", ".pdf")
    # [1] gets the second part (the extension)
    # .lower() converts to lowercase so ".PDF" == ".pdf"
    file_extension = os.path.splitext(file_path)[1].lower()

    # Check which type of file it is and call the right parser
    if file_extension == ".pdf":
        print(f"[INFO] Parsing PDF resume: {file_path}")
        return extract_text_from_pdf(file_path)

    elif file_extension == ".docx":
        print(f"[INFO] Parsing DOCX resume: {file_path}")
        return extract_text_from_docx(file_path)

    else:
        # File type not supported
        print(f"[ERROR] Unsupported file type: {file_extension}. Use PDF or DOCX.")
        return ""


def parse_resume_from_text(text):
    """
    If resume is already plain text (for testing/demo), just clean and return it.

    PARAMETER:
        text (str): Raw resume text

    RETURNS:
        str: Cleaned resume text
    """
    # Strip leading/trailing whitespace and return
    return text.strip()


# ---- TEST / DEMO ----
# This block only runs when you run THIS file directly (python resume_parser.py)
# It does NOT run when imported by another file
if __name__ == "__main__":
    print("=== Resume Parser Test ===")
    sample_text = """
    John Doe
    Email: john@example.com
    Skills: Python, Machine Learning, Data Analysis
    Experience: 3 years at XYZ Corp
    """
    result = parse_resume_from_text(sample_text)
    print("Parsed Text:\n", result)
```

## `skill_matching.py`

```python
"""
skill_matching.py
=================
PURPOSE: Extract specific skills from text and compare them with job requirements.

HOW IT WORKS:
- We maintain a master list of known technical and soft skills
- We scan resume/JD text and find which skills are mentioned
- We then compare: which skills match, which are missing

REAL WORLD ANALOGY:
Think of this as a "checklist" system.
The HR has a checklist of required skills.
We scan the resume and tick off which skills are found.
At the end, we see: ✅ matched skills and ❌ missing skills.
"""

# --- IMPORTS ---
import re  # For text pattern matching


# ============================================================
# MASTER SKILLS DATABASE
# ============================================================
# This is a comprehensive list of skills organized by category.
# We use sets for fast lookup (checking if a skill exists is O(1)).

TECHNICAL_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "c", "c++", "c#", "r", "scala",
    "kotlin", "swift", "ruby", "php", "golang", "rust", "matlab",
    "perl", "bash", "shell", "typescript",

    # Data Science / ML / AI
    "machine learning", "deep learning", "neural networks",
    "natural language processing", "nlp", "computer vision",
    "reinforcement learning", "data science", "data analysis",
    "data visualization", "statistical analysis", "statistics",
    "predictive modeling", "feature engineering",

    # ML Libraries / Frameworks
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "catboost", "opencv", "nltk", "spacy",
    "hugging face", "transformers", "fastai",

    # Data Tools
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "scipy", "jupyter", "anaconda",

    # Databases
    "sql", "mysql", "postgresql", "sqlite", "oracle", "mongodb",
    "cassandra", "redis", "elasticsearch", "firebase", "dynamodb",

    # Cloud Platforms
    "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean",

    # Web Development
    "html", "css", "react", "angular", "vue", "node.js", "nodejs",
    "django", "flask", "fastapi", "spring", "spring boot",
    "rest api", "graphql", "bootstrap", "tailwind", "jquery",
    "next.js", "express", "webpack",

    # DevOps / Tools
    "docker", "kubernetes", "git", "github", "gitlab", "ci/cd",
    "jenkins", "ansible", "terraform", "linux", "unix",

    # Business Intelligence / Analytics
    "tableau", "power bi", "excel", "google analytics",
    "looker", "qlik", "business intelligence",

    # Other Tech
    "blockchain", "cybersecurity", "networking", "api",
    "microservices", "agile", "scrum", "jira", "figma"
}

SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "time management", "creativity", "adaptability",
    "negotiation", "presentation", "collaboration", "interpersonal",
    "analytical", "attention to detail", "decision making",
    "project management", "customer service", "emotional intelligence"
}

# Combine both into one master set for searching
ALL_SKILLS = TECHNICAL_SKILLS.union(SOFT_SKILLS)


def extract_skills(text):
    """
    Scans text and finds all recognized skills from our master list.

    HOW IT WORKS:
    - Convert text to lowercase for case-insensitive matching
    - For each skill in our database, check if it appears in the text
    - Return all found skills as a set

    PARAMETER:
        text (str): Resume or job description text

    RETURNS:
        set: Set of skill strings found in the text
    """

    # Convert text to lowercase for case-insensitive comparison
    text_lower = text.lower()

    # Set to store found skills (sets automatically prevent duplicates)
    found_skills = set()

    # Check each skill in our master skills database
    for skill in ALL_SKILLS:

        # Use regex word boundary \b to match whole words only
        # Example: "sql" should NOT match inside "mysql" when searching for "sql" standalone
        # But here we use simple "in" for multi-word skills like "machine learning"

        # For multi-word skills (e.g., "machine learning"), check directly
        # For single-word skills, use word boundary to avoid partial matches
        if " " in skill:
            # Multi-word skill: check if the phrase appears in text
            if skill in text_lower:
                found_skills.add(skill)
        else:
            # Single-word skill: use word boundary to find exact match
            # \b means "word boundary" — matches at start/end of a word
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)

    return found_skills


def get_matching_skills(resume_text, jd_text):
    """
    Finds skills that appear in BOTH the resume AND the job description.

    These are the skills the candidate HAS that the job REQUIRES.
    This is what earns the candidate a higher score.

    PARAMETERS:
        resume_text (str): Text extracted from the resume
        jd_text (str): Text of the job description

    RETURNS:
        set: Skills present in both resume and JD
    """

    # Extract skills from each document
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    # Set intersection: elements common to BOTH sets
    # Example: {python, java, sql} ∩ {python, sql, react} = {python, sql}
    matching = resume_skills.intersection(jd_skills)

    return matching


def get_missing_skills(resume_text, jd_text):
    """
    Finds skills that the JD REQUIRES but the resume DOESN'T HAVE.

    These are skills the candidate is missing — areas for improvement.

    PARAMETERS:
        resume_text (str): Text extracted from the resume
        jd_text (str): Text of the job description

    RETURNS:
        set: Skills in JD but not in resume
    """

    # Extract skills from each document
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    # Set difference: elements in jd_skills but NOT in resume_skills
    # Example: {python, sql, react} - {python, java, sql} = {react}
    missing = jd_skills.difference(resume_skills)

    return missing


def calculate_skill_match_score(resume_text, jd_text):
    """
    Calculates what percentage of required skills the candidate has.

    FORMULA:
        Score = (Matching Skills / Total JD Skills) × 100

    EXAMPLE:
        JD requires 10 skills, candidate has 7 → Score = 70%

    PARAMETERS:
        resume_text (str): Resume text
        jd_text (str): Job description text

    RETURNS:
        float: Skill match percentage (0 to 100)
    """

    jd_skills = extract_skills(jd_text)
    matching_skills = get_matching_skills(resume_text, jd_text)

    # Avoid division by zero if JD has no recognized skills
    if len(jd_skills) == 0:
        return 0.0

    # Calculate percentage
    score = (len(matching_skills) / len(jd_skills)) * 100

    # Round to 2 decimal places for clean display
    return round(score, 2)


def get_skill_analysis(resume_text, jd_text):
    """
    MAIN FUNCTION: Returns a complete skill analysis report.

    Combines all skill-related info into one dictionary.

    RETURNS:
        dict: {
            'resume_skills': set of all skills found in resume,
            'jd_skills': set of all skills required by JD,
            'matching_skills': set of skills present in both,
            'missing_skills': set of skills in JD but not resume,
            'skill_score': percentage match score
        }
    """

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    matching = resume_skills.intersection(jd_skills)
    missing = jd_skills.difference(resume_skills)
    score = calculate_skill_match_score(resume_text, jd_text)

    return {
        'resume_skills': resume_skills,
        'jd_skills': jd_skills,
        'matching_skills': matching,
        'missing_skills': missing,
        'skill_score': score
    }


# ---- TEST / DEMO ----
if __name__ == "__main__":
    print("=== Skill Matching Test ===\n")

    sample_resume = """
    John Doe — Data Scientist
    Skills: Python, Machine Learning, TensorFlow, Pandas, NumPy,
    SQL, Data Visualization, Matplotlib, Git, Communication, Leadership.
    """

    sample_jd = """
    Required: Python, Machine Learning, Deep Learning, TensorFlow, PyTorch,
    SQL, Data Analysis, Pandas, Scikit-learn, Communication, Teamwork.
    """

    analysis = get_skill_analysis(sample_resume, sample_jd)

    print("Resume Skills Found:", sorted(analysis['resume_skills']))
    print("\nJD Skills Required:", sorted(analysis['jd_skills']))
    print("\n✅ Matching Skills:", sorted(analysis['matching_skills']))
    print("\n❌ Missing Skills:", sorted(analysis['missing_skills']))
    print(f"\n📊 Skill Match Score: {analysis['skill_score']}%")
```

## `streamit_app.py`

```python
"""
streamlit_app.py
================
PURPOSE: Web-based User Interface (UI) for the Resume Screening System.

WHAT IS STREAMLIT?
Streamlit is a Python library that lets you build web apps with just Python code.
No HTML, CSS, or JavaScript needed!

HOW TO RUN:
    streamlit run streamlit_app.py
    (Then open your browser at http://localhost:8501)

FEATURES:
- Upload multiple PDF/DOCX resumes
- Select or enter job description
- See visual results with charts
- Download screening report
"""

# --- IMPORTS ---
import streamlit as st          # Main Streamlit library for web UI
import pandas as pd             # For creating data tables
import plotly.express as px     # For interactive charts/graphs
import os                       # For file operations
import tempfile                 # For handling uploaded files temporarily

# Import our project modules
from resume_parser import parse_resume, parse_resume_from_text
from job_description import get_job_description, list_available_roles, JOB_DESCRIPTIONS
from nlp_processing import preprocess_to_string
from skill_matching import get_skill_analysis
from matching_algorithm import match_resume_to_jd
from candidate_ranking import rank_candidates, generate_full_report


# ============================================================
# PAGE CONFIGURATION
# ============================================================
# Must be the FIRST Streamlit command in the script
st.set_page_config(
    page_title="AI Resume Screener",     # Browser tab title
    page_icon="🤖",                       # Browser tab icon
    layout="wide",                        # Use full page width
    initial_sidebar_state="expanded"      # Sidebar open by default
)


# ============================================================
# CUSTOM CSS STYLING
# ============================================================
# st.markdown with unsafe_allow_html=True lets us add custom CSS
st.markdown("""
    <style>
    /* Make the main title bigger and blue */
    .main-title {
        font-size: 2.5rem;
        color: #1F77B4;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Score card styling */
    .score-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }

    /* Custom metric styling */
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1F77B4;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def process_single_resume(name, resume_text, jd_text):
    """
    Processes one resume through the full pipeline.
    Returns a candidate dict with all scores and skill data.
    """
    # Preprocess both texts
    processed_resume = preprocess_to_string(resume_text)
    processed_jd = preprocess_to_string(jd_text)

    # Get skill analysis
    skill_analysis = get_skill_analysis(resume_text, jd_text)

    # Get match result
    match_result = match_resume_to_jd(
        processed_resume,
        processed_jd,
        skill_analysis['skill_score']
    )

    return {
        'name': name,
        'tfidf_score': match_result['tfidf_score'],
        'tfidf_percent': match_result['tfidf_percent'],
        'skill_score': match_result['skill_score'],
        'final_score': match_result['final_score'],
        'interpretation': match_result['interpretation'],
        'matching_skills': skill_analysis['matching_skills'],
        'missing_skills': skill_analysis['missing_skills'],
    }


def score_to_color(score):
    """Returns a color code based on the score value."""
    if score >= 80:
        return "#28a745"    # Green
    elif score >= 65:
        return "#17a2b8"    # Blue
    elif score >= 50:
        return "#ffc107"    # Yellow
    elif score >= 35:
        return "#fd7e14"    # Orange
    else:
        return "#dc3545"    # Red


# ============================================================
# SIDEBAR — INPUT SECTION
# ============================================================

# App title in sidebar
st.sidebar.markdown("# ⚙️ Configuration")
st.sidebar.markdown("---")

# Job Description Source Selection
st.sidebar.subheader("1️⃣ Select Job Role")
jd_source = st.sidebar.radio(
    "Job Description Source:",
    ["Select Pre-defined Role", "Enter Custom JD"],
    help="Choose from our built-in job roles or paste your own JD"
)

# Based on selection, show appropriate input
jd_text = ""
selected_role = ""

if jd_source == "Select Pre-defined Role":
    # Dropdown of available roles
    roles = list_available_roles()
    role_display = {r.replace('_', ' ').title(): r for r in roles}  # Pretty names

    selected_role_display = st.sidebar.selectbox(
        "Choose Role:",
        list(role_display.keys())
    )
    selected_role = role_display[selected_role_display]

    # Fetch and display the JD
    jd_text = get_job_description(selected_role)
    with st.sidebar.expander("📄 View Job Description"):
        st.text(jd_text[:500] + "..." if len(jd_text) > 500 else jd_text)

else:
    # Text area for custom JD
    jd_text = st.sidebar.text_area(
        "Paste Job Description:",
        height=200,
        placeholder="Enter the job description here..."
    )
    selected_role = "custom"

st.sidebar.markdown("---")

# Resume Input Method
st.sidebar.subheader("2️⃣ Add Resumes")
resume_source = st.sidebar.radio(
    "Resume Input Method:",
    ["Upload Files (PDF/DOCX)", "Use Built-in Demo Resumes"]
)

st.sidebar.markdown("---")

# Scoring weights configuration
st.sidebar.subheader("3️⃣ Scoring Weights")
tfidf_weight = st.sidebar.slider(
    "TF-IDF Similarity Weight",
    min_value=0.0, max_value=1.0, value=0.5, step=0.1,
    help="Weight given to overall text similarity"
)
skill_weight = round(1.0 - tfidf_weight, 1)  # Skill weight is complementary
st.sidebar.info(f"Skill Match Weight: {skill_weight}")

st.sidebar.markdown("---")
run_button = st.sidebar.button("🚀 Run Screening", type="primary", use_container_width=True)


# ============================================================
# MAIN PAGE CONTENT
# ============================================================

# Page title and description
st.markdown('<div class="main-title">🤖 AI-Based Smart Resume Screening System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automatically screen, rank, and analyze candidates using NLP & Machine Learning</div>', unsafe_allow_html=True)
st.markdown("---")

# Show tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Results", "📋 Detailed Analysis", "📖 How It Works"])

# How It Works tab — always visible
with tab3:
    st.subheader("How the System Works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Step 1: Text Extraction**
        - PDF parser reads resume
        - DOCX parser reads Word files
        - Raw text is extracted
        """)

    with col2:
        st.markdown("""
        **Step 2: NLP Processing**
        - Remove punctuation & stopwords
        - Tokenize into individual words
        - Apply stemming (root words)
        """)

    with col3:
        st.markdown("""
        **Step 3: Matching & Ranking**
        - TF-IDF converts text to vectors
        - Cosine Similarity measures match
        - Skills are extracted and compared
        - Candidates are ranked by score
        """)

    st.markdown("---")
    st.subheader("📐 Scoring Formula")
    st.latex(r"\text{Final Score} = (TF\text{-}IDF\_Score \times W_1) + (Skill\_Score \times W_2)")
    st.markdown("Where W1 + W2 = 1.0 (configurable in sidebar)")

    st.markdown("---")
    st.subheader("🎯 Score Interpretation")
    score_data = {
        "Score Range": ["80%+", "65-80%", "50-65%", "35-50%", "Below 35%"],
        "Interpretation": ["Excellent Match", "Good Match", "Moderate Match", "Weak Match", "Poor Match"],
        "Action": ["Shortlist Immediately", "Schedule Interview", "Review Manually", "Consider if shortage", "Not Recommended"],
        "Color": ["🟢", "🔵", "🟡", "🟠", "🔴"]
    }
    st.dataframe(pd.DataFrame(score_data), use_container_width=True, hide_index=True)


# ============================================================
# HANDLE RESUME INPUT
# ============================================================

# Demo resumes (same as in main.py)
DEMO_RESUMES = [
    {"name": "Alice Johnson", "text": """Alice Johnson | Email: alice@email.com
    Skills: Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, Scikit-learn,
    NLP, Natural Language Processing, Pandas, NumPy, SQL, Tableau, Power BI, AWS,
    Git, Docker, Data Visualization, Data Analysis, Matplotlib, Statistics,
    Communication, Leadership, Teamwork, Problem Solving.
    Experience: 4 years as Senior Data Scientist at TechCorp.
    Education: M.Tech Computer Science, IIT Delhi 2019.
    Certifications: AWS ML Specialty, TensorFlow Developer Certificate."""},

    {"name": "Bob Smith", "text": """Bob Smith | Email: bob@email.com
    Skills: Python (basic), SQL (basic), Excel, Pandas, Matplotlib, Git,
    Communication, Teamwork, Problem Solving.
    Projects: Student Grade Predictor using Scikit-learn. Movie Recommender System.
    Education: B.Tech Computer Science, Mumbai University 2024. CGPA: 7.8
    Certifications: Coursera Machine Learning, Python for Data Science."""},

    {"name": "Carol White", "text": """Carol White | Email: carol@email.com
    Skills: Python, SQL, R, Machine Learning, TensorFlow, Scikit-learn, XGBoost,
    NLP, Natural Language Processing, NLTK, SpaCy, Pandas, NumPy,
    Data Analysis, Data Visualization, Matplotlib, Seaborn, Tableau,
    AWS, GCP, Git, GitHub, Docker, Agile, Communication, Leadership.
    Experience: 2.5 years Data Scientist at Analytics Hub.
    Education: B.Sc Statistics, Delhi University 2021."""},

    {"name": "David Lee", "text": """David Lee | Email: david@email.com
    Skills: HTML, CSS, JavaScript, React, Node.js, Python (basic),
    MySQL, Excel, Git, Communication, Teamwork.
    Experience: 2 years Freelance Web Developer.
    Built 10+ websites using React, HTML, CSS.
    Education: B.Sc IT, Pune University 2022."""}
]

resumes_to_process = []

if resume_source == "Use Built-in Demo Resumes":
    resumes_to_process = DEMO_RESUMES
    st.info(f"📌 Using {len(DEMO_RESUMES)} built-in demo resumes: {', '.join([r['name'] for r in DEMO_RESUMES])}")

else:
    # File upload widget
    uploaded_files = st.file_uploader(
        "Upload Resume Files (PDF or DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Upload one or more resume files"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        for uploaded_file in uploaded_files:
            # Save to temp file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(uploaded_file.name)[1]
            ) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            # Parse the file
            text = parse_resume(tmp_path)
            os.unlink(tmp_path)  # Delete temp file after parsing

            if text:
                resumes_to_process.append({
                    "name": uploaded_file.name.replace(".pdf", "").replace(".docx", ""),
                    "text": text
                })
    else:
        st.info("👆 Upload resume files or switch to Demo mode in the sidebar.")


# ============================================================
# RUN SCREENING WHEN BUTTON CLICKED
# ============================================================

if run_button:

    # Validation checks
    if not jd_text or not jd_text.strip():
        st.error("❌ Please provide a job description first!")
        st.stop()

    if not resumes_to_process:
        st.error("❌ Please upload resumes or select Demo mode!")
        st.stop()

    # Show progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()  # Placeholder for status messages

    # Process all resumes
    candidates_data = []
    total = len(resumes_to_process)

    for i, resume in enumerate(resumes_to_process):
        status_text.text(f"Processing {resume['name']}... ({i+1}/{total})")
        progress_bar.progress((i + 1) / total)

        # Run through pipeline
        candidate = process_single_resume(resume['name'], resume['text'], jd_text)
        candidates_data.append(candidate)

    # Rank candidates
    ranked = rank_candidates(candidates_data)

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # Store results in session state (persists across reruns)
    st.session_state['ranked'] = ranked
    st.session_state['role'] = selected_role.replace('_', ' ').title()

    st.success(f"✅ Screening complete! {len(ranked)} candidates processed.")


# ============================================================
# DISPLAY RESULTS (if screening has been run)
# ============================================================

if 'ranked' in st.session_state:
    ranked = st.session_state['ranked']
    role_name = st.session_state.get('role', 'Job Role')

    with tab1:
        st.subheader(f"📊 Screening Results — {role_name}")

        # ---- TOP SUMMARY METRICS ----
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Candidates", len(ranked))
        with col2:
            shortlisted = len([c for c in ranked if c['final_score'] >= 65])
            st.metric("Shortlisted", shortlisted, f"{shortlisted/len(ranked)*100:.0f}%")
        with col3:
            avg_score = sum(c['final_score'] for c in ranked) / len(ranked)
            st.metric("Average Score", f"{avg_score:.1f}%")
        with col4:
            top_score = ranked[0]['final_score'] if ranked else 0
            st.metric("Top Score", f"{top_score:.1f}%")

        st.markdown("---")

        # ---- RANKING TABLE ----
        st.subheader("🏆 Candidate Rankings")

        table_data = []
        for c in ranked:
            table_data.append({
                "Rank": f"#{c['rank']}",
                "Name": c['name'],
                "Final Score (%)": f"{c['final_score']:.2f}%",
                "TF-IDF (%)": f"{c['tfidf_percent']:.2f}%",
                "Skill Match (%)": f"{c['skill_score']:.2f}%",
                "Verdict": c['interpretation'].split("—")[-1].strip() if "—" in c['interpretation'] else c['interpretation'],
                "Matching Skills": len(c['matching_skills']),
                "Missing Skills": len(c['missing_skills'])
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ---- BAR CHART ----
        st.subheader("📈 Score Comparison Chart")

        chart_data = pd.DataFrame({
            'Candidate': [c['name'] for c in ranked],
            'Final Score': [c['final_score'] for c in ranked],
            'TF-IDF Score': [c['tfidf_percent'] for c in ranked],
            'Skill Score': [c['skill_score'] for c in ranked],
        })

        fig = px.bar(
            chart_data.melt(id_vars='Candidate', var_name='Score Type', value_name='Score'),
            x='Candidate',
            y='Score',
            color='Score Type',
            barmode='group',
            title="Candidate Score Comparison",
            labels={'Score': 'Score (%)', 'Candidate': 'Candidate Name'},
            color_discrete_map={
                'Final Score': '#1F77B4',
                'TF-IDF Score': '#FF7F0E',
                'Skill Score': '#2CA02C'
            }
        )
        fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Shortlist Threshold (65%)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        # ---- DOWNLOAD REPORT ----
        full_report = generate_full_report(ranked, role_name)
        st.download_button(
            label="📥 Download Full Report (.txt)",
            data=full_report,
            file_name="resume_screening_report.txt",
            mime="text/plain"
        )

    with tab2:
        st.subheader("📋 Detailed Candidate Analysis")

        # Candidate selector
        candidate_names = [c['name'] for c in ranked]
        selected_candidate_name = st.selectbox("Select Candidate:", candidate_names)

        # Find selected candidate data
        selected = next(c for c in ranked if c['name'] == selected_candidate_name)

        # ---- SCORE CARDS ----
        col1, col2, col3 = st.columns(3)
        with col1:
            color = score_to_color(selected['final_score'])
            st.markdown(f"""
            <div style="background:{color}; color:white; padding:1.5rem;
                        border-radius:10px; text-align:center;">
                <div style="font-size:2.5rem; font-weight:bold;">{selected['final_score']:.1f}%</div>
                <div>Overall Score</div>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.metric("TF-IDF Similarity", f"{selected['tfidf_percent']:.1f}%")
            st.metric("Rank", f"#{selected['rank']} of {len(ranked)}")

        with col3:
            st.metric("Skill Match", f"{selected['skill_score']:.1f}%")
            st.metric("Verdict", "✅ Shortlisted" if selected['final_score'] >= 65 else "❌ Not Shortlisted")

        st.info(f"**Verdict:** {selected['interpretation']}")

        # ---- SKILLS ANALYSIS ----
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"✅ Matching Skills ({len(selected['matching_skills'])})")
            if selected['matching_skills']:
                for skill in sorted(selected['matching_skills']):
                    st.success(f"✔ {skill.title()}")
            else:
                st.warning("No matching skills found.")

        with col2:
            st.subheader(f"❌ Missing Skills ({len(selected['missing_skills'])})")
            if selected['missing_skills']:
                for skill in sorted(selected['missing_skills']):
                    st.error(f"✗ {skill.title()}")
            else:
                st.success("🎉 No missing skills — candidate meets all requirements!")

        # ---- PIE CHART for skills ----
        st.markdown("---")
        total_jd_skills = len(selected['matching_skills']) + len(selected['missing_skills'])
        if total_jd_skills > 0:
            fig_pie = px.pie(
                values=[len(selected['matching_skills']), len(selected['missing_skills'])],
                names=['Matching Skills', 'Missing Skills'],
                title=f"Skill Coverage — {selected['name']}",
                color_discrete_map={'Matching Skills': '#28a745', 'Missing Skills': '#dc3545'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)

else:
    # Show placeholder when no results yet
    with tab1:
        st.info("👈 Configure settings in the sidebar and click **Run Screening** to see results.")

        # Show sample screenshot / walkthrough
        st.markdown("""
        ### How to use this app:
        1. **Select a Job Role** (or enter custom JD) in the sidebar
        2. **Choose Resume Source** — demo data or upload your own files
        3. **Adjust Weights** if desired (default: 50/50)
        4. Click **🚀 Run Screening**
        5. View ranked results and download the report
        """)
```

## `api/index.py`

```python
import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resume_system.settings")
app = get_wsgi_application()
```

## `core/__init__.py`

```python

```

## `core/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Application, Interview, Job, OTPCode, Organization, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Role", {"fields": ("role", "organization")}),)


admin.site.register(Organization)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Interview)
admin.site.register(OTPCode)
```

## `core/apps.py`

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
```

## `core/forms.py`

```python
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Application, Interview, Job, Organization, User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    organization_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "role", "organization_name", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]

        org_name = self.cleaned_data.get("organization_name", "").strip()
        if user.role == User.ROLE_HR and org_name:
            org, _ = Organization.objects.get_or_create(name=org_name)
            user.organization = org
        if commit:
            user.save()
        return user


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6)


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "min_experience", "is_active"]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["resume"]
        widgets = {
            "resume": forms.ClearableFileInput(
                attrs={"class": "form-control", "data-max-bytes": settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024}
            )
        }

    def clean_resume(self):
        resume = self.cleaned_data["resume"]
        ext = resume.name.lower().split(".")[-1]
        if ext not in {"pdf", "docx"}:
            raise forms.ValidationError("Only PDF and DOCX files are allowed.")
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if resume.size > max_bytes:
            raise forms.ValidationError(f"Max file size is {settings.MAX_UPLOAD_SIZE_MB}MB.")
        return resume


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ["scheduled_at", "meeting_link", "notes"]
        widgets = {"scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class ApplicationReviewForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status", "selection_stage", "is_selected", "feedback"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "selection_stage": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "is_selected": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "feedback": forms.Textarea(attrs={"class": "form-control form-control-sm", "rows": 2}),
        }
```

## `core/models.py`

```python
from datetime import timedelta
import random

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    email = models.EmailField(blank=True)
    is_approved = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_ADMIN = "ADMIN"
    ROLE_HR = "HR"
    ROLE_CLIENT = "CLIENT"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_HR, "HR"),
        (ROLE_CLIENT, "Client"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CLIENT)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )


class OTPCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @classmethod
    def create_for_user(cls, user):
        code = f"{random.randint(0, 999999):06d}"
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        )

    def is_valid(self, entered_code):
        return (not self.is_used) and self.expires_at >= timezone.now() and self.code == entered_code


class Job(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)
    description = models.TextField()
    min_experience = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.organization.name})"


def resume_upload_path(instance, filename):
    return f"resumes/{instance.candidate_id}/{filename}"


def offer_upload_path(instance, filename):
    return f"offers/{instance.candidate_id}/{filename}"


class Application(models.Model):
    STATUS_APPLIED = "APPLIED"
    STATUS_SHORTLISTED = "SHORTLISTED"
    STATUS_REJECTED = "REJECTED"
    STATUS_INTERVIEW = "INTERVIEW"
    STATUS_CHOICES = [
        (STATUS_APPLIED, "Applied"),
        (STATUS_SHORTLISTED, "Shortlisted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_INTERVIEW, "Interview Scheduled"),
    ]
    SELECTION_NONE = "NONE"
    SELECTION_ROUND2 = "ROUND2"
    SELECTION_ROUND3 = "ROUND3"
    SELECTION_DIRECT = "DIRECT"
    SELECTION_CHOICES = [
        (SELECTION_NONE, "Not Selected"),
        (SELECTION_ROUND2, "Round 2 Selected"),
        (SELECTION_ROUND3, "Round 3 Selected"),
        (SELECTION_DIRECT, "Direct Selection"),
    ]

    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    assigned_hr = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_applications",
        limit_choices_to={"role": User.ROLE_HR},
    )
    resume = models.FileField(upload_to=resume_upload_path)
    ai_score = models.FloatField(default=0.0)
    matched_skills = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    selection_stage = models.CharField(max_length=20, choices=SELECTION_CHOICES, default=SELECTION_NONE)
    is_selected = models.BooleanField(default=False)
    offer_sent = models.BooleanField(default=False)
    custom_offer_letter = models.FileField(upload_to=offer_upload_path, blank=True, null=True)
    feedback = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("candidate", "job")
        ordering = ["-ai_score", "-applied_at"]


class Interview(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="interview")
    scheduled_at = models.DateTimeField()
    meeting_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## `core/services.py`

```python
from io import BytesIO

from django.core.mail import EmailMultiAlternatives, send_mail

from matching_algorithm import match_resume_to_jd
from nlp_processing import preprocess_to_string
from resume_parser import parse_resume
from skill_matching import get_skill_analysis


def score_resume_against_job(resume_path, jd_text):
    resume_text = parse_resume(resume_path)
    clean_resume = preprocess_to_string(resume_text or "")
    clean_jd = preprocess_to_string(jd_text or "")
    skill_analysis = get_skill_analysis(resume_text or "", jd_text or "")
    score_details = match_resume_to_jd(clean_resume, clean_jd, skill_analysis["skill_score"])
    return {
        "ai_score": score_details["final_score"],
        "matched_skills": sorted(skill_analysis["matching_skills"]),
        "missing_skills": sorted(skill_analysis["missing_skills"]),
    }


def send_plain_mail(subject, body, to_email):
    send_mail(
        subject=subject,
        message=body,
        from_email=None,
        recipient_list=[to_email],
        fail_silently=False,
    )


def send_offer_letter_email(candidate_name, job_title, organization_name, to_email):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    subject = f"Offer Letter - {job_title}"
    text_body = (
        f"Dear {candidate_name},\n\n"
        f"Congratulations! You are selected for the position of {job_title} at {organization_name}.\n"
        "Please find your offer letter attached as PDF.\n\n"
        "Regards,\n"
        f"{organization_name} HR Team"
    )
    html_body = f"""
    <html>
      <body>
        <h2 style="color:#1d4ed8;">Offer Letter</h2>
        <p>Dear <strong>{candidate_name}</strong>,</p>
        <p>Congratulations! You are selected for the position of <strong>{job_title}</strong> at <strong>{organization_name}</strong>.</p>
        <p>Please find your offer letter attached as PDF.</p>
        <p>Regards,<br>{organization_name} HR Team</p>
      </body>
    </html>
    """

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    y = height - 70
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(60, y, "Offer Letter")
    y -= 40
    pdf.setFont("Helvetica", 11)
    pdf.drawString(60, y, f"Date: __________________")
    y -= 35
    pdf.drawString(60, y, f"Candidate Name: {candidate_name}")
    y -= 24
    pdf.drawString(60, y, f"Position: {job_title}")
    y -= 24
    pdf.drawString(60, y, f"Organization: {organization_name}")
    y -= 36
    pdf.drawString(60, y, "Dear Candidate,")
    y -= 24
    pdf.drawString(60, y, "We are pleased to offer you employment for the above position.")
    y -= 20
    pdf.drawString(60, y, "Please contact HR for compensation details, joining date, and documentation.")
    y -= 40
    pdf.drawString(60, y, "Sincerely,")
    y -= 24
    pdf.drawString(60, y, f"{organization_name} HR Team")
    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    email = EmailMultiAlternatives(subject=subject, body=text_body, to=[to_email])
    email.attach_alternative(html_body, "text/html")
    email.attach("offer_letter.pdf", pdf_buffer.getvalue(), "application/pdf")
    email.send(fail_silently=False)
```

## `core/urls.py`

```python
from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("verify-otp/", views.verify_otp_view, name="verify-otp"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("jobs/create/", views.create_job, name="create-job"),
    path("jobs/<int:job_id>/apply/", views.apply_job, name="apply-job"),
    path("applications/<int:application_id>/schedule/", views.schedule_interview, name="schedule-interview"),
    path("applications/<int:application_id>/review/", views.review_application, name="review-application"),
    path("applications/<int:application_id>/assign-hr/", views.assign_hr, name="assign-hr"),
    path("applications/<int:application_id>/upload-offer/", views.upload_offer_letter, name="upload-offer"),
    path("analytics/admin/", views.admin_analytics, name="admin-analytics"),
    path("applications/export/", views.export_applications, name="export-applications"),
]
```

## `core/views.py`

```python
import csv
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ApplicationForm,
    ApplicationReviewForm,
    InterviewForm,
    JobForm,
    LoginForm,
    OTPForm,
    UserRegisterForm,
)
from .models import Application, Job, OTPCode, Organization, User
from .services import score_resume_against_job, send_offer_letter_email, send_plain_mail


def home(request):
    jobs = Job.objects.filter(is_active=True, organization__is_blocked=False)
    q = request.GET.get("q", "").strip()
    if q:
        jobs = jobs.filter(title__icontains=q) | jobs.filter(description__icontains=q)
    return render(request, "home.html", {"jobs": jobs})


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_plain_mail(
                "Registration Successful",
                "Your account has been created successfully.",
                user.email,
            )
            messages.success(request, "Registration complete. Please login.")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            otp = OTPCode.create_for_user(user)
            request.session["otp_user_id"] = user.id
            try:
                send_plain_mail("Your OTP Code", f"OTP: {otp.code}. Expires in 5 minutes.", user.email)
            except Exception as exc:
                messages.error(request, f"OTP email failed: {exc}")
                return redirect("login")
            messages.info(request, "OTP sent to your email.")
            return redirect("verify-otp")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def verify_otp_view(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("login")
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data["otp"]
            otp = OTPCode.objects.filter(user=user, is_used=False).order_by("-created_at").first()
            if otp and otp.is_valid(entered):
                otp.is_used = True
                otp.save(update_fields=["is_used"])
                login(request, user)
                request.session.pop("otp_user_id", None)
                return redirect("dashboard")
            messages.error(request, "Invalid or expired OTP.")
    else:
        form = OTPForm()
    return render(request, "registration/verify_otp.html", {"form": form})


class CustomLogoutView(LogoutView):
    next_page = "login"


@login_required
def dashboard(request):
    user = request.user
    if user.role == User.ROLE_ADMIN:
        admin_apps_qs = Application.objects.select_related("candidate", "job", "job__organization").order_by("-applied_at")
        admin_paginator = Paginator(admin_apps_qs, 8)
        admin_page_obj = admin_paginator.get_page(request.GET.get("page"))
        context = {
            "organizations": user.__class__.objects.filter(role=User.ROLE_HR).count(),
            "jobs_count": Job.objects.count(),
            "applications_count": Application.objects.count(),
            "shortlisted_count": Application.objects.filter(status=Application.STATUS_SHORTLISTED).count(),
            "applications": admin_page_obj,
            "page_obj": admin_page_obj,
        }
        return render(request, "dashboard_admin.html", context)

    if user.role == User.ROLE_HR:
        jobs = Job.objects.filter(organization=user.organization)
        applications_qs = Application.objects.filter(job__organization=user.organization).select_related(
            "candidate", "job", "job__organization"
        )
        status_filter = request.GET.get("status", "").strip()
        min_score = request.GET.get("min_score", "").strip()
        skill = request.GET.get("skill", "").strip()
        sort = request.GET.get("sort", "score_desc").strip()
        if status_filter:
            applications_qs = applications_qs.filter(status=status_filter)
        if min_score:
            try:
                applications_qs = applications_qs.filter(ai_score__gte=float(min_score))
            except ValueError:
                messages.warning(request, "Invalid min score filter ignored.")
        if skill:
            applications_qs = applications_qs.filter(matched_skills__icontains=skill)
        ordering_map = {
            "score_desc": "-ai_score",
            "score_asc": "ai_score",
            "latest": "-applied_at",
            "oldest": "applied_at",
        }
        ordering = ordering_map.get(sort, "-ai_score")
        applications_qs = applications_qs.order_by(ordering, "-applied_at")
        paginator = Paginator(applications_qs, 8)
        page_obj = paginator.get_page(request.GET.get("page"))
        context = {
            "jobs": jobs,
            "applications": page_obj,
            "page_obj": page_obj,
            "sort": sort,
            "total_apps": applications_qs.count(),
            "shortlisted_apps": applications_qs.filter(status=Application.STATUS_SHORTLISTED).count(),
            "interview_apps": applications_qs.filter(status=Application.STATUS_INTERVIEW).count(),
            "status_chart_labels": ["Applied", "Shortlisted", "Rejected", "Interview"],
            "status_chart_values": [
                applications_qs.filter(status=Application.STATUS_APPLIED).count(),
                applications_qs.filter(status=Application.STATUS_SHORTLISTED).count(),
                applications_qs.filter(status=Application.STATUS_REJECTED).count(),
                applications_qs.filter(status=Application.STATUS_INTERVIEW).count(),
            ],
        }
        return render(request, "dashboard_hr.html", context)

    my_apps_qs = Application.objects.filter(candidate=user).select_related("job", "job__organization", "interview")
    paginator = Paginator(my_apps_qs, 8)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard_client.html", {"applications": page_obj, "page_obj": page_obj})


@login_required
def create_job(request):
    if request.user.role != User.ROLE_HR:
        return redirect("dashboard")
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.organization = request.user.organization
            job.created_by = request.user
            job.save()
            messages.success(request, "Job posted.")
            return redirect("dashboard")
    else:
        form = JobForm()
    return render(request, "job_form.html", {"form": form})


@login_required
def apply_job(request, job_id):
    if request.user.role != User.ROLE_CLIENT:
        return redirect("dashboard")
    job = get_object_or_404(Job, id=job_id, is_active=True)
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = request.user
            application.job = job
            # default: unassigned HR; can be set later by client/HR
            application.save()

            result = score_resume_against_job(application.resume.path, job.description)
            application.ai_score = result["ai_score"]
            application.matched_skills = ", ".join(result["matched_skills"])
            application.missing_skills = ", ".join(result["missing_skills"])
            if application.ai_score >= 65:
                application.status = Application.STATUS_SHORTLISTED
                send_plain_mail(
                    "Shortlisted for Interview",
                    "Congratulations! You have been shortlisted. Please login to continue.",
                    request.user.email,
                )
            application.save()

            send_plain_mail(
                "Application Submitted",
                f"You have applied for {job.title}.",
                request.user.email,
            )
            messages.success(request, "Application submitted successfully.")
            return redirect("dashboard")
    else:
        form = ApplicationForm()
    return render(request, "apply_job.html", {"form": form, "job": job})


@login_required
def schedule_interview(request, application_id):
    if request.user.role != User.ROLE_HR:
        return redirect("dashboard")
    application = get_object_or_404(Application, id=application_id, job__organization=request.user.organization)
    if request.method == "POST":
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.created_by = request.user
            interview.save()
            application.status = Application.STATUS_INTERVIEW
            application.save(update_fields=["status"])
            interview_dt = timezone.localtime(interview.scheduled_at)
            meeting_link = interview.meeting_link if interview.meeting_link else "Will be shared soon."
            notes = interview.notes if interview.notes else "No additional notes."
            send_plain_mail(
                "Interview Scheduled",
                (
                    f"Hello {application.candidate.username},\n\n"
                    f"Your interview has been scheduled for: {application.job.title}\n"
                    f"Organization: {application.job.organization.name}\n"
                    f"Date: {interview_dt.strftime('%Y-%m-%d')}\n"
                    f"Time: {interview_dt.strftime('%I:%M %p')}\n"
                    f"Meeting Link: {meeting_link}\n"
                    f"Notes: {notes}\n\n"
                    "Please login to your dashboard for the latest updates."
                ),
                application.candidate.email,
            )
            messages.success(request, "Interview scheduled.")
            return redirect("dashboard")
    else:
        form = InterviewForm()
    return render(request, "schedule_interview.html", {"form": form, "application": application})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def review_application(request, application_id):
    if request.user.role not in {User.ROLE_HR, User.ROLE_ADMIN}:
        return redirect("dashboard")
    if request.user.role == User.ROLE_HR:
        application = get_object_or_404(Application, id=application_id, job__organization=request.user.organization)
    else:
        application = get_object_or_404(Application, id=application_id)
    if request.method == "POST":
        form = ApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            updated = form.save()
            if request.user.role == User.ROLE_HR and updated.assigned_hr is None:
                updated.assigned_hr = request.user
                updated.save(update_fields=["assigned_hr"])
            if updated.status == Application.STATUS_SHORTLISTED:
                send_plain_mail(
                    "Application Shortlisted",
                    "Congratulations! You have been shortlisted. Please login to continue.",
                    updated.candidate.email,
                )
            elif updated.status == Application.STATUS_REJECTED:
                send_plain_mail(
                    "Application Update",
                    "Thank you for applying. Your application is not selected for this role.",
                    updated.candidate.email,
                )
            if (
                updated.status == Application.STATUS_INTERVIEW
                and updated.is_selected
                and not updated.offer_sent
            ):
                send_offer_letter_email(
                    candidate_name=updated.candidate.username,
                    job_title=updated.job.title,
                    organization_name=updated.job.organization.name,
                    to_email=updated.candidate.email,
                )
                updated.offer_sent = True
                updated.save(update_fields=["offer_sent"])
            messages.success(request, "Application review updated.")
    return redirect("dashboard")


@login_required
def assign_hr(request, application_id):
    if request.user.role != User.ROLE_CLIENT:
        return redirect("dashboard")
    application = get_object_or_404(Application, id=application_id, candidate=request.user)
    if request.method == "POST":
        hr_id = request.POST.get("hr_id")
        if hr_id:
            hr = get_object_or_404(
                User,
                id=hr_id,
                role=User.ROLE_HR,
                organization=application.job.organization,
            )
            application.assigned_hr = hr
            application.save(update_fields=["assigned_hr"])
            messages.success(request, f"Assigned HR set to {hr.username}.")
    return redirect("dashboard")


@login_required
def upload_offer_letter(request, application_id):
    if request.user.role not in {User.ROLE_HR, User.ROLE_ADMIN}:
        return redirect("dashboard")
    if request.user.role == User.ROLE_HR:
        application = get_object_or_404(Application, id=application_id, job__organization=request.user.organization)
    else:
        application = get_object_or_404(Application, id=application_id)

    if request.method == "POST":
        offer_file = request.FILES.get("offer_letter")
        if not offer_file:
            messages.error(request, "Please choose a PDF file.")
            return redirect("dashboard")
        if not offer_file.name.lower().endswith(".pdf"):
            messages.error(request, "Only PDF offer letters are allowed.")
            return redirect("dashboard")

        application.custom_offer_letter = offer_file
        application.save(update_fields=["custom_offer_letter"])

        email = EmailMessage(
            subject=f"Offer Letter - {application.job.title}",
            body=(
                f"Dear {application.candidate.username},\n\n"
                "Please find your offer letter attached.\n\n"
                "Regards,\n"
                f"{application.job.organization.name} HR Team"
            ),
            to=[application.candidate.email],
        )
        email.attach(offer_file.name, offer_file.read(), "application/pdf")
        email.send(fail_silently=False)

        application.offer_sent = True
        application.save(update_fields=["offer_sent"])
        messages.success(request, "Custom offer letter uploaded and emailed successfully.")
    return redirect("dashboard")


@login_required
def admin_analytics(request):
    if request.user.role != User.ROLE_ADMIN:
        return redirect("dashboard")
    context = {
        "total_orgs": Organization.objects.count(),
        "approved_orgs": Organization.objects.filter(is_approved=True).count(),
        "blocked_orgs": Organization.objects.filter(is_blocked=True).count(),
        "total_hr": User.objects.filter(role=User.ROLE_HR).count(),
        "total_candidates": User.objects.filter(role=User.ROLE_CLIENT).count(),
        "total_jobs": Job.objects.count(),
        "active_jobs": Job.objects.filter(is_active=True).count(),
        "total_apps": Application.objects.count(),
        "shortlisted_apps": Application.objects.filter(status=Application.STATUS_SHORTLISTED).count(),
        "interview_apps": Application.objects.filter(status=Application.STATUS_INTERVIEW).count(),
        "generated_at": timezone.now(),
        "chart_labels": ["Applied", "Shortlisted", "Rejected", "Interview"],
        "chart_values": [
            Application.objects.filter(status=Application.STATUS_APPLIED).count(),
            Application.objects.filter(status=Application.STATUS_SHORTLISTED).count(),
            Application.objects.filter(status=Application.STATUS_REJECTED).count(),
            Application.objects.filter(status=Application.STATUS_INTERVIEW).count(),
        ],
    }
    return render(request, "admin_analytics.html", context)


@login_required
def export_applications(request):
    if request.user.role != User.ROLE_HR:
        return redirect("dashboard")
    export_format = request.GET.get("format", "csv").lower()
    applications = (
        Application.objects.filter(job__organization=request.user.organization)
        .select_related("candidate", "job")
        .order_by("-ai_score")
    )

    rows = [
        {
            "Candidate": app.candidate.username,
            "Email": app.candidate.email,
            "Job": app.job.title,
            "Score": app.ai_score,
            "Status": app.status,
            "Matched Skills": app.matched_skills,
            "Missing Skills": app.missing_skills,
            "Applied At": app.applied_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for app in applications
    ]

    if export_format == "pdf":
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception:
            messages.error(request, "PDF package not installed; downloaded CSV instead.")
            export_format = "csv"
        else:
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 40
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(40, y, "Applications Export Report")
            y -= 24
            pdf.setFont("Helvetica", 9)
            for idx, row in enumerate(rows, start=1):
                line = (
                    f"{idx}. {row['Candidate']} | {row['Job']} | "
                    f"Score: {row['Score']} | Status: {row['Status']}"
                )
                pdf.drawString(40, y, line[:130])
                y -= 14
                if y < 50:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 9)
                    y = height - 40
            pdf.save()
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="applications_export.pdf"'
            return response

    if export_format == "xlsx":
        try:
            import pandas as pd
        except Exception:
            messages.error(request, "Pandas/openpyxl not installed; downloaded CSV instead.")
            export_format = "csv"
        else:
            df = pd.DataFrame(rows)
            output = BytesIO()
            df.to_excel(output, index=False, engine="openpyxl")
            output.seek(0)
            response = HttpResponse(
                output.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = 'attachment; filename="applications_export.xlsx"'
            return response

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="applications_export.csv"'
    writer = csv.DictWriter(
        response,
        fieldnames=["Candidate", "Email", "Job", "Score", "Status", "Matched Skills", "Missing Skills", "Applied At"],
    )
    writer.writeheader()
    writer.writerows(rows)
    return response
```

## `docs/build_full_codebook.py`

```python
"""
Bundle all project Python source into CODEBOOK_FULL.md, CODEBOOK_FULL.pdf, CODEBOOK_FULL.docx.

Run from project root: python docs/build_full_codebook.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = Path(__file__).resolve().parent
SKIP_PARTS = frozenset({".venv", "venv", "__pycache__", ".git", "site-packages", "node_modules"})
MD_OUT = DOCS / "CODEBOOK_FULL.md"
PDF_OUT = DOCS / "CODEBOOK_FULL.pdf"
DOCX_OUT = DOCS / "CODEBOOK_FULL.docx"


def skip_path(p: Path) -> bool:
    return any(part in SKIP_PARTS for part in p.parts)


def collect_py_files() -> list[Path]:
    files = [p for p in ROOT.rglob("*.py") if not skip_path(p)]
    return sorted(files, key=lambda x: (len(x.parts), str(x).lower()))


def build_markdown(files: list[Path]) -> str:
    lines = [
        "# Smart Resume Screening — Full Python Source Codebook",
        "",
        "Auto-generated bundle of all `.py` files (excluding `.venv`, `__pycache__`, etc.).",
        "",
        "---",
        "",
    ]
    for fp in files:
        rel = fp.relative_to(ROOT)
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            text = f"<could not read file: {e}>"
        lines.append(f"## `{rel.as_posix()}`")
        lines.append("")
        lines.append("```python")
        lines.append(text.rstrip())
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def build_pdf(files: list[Path], out_path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
    from xml.sax.saxutils import escape

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "T", parent=styles["Heading1"], fontSize=12, spaceAfter=10, spaceBefore=0
    )
    path_style = ParagraphStyle(
        "P", parent=styles["Heading2"], fontSize=9, spaceAfter=6, spaceBefore=14
    )
    code_style = ParagraphStyle(
        "C",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=6,
        leading=7,
    )

    story = []
    story.append(Paragraph(escape("Smart Resume Screening — Full Python Source (PDF)"), title_style))
    story.append(
        Paragraph(
            escape("One section per file. Generated by docs/build_full_codebook.py"),
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    for i, fp in enumerate(files):
        if i:
            story.append(PageBreak())
        rel = fp.relative_to(ROOT)
        story.append(Paragraph(escape(rel.as_posix()), path_style))
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            text = f"<could not read file: {e}>"
        for line in text.splitlines():
            story.append(Paragraph(escape(line[:3000]), code_style))

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=1.0 * cm,
        rightMargin=1.0 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )
    doc.build(story)


def build_docx(files: list[Path], out_path: Path) -> None:
    from docx import Document
    from docx.enum.text import WD_LINE_SPACING
    from docx.shared import Pt

    doc = Document()
    doc.add_heading("Smart Resume Screening — Full Python Source", level=0)
    doc.add_paragraph(
        "Auto-generated. Excludes .venv and __pycache__. Each heading is one file; body is full source."
    )

    for fp in files:
        rel = fp.relative_to(ROOT)
        doc.add_heading(str(rel).replace("\\", "/"), level=1)
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            text = f"<read error: {e}>"
        p = doc.add_paragraph(text)
        for run in p.runs:
            run.font.name = "Consolas"
            run.font.size = Pt(6.5)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.space_after = Pt(4)

    doc.save(out_path)


def main() -> int:
    files = collect_py_files()
    md = build_markdown(files)
    MD_OUT.write_text(md, encoding="utf-8")
    print(f"Wrote {MD_OUT} ({len(files)} files)")

    build_pdf(files, PDF_OUT)
    print(f"Wrote {PDF_OUT}")

    build_docx(files, DOCX_OUT)
    print(f"Wrote {DOCX_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## `docs/build_project_docs.py`

```python
"""
Build PDF and Word documents from docs/PROJECT_EXPLANATION.md
Run from project root: python docs/build_project_docs.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MD_PATH = BASE / "PROJECT_EXPLANATION.md"


def _escape_reportlab(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_pdf(md_text: str, out_path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        spaceAfter=6,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=14,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=11,
        spaceAfter=8,
        spaceBefore=10,
    )
    mono = ParagraphStyle(
        "Mono",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7,
        leading=9,
        leftIndent=0,
    )

    story = []
    blocks = re.split(r"\n{2,}", md_text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        first = lines[0].strip()
        if first.startswith("# "):
            story.append(Paragraph(_escape_reportlab(first[2:].strip()), h1))
        elif first.startswith("## "):
            story.append(Paragraph(_escape_reportlab(first[3:].strip()), h2))
        elif first.startswith("```"):
            code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            for line in code.split("\n"):
                story.append(Paragraph(_escape_reportlab(line[:2000]), mono))
            story.append(Spacer(1, 0.15 * cm))
        else:
            para = " ".join(lines)
            story.append(Paragraph(_escape_reportlab(para), body))

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    doc.build(story)


def build_docx(md_text: str, out_path: Path) -> None:
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    style = doc.styles["Normal"]
    style.font.size = Pt(10)

    blocks = re.split(r"\n{2,}", md_text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        first = lines[0].strip()
        if first.startswith("# "):
            p = doc.add_heading(first[2:].strip(), level=1)
        elif first.startswith("## "):
            p = doc.add_heading(first[3:].strip(), level=2)
        elif first.startswith("### "):
            p = doc.add_heading(first[4:].strip(), level=3)
        elif first.startswith("```"):
            code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            p = doc.add_paragraph(code)
            for run in p.runs:
                run.font.name = "Courier New"
        else:
            doc.add_paragraph(" ".join(lines))

    doc.save(out_path)


def main() -> int:
    if not MD_PATH.is_file():
        print(f"Missing {MD_PATH}", file=sys.stderr)
        return 1
    text = MD_PATH.read_text(encoding="utf-8")
    pdf_out = BASE / "PROJECT_EXPLANATION.pdf"
    docx_out = BASE / "PROJECT_EXPLANATION.docx"
    build_pdf(text, pdf_out)
    print(f"Wrote {pdf_out}")
    build_docx(text, docx_out)
    print(f"Wrote {docx_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## `resume_system/__init__.py`

```python

```

## `resume_system/asgi.py`

```python
import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resume_system.settings")
application = get_asgi_application()
```

## `resume_system/settings.py`

```python
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change-me")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "resume_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "resume_system.wsgi.application"

'''if os.getenv("DATABASE_URL"):
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }'''
# Default: SQLite (works immediately, no setup needed)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Auto-switch to PostgreSQL ONLY if valid URL exists
db_url = os.getenv("DATABASE_URL", "").strip()
if db_url and db_url.startswith(("postgres://", "postgresql://")):
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(
        db_url, conn_max_age=600, ssl_require=True
    )


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "core.User"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "").replace(" ", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@resume-screening.local")

OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "200"))

SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE_SECONDS", "1800"))
SESSION_SAVE_EVERY_REQUEST = True

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

## `resume_system/urls.py`

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## `resume_system/wsgi.py`

```python
import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resume_system.settings")
application = get_wsgi_application()
```

## `core/management/__init__.py`

```python

```

## `core/migrations/0001_initial.py`

```python
# Generated by Django 6.0.3 on 2026-04-07 10:12

import core.models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('HR', 'HR'), ('CLIENT', 'Client')], default='CLIENT', max_length=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='core.organization')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resume', models.FileField(upload_to=core.models.resume_upload_path)),
                ('ai_score', models.FloatField(default=0.0)),
                ('matched_skills', models.TextField(blank=True)),
                ('missing_skills', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('APPLIED', 'Applied'), ('SHORTLISTED', 'Shortlisted'), ('REJECTED', 'Rejected'), ('INTERVIEW', 'Interview Scheduled')], default='APPLIED', max_length=20)),
                ('feedback', models.TextField(blank=True)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-ai_score', '-applied_at'],
            },
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_at', models.DateTimeField()),
                ('meeting_link', models.URLField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='interview', to='core.application')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('min_experience', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='core.organization')),
            ],
        ),
        migrations.AddField(
            model_name='application',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='core.job'),
        ),
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otp_codes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='application',
            unique_together={('candidate', 'job')},
        ),
    ]
```

## `core/migrations/0002_application_assigned_hr.py`

```python
# Generated by Django 6.0.3 on 2026-04-08 07:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='assigned_hr',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'HR'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_applications', to=settings.AUTH_USER_MODEL),
        ),
    ]
```

## `core/migrations/0003_application_is_selected_application_offer_sent_and_more.py`

```python
# Generated by Django 6.0.3 on 2026-04-08 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_application_assigned_hr'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='is_selected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='application',
            name='offer_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='application',
            name='selection_stage',
            field=models.CharField(choices=[('NONE', 'Not Selected'), ('ROUND2', 'Round 2 Selected'), ('ROUND3', 'Round 3 Selected'), ('DIRECT', 'Direct Selection')], default='NONE', max_length=20),
        ),
    ]
```

## `core/migrations/0004_application_custom_offer_letter.py`

```python
# Generated by Django 6.0.3 on 2026-04-08 11:20

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_application_is_selected_application_offer_sent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='custom_offer_letter',
            field=models.FileField(blank=True, null=True, upload_to=core.models.offer_upload_path),
        ),
    ]
```

## `core/migrations/__init__.py`

```python

```

## `core/management/commands/__init__.py`

```python

```

## `core/management/commands/seed_demo.py`

```python
from django.core.management.base import BaseCommand

from core.models import Job, Organization, User


class Command(BaseCommand):
    help = "Seed demo organization, HR, candidate, and jobs."

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            name="Demo Organization",
            defaults={"email": "demo-org@example.com", "is_approved": True},
        )
        if not org.is_approved:
            org.is_approved = True
            org.save(update_fields=["is_approved"])

        admin, created = User.objects.get_or_create(
            username="admin_demo",
            defaults={"email": "admin_demo@example.com", "role": User.ROLE_ADMIN, "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("AdminDemo@123")
            admin.save()

        hr, created = User.objects.get_or_create(
            username="hr_demo",
            defaults={"email": "hr_demo@example.com", "role": User.ROLE_HR, "organization": org},
        )
        if created:
            hr.set_password("HrDemo@123")
            hr.save()

        client, created = User.objects.get_or_create(
            username="client_demo",
            defaults={"email": "client_demo@example.com", "role": User.ROLE_CLIENT},
        )
        if created:
            client.set_password("ClientDemo@123")
            client.save()

        Job.objects.get_or_create(
            organization=org,
            title="Junior Data Scientist",
            defaults={
                "description": "Python, Machine Learning, SQL, Pandas, Communication",
                "min_experience": 1,
                "is_active": True,
                "created_by": hr,
            },
        )
        Job.objects.get_or_create(
            organization=org,
            title="Backend Python Developer",
            defaults={
                "description": "Python, Django, REST API, PostgreSQL, Git, Docker",
                "min_experience": 2,
                "is_active": True,
                "created_by": hr,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo seed complete."))
        self.stdout.write("Users: admin_demo / hr_demo / client_demo")
        self.stdout.write("Passwords: AdminDemo@123 | HrDemo@123 | ClientDemo@123")
```
