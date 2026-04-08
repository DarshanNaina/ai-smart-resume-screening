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