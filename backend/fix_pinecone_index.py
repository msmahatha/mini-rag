#!/usr/bin/env python3
"""
Script to fix Pinecone index dimension mismatch.
This will delete the existing index and create a new one with 768 dimensions for Gemini embeddings.
"""

import os
import time
from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME

def fix_pinecone_index():
    """Delete existing index and create new one with correct dimensions for Gemini."""
    
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in environment variables")
        return False
    
    if not PINECONE_INDEX_NAME:
        print("❌ Error: PINECONE_INDEX_NAME not found in environment variables")
        return False
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists
        existing_indexes = pc.list_indexes().names()
        print(f"📋 Existing indexes: {existing_indexes}")
        
        if PINECONE_INDEX_NAME in existing_indexes:
            print(f"🗑️  Deleting existing index: {PINECONE_INDEX_NAME}")
            pc.delete_index(PINECONE_INDEX_NAME)
            
            # Wait for deletion to complete
            print("⏳ Waiting for deletion to complete...")
            while PINECONE_INDEX_NAME in pc.list_indexes().names():
                time.sleep(5)
            print("✅ Index deleted successfully")
        else:
            print(f"ℹ️  Index {PINECONE_INDEX_NAME} doesn't exist, creating new one")
        
        # Create new index with correct dimensions for Gemini (768)
        print(f"🔨 Creating new index: {PINECONE_INDEX_NAME} with 768 dimensions")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=768,  # Gemini text-embedding-004 dimensions
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        
        # Wait for creation to complete
        print("⏳ Waiting for index creation to complete...")
        while PINECONE_INDEX_NAME not in pc.list_indexes().names():
            time.sleep(5)
        
        # Wait a bit more for the index to be ready
        time.sleep(10)
        
        print("✅ Index created successfully!")
        
        # Verify the index
        index_info = pc.describe_index(PINECONE_INDEX_NAME)
        print(f"📊 Index info:")
        print(f"   - Name: {index_info.name}")
        print(f"   - Dimension: {index_info.dimension}")
        print(f"   - Metric: {index_info.metric}")
        print(f"   - Status: {index_info.status.state}")
        
        if index_info.dimension == 768:
            print("🎉 Perfect! Index now has correct dimensions for Gemini embeddings")
            return True
        else:
            print(f"❌ Error: Index still has wrong dimensions: {index_info.dimension}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing Pinecone index: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Pinecone index dimensions for Gemini embeddings...")
    print("=" * 60)
    
    success = fix_pinecone_index()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Your Pinecone index is now ready for Gemini embeddings.")
        print("You can now upload documents and query your RAG system.")
        print("\nNext steps:")
        print("1. The deployed backend should now work correctly")
        print("2. Try uploading a document through your frontend")
        print("3. Test querying the system")
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED! Please check your API keys and try again.")
        print("Make sure PINECONE_API_KEY and PINECONE_INDEX_NAME are set correctly.")
