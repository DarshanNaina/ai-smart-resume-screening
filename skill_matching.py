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