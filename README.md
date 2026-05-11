# ⚖️ Legal Document Summarizer

NLP summarization pipeline for legal documents using BART, FastAPI, PyPDF2, and python-docx.

## Architecture

```
Upload (PDF / DOCX / text)
        │
        ▼
  Text Extraction
  ├── PDF  → PyPDF2
  └── DOCX → python-docx
        │
        ▼
 Sliding-Window Chunking          ← key improvement over fixed 512-char slicing
  ├── chunk_size = 3000 chars
  ├── overlap    = 300 chars
  └── sentence-boundary snapping  ← never cuts mid-sentence
        │
        ▼
  BART Summarization (per chunk)
  └── facebook/bart-large-cnn
  └── auto max_length per chunk
        │
        ▼
  Post-processing
  ├── Combine chunk summaries
  ├── Key clause detection (18 legal terms)
  └── Markdown highlighting
        │
        ▼
  FastAPI JSON Response
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app — routes for file upload and plain text |
| `summarizer.py` | Core NLP pipeline (extraction, chunking, summarization) |
| `requirements.txt` | Python dependencies |
| `LegalDocSummarizer_v2.ipynb` | Colab-compatible notebook version |

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

Server starts at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

## API Endpoints

### `POST /summarize/file`
Upload a PDF or DOCX file.

```bash
curl -X POST http://localhost:8000/summarize/file \
     -F 'file=@contract.pdf'
```

**Response:**
```json
{
  "filename": "contract.pdf",
  "file_type": "PDF",
  "processing_time_seconds": 8.4,
  "word_count_original": 4200,
  "summary": "Party 1 agrees to provide services...",
  "key_clauses": [
    { "term": "Termination", "sentence": "Either party may terminate..." }
  ],
  "highlighted_summary": "Party 1 agrees to provide **Services**..."
}
```

### `POST /summarize/text`
Submit plain text.

```bash
curl -X POST http://localhost:8000/summarize/text \
     -F 'text=This Agreement is entered into as of...'
```

### `GET /health`
```json
{ "status": "ok", "model": "facebook/bart-large-cnn" }
```

## Key Improvements Over v1

| Feature | v1 (Notebook) | v2 (This project) |
|---------|--------------|-------------------|
| Chunking | Fixed 512-char slices | Sliding window + sentence snapping |
| Input formats | PDF only | PDF, DOCX, plain text |
| API | None | FastAPI REST endpoint |
| Key terms | 8 | 18 |
| max_length | Fixed 150 | Auto-adjusted to input size |
| Serving | Colab only | Local / any server |