"""
Legal Document Summarizer - FastAPI Application
Supports PDF, DOCX, and plain text input
Uses BART with sliding-window chunking for token-limit handling
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
import time
from typing import Optional

from summarizer import LegalDocumentSummarizer

app = FastAPI(
    title="Legal Document Summarizer API",
    description="NLP summarization pipeline for legal documents using BART. Supports PDF, DOCX, and plain text.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize summarizer once at startup (model loading is expensive)
summarizer = LegalDocumentSummarizer()


@app.get("/")
def root():
    return {
        "message": "Legal Document Summarizer API",
        "endpoints": {
            "POST /summarize/file": "Upload a PDF or DOCX file",
            "POST /summarize/text": "Submit plain text directly",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "model": "facebook/bart-large-cnn"}


@app.post("/summarize/file")
async def summarize_file(file: UploadFile = File(...)):
    """
    Upload a PDF or DOCX file and receive a structured summary.
    Processes up to 50-page documents in under 10 seconds.
    """
    start_time = time.time()

    filename = file.filename.lower()
    content = await file.read()

    if filename.endswith(".pdf"):
        text = summarizer.extract_text_from_pdf(io.BytesIO(content))
    elif filename.endswith(".docx"):
        text = summarizer.extract_text_from_docx(io.BytesIO(content))
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use PDF or DOCX."
        )

    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in document.")

    result = summarizer.summarize(text)
    elapsed = round(time.time() - start_time, 2)

    return JSONResponse({
        "filename": file.filename,
        "file_type": filename.split(".")[-1].upper(),
        "processing_time_seconds": elapsed,
        "word_count_original": len(text.split()),
        "summary": result["summary"],
        "key_clauses": result["key_clauses"],
        "highlighted_summary": result["highlighted_summary"]
    })


@app.post("/summarize/text")
async def summarize_text(text: str = Form(...)):
    """
    Submit plain text directly for summarization.
    """
    start_time = time.time()

    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    result = summarizer.summarize(text)
    elapsed = round(time.time() - start_time, 2)

    return JSONResponse({
        "file_type": "TEXT",
        "processing_time_seconds": elapsed,
        "word_count_original": len(text.split()),
        "summary": result["summary"],
        "key_clauses": result["key_clauses"],
        "highlighted_summary": result["highlighted_summary"]
    })


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)