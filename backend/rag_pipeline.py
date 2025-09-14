# backend/rag_pipeline.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_cohere import CohereRerank
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers import ContextualCompressionRetriever
from langchain.docstore.document import Document
import tiktoken
import time

from config import PINECONE_INDEX_NAME, GOOGLE_API_KEY, COHERE_API_KEY, GROQ_API_KEY

# Token counting utility
def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback estimation: ~4 chars per token
        return len(text) // 4

# Cost estimation utility
def estimate_costs(embedding_tokens: int, llm_input_tokens: int, llm_output_tokens: int) -> dict:
    """Estimate costs based on current API pricing (approximate)."""
    # Approximate pricing (as of 2024)
    gemini_embedding_cost_per_1k = 0.0000125  # Gemini text-embedding-004 is much cheaper
    groq_input_cost_per_1k = 0.0001  # Groq Llama3
    groq_output_cost_per_1k = 0.0001  # Groq Llama3
    
    embedding_cost = (embedding_tokens / 1000) * gemini_embedding_cost_per_1k
    llm_input_cost = (llm_input_tokens / 1000) * groq_input_cost_per_1k
    llm_output_cost = (llm_output_tokens / 1000) * groq_output_cost_per_1k
    
    total_cost = embedding_cost + llm_input_cost + llm_output_cost
    
    return {
        "embedding_tokens": embedding_tokens,
        "llm_input_tokens": llm_input_tokens,
        "llm_output_tokens": llm_output_tokens,
        "embedding_cost": round(embedding_cost, 6),
        "llm_input_cost": round(llm_input_cost, 6),
        "llm_output_cost": round(llm_output_cost, 6),
        "total_cost": round(total_cost, 6)
    }

# 1. Chunking Strategy
def get_text_chunks(text_content: str, source_name: str):
    """
    Splits the text into chunks using a token-based strategy.
    - Chunk size: 1000 tokens
    - Chunk overlap: 15% (150 tokens)
    - Metadata: source, title (use source_name), section (not used), position (chunk_index)
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunks = text_splitter.split_text(text_content)
    
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk, 
            metadata={
                "source": source_name,
                "title": source_name,
                "position": i + 1
            }
        )
        documents.append(doc)
    return documents

# 2. Vector Store and Upsert Logic
def get_vectorstore(documents):
    """
    Initializes embeddings and upserts documents to a Pinecone index.
    - Embedding Model: Google's text-embedding-004 (via Gemini)
    - Vector DB: Pinecone
    - Index Name: From config
    - Upsert Strategy: from_documents will clear the index and add new docs.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=GOOGLE_API_KEY
    )
    
    # NOTE: from_documents will create a new index if it doesn't exist 
    # and will upsert the documents. For a production scenario, you might want
    # a more nuanced upsert/update strategy.
    vectorstore = PineconeVectorStore.from_documents(
        documents,
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings
    )
    return vectorstore

# 3. Retriever + Reranker
def configure_retriever_and_reranker(vectorstore):
    """
    Configures a retriever with a Cohere Rerank compressor.
    - Retriever: Standard vector store retriever (top-k=10)
    - Reranker: CohereRerank (top_n=3)
    """
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 10})
    
    reranker = CohereRerank(
        model="rerank-english-v3.0",
        cohere_api_key=COHERE_API_KEY,
        top_n=3
    )
    
    # The compression retriever will fetch documents and then pass them to the reranker
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=reranker, 
        base_retriever=retriever
    )
    return compression_retriever

# 4. LLM & Answering with Citations
def get_answer(query: str, retriever):
    """
    Generates an answer using an LLM with inline citations.
    - LLM Provider: Groq (Llama3-8b)
    - Handles no-answer cases by instructing the LLM.
    - Tracks tokens and costs.
    """
    
    # Prompt Engineering for Citations
    prompt_template = """
    Use the following documents to answer the user's question.
    Each document is formatted as [DOCUMENT n] where n is the document number, followed by its content.
    Your answer MUST be grounded in the information from these documents.
    For each sentence in your answer, you MUST include an inline citation to the document number that supports it. For example: "This is a statement from a document [1]."
    If multiple documents support a sentence, cite them all, like: "This is a complex statement [2][3]."
    If the documents do not contain enough information to answer the question, you MUST explicitly state: "Based on the provided documents, I cannot answer this question as the information is not available in the sources."
    Do not make up information that is not directly supported by the documents.

    Documents:
    {context}

    Question: {question}
    Answer:
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    llm = ChatGroq(temperature=0, model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY)

    def format_docs(docs):
        # Prepares the context string for the LLM, including citation numbers
        return "\n\n".join(f"[DOCUMENT {i+1}] {doc.page_content}" for i, doc in enumerate(docs))

    # Retrieve source documents first for token counting
    source_documents = retriever.get_relevant_documents(query)
    formatted_context = format_docs(source_documents)
    
    # Count tokens for cost estimation
    context_tokens = count_tokens(formatted_context)
    query_tokens = count_tokens(query)
    prompt_tokens = count_tokens(prompt_template.format(context=formatted_context, question=query))
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
    )
    
    start_time = time.time()
    response = rag_chain.invoke(query)
    end_time = time.time()
    
    # Count output tokens and estimate costs
    output_tokens = count_tokens(response.content)
    
    # Estimate embedding tokens (approximate based on document chunks)
    embedding_tokens = sum(count_tokens(doc.page_content) for doc in source_documents)
    
    cost_breakdown = estimate_costs(
        embedding_tokens=embedding_tokens,
        llm_input_tokens=prompt_tokens,
        llm_output_tokens=output_tokens
    )
    
    return {
        "answer": response.content,
        "sources": source_documents,
        "timing": end_time - start_time,
        "cost_breakdown": cost_breakdown,
        "token_usage": {
            "context_tokens": context_tokens,
            "query_tokens": query_tokens,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_llm_tokens": prompt_tokens + output_tokens
        }
    }
