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