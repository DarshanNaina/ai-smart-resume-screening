"""
nlp_processing.py
=================
PURPOSE: Clean and preprocess text using Natural Language Processing (NLP) techniques.

HOW IT WORKS:
1. Convert text to lowercase
2. Remove punctuation and special characters
3. Tokenize (split into individual words)
4. Remove stopwords (common words like "the", "is", "and" that don't add meaning)
5. Apply stemming (reduce words to base form using Porter Stemmer algorithm)

REAL WORLD ANALOGY:
Think of this as a "text cleaner". Before comparing two documents,
we remove all the noise (punctuation, filler words) so we compare
only the meaningful words. Like cleaning vegetables before cooking.

EXAMPLE:
Input:  "The candidate has experience in Python programming and Machine Learning."
Output: ['candidat', 'experi', 'python', 'program', 'machin', 'learn']

NOTE: This version works with built-in Python + scikit-learn (no NLTK required).
      Optionally uses NLTK if installed for enhanced processing.
"""

# --- IMPORTS ---
import re           # Regular Expressions - for pattern matching in text
import string       # Provides list of punctuation characters

# Try to import NLTK (optional, for enhanced NLP)
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords as nltk_stopwords
    from nltk.stem import PorterStemmer

    for resource, path in [('punkt', 'tokenizers/punkt'),
                            ('punkt_tab', 'tokenizers/punkt_tab'),
                            ('stopwords', 'corpora/stopwords')]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource, quiet=True)

    NLTK_AVAILABLE = True
    _stemmer = PorterStemmer()
    _stop_words_base = set(nltk_stopwords.words('english'))

except ImportError:
    NLTK_AVAILABLE = False


# ============================================================
# BUILT-IN PORTER STEMMER (No external dependency version)
# ============================================================

class SimplePorterStemmer:
    """
    A lightweight stemmer that handles common English word endings.
    Reduces words to approximate root form without needing NLTK.

    EXAMPLE:
        stem("programming") -> "program"
        stem("learning")    -> "learn"
        stem("databases")   -> "databas"
    """

    def stem(self, word):
        """Reduce word to its approximate root form."""
        if len(word) <= 3:
            return word  # Very short words: don't stem them

        # List of (suffix_to_remove, replacement) pairs
        # Ordered from most specific to most general
        suffixes = [
            ('ational', 'ate'), ('tional', 'tion'), ('enci', 'ence'),
            ('anci', 'ance'), ('izer', 'ize'), ('ization', 'ize'),
            ('isation', 'ise'), ('ising', 'ise'), ('izing', 'ize'),
            ('nesses', ''), ('fulness', 'ful'), ('ousness', 'ous'),
            ('iveness', 'ive'), ('ations', 'ate'), ('ation', 'ate'),
            ('alism', 'al'), ('ments', ''), ('ment', ''),
            ('ness', ''), ('ings', ''), ('ing', ''),
            ('tions', ''), ('tion', ''), ('sion', ''),
            ('edly', ''), ('ingly', ''), ('lly', 'l'),
            ('ally', 'al'), ('ful', ''), ('less', ''),
            ('ous', ''), ('ive', ''), ('al', ''),
            ('ers', ''), ('ied', 'y'), ('ies', 'y'),
            ('ses', 's'), ('ed', ''), ('er', ''),
            ('ly', ''), ('ry', ''), ('es', ''), ('s', '')
        ]

        for suffix, replacement in suffixes:
            # Only apply if: word ends with suffix AND remaining stem >= 3 chars
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                return word[:-len(suffix)] + replacement

        return word  # No suffix matched — return original word


# ============================================================
# STOPWORDS (Built-in English stopwords list)
# ============================================================

BUILT_IN_STOPWORDS = {
    # Articles
    'a', 'an', 'the', 'this', 'that', 'these', 'those',
    # Pronouns
    'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his',
    'she', 'her', 'it', 'its', 'they', 'them', 'their', 'who', 'whom',
    # Prepositions
    'at', 'by', 'for', 'in', 'of', 'on', 'to', 'up', 'as', 'from',
    'with', 'into', 'through', 'about', 'between', 'during', 'before',
    'after', 'above', 'below', 'over', 'under', 'per', 'via',
    # Conjunctions
    'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
    'neither', 'not', 'only', 'than', 'if', 'then', 'when',
    'where', 'while', 'how', 'although', 'though', 'because',
    # Common verbs
    'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'must', 'can',
    # Other filler words
    'also', 'just', 'more', 'most', 'other', 'some', 'such',
    'no', 'all', 'each', 'every', 'any', 'many', 'very',
    'however', 'therefore', 'thus', 'hence', 'including',
    'without', 'across', 'within', 'us', 'eg', 'ie',
    # Resume/JD specific filler words
    'experience', 'year', 'years', 'work', 'working', 'company',
    'role', 'position', 'responsibilities', 'job', 'candidate',
    'required', 'requirement', 'skill', 'skills', 'ability',
    'knowledge', 'understand', 'understanding', 'using', 'use',
    'good', 'strong', 'excellent', 'etc', 'please', 'well',
    'new', 'high', 'like', 'include', 'includes', 'including'
}

# Use NLTK stopwords if available (more comprehensive), else use built-in
if NLTK_AVAILABLE:
    STOP_WORDS = _stop_words_base.union(BUILT_IN_STOPWORDS)
    stemmer = _stemmer
else:
    STOP_WORDS = BUILT_IN_STOPWORDS
    stemmer = SimplePorterStemmer()


# ============================================================
# MAIN PREPROCESSING FUNCTIONS
# ============================================================

def clean_text(text):
    """
    STEP 1 & 2: Clean the text.

    REMOVES: URLs, emails, phone numbers, punctuation, extra spaces.
    CONVERTS: All text to lowercase.

    PARAMETER:
        text (str): Raw input text

    RETURNS:
        str: Cleaned text
    """

    # Convert to lowercase so "Python" == "python"
    text = text.lower()

    # Remove URLs (http://..., www....)
    # \S+ means "one or more non-whitespace characters"
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remove email addresses (word@word.word pattern)
    text = re.sub(r'\S+@\S+', '', text)

    # Remove phone numbers (various formats like +1-234-567-8901)
    text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', '', text)

    # Remove all punctuation characters
    # string.punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Replace multiple spaces with single space
    # \s+ matches one or more whitespace characters (spaces, tabs, newlines)
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def tokenize(text):
    """
    STEP 3: Split text into individual words.

    EXAMPLE:
        "python data science" → ["python", "data", "science"]

    PARAMETER:
        text (str): Cleaned text

    RETURNS:
        list: List of individual word strings
    """
    if NLTK_AVAILABLE:
        # NLTK's word_tokenize handles contractions etc. more intelligently
        tokens = word_tokenize(text)
    else:
        # Python's built-in split() — works well enough for our purpose
        tokens = text.split()

    # Keep ONLY pure alphabetic tokens (no numbers like "2024", no symbols)
    # token.isalpha() returns True only if ALL characters are letters
    tokens = [token for token in tokens if token.isalpha()]

    return tokens


def remove_stopwords(tokens):
    """
    STEP 4: Remove common filler words.

    EXAMPLE:
        ["the", "candidate", "has", "python", "skills"] → ["candidate", "python"]

    PARAMETER:
        tokens (list): List of word strings

    RETURNS:
        list: Filtered list without stopwords
    """
    # List comprehension: keep word ONLY IF it's not in stopwords AND length > 2
    filtered = [word for word in tokens
                if word not in STOP_WORDS and len(word) > 2]
    return filtered


def apply_stemming(tokens):
    """
    STEP 5: Reduce words to their root/base form.

    EXAMPLE:
        ["programming", "learning", "databases"] → ["program", "learn", "databas"]

    WHY STEM?
    So "programmer" and "programming" both match when searching for "program".

    PARAMETER:
        tokens (list): List of word strings

    RETURNS:
        list: List of stemmed words
    """
    # Apply stemmer to each word using a list comprehension
    stemmed = [stemmer.stem(word) for word in tokens]
    return stemmed


def preprocess(text, use_stemming=True):
    """
    MAIN FUNCTION: Run the complete 4-step preprocessing pipeline.

    Pipeline: Raw Text → Clean → Tokenize → Remove Stopwords → Stem

    PARAMETERS:
        text (str): Raw input text (resume or job description)
        use_stemming (bool): Whether to apply stemming (default: True)

    RETURNS:
        list: Fully processed list of word tokens
    """
    # STEP 1+2: Clean the text
    cleaned = clean_text(text)

    # STEP 3: Split into words
    tokens = tokenize(cleaned)

    # STEP 4: Remove stopwords
    filtered = remove_stopwords(tokens)

    # STEP 5: Apply stemming (if enabled)
    if use_stemming:
        result = apply_stemming(filtered)
    else:
        result = filtered

    return result


def preprocess_to_string(text, use_stemming=True):
    """
    Same as preprocess() but returns result as a STRING (not list).

    WHY: TF-IDF Vectorizer needs a string, not a list.

    EXAMPLE:
        Input:  "Python programming and Machine Learning"
        Output: "python program machin learn"

    RETURNS:
        str: Space-joined string of processed tokens
    """
    tokens = preprocess(text, use_stemming)
    # " ".join() connects list items with spaces
    # ["python", "program", "learn"] → "python program learn"
    return " ".join(tokens)


# ---- TEST / DEMO ----
if __name__ == "__main__":
    print("=== NLP Processing Test ===")
    print(f"Using NLTK: {NLTK_AVAILABLE}\n")

    sample_text = """
    The candidate has 3 years of experience in Python programming, Machine Learning,
    and Data Analysis. They have worked with TensorFlow, Scikit-learn, and Pandas.
    """

    print("Original Text:", sample_text.strip())
    print("\nAfter Cleaning:")
    print(clean_text(sample_text))

    print("\nAfter Tokenizing:")
    print(tokenize(clean_text(sample_text)))

    print("\nAfter Removing Stopwords:")
    tokens = tokenize(clean_text(sample_text))
    print(remove_stopwords(tokens))

    print("\nFinal Output (with stemming):")
    print(preprocess(sample_text))

    print("\nAs String (for TF-IDF):")
    print(preprocess_to_string(sample_text))