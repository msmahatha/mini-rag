# backend/main.py - Mini RAG Backend API
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import rag_pipeline
import mock_rag_pipeline
import os
import PyPDF2
import io

app = FastAPI(title="Mini RAG API", description="Retrieval-Augmented Generation API")

# Demo mode toggle - set to True to use mock pipeline (no API keys required)
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Configure CORS - Allow all origins for demo deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=False,  # Set to False when using "*"
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# In-memory storage for the retriever. In a real app, you'd persist this differently.
retriever = None
vectorstore = None

class QueryRequest(BaseModel):
    query: str

class TextUploadRequest(BaseModel):
    text: str
    source_name: Optional[str] = "Direct Input"

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Endpoint to upload a text or PDF file, process it, and create a retriever.
    """
    global retriever, vectorstore
    
    # Check file extension
    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")
    
    try:
        content_bytes = await file.read()
        
        # Extract text based on file type
        if file.filename.endswith(".pdf"):
            content = extract_text_from_pdf(content_bytes)
        else:  # .txt file
            content = content_bytes.decode("utf-8")
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the file.")
        
        if DEMO_MODE:
            # Use mock pipeline
            documents = mock_rag_pipeline.mock_get_text_chunks(content, source_name=file.filename)
            vectorstore = mock_rag_pipeline.mock_get_vectorstore(documents)
            retriever = mock_rag_pipeline.mock_configure_retriever_and_reranker(vectorstore)
        else:
            # Use real pipeline
            documents = rag_pipeline.get_text_chunks(content, source_name=file.filename)
            vectorstore = rag_pipeline.get_vectorstore(documents)
            retriever = rag_pipeline.configure_retriever_and_reranker(vectorstore)
        
        mode_msg = " (Demo Mode)" if DEMO_MODE else ""
        file_type = "PDF" if file.filename.endswith(".pdf") else "text"
        return {"message": f"Successfully processed and indexed {file_type} file: {file.filename}.{mode_msg}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-text")
async def upload_text(request: TextUploadRequest):
    """
    Endpoint to upload text directly (paste area), process it, and create a retriever.
    """
    global retriever, vectorstore
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")
    
    try:
        if DEMO_MODE:
            # Use mock pipeline
            documents = mock_rag_pipeline.mock_get_text_chunks(request.text, source_name=request.source_name)
            vectorstore = mock_rag_pipeline.mock_get_vectorstore(documents)
            retriever = mock_rag_pipeline.mock_configure_retriever_and_reranker(vectorstore)
        else:
            # Use real pipeline
            documents = rag_pipeline.get_text_chunks(request.text, source_name=request.source_name)
            vectorstore = rag_pipeline.get_vectorstore(documents)
            retriever = rag_pipeline.configure_retriever_and_reranker(vectorstore)
        
        mode_msg = " (Demo Mode)" if DEMO_MODE else ""
        return {"message": f"Successfully processed and indexed text from {request.source_name}.{mode_msg}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def handle_query(request: QueryRequest):
    """
    Endpoint to ask a question and get a cited answer.
    """
    global retriever
    if retriever is None:
        raise HTTPException(status_code=400, detail="No document has been uploaded and processed yet.")
    
    try:
        if DEMO_MODE:
            # Use mock pipeline
            result = mock_rag_pipeline.mock_get_answer(request.query, retriever)
        else:
            # Use real pipeline
            result = rag_pipeline.get_answer(request.query, retriever)
        
        # Convert Document objects to dicts for JSON serialization (real pipeline)
        if not DEMO_MODE and 'sources' in result:
            result['sources'] = [
                {"page_content": doc.page_content, "metadata": doc.metadata}
                for doc in result['sources']
            ]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/")
def read_root():
    mode_msg = "Demo Mode - No API keys required!" if DEMO_MODE else "Production Mode"
    return {"status": f"Backend is running - {mode_msg}"}
