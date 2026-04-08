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