# Smart Resume Screening — Project Explanation (Consolidated)

This document consolidates the technical walkthrough of the AI-Based Smart Resume Screening System: architecture, technologies, and line-by-line notes for core Django modules.

## 1. Project purpose

A Django web application where organizations employ HR users to post jobs, candidates (clients) apply with PDF/DOCX resumes, and the system extracts text, preprocesses it, matches skills against a curated list, computes TF-IDF cosine similarity against the job description, combines scores, stores results on each Application, and supports shortlisting, interviews, and offer-related emails.

## 2. Technology stack

- Web framework: Django (project package `resume_system`, app `core`)
- Database: SQLite locally; PostgreSQL when `DATABASE_URL` is set (`dj-database-url`, `psycopg2-binary`)
- Static files in production: WhiteNoise
- HTTP server on Linux hosts: Gunicorn (`resume_system.wsgi:application`)
- ML/NLP: scikit-learn (TfidfVectorizer, cosine_similarity), optional NLTK in `nlp_processing.py`
- Resume parsing: PyPDF2/pypdf, python-docx
- PDF generation: ReportLab (offer letters, exports)
- Configuration: python-dotenv (`.env`)

## 3. High-level folder map

- `resume_system/` — settings, root `urls.py`, `wsgi.py`, `asgi.py`
- `core/` — models, views, forms, urls, services (scoring + mail orchestration)
- Root modules — `resume_parser.py`, `nlp_processing.py`, `skill_matching.py`, `matching_algorithm.py`, `candidate_ranking.py`, `job_description.py`, `main.py` (CLI demo), `streamlit_app.py` (optional UI)
- `templates/`, `static/` — HTML and assets
- `manage.py` — Django CLI entry

## 4. core/views.py — imports (lines 1–24)

- `csv`, `BytesIO` — CSV export and in-memory PDF/XLSX buffers
- Django: `messages`, `login`/`logout`, `login_required`, `Paginator`, `EmailMessage`, `HttpResponse`, `get_object_or_404`, `redirect`, `render`, `timezone`
- Local: forms (`UserRegisterForm`, `LoginForm`, `OTPForm`, job/application/interview forms), models (`Application`, `Job`, `OTPCode`, `Organization`, `User`), services (`score_resume_against_job`, `send_offer_letter_email`, `send_plain_mail`)

## 5. home (27–32)

- Filters active jobs for non-blocked organizations
- Optional `?q=` search on title or description (case-insensitive OR)
- Renders `home.html` with `jobs`

## 6. register_view (35–49)

- POST: validates `UserRegisterForm`, saves user (HR org creation inside form), sends confirmation email, flash message, redirect to login
- GET: empty registration form

## 7. login_view (52–68)

- POST: `LoginForm` validates username/password
- On success: `OTPCode.create_for_user`, stores `otp_user_id` in session, emails OTP, redirect to `verify-otp`
- Email failure shows error and redirects back to login
- GET: empty login form

## 8. verify_otp_view (71–91)

- Requires `otp_user_id` in session; else redirect login
- POST: validates 6-char OTP against latest unused OTP for user; on success marks OTP used, calls `login(request, user)`, clears session key, redirect dashboard
- Invalid/expired OTP shows error

## 9. CustomLogoutView (94–95)

- Class-based logout with `next_page = "login"` (use only if wired in urls; `logout_view` function may be used instead)

## 10. dashboard (98–164)

- Admin: paginated applications (8 per page), global counts; template `dashboard_admin.html`
- HR: org jobs + applications with filters (`status`, `min_score`, `skill` substring on `matched_skills`), sort keys mapped to `order_by`, chart counts on filtered queryset; `dashboard_hr.html`
- Client: own applications with `select_related("job", "job__organization", "interview")`; `dashboard_client.html`

## 11. create_job (167–182)

- HR only; POST saves `Job` with `organization` and `created_by` from `request.user`

## 12. apply_job (185–221)

- Client only; loads active job
- POST: `ApplicationForm` with files; saves `Application` with candidate and job
- Calls `score_resume_against_job(application.resume.path, job.description)`; writes `ai_score`, `matched_skills`, `missing_skills`
- If `ai_score >= 65`: status SHORTLISTED + email
- Always sends “application submitted” email

