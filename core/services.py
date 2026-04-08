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
