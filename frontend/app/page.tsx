// frontend/app/page.tsx
'use client';

import { useState } from 'react';

// Define types for our data structures
interface Source {
  page_content: string;
  metadata: {
    source: string;
    title: string;
    position: number;
  };
}

interface CostBreakdown {
  embedding_tokens: number;
  llm_input_tokens: number;
  llm_output_tokens: number;
  embedding_cost: number;
  llm_input_cost: number;
  llm_output_cost: number;
  total_cost: number;
}

interface TokenUsage {
  context_tokens: number;
  query_tokens: number;
  prompt_tokens: number;
  output_tokens: number;
  total_llm_tokens: number;
}

interface ApiResponse {
  answer: string;
  sources: Source[];
  timing: number;
  cost_breakdown: CostBreakdown;
  token_usage: TokenUsage;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState<string>('');
  const [sourceName, setSourceName] = useState<string>('Direct Input');
  const [query, setQuery] = useState<string>('');
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string>('');
  const [uploadType, setUploadType] = useState<'file' | 'text'>('file');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setUploadMessage('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        throw new Error(`Upload failed: ${res.statusText}`);
      }
      const data = await res.json();
      setUploadMessage(data.message || 'File uploaded successfully!');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextUpload = async () => {
    if (!textInput.trim()) {
      setError('Please enter some text to process.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setUploadMessage('');

    try {
      const res = await fetch('http://127.0.0.1:8000/upload-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: textInput, 
          source_name: sourceName || 'Direct Input' 
        }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Text upload failed');
      }
      const data = await res.json();
      setUploadMessage(data.message || 'Text processed successfully!');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!query) {
      setError('Please enter a query.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Query failed');
      }
      const data: ApiResponse = await res.json();
      setResponse(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to format the answer with citations
  const formatAnswer = (answer: string) => {
    const parts = answer.split(/(\[\d+\])/g);
    return parts.map((part, index) => {
      if (/(\[\d+\])/.test(part)) {
        const docNum = part.replace(/[\[\]]/g, '');
        return (
          <a
            key={index}
            href={`#source-${docNum}`}
            className="text-blue-500 font-bold hover:underline"
          >
            {part}
          </a>
        );
      }
      return part;
    });
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-50">
      <h1 className="text-4xl font-bold mb-8 text-center">Mini RAG Application</h1>
      <p className="text-gray-600 text-center mb-8 max-w-2xl">
        Upload a document (.txt or .pdf) or paste text, then ask questions to get answers with citations.
      </p>
      
      {/* Step 1: Input Selection */}
      <div className="w-full max-w-4xl bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-2xl font-semibold mb-4">1. Add Your Content</h2>
        
        {/* Toggle between file upload and text input */}
        <div className="mb-4">
          <div className="flex space-x-4 mb-4">
            <button
              onClick={() => setUploadType('file')}
              className={`px-4 py-2 rounded-md transition-colors ${
                uploadType === 'file' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Upload File
            </button>
            <button
              onClick={() => setUploadType('text')}
              className={`px-4 py-2 rounded-md transition-colors ${
                uploadType === 'text' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Paste Text
            </button>
          </div>
        </div>

        {uploadType === 'file' ? (
          <div>
            <input 
              type="file" 
              accept=".txt,.pdf" 
              onChange={handleFileChange} 
              className="mb-4 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
            />
            <p className="text-sm text-gray-500 mb-3">Supported formats: .txt, .pdf</p>
            <button 
              onClick={handleUpload} 
              disabled={isLoading || !file} 
              className="bg-blue-500 text-white px-4 py-2 rounded-md disabled:bg-gray-400 hover:bg-blue-600 transition-colors"
            >
              {isLoading ? 'Processing...' : 'Upload & Process'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Source Name (optional)
              </label>
              <input
                type="text"
                value={sourceName}
                onChange={(e) => setSourceName(e.target.value)}
                placeholder="e.g., Research Paper, Article Title"
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Text Content
              </label>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste your text content here..."
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={8}
              />
            </div>
            <button 
              onClick={handleTextUpload} 
              disabled={isLoading || !textInput.trim()} 
              className="bg-blue-500 text-white px-4 py-2 rounded-md disabled:bg-gray-400 hover:bg-blue-600 transition-colors"
            >
              {isLoading ? 'Processing...' : 'Process Text'}
            </button>
          </div>
        )}
        
        {uploadMessage && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-800">{uploadMessage}</p>
          </div>
        )}
      </div>

      {/* Step 2: Query */}
      <div className="w-full max-w-4xl bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4">2. Ask a Question</h2>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., What are the main findings? What methodology was used? What are the key conclusions?"
          className="w-full p-3 border border-gray-300 rounded-md mb-4 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          rows={3}
        />
        <button 
          onClick={handleQuery} 
          disabled={isLoading || !query.trim()} 
          className="bg-green-500 text-white px-4 py-2 rounded-md disabled:bg-gray-400 hover:bg-green-600 transition-colors"
        >
          {isLoading ? 'Thinking...' : 'Get Answer'}
        </button>
      </div>

      {error && (
        <div className="w-full max-w-4xl mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}
      
      {/* Step 3: Answer & Sources */}
      {response && (
        <div className="w-full max-w-4xl bg-white p-6 rounded-lg shadow-md mt-8">
          <h3 className="text-xl font-semibold mb-4">Answer</h3>
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{formatAnswer(response.answer)}</p>
          </div>
          
          {/* Performance & Cost Metrics */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <h4 className="font-semibold text-gray-700">Performance</h4>
              <p className="text-sm text-gray-600">Response Time: {response.timing.toFixed(2)} seconds</p>
              <p className="text-sm text-gray-600">Total Tokens: {response.token_usage.total_llm_tokens}</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700">Cost Estimate</h4>
              <p className="text-sm text-gray-600">Total Cost: ${response.cost_breakdown.total_cost.toFixed(6)}</p>
              <p className="text-sm text-gray-600">
                Embedding: ${response.cost_breakdown.embedding_cost.toFixed(6)} | 
                LLM: ${(response.cost_breakdown.llm_input_cost + response.cost_breakdown.llm_output_cost).toFixed(6)}
              </p>
            </div>
          </div>
          
          <h3 className="text-xl font-semibold mt-8 mb-4">Sources & Citations</h3>
          <div className="space-y-4">
            {response.sources.map((source, index) => (
              <div key={index} id={`source-${index + 1}`} className="bg-gray-50 p-4 rounded-lg border-l-4 border-blue-500">
                <p className="font-bold text-sm text-gray-800 mb-2">
                  [DOCUMENT {index + 1}] From: {source.metadata.source} (Chunk: {source.metadata.position})
                </p>
                <p className="text-sm text-gray-700 leading-relaxed">{source.page_content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
