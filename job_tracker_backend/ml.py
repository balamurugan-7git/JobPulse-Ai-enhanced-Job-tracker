import os
import io
import joblib
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader
from docx import Document

# ---------- Sentence embedding model (for match scoring) ----------
_model = SentenceTransformer("all-MiniLM-L6-v2")


def compute_match_score(resume_text: str, job_description: str) -> float:
    """
    Returns a similarity score between 0 and 1, indicating how well
    the resume matches the job description.
    """
    if not resume_text or not job_description:
        return 0.0

    embeddings = _model.encode([resume_text, job_description])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(max(0.0, min(1.0, score)))


# ---------- Role classifier (trained scikit-learn pipeline) ----------
_classifier_path = os.path.join(os.path.dirname(__file__), "role_classifier.pkl")
_role_classifier = joblib.load(_classifier_path)


def predict_role_type(role_title: str, job_description: str = "") -> str:
    """
    Predicts the RoleType category from role title + job description text.
    """
    text = f"{role_title} {job_description or ''}".strip()
    if not text:
        return "other"
    prediction = _role_classifier.predict([text])[0]
    return prediction


# ---------- Resume file parsing (PDF/DOCX text extraction) ----------
def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """
    Extracts plain text from an uploaded PDF or DOCX file.
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()

    elif filename_lower.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join(para.text for para in doc.paragraphs)
        return text.strip()

    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")