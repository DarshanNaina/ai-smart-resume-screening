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