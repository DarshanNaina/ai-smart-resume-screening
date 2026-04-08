#!/bin/bash
pip install -r requirements.txt

# Create nltk_data directory and download data
mkdir -p nltk_data
python -c "import nltk; nltk.download('punkt', download_dir='./nltk_data'); nltk.download('stopwords', download_dir='./nltk_data')"

python manage.py migrate
python manage.py collectstatic --noinput
