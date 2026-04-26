#!/bin/bash
set -e

pip install -r requirements.txt

# Create nltk_data directory and download data
mkdir -p nltk_data
python -c "import nltk; nltk.download('punkt', download_dir='./nltk_data'); nltk.download('stopwords', download_dir='./nltk_data')"

# Create media directories
mkdir -p media/resumes media/offers

# Initialize database if needed
python -c "from app import app, db; app.app_context().push(); db.create_all()"
