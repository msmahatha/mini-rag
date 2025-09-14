#!/bin/bash

# Render startup script for Mini RAG backend
echo "Starting Mini RAG backend on Render..."

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port $PORT
