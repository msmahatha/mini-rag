# Mini RAG - AI Engineer Assessment

This project is a small, full-stack Retrieval-Augmented Generation (RAG) application. It allows users to upload a text document and ask questions a- **File Storage:** Currently supports `.txt` and `.pdf` files loaded into memory. A production system would support multiple file formats and implement proper file storage.out its content, receiving answers with inline citations.

## Quick Start

**1. Backend Setup**
```bash
cd backend
pip install -r requirements.txt
# Add your API keys to a new .env file
cp .env.example .env
uvicorn main:app --reload
```
The backend will be running at `http://127.0.0.1:8000`.

**2. Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```
The frontend will be running at `http://localhost:3000`.

## Architecture Diagram

```
[User's Browser] --(HTTP Request)--> [Next.js Frontend on Vercel]
      |
      |--(API Calls /upload, /query)--> [FastAPI Backend on Render/Railway]
                                                    |
                                                    | 1. Chunking (LangChain)
                                                    | 2. Embeddings (Google Gemini)
                                                    | 3. Upsert
                                                    v
                                      [Vector DB: Pinecone]
                                                    ^
                                                    | 4. Retrieve Top-K Chunks (MMR)
                                                    |
      [FastAPI Backend] --(API Call)------------> [Cohere API for Reranking]
            |                                         ^
            | 5. Rerank Chunks                        |
            | 6. Construct Prompt w/ Context          |
            v                                         |
      [Groq API w/ Llama3] --(API Call)---------------
            |
            | 7. Generate Answer with Citations
            v
[FastAPI Backend] --(JSON Response)--> [Next.js Frontend] --> [Displays to User]
```

## Technical Choices & Settings

* **Vector Database (Pinecone):**
    * **Index Name:** `mini-rag-index` (from `.env`)
    * **Dimensionality:** `768` (for Google Gemini `text-embedding-004`)
    * **Upsert Strategy:** The `PineconeVectorStore.from_documents` method is used, which creates the index if it doesn't exist and overwrites content on each upload for simplicity.

* **Embeddings & Chunking (LangChain):**
    * **Provider:** Google Gemini
    * **Model:** `text-embedding-004`
    * **Chunking Strategy:** `RecursiveCharacterTextSplitter` with a chunk size of **1000 tokens** and an overlap of **150 tokens**.

* **Retriever & Reranker:**
    * **Retriever:** Pinecone's vector store retriever using **Maximal Marginal Relevance (MMR)** to fetch a diverse set of 10 initial documents (`k=10`).
    * **Reranker Provider:** Cohere
    * **Model:** `rerank-english-v3.0` to reorder the 10 documents and return the top 3 most relevant (`top_n=3`).

* **LLM & Answering:**
    * **Provider:** Groq for its high speed.
    * **Model:** `llama3-8b-8192`
    * **Citations:** The prompt explicitly instructs the LLM to ground its answer in the provided context and add inline citations like `[1]`, `[2]`, etc. It is also instructed to handle cases where the answer is not in the context.

## Project Structure

```
mini-rag/
├── backend/
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment variables template
│   ├── config.py            # Configuration loading
│   ├── rag_pipeline.py      # Core RAG logic with cost tracking
│   ├── main.py              # FastAPI server with dual upload
│   ├── railway.toml         # Railway deployment config
│   └── render.yaml          # Render deployment config
├── frontend/
│   ├── package.json         # Node.js dependencies
│   ├── next.config.js       # Next.js configuration
│   ├── tsconfig.json        # TypeScript configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   ├── postcss.config.js    # PostCSS configuration
│   ├── vercel.json          # Vercel deployment config
│   └── app/
│       ├── layout.tsx       # Root layout component
│       ├── page.tsx         # Enhanced main UI with dual input
│       └── globals.css      # Global styles
├── sample_document.txt      # Sample document for testing
├── evaluation_gold_set.md   # Evaluation framework with 5 Q&A pairs
└── README.md               # This comprehensive documentation
```

## Environment Variables

Before running the application, you need to set up your API keys:

1. Copy `backend/.env.example` to `backend/.env`
2. Fill in your API keys:
   - **PINECONE_API_KEY**: Your Pinecone API key
   - **PINECONE_INDEX_NAME**: Name for your Pinecone index (e.g., `mini-rag-index`)
   - **GOOGLE_API_KEY**: Your Google Gemini API key
   - **COHERE_API_KEY**: Your Cohere API key
   - **GROQ_API_KEY**: Your Groq API key

## API Endpoints

### Backend (`http://127.0.0.1:8000`)

