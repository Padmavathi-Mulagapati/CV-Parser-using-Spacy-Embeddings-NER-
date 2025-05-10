# 📄 CV Parser using spaCy NER + Streamlit

This project is a **Resume Parser** built using [spaCy](https://spacy.io/) and deployed with [Streamlit](https://streamlit.io/). It extracts key information from resumes including name, email, phone, location, education, skills, certifications, project details, and profile links (LinkedIn, GitHub, etc.).

The parser is backed by a **custom-trained spaCy model** using the `tok2vec + ner` architecture.

---

## Features

- Upload resumes in **PDF, DOCX, JPG, PNG** formats
- Paste raw resume text manually
- Extract:
  - 👤 Name, ✉️ Email, 📞 Phone, 📍 Location
  - 🎓 Degrees, 🛠 Skills, 🏢 Organizations, 🕒 Dates
  - 🧪 Project titles, durations, organizations
  - 📜 Certifications
  - 🔗 Profile links: LinkedIn, GitHub, LeetCode, HackerRank, Portfolio
- View results in **JSON** and **table format**
- Download extracted data as **CSV**

---

## Model Training Overview

The custom model was trained using **spaCy v3** on manually annotated data in the format:

```python
TRAIN_DATA = [
    ("John Doe is a software engineer at Google", {"entities": [(0, 8, "PERSON"), (31, 37, "ORG")]}),
    ...
]
```

## Labels Trained - Entity Extraction
# NER-based Entities (via spaCy model):

- PERSON

- EMAIL

- PHONE

- LOC

- SKILL

- DEGREE

- CERTIFICATION

- PROJECT_TITLE

- PROJECT_DURATION

- PROJECT_ORG

- ORG

# Rule-based Extraction (via regex for profile links):

- LinkedIn

- GitHub

- LeetCode

- HackerRank

- Portfolio

## Training Pipeline:

- tok2vec: Pretrained context-sensitive word embeddings

- ner: Named Entity Recognition component

## 📈 Performance:
F1 Score: 56%

Trained on 2160 resumes and tested on 541 resumes

## NER Model Details
The custom NER model was trained using spaCy v3 with the following configuration:

- Pipeline: tok2vec + ner

- Embedding: MultiHashEmbed using features like NORM, PREFIX, SUFFIX, SHAPE

- Encoder: MaxoutWindowEncoder with:

- width = 256

- depth = 8

- window_size = 1

- maxout_pieces = 3

- Training Data: 2160 annotated resumes for training, 541 for evaluation.

- Dropout: 0.2

- Max Epochs: 30

- Batch Size: Compounding from 100 to 1000

- Optimizer: Adam with L2 regularization

## Model Performance
The model achieved the following results on the test set:

- Overall F1 Score: 0.53

- Precision: ~52%

- Recall: ~54%

## Acknowledgments
Special thanks to the spaCy community for excellent documentation and training tools.

UI built using Streamlit.

Resume datasets created and annotated manually for custom training.