## 13. schedule_interview (224–259)

- HR only; application must belong to HR’s organization
- Creates `Interview`, sets application status to INTERVIEW, emails candidate with local time and optional link/notes

## 14. logout_view (262–264)

- Calls `logout(request)` and redirects to login

## 15. review_application (267–308)

- HR or admin; HR scoped by organization
- POST: `ApplicationReviewForm`; HR auto-sets `assigned_hr` if empty
- Emails on shortlist/reject
- If status INTERVIEW and `is_selected` and not `offer_sent`: `send_offer_letter_email`, then set `offer_sent`

## 16. assign_hr (311–328)

- Client only; assigns an HR user from the same organization as the job

## 17. upload_offer_letter (331–368)

- HR or admin; validates PDF upload; saves `custom_offer_letter`; emails attachment; sets `offer_sent`

## 18. admin_analytics (371–395)

- Admin only; aggregates org/user/job/application counts and status chart values

## 19. export_applications (398–482)

- HR only; org applications ordered by `-ai_score`
- Query param `format`: `pdf` (ReportLab), `xlsx` (pandas), default `csv`
- Builds row dicts with candidate, job, score, skills, applied_at

## 20. core/models.py — Organization (10–18)

- `name` unique; optional `email`; `is_approved`, `is_blocked`; `created_at` auto

## 21. User (21–38)

- Extends `AbstractUser`; `role` ADMIN/HR/CLIENT; optional `ForeignKey` to `Organization` with `SET_NULL`

## 22. OTPCode (41–58)

- FK to user CASCADE; 6-char `code`; `expires_at`; `is_used`
- `create_for_user`: random 000000–999999, expiry from `settings.OTP_EXPIRY_MINUTES`
- `is_valid`: not used, not expired, code match

## 23. Job (61–72)

- FK to Organization CASCADE; `description` used as JD text for scoring; `is_active`, `created_by`, timestamps

## 24. Upload path helpers (74–79)

- `resume_upload_path`: `resumes/{candidate_id}/{filename}`
- `offer_upload_path`: `offers/{candidate_id}/{filename}`

## 25. Application (82–128)

- FK candidate and job; unique_together (candidate, job)
- `assigned_hr` limited to role HR; `resume` FileField; `ai_score` float; `matched_skills` / `missing_skills` text; status and selection fields; `custom_offer_letter`; default ordering `-ai_score`, `-applied_at`

## 26. Interview (131–137)

- OneToOne to Application CASCADE; `scheduled_at`; optional `meeting_link`; `notes`; `created_by`

## 27. core/services.py — scoring pipeline

- `score_resume_against_job(resume_path, jd_text)`:
  1. `parse_resume` → raw text
  2. `preprocess_to_string` on resume and JD
  3. `get_skill_analysis` on raw texts for skills
  4. `match_resume_to_jd` with skill_score → final combined score
- `send_plain_mail` — thin `send_mail` wrapper
- `send_offer_letter_email` — ReportLab PDF in memory + `EmailMultiAlternatives` with attachment

## 28. matching_algorithm.py (summary)

- `calculate_tfidf_cosine_similarity`: corpus [resume, JD], TfidfVectorizer (1–2 grams), cosine similarity between rows
- `calculate_weighted_score`: default 50% TF-IDF (0–100 scale) + 50% skill score
- `match_resume_to_jd`: returns tfidf metrics, final score, interpretation string

## 29. Deployment note (Render / Gunicorn)

- WSGI module must match this repo: `resume_system.wsgi:application` (not `smart_resume_screening`)
- Set `DJANGO_SECRET_KEY`, `DEBUG=False`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, email settings

## 30. Generating this guide as PDF or Word

From the project root run:

python docs/build_project_docs.py

Outputs:

- docs/PROJECT_EXPLANATION.pdf
- docs/PROJECT_EXPLANATION.docx

The Markdown source is docs/PROJECT_EXPLANATION.md (this file).

---
Document generated for local use; open files from the docs folder in File Explorer or your editor to copy or share.
