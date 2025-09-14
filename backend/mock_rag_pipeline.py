# backend/mock_rag_pipeline.py
"""
Mock RAG pipeline for testing without API keys
"""
import time
import re
from typing import List, Dict, Any

# Mock document storage
mock_documents = []
mock_processed = False

def mock_get_text_chunks(text_content: str, source_name: str):
    """Mock text chunking"""
    global mock_documents, mock_processed
    
    # Simple chunking by paragraphs or sentences
    chunks = []
    paragraphs = text_content.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():
            chunks.append({
                "page_content": paragraph.strip(),
                "metadata": {
                    "source": source_name,
                    "title": source_name,
                    "position": i + 1
                }
            })
    
    mock_documents = chunks
    mock_processed = True
    return chunks

def mock_get_vectorstore(documents):
    """Mock vector store creation"""
    return {"status": "created", "documents": len(documents)}

def mock_configure_retriever_and_reranker(vectorstore):
    """Mock retriever configuration"""
    return {"status": "configured"}

def mock_get_answer(query: str, retriever):
    """Mock answer generation with citations"""
    global mock_documents
    
    if not mock_documents:
        return {
            "answer": "Based on the provided documents, I cannot answer this question as no documents have been processed yet.",
            "sources": [],
            "timing": 0.1,
            "cost_breakdown": {
                "embedding_tokens": 0,
                "llm_input_tokens": 0,
                "llm_output_tokens": 0,
                "embedding_cost": 0.0,
                "llm_input_cost": 0.0,
                "llm_output_cost": 0.0,
                "total_cost": 0.0
            },
            "token_usage": {
                "context_tokens": 0,
                "query_tokens": len(query.split()),
                "prompt_tokens": 0,
                "output_tokens": 0,
                "total_llm_tokens": 0
            }
        }
    
    start_time = time.time()
    
    # Simple keyword matching for demo
    query_words = set(query.lower().split())
    relevant_docs = []
    
    for doc in mock_documents:
        doc_words = set(doc["page_content"].lower().split())
        if query_words.intersection(doc_words):
            relevant_docs.append(doc)
    
    # Take top 3 most relevant (mock reranking)
    relevant_docs = relevant_docs[:3]
    
    if not relevant_docs:
        answer = "Based on the provided documents, I cannot find specific information to answer this question."
    else:
        # Generate a mock answer with citations
        answer_parts = []
        for i, doc in enumerate(relevant_docs):
            # Extract a relevant sentence from the document
            sentences = doc["page_content"].split('.')
            relevant_sentence = sentences[0] if sentences else doc["page_content"][:100]
            answer_parts.append(f"{relevant_sentence.strip()} [{i+1}]")
        
        answer = ". ".join(answer_parts) + "."
    
    end_time = time.time()
    
    # Mock cost calculation
    context_tokens = sum(len(doc["page_content"].split()) for doc in relevant_docs)
    query_tokens = len(query.split())
    output_tokens = len(answer.split())
    
    return {
        "answer": answer,
        "sources": relevant_docs,
        "timing": end_time - start_time,
        "cost_breakdown": {
            "embedding_tokens": context_tokens,
            "llm_input_tokens": context_tokens + query_tokens,
            "llm_output_tokens": output_tokens,
            "embedding_cost": context_tokens * 0.0001 / 1000,
            "llm_input_cost": (context_tokens + query_tokens) * 0.0001 / 1000,
            "llm_output_cost": output_tokens * 0.0001 / 1000,
            "total_cost": (context_tokens * 2 + query_tokens + output_tokens) * 0.0001 / 1000
        },
        "token_usage": {
            "context_tokens": context_tokens,
            "query_tokens": query_tokens,
            "prompt_tokens": context_tokens + query_tokens,
            "output_tokens": output_tokens,
            "total_llm_tokens": context_tokens + query_tokens + output_tokens
        }
    }
