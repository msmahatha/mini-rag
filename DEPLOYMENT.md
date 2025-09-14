# Deployment Guide

This guide covers deploying the Mini RAG application with the frontend on Netlify and the backend on Render.

## Prerequisites

1. GitHub account with the repository
2. Netlify account
3. Render account
4. Required API keys:
   - Pinecone API key and index name
   - Google AI (Gemini) API key
   - Cohere API key
   - Groq API key

## Backend Deployment (Render)

### Step 1: Create a New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Select the `mini-rag` repository

### Step 2: Configure the Service

```
Name: mini-rag-backend
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 3: Set Environment Variables

In the Render dashboard, add these environment variables:

```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index_name
GOOGLE_API_KEY=your_google_api_key
COHERE_API_KEY=your_cohere_api_key
GROQ_API_KEY=your_groq_api_key
DEMO_MODE=false
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for the deployment to complete
3. Note the service URL (e.g., `https://mini-rag-backend.onrender.com`)

## Frontend Deployment (Netlify)

### Step 1: Create a New Site

1. Go to [Netlify Dashboard](https://app.netlify.com/)
2. Click "Add new site" → "Import an existing project"
3. Connect to GitHub and select your repository
4. Choose the `frontend` folder as the base directory

### Step 2: Configure Build Settings

```
Base directory: frontend
Build command: npm run build
Publish directory: .next
```

### Step 3: Set Environment Variables

In Netlify dashboard, go to Site settings → Environment variables:

```
NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com
```

Replace `your-render-backend-url` with your actual Render service URL.

### Step 4: Deploy

1. Click "Deploy site"
2. Wait for the deployment to complete
3. Your site will be available at a Netlify URL (e.g., `https://amazing-app-123456.netlify.app`)

## Custom Domains (Optional)

### Netlify Custom Domain

1. Go to Site settings → Domain management
2. Click "Add custom domain"
3. Follow the DNS configuration instructions

### Render Custom Domain

1. Go to your service dashboard
2. Click "Settings" → "Custom Domain"
3. Add your domain and configure DNS

## Environment Configuration

### Production Environment Variables

**Render (Backend):**
```env
PINECONE_API_KEY=your_actual_key
PINECONE_INDEX_NAME=mini-rag-index
GOOGLE_API_KEY=your_actual_key
COHERE_API_KEY=your_actual_key
GROQ_API_KEY=your_actual_key
DEMO_MODE=false
```

**Netlify (Frontend):**
```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your Netlify domain is added to the CORS configuration in `main.py`
2. **Build Failures**: Check that all dependencies are listed in `requirements.txt` and `package.json`
3. **API Connection Issues**: Verify the `NEXT_PUBLIC_API_URL` environment variable is set correctly

### Logs

- **Render**: View logs in the service dashboard
- **Netlify**: Check the deploy logs and function logs

### Demo Mode

For testing without API keys, you can set `DEMO_MODE=true` in Render environment variables.

## Monitoring and Maintenance

1. Monitor service health on both platforms
2. Check logs regularly for errors
3. Update dependencies periodically
4. Monitor API usage and costs

## Scaling Considerations

- **Render**: Upgrade to paid plans for better performance and no sleep mode
- **Netlify**: Consider Netlify Pro for more build minutes and advanced features
- **Database**: Consider moving from in-memory storage to a persistent database for production

## Security Notes

1. Never commit API keys to the repository
2. Use environment variables for all sensitive configuration
3. Regularly rotate API keys
4. Monitor for unusual API usage

## Support

- Render Documentation: https://render.com/docs
- Netlify Documentation: https://docs.netlify.com
- GitHub Issues: Create issues in your repository for problems
