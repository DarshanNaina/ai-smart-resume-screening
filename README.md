# AI Smart Resume Screening

<<<<<<< HEAD
A Flask-based resume screening application that uses AI to match candidates with job descriptions.

## Features

- Upload PDF/DOCX resumes
- AI-powered skill matching
- Candidate ranking by compatibility
- Multiple user roles (Admin, HR, Client)
- Job posting and application management

## Tech Stack

- **Backend**: Flask, Python
- **Database**: SQLite (local) / PostgreSQL (production)
- **NLP**: NLTK, spaCy, scikit-learn
- **Deployment**: Gunicorn, Render

## Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Or with Gunicorn:
```bash
gunicorn app:app
```

## Deployment on Render

### Option 1: Using render.yaml Blueprint

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Create a new service from the blueprint
4. Select your repository and the `render.yaml` file

### Option 2: Manual Deploy

1. Create a PostgreSQL database on Render
2. Create a Web Service and connect your GitHub
3. Set environment variables:
   - `SECRET_KEY` = (generate a secure key)
   - `RENDER` = `true`
   - `DATABASE_URL` = (your PostgreSQL connection string)
4. Deploy!

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key |
| `RENDER` | Set to `true` for production |
| `DATABASE_URL` | PostgreSQL connection string |

## License

MIT
=======
This repository contains a Flask-based resume screening web app that can be deployed on Render.

## Project structure

- `app.py` — main Flask application
- `requirements.txt` — Python dependencies
- `templates/` — HTML templates
- `static/` — CSS and JS assets
- `db.sqlite3` — local SQLite database for demo use

## Local setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables in `.env` or your shell:
   - `SECRET_KEY`
   - `ADMIN_HR_SECRET_CODE`
4. Run locally:
   ```bash
   python app.py
   ```
5. Visit `http://127.0.0.1:5000`

## Render deployment

This project includes a `render.yaml` file for Render Web Service deployment.

### 1) Create a Render account

- Go to https://render.com and sign up or log in.
- Confirm your email address if required.

### 2) Connect your repository

- Click **New** → **Web Service**.
- Choose **Connect account** if your GitHub repo is not already linked.
- Select the repository containing this project.

### 3) Configure the Render service

- **Name**: choose a name for your app
- **Environment**: `Python`
- **Branch**: `main` (or the branch you want to deploy)
- **Root Directory**: `/` (project root)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

Render can also read the `render.yaml` file automatically if you use the same repository.

### 4) Set up PostgreSQL database

- In Render, click **New** → **PostgreSQL**
- **Name**: `smart-resume-screening-db`
- **Database**: `smart_resume_screening`
- **User**: `smart_resume_user`
- Choose a plan (free tier available)
- Click **Create Database**

The database connection string will be automatically available to your web service.

### 5) Set environment variables in Render

In your Render service settings, add the following secrets:

- `SECRET_KEY` = a long random value
- `ADMIN_HR_SECRET_CODE` = the secret code for Admin/HR access

The `DATABASE_URL` will be set automatically by Render when you link the database.

### 6) Deploy on Render

- Click **Create Web Service**.
- Render will build and start the app.
- After deployment, open the provided URL.

### 7) Verify the live app

- Visit the Render URL.
- Confirm the home page loads.
- Use the Register page to create a normal user and an HR/Admin user.

## Optional: view deploy logs

- In Render, open the Web Service dashboard.
- Select **Logs** to troubleshoot build or startup errors.

## Notes

- The app uses PostgreSQL for production persistence (via Render's managed database).
- For local development, it falls back to SQLite.
- `app.py` is the service entrypoint for Render.
>>>>>>> 7216b07 (Ready for Render deployment with PostgreSQL)
