# AI Smart Resume Screening

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
