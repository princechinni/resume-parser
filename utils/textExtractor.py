import pdfplumber
import docx
import re

class TextExtractor:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_path):
        text = ''
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return self.clean_text(text)

    def extract_text_from_docx(self, docx_path):
        doc = docx.Document(docx_path)
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'
        return text

    def extract_text(self, file_path):
        if file_path.endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError('Unsupported file format')

    def clean_text(self, text):
        # Clean the extracted text
        cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text

