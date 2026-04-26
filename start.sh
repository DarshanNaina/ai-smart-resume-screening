#!/bin/bash
set -e

# For Flask app (gunicorn app:app)
# Create necessary directories
mkdir -p media/resumes media/offers nltk_data

# Download NLTK data
python -c "import nltk; nltk.download('punkt', download_dir='./nltk_data'); nltk.download('stopwords', download_dir='./nltk_data')"

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Start gunicorn
exec gunicorn app:app --workers 4 --timeout 120 --bind 0.0.0.0:$PORT
