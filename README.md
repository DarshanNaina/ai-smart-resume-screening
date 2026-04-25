<<<<<<< HEAD
# AI-Based Smart Resume Screening System

Flask web app for resume screening with enhanced security and Hugging Face Spaces deployment.

## Features

- **Security Layer**: Secret code verification for Admin/HR access
- **OTP Login**: Secure authentication via email
- **Role-based Access**: Admin, HR, Client roles
- **Resume Processing**: AI-powered scoring and ranking
- **SQLite Database**: Easy deployment
- **Hugging Face Spaces**: Online deployment

## Security Enhancement

For Admin and HR roles, users must enter a secret code before accessing login/registration pages. The secret code is stored securely in environment variables.

## Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   - `SECRET_KEY`: Flask secret key
   - `ADMIN_HR_SECRET_CODE`: Secret code for Admin/HR access

3. Run the app:
   ```bash
   python app.py
   ```

## Deployment on Hugging Face Spaces

1. **Create Account**: Sign up at [Hugging Face](https://huggingface.co)

2. **Create New Space**:
   - Go to Spaces
   - Click "New Space"
   - Choose "Flask" as the SDK
   - Name your space

3. **Upload Project Files**:
   - Upload all files from your project
   - Ensure `app.py`, `requirements.txt`, `templates/`, `static/` are included

4. **Set Up Requirements**:
   - The `requirements.txt` is automatically used

5. **Configure Environment Variables**:
   - In Space settings, add:
     - `SECRET_KEY`: Your Flask secret key
     - `ADMIN_HR_SECRET_CODE`: The secret code for Admin/HR

6. **Run the Application**:
   - Hugging Face will automatically run `python app.py`
   - Your app will be live at `https://yourusername-yourspace.hf.space`

## Usage

- **Home**: Browse jobs
- **Register/Login**: With role selection
- **Admin/HR**: Requires secret code verification first
- **Dashboard**: Role-specific functionality
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
=======
# AIsmart-resume-screening
>>>>>>> cac77764d27682fb7bd463809a2271da607aeee1
"# ai-smart-resume-screening" 
