
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