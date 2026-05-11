"""
summarizer.py - Core NLP pipeline for Legal Document Summarizer
"""

import re
import io
from typing import List, Dict

import PyPDF2
import docx
from transformers import pipeline

CHUNK_SIZE = 3000
OVERLAP    = 300

KEY_TERMS = [
    "Confidential Information", "Services", "Fees", "Termination",
    "Dispute Resolution", "Arbitration", "Amendments", "Obligations",
    "Liability", "Indemnification", "Governing Law", "Intellectual Property",
    "Force Majeure", "Non-Compete", "Non-Disclosure", "Payment",
    "Warranty", "Representations",
]


class LegalDocumentSummarizer:
    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        print(f"[INFO] Loading model: {model_name} ...")
        self.summarizer = pipeline("summarization", model=model_name)
        print("[INFO] Model loaded successfully.")

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"-\s*\n\s*", "", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2014", " - ").replace("\u2013", " - ")
        return text.strip()

    def extract_text_from_pdf(self, file_obj: io.BytesIO) -> str:
        reader = PyPDF2.PdfReader(file_obj)
        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text.strip())
        return self._clean_text("\n\n".join(pages_text))

    def extract_text_from_docx(self, file_obj: io.BytesIO) -> str:
        document = docx.Document(file_obj)
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        return self._clean_text("\n\n".join(paragraphs))

    def sliding_window_chunks(self, text: str) -> List[str]:
        chunks, start, text_len = [], 0, len(text)
        while start < text_len:
            end = min(start + CHUNK_SIZE, text_len)
            if end < text_len:
                snap = text[end - 200: end]
                offset = max(snap.rfind(". "), snap.rfind("\n"))
                if offset != -1:
                    end = (end - 200) + offset + 1
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - OVERLAP if end < text_len else text_len
        return chunks

    def _summarize_chunks(self, chunks: List[str]) -> List[str]:
        results = []
        for i, chunk in enumerate(chunks):
            input_len = len(chunk.split())
            max_len   = min(130, max(20, int(input_len * 0.4)))
            print(f"[INFO] Chunk {i+1}/{len(chunks)} ({input_len} words -> max {max_len} tokens)")
            out = self.summarizer(
                chunk,
                max_length=max_len,
                min_length=0,
                do_sample=False,
                truncation=True,
            )
            results.append(out[0]["summary_text"])
        return results

    def _detect_key_clauses(self, text: str) -> List[Dict[str, str]]:
        found, seen = [], set()
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            for term in KEY_TERMS:
                if term.lower() in sentence.lower() and term not in seen:
                    found.append({"term": term, "sentence": re.sub(r"\s+", " ", sentence).strip()})
                    seen.add(term)
                    break
        return found

    def _highlight_key_terms(self, text: str) -> str:
        for term in KEY_TERMS:
            text = re.compile(re.escape(term), re.IGNORECASE).sub(f"**{term}**", text)
        return text

    def summarize(self, text: str) -> Dict:
        chunks           = self.sliding_window_chunks(text)
        print(f"[INFO] {len(chunks)} chunk(s) to process ...")
        combined_summary = " ".join(self._summarize_chunks(chunks))
        return {
            "summary":             combined_summary,
            "key_clauses":         self._detect_key_clauses(text),
            "highlighted_summary": self._highlight_key_terms(combined_summary),
        }
