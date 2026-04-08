"""
resume_parser.py
================
PURPOSE: Extract raw text from resume files (PDF and DOCX formats).

HOW IT WORKS:
- Reads PDF resumes using PyPDF2
- Reads DOCX resumes using python-docx
- Returns plain text for further processing

REAL WORLD ANALOGY:
Think of this as a "scanner" that reads physical resumes and converts
them into plain text so the computer can understand them.
"""

# --- IMPORTS ---
import os                      # os: used to check if file exists and get file extension
# Try PyPDF2 first; fall back to pypdf (newer package name)
try:
    import PyPDF2 as _pdf_lib   # PyPDF2: library to read PDF files
    _PDF_LIB = "PyPDF2"
except ImportError:
    import pypdf as _pdf_lib    # pypdf: the updated successor to PyPDF2
    _PDF_LIB = "pypdf"
from docx import Document      # docx: library to read Word (.docx) files


def extract_text_from_pdf(pdf_path):
    """
    Reads a PDF file and returns all text from it.

    PARAMETER:
        pdf_path (str): Full path to the PDF file on your computer

    RETURNS:
        str: All text content found in the PDF
    """
    text = ""  # Start with empty string; we'll add text to this

    try:
        # Open the PDF file in binary read mode ("rb")
        # "rb" = read binary — needed for non-text files like PDFs
        with open(pdf_path, "rb") as pdf_file:

            # Create a PDF reader object — like "opening" the file
            # Uses whichever PDF library was successfully imported
            pdf_reader = _pdf_lib.PdfReader(pdf_file)

            # Loop through every page in the PDF
            # len(pdf_reader.pages) gives us total number of pages
            for page_number in range(len(pdf_reader.pages)):

                # Get the specific page object
                page = pdf_reader.pages[page_number]

                # Extract text from this page and add to our full text
                # The "\n" adds a new line between pages
                text += page.extract_text() + "\n"

    except Exception as e:
        # If something goes wrong (file not found, corrupted PDF, etc.)
        # Print the error and return empty string instead of crashing
        print(f"[ERROR] Could not read PDF: {pdf_path} | Reason: {e}")
        return ""

    return text  # Return all the text we collected


def extract_text_from_docx(docx_path):
    """
    Reads a Word (.docx) file and returns all text from it.

    PARAMETER:
        docx_path (str): Full path to the DOCX file

    RETURNS:
        str: All text content found in the DOCX file
    """
    text = ""  # Start with empty string

    try:
        # Open the DOCX file using python-docx's Document class
        doc = Document(docx_path)

        # A DOCX file contains "paragraphs" — each line/block of text
        # Loop through all paragraphs in the document
        for paragraph in doc.paragraphs:

            # paragraph.text gives us the text of one paragraph
            # Strip() removes extra spaces at start and end
            # "\n" adds a newline after each paragraph
            text += paragraph.text.strip() + "\n"

    except Exception as e:
        print(f"[ERROR] Could not read DOCX: {docx_path} | Reason: {e}")
        return ""

    return text  # Return all collected text


def parse_resume(file_path):
    """
    MAIN FUNCTION: Automatically detects file type and extracts text.

    This is the function you call from other files.
    It figures out if the file is PDF or DOCX and calls the right function.

    PARAMETER:
        file_path (str): Path to the resume file (PDF or DOCX)

    RETURNS:
        str: Extracted text from the resume
    """

    # First, check if the file actually exists on the computer
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return ""

    # Get the file extension (e.g., ".pdf" or ".docx")
    # os.path.splitext splits "resume.pdf" into ("resume", ".pdf")
    # [1] gets the second part (the extension)
    # .lower() converts to lowercase so ".PDF" == ".pdf"
    file_extension = os.path.splitext(file_path)[1].lower()

    # Check which type of file it is and call the right parser
    if file_extension == ".pdf":
        print(f"[INFO] Parsing PDF resume: {file_path}")
        return extract_text_from_pdf(file_path)

    elif file_extension == ".docx":
        print(f"[INFO] Parsing DOCX resume: {file_path}")
        return extract_text_from_docx(file_path)

    else:
        # File type not supported
        print(f"[ERROR] Unsupported file type: {file_extension}. Use PDF or DOCX.")
        return ""


def parse_resume_from_text(text):
    """
    If resume is already plain text (for testing/demo), just clean and return it.

    PARAMETER:
        text (str): Raw resume text

    RETURNS:
        str: Cleaned resume text
    """
    # Strip leading/trailing whitespace and return
    return text.strip()


# ---- TEST / DEMO ----
# This block only runs when you run THIS file directly (python resume_parser.py)
# It does NOT run when imported by another file
if __name__ == "__main__":
    print("=== Resume Parser Test ===")
    sample_text = """
    John Doe
    Email: john@example.com
    Skills: Python, Machine Learning, Data Analysis
    Experience: 3 years at XYZ Corp
    """
    result = parse_resume_from_text(sample_text)
    print("Parsed Text:\n", result)