# ⚖️ Legal Case Argument Extractor

A lightweight **AI-powered Streamlit app** for extracting and ranking legal case arguments **“for” and “against”** from PDF documents.  
Optimized to run on systems with **low RAM (4GB)**, this tool uses **keyword-based classification** and **TF-IDF ranking** for fast and reliable analysis.

---

## 📝 Features

- Extracts text from PDF legal documents using `pdfplumber`.  
- Classifies sentences into **For**, **Against**, and **Neutral** using keyword-based rules.  
- Ranks top arguments by importance using **TF-IDF** scoring.  
- Provides **statistics** of total sentences, for/against/neutral counts.  
- Allows **downloadable analysis report** in plain text.  
- Fully **lightweight**, no heavy transformer models required.  

---

## ⚡ Installation

1. **Clone the repository**
```bash
git clone <(https://github.com/Mohammad-Rizwan07/legal_prep_extract)>
cd <legal_prep_extract>
```


2. **Create and activate a virtual environment**
```bash
python -m venv venv
```
# Windows
```bash
.\venv\Scripts\activate
```
# macOS/Linux
```bash
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🚀 Usage

**Run the Streamlit app** :
```bash
streamlit run streamlit_app.py
```

Upload a PDF containing legal case details.

Adjust the number of top arguments to extract (default 10).

Click “Extract Arguments”.

View top arguments for and against, along with statistics.

Download a text report of the analysis.

## 🧩 Dependencies
```bash
streamlit

pdfplumber

nltk

scikit-learn

numpy
```

Note: The app automatically downloads NLTK data (punkt) on first run.

## 📂 Project Structure
```bash
legal_prep_extract/
│
├─ streamlit_app.py         # Main Streamlit application
├─ requirements.txt         # Python dependencies
└─ README.md                # Project documentation

```