- **GET /** - Health check endpoint
- **POST /upload** - Upload and process a text or PDF document
  - Accepts: `multipart/form-data` with a `.txt` or `.pdf` file
  - Returns: Success message with processing status
- **POST /upload-text** - Process text content directly
  - Accepts: JSON with `{"text": "content", "source_name": "optional name"}`
  - Returns: Success message with processing status
- **POST /query** - Query the processed document
  - Accepts: JSON with `{"query": "your question"}`
  - Returns: Answer with citations, source documents, timing, and cost breakdown

## Frontend Features

- **Dual Input Methods**: Upload `.txt` or `.pdf` files OR paste text directly into the interface
- **Source Naming**: Custom naming for pasted text content
- **PDF Processing**: Automatic text extraction from PDF documents
- **Real-time Processing**: Shows upload progress and processing status
- **Interactive Querying**: Enhanced text area for entering questions with examples
- **Cited Answers**: Displays answers with clickable citation links that scroll to sources
- **Detailed Metrics**: Shows comprehensive timing, token usage, and cost breakdowns
- **Source Display**: Enhanced display of original text chunks with proper formatting
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Error Handling**: Graceful handling of API errors and edge cases

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for Python APIs
- **LangChain**: Framework for developing applications with language models
- **Pinecone**: Vector database for similarity search
- **Google Gemini**: Text embeddings (`text-embedding-004`)
- **Cohere**: Reranking service (`rerank-english-v3.0`)
- **Groq**: Fast LLM inference (`llama3-8b-8192`)

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **React Hooks**: State management and side effects

## Deployment

### Frontend (Vercel)
1. Connect your repository to Vercel
2. Set the build command to `npm run build`
3. Set the root directory to `frontend`
4. Deploy

### Backend (Render/Railway)
1. Connect your repository to your chosen platform
2. Set the build command to `pip install -r requirements.txt`
3. Set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add your environment variables
5. Deploy

## Remarks & Tradeoffs

* **State Management:** The current implementation is stateless. The processed document and its vector embeddings are held in memory on the backend and are lost on server restart. A production system would use a persistent index and manage document states more robustly.

* **Cost/Token Estimation:** The frontend shows a placeholder for token/cost estimates. A real implementation would require counting tokens for both the embedding/LLM calls and calculating costs based on provider pricing.

* **Error Handling:** Error handling is basic. A more robust app would provide more specific feedback to the user (e.g., file type validation on the frontend, more detailed API error messages).

* **Scalability:** The current `upload` endpoint processes the entire document synchronously. For large documents, this should be an asynchronous background job.

* **Security:** The CORS configuration allows all origins for simplicity. In production, this should be restricted to your frontend domain.

* **File Storage:** Currently only supports `.txt` files loaded into memory. A production system would support multiple file formats and implement proper file storage.

## Development Notes

### Running in Development

1. **Backend Development:**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Frontend Development:**
   ```bash
   cd frontend
   npm run dev
   ```

### Testing the Application

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in your browser
3. Upload a `.txt` file (try creating a simple text document with some factual content)
4. Ask questions about the content
5. Verify that citations link to the correct source chunks

## Evaluation Framework

The application includes a comprehensive evaluation framework with:

### Sample Document (`sample_document.txt`)
A 2000+ word document about AI technologies, applications, and challenges.

### Gold Set Evaluation (`evaluation_gold_set.md`)
- **5 Test Questions**: Covering different aspects of the sample document
- **Expected Answers**: With proper citations and comprehensive coverage
- **Evaluation Metrics**: Precision, Recall, Citation Accuracy, and Grounding
- **Success Criteria**: Clear scoring rubric from Poor (0-49%) to Excellent (90-100%)

### Testing Process
1. Upload the sample document
2. Ask each of the 5 test questions
3. Evaluate responses against expected answers
4. Measure citation accuracy and fact grounding
5. Check for hallucination or fabrication

### Key Evaluation Metrics
- **Precision**: Are all facts in the answer correct?
- **Recall**: Does the answer include all relevant information?
- **Citation Accuracy**: Are citations properly formatted and linked?
- **Grounding**: Is the answer fully based on source documents?

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all Python packages are installed with `pip install -r requirements.txt`
2. **CORS Errors**: Ensure the backend is running on `http://127.0.0.1:8000`
3. **API Key Errors**: Check that all environment variables are set correctly in `.env`
4. **Pinecone Index Issues**: Ensure your Pinecone project and API key have the correct permissions
5. **File Upload Fails**: Verify the file is a `.txt` file and not empty

### Performance Optimization

- **Chunk Size**: Adjust the chunk size in `rag_pipeline.py` based on your document types
- **Retrieval Count**: Modify the `k` parameter in the retriever for more/fewer initial results
- **Reranking**: Adjust the `top_n` parameter in the reranker for more/fewer final results

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
