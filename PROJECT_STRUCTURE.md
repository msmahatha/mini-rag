# Project Structure

```
mini-rag/
├── README.md                 # Main project documentation
├── .gitignore               # Git ignore rules
├── .env.example             # Environment variables template
├── sample_document.txt      # Sample document for testing
│
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application entry point
│   ├── rag_pipeline.py     # RAG pipeline implementation
│   ├── mock_rag_pipeline.py # Mock pipeline for demo mode
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables (create from .env.example)
│
└── frontend/               # Next.js frontend
    ├── app/
    │   ├── layout.tsx     # Root layout
    │   ├── page.tsx       # Main page component
    │   └── globals.css    # Global styles
    ├── package.json       # Node.js dependencies
    ├── package-lock.json  # Lock file
    ├── tailwind.config.ts # Tailwind CSS configuration
    ├── tsconfig.json      # TypeScript configuration
    └── next.config.js     # Next.js configuration
```

## Key Files

### Backend
- **main.py**: FastAPI server with upload and query endpoints
- **rag_pipeline.py**: Production RAG pipeline using Pinecone, Gemini, Cohere, and Groq
- **mock_rag_pipeline.py**: Demo mode pipeline that works without API keys
- **config.py**: Centralized configuration management

### Frontend
- **app/page.tsx**: Main UI with file upload and chat interface
- **app/layout.tsx**: Root layout with metadata and fonts
- **app/globals.css**: Global styles with Tailwind CSS

### Configuration
- **.env.example**: Template for environment variables
- **requirements.txt**: Python dependencies
- **package.json**: Node.js dependencies and scripts
