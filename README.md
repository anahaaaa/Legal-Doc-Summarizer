# ⚖️ Legal Document Summarizer

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green?style=for-the-badge&logo=fastapi)
![Transformers](https://img.shields.io/badge/HuggingFace-BART-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</p>

<p align="center">
Production-ready NLP pipeline for summarizing legal documents using BART, FastAPI, PyPDF2, and python-docx.
</p>

---

## ✨ Features

- 📄 Supports **PDF**, **DOCX**, and **plain text**
- 🧠 Transformer-based summarization using `facebook/bart-large-cnn`
- 🔁 Sliding-window chunking for long-document processing
- ⚖️ Legal clause extraction and highlighting
- 🚀 FastAPI REST API for real-time inference
- 📑 Structured JSON responses
- 🔍 Sentence-boundary-aware chunking
- 🏷️ Key legal term detection
- 🧩 Modular NLP pipeline architecture

---

## 🏗️ Architecture

```text
Upload (PDF / DOCX / text)
        │
        ▼
  Text Extraction
  ├── PDF  → PyPDF2
  └── DOCX → python-docx
        │
        ▼
 Sliding-Window Chunking
  ├── chunk_size = 3000 chars
  ├── overlap    = 300 chars
  └── sentence-boundary snapping
        │
        ▼
  BART Summarization
  └── facebook/bart-large-cnn
        │
        ▼
  Post-processing
  ├── Combine chunk summaries
  ├── Key clause detection
  └── Markdown highlighting
        │
        ▼
  FastAPI JSON Response
```

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Backend | FastAPI |
| NLP | Hugging Face Transformers |
| Model | facebook/bart-large-cnn |
| PDF Parsing | PyPDF2 |
| DOCX Parsing | python-docx |
| Language | Python |
| API Server | Uvicorn |

---

## 📂 Project Structure

| File | Purpose |
|------|---------|
| `main.py` | FastAPI routes and API logic |
| `summarizer.py` | Core NLP summarization pipeline |
| `requirements.txt` | Python dependencies |
| `LegalDocSummarizer_v2.ipynb` | Colab notebook version |

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python main.py
```

Server starts at:

```text
http://localhost:8000
```

Swagger Docs:

```text
http://localhost:8000/docs
```

---

## 📡 API Endpoints

### POST `/summarize/file`

Upload PDF or DOCX files.

```bash
curl -X POST http://localhost:8000/summarize/file \
     -F 'file=@contract.pdf'
```

### POST `/summarize/text`

Submit plain text directly.

```bash
curl -X POST http://localhost:8000/summarize/text \
     -F 'text=This Agreement is entered into as of...'
```

### GET `/health`

```json
{
  "status": "ok",
  "model": "facebook/bart-large-cnn"
}
```

---

## 📈 Improvements Over v1

| Feature | v1 | v2 |
|---|---|---|
| Chunking | Fixed slicing | Sliding window |
| Input formats | PDF only | PDF + DOCX + text |
| API | None | FastAPI |
| Key terms | 8 | 18 |
| Deployment | Colab only | Production-ready |
| Summarization | Static params | Dynamic tuning |

---

## 🔮 Future Improvements

- Semantic deduplication
- RAG-based legal retrieval
- OCR support for scanned PDFs
- Multi-language legal summarization
- Docker deployment
- Authentication & rate limiting

---

## 📜 License

This project is licensed under the MIT License.