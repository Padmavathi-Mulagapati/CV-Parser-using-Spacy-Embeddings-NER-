import streamlit as st  
import pdfplumber
import docx
import spacy
import re
import pandas as pd
import tempfile
import time  
import pytesseract
from PIL import Image


def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + ' '
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + ' '
    return text

def extract_text_from_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

def clean_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)  
    text = text.strip()
    return text

def parse_resume(text, model):
    doc = model(text)
    extracted_data = {
        'PERSON': None,
        'EMAIL': None,
        'PHONE': None,
        'LOC': None,
        'DEGREE': [],
        'ORG': [],
        'DATE': [],
        'PROJECT_TITLE': [],
        'PROJECT_ORG': [],
        'PROJECT_DURATION': [],
        'SKILL': [],
        'CERTIFICATION': []
    }
    for ent in doc.ents:
        if ent.label_ == 'PERSON' and not extracted_data['PERSON']:
            extracted_data['PERSON'] = ent.text
        elif ent.label_ == 'EMAIL' and not extracted_data['EMAIL']:
            extracted_data['EMAIL'] = ent.text
        elif ent.label_ == 'PHONE' and not extracted_data['PHONE']:
            extracted_data['PHONE'] = ent.text
        elif ent.label_ == 'LOC' and not extracted_data['LOC']:
            extracted_data['LOC'] = ent.text
        elif ent.label_ in ['SKILL', 'DEGREE', 'ORG', 'DATE', 'PROJECT_TITLE', 'PROJECT_ORG', 'PROJECT_DURATION', 'CERTIFICATION']:
            extracted_data[ent.label_].append(ent.text)
    return extracted_data

def extract_profile_links(text):
    links = {}
    linkedin = re.search(r'https?://(www\.)?linkedin\.com/in/[^\s]+', text)
    github = re.search(r'https?://(www\.)?github\.com/[^\s]+', text)
    leetcode = re.search(r'https?://(www\.)?leetcode\.com/[^\s]+', text)
    hackerrank = re.search(r'https?://(www\.)?hackerrank\.com/[^\s]+', text)
    portfolio = re.search(r'https?://(?!www\.linkedin\.com|www\.github\.com|www\.leetcode\.com|www\.hackerrank\.com)[^\s]+\.(com|in|net|me|dev)', text)

    links['LINKEDIN'] = linkedin.group() if linkedin else None
    links['GITHUB'] = github.group() if github else None
    links['LEETCODE'] = leetcode.group() if leetcode else None
    links['HACKERRANK'] = hackerrank.group() if hackerrank else None
    links['PORTFOLIO'] = portfolio.group() if portfolio else None

    return links

st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="wide")
st.title("Resume Parser")

@st.cache_resource
def load_model():
    return spacy.load("E:/CV Parser App/53 F1 Score")

nlp_model = load_model()

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF, DOCX, or Image)", 
    type=["pdf", "docx", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

st.markdown("---")
st.subheader("Or Paste Your Resume Text Below")
manual_text = st.text_area("Enter resume text here", height=200)

parsed_results = []

def process_resume(text, filename):
    clean_resume = clean_text(text)
    extracted_data = parse_resume(clean_resume, nlp_model)
    profile_links = extract_profile_links(clean_resume)
    extracted_data.update(profile_links)
    extracted_data['filename'] = filename
    return extracted_data

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.markdown(f"Processing: `{uploaded_file.name}`")

        start_time = time.time()  

        file_extension = uploaded_file.name.split('.')[-1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        if file_extension == 'pdf':
            text = extract_text_from_pdf(temp_path)
        elif file_extension == 'docx':
            text = extract_text_from_docx(temp_path)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            text = extract_text_from_image(temp_path)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue
        
        if not text.strip():
            st.warning(f"No extractable text found in `{uploaded_file.name}`.")
            continue

        extracted_data = process_resume(text, uploaded_file.name)

        end_time = time.time()  
        elapsed_time = round(end_time - start_time, 2)  

        extracted_data['execution_time_sec'] = elapsed_time  

        parsed_results.append(extracted_data)

elif manual_text.strip():
    start_time = time.time()
    extracted_data = process_resume(manual_text, 'manual_entry')
    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    extracted_data['execution_time_sec'] = elapsed_time
    parsed_results.append(extracted_data)

if parsed_results:
    st.subheader("Extracted Details (JSON View)")
    for idx, parsed_data in enumerate(parsed_results):
        with st.expander(f"Details for {parsed_data['filename']} (Execution Time: {parsed_data['execution_time_sec']} sec)") :
            st.json(parsed_data)

    st.subheader("Extracted Resume Details (Table View)")
    df = pd.DataFrame(parsed_results)

    list_fields = ['SKILL', 'DEGREE', 'ORG', 'DATE', 'PROJECT_TITLE', 'PROJECT_ORG', 'PROJECT_DURATION', 'CERTIFICATION']
    for field in list_fields:
        df[field] = df[field].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label = "Download Extracted Data as CSV",
        data = csv,
        file_name = 'parsed_resumes.csv',
        mime = 'text/csv'
    )