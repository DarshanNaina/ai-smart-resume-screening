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