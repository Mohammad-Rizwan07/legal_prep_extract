import streamlit as st
import pdfplumber
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="Legal Case Argument Extractor",
    page_icon="⚖️",
    layout="wide"
)

# Download required NLTK data
@st.cache_resource
def setup_nltk():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

setup_nltk()

class ArgumentExtractor:
    def __init__(self):
        self.for_keywords = [
            'support', 'favor', 'agree', 'endorse', 'approve', 'advocate', 'beneficial',
            'positive', 'advantage', 'merit', 'strengthen', 'uphold', 'affirm',
            'constitutional', 'legal', 'valid', 'justified', 'reasonable', 'proper'
        ]
        self.against_keywords = [
            'oppose', 'against', 'disagree', 'reject', 'deny', 'refute', 'challenge',
            'unconstitutional', 'illegal', 'invalid', 'improper', 'unreasonable',
            'violate', 'breach', 'contrary', 'conflict', 'harmful', 'detrimental'
        ]

    def extract_text_from_pdf(self, pdf_file) -> str:
        all_pages = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    all_pages.append(txt)
        return "\n".join(all_pages)

    def clean_text(self, raw: str) -> str:
        text = raw.replace("\r", "\n")
        text = re.sub(r"\n\s*\n", "\n", text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def split_into_sentences(self, text: str):
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text)

    def classify_arguments(self, sentences):
        for_args = []
        against_args = []
        neutral_args = []

        for sent in sentences:
            if len(sent.strip()) < 20:
                continue
            sent_lower = sent.lower()
            for_score = sum(1 for keyword in self.for_keywords if keyword in sent_lower)
            against_score = sum(1 for keyword in self.against_keywords if keyword in sent_lower)

            if for_score > against_score and for_score > 0:
                for_args.append(sent)
            elif against_score > for_score and against_score > 0:
                against_args.append(sent)
            else:
                neutral_args.append(sent)

        return for_args, against_args, neutral_args

    def rank_sentences_by_importance(self, sentences, top_k=10):
        if not sentences:
            return []
        filtered_sentences = [s for s in sentences if len(s.strip()) > 30]
        if not filtered_sentences:
            return sentences[:top_k]
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(filtered_sentences)
        scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
        ranked_indices = np.argsort(scores)[::-1]
        return [{'text': filtered_sentences[i], 'score': float(scores[i])} for i in ranked_indices[:top_k]]

    def extract_arguments(self, pdf_file, top_k=10):
        raw_text = self.extract_text_from_pdf(pdf_file)
        if not raw_text.strip():
            return None, "No text found in PDF"
        cleaned_text = self.clean_text(raw_text)
        sentences = self.split_into_sentences(cleaned_text)
        for_args, against_args, neutral_args = self.classify_arguments(sentences)
        top_for = self.rank_sentences_by_importance(for_args, top_k)
        top_against = self.rank_sentences_by_importance(against_args, top_k)
        return {
            'for_arguments': top_for,
            'against_arguments': top_against,
            'total_sentences': len(sentences),
            'for_count': len(for_args),
            'against_count': len(against_args),
            'neutral_count': len(neutral_args)
        }, None

def main():
    st.title("⚖️ Legal Case Argument Extractor")
    st.markdown("Upload a PDF of legal case details to extract top arguments for and against.")

    st.sidebar.header("Settings")
    top_k = st.sidebar.slider("Number of top arguments to extract", 5, 20, 10)

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF containing legal case details"
    )

    if uploaded_file is not None:
        st.info(f"📄 File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")

        if 'extractor' not in st.session_state:
            st.session_state.extractor = ArgumentExtractor()

        if st.button("🔍 Extract Arguments", type="primary"):
            with st.spinner("Processing PDF and extracting arguments..."):
                results, error = st.session_state.extractor.extract_arguments(uploaded_file, top_k)

            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ Arguments extracted successfully!")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Sentences", results['total_sentences'])
                col2.metric("For Arguments", results['for_count'])
                col3.metric("Against Arguments", results['against_count'])
                col4.metric("Neutral", results['neutral_count'])

                col_for, col_against = st.columns(2)

                with col_for:
                    st.subheader("🟢 Top Arguments FOR")
                    if results['for_arguments']:
                        for i, arg in enumerate(results['for_arguments'], 1):
                            with st.expander(f"Argument {i} (Score: {arg['score']:.3f})"):
                                st.write(arg['text'])
                    else:
                        st.info("No 'for' arguments found in the document.")

                with col_against:
                    st.subheader("🔴 Top Arguments AGAINST")
                    if results['against_arguments']:
                        for i, arg in enumerate(results['against_arguments'], 1):
                            with st.expander(f"Argument {i} (Score: {arg['score']:.3f})"):
                                st.write(arg['text'])
                    else:
                        st.info("No 'against' arguments found in the document.")

                # Download results
                download_text = f"Legal Case Argument Analysis\n"
                download_text += f"Document: {uploaded_file.name}\n"
                download_text += f"Total Sentences Analyzed: {results['total_sentences']}\n"
                download_text += f"Arguments For: {results['for_count']}\n"
                download_text += f"Arguments Against: {results['against_count']}\n\n"

                download_text += "TOP ARGUMENTS FOR:\n" + "==================\n"
                for i, arg in enumerate(results['for_arguments'], 1):
                    download_text += f"{i}. {arg['text']}\n\n"

                download_text += "TOP ARGUMENTS AGAINST:\n" + "=====================\n"
                for i, arg in enumerate(results['against_arguments'], 1):
                    download_text += f"{i}. {arg['text']}\n\n"

                st.download_button(
                    label="📄 Download Analysis Report",
                    data=download_text,
                    file_name=f"argument_analysis_{uploaded_file.name.replace('.pdf', '')}.txt",
                    mime="text/plain"
                )

    else:
        st.info("👆 Please upload a PDF file to begin argument extraction.")

if __name__ == "__main__":
    main()
