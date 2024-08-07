import PyPDF2
import docx
import re
import spacy
import pdfplumber

# Load spaCy model for Named Entity Recognition
nlp = spacy.load('en_core_web_sm')

def extract_text_from_pdf(pdf_path):
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return clean_text(text)

def clean_text(text):
    # Replace common non-text elements or icons with a space
    # You can customize this based on the specific icons in your PDF
    cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return cleaned_text

# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         text = ''
#         for page in reader.pages:
#             text += page.extract_text()
#     return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError('Unsupported file format')

def parse_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return None

def parse_email(text):
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    match = email_pattern.search(text)
    if match:
        return match.group(0)
    return None

def parse_phone_number(text):
    phone_pattern = re.compile(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
    match = phone_pattern.search(text)
    if match:
        return match.group(0)
    return None

def parse_education(text):
    education_keywords = ['school', 'university', 'college', 'bachelor', 'master', 'phd', 'degree', 'cgpa']
    sentences = text.split('\n')
    education = []
    for sentence in sentences:
        for keyword in education_keywords:
            if keyword.lower() in sentence.lower():
                education.append(sentence.strip())
                break
    return education

def parse_experience(text):
    experience_keywords = ['experience', 'worked', 'position', 'job', 'role', 'responsibility']
    sentences = text.split('\n')
    experience = []
    for sentence in sentences:
        for keyword in experience_keywords:
            if keyword.lower() in sentence.lower():
                experience.append(sentence.strip())
                break
    return experience

def parse_skills(text):
    skills_keywords = ['skills', 'proficiencies', 'competencies', 'technologies', 'technical']
    sentences = text.split('\n')
    skills = []
    for sentence in sentences:
        for keyword in skills_keywords:
            if keyword.lower() in sentence.lower():
                skills.append(sentence.strip())
                break
    return skills

def parse_resume(file_path):
    text = extract_text(file_path)
    resume_data = {
        'Name': parse_name(text),
        'Email': parse_email(text),
        'Phone': parse_phone_number(text),
        'Education': parse_education(text),
        'Experience': parse_experience(text),
        'Skills': parse_skills(text)
    }
    return resume_data

if __name__ == '__main__':
    file_path = 'divakarSaiCV.pdf'  # Change to your resume file path
    parsed_data = parse_resume(file_path)
    for key, value in parsed_data.items():
        print(f'{key}: {value}')
        # print("extracted text: " + extract_text(file_path)) 

