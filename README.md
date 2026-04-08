# AI-Based Smart Resume Screening System

Production-ready Django web app for resume screening with:
- OTP login via email
- Role-based access (Admin, HR, Client)
- Resume parsing (PDF/DOCX)
- AI scoring (TF-IDF + cosine similarity + skill gap analysis)
- Candidate ranking and interview scheduling
- PostgreSQL + Gunicorn + WhiteNoise deployment support

## 1) Project Structure

- `resume_system/` Django project settings and WSGI/ASGI
- `core/` app for auth, roles, jobs, applications, interviews
- `templates/` all UI templates
- `resume_parser.py`, `nlp_processing.py`, `skill_matching.py`, `matching_algorithm.py` reused AI engine modules

## 2) Local Setup (Step-by-Step)

1. Create and activate virtual environment:
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Create `.env` from `.env.example` and fill values.
4. Run migrations:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
5. Create admin account:
   - `python manage.py createsuperuser`
6. Run development server:
   - `python manage.py runserver`
7. Open:
   - `http://127.0.0.1:8000/`

## 3) Role Flow

- **Admin**
  - Access `/admin/`
  - Manage users (HR/Client), organizations, jobs, applications, OTP records
- **HR**
  - Register as HR with organization
  - Post jobs
  - View AI-ranked applications
  - Schedule interviews and send email
- **Client**
  - Register/login with OTP
  - Apply to jobs with PDF/DOCX resume
  - See status and AI score

## 4) OTP + Email

- Login checks credentials first, then sends OTP to user email.
- OTP expires based on `OTP_EXPIRY_MINUTES`.
- On valid OTP, user session is authenticated.

### SMTP (Gmail) example
- `EMAIL_HOST=smtp.gmail.com`
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_HOST_USER=your-email@gmail.com`
- `EMAIL_HOST_PASSWORD=<gmail-app-password>`

## 5) AI Scoring Logic

When candidate applies:
1. Resume text extraction from PDF/DOCX (`resume_parser.py`)
2. NLP preprocessing (`nlp_processing.py`)
3. Skill extraction and gap analysis (`skill_matching.py`)
4. TF-IDF + cosine similarity score (`matching_algorithm.py`)
5. Combined score stored in `Application.ai_score`

Default shortlist threshold:
- `ai_score >= 65` -> status becomes `SHORTLISTED`

## 6) Production Security Included

- Password hashing via Django auth
- CSRF middleware enabled
- XSS protections enabled
- Role-based route checks in views
- File type and file size validation
- Secure cookie/SSL flags enabled in `DEBUG=False`

## 7) Deploy to Render (Global Hosting)

1. Push code to GitHub.
2. Create PostgreSQL database in Render.
3. Create new Web Service connected to this repo.
4. Build command:
   - `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
5. Start command:
   - `gunicorn resume_system.wsgi`
6. Add environment variables from `.env.example`:
   - `DJANGO_SECRET_KEY`, `DEBUG=False`, `DATABASE_URL`, email vars, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
7. After deploy, create superuser from Render shell:
   - `python manage.py createsuperuser`

Your public URL will look like:
- `https://your-app-name.onrender.com`

## 8) Deploy to Vercel

1. Push code to GitHub.
2. Ensure these files exist in project root:
   - `vercel.json`
   - `api/index.py`
3. In Vercel dashboard, import the GitHub repo.
4. Add environment variables:
   - `DJANGO_SECRET_KEY`
   - `DEBUG=False`
   - `DATABASE_URL` (recommended: Neon or Render PostgreSQL)
   - `ALLOWED_HOSTS=.vercel.app`
   - `CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app`
   - Email variables (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, etc.)
5. Deploy.
6. Run migrations using one-time local command against production DB:
   - `python manage.py migrate`

Important for Vercel:
- Use external PostgreSQL (required).
- Vercel filesystem is ephemeral, so for long-term uploaded files use cloud storage (S3/Cloudinary).

## 9) Deploy to Railway / Heroku

Use same environment values and commands:
- Build: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- Start: `gunicorn resume_system.wsgi`

## 10) Important Notes

- `gunicorn` is for Linux hosting (Render/Railway/Heroku).
- On Windows local machine, use `python manage.py runserver`.
- Keep `.env` private and never commit secrets.
"# smart-resume-screening" 
"# AIsmart-resume-screening" 
"# AIsmart-resume-screening" 
