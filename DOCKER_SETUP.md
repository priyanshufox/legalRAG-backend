# Docker Setup Instructions

## Prerequisites

1. **Docker Desktop** installed and running on your system
2. **OpenAI API Key** - You'll need to set this as an environment variable

### Starting Docker Desktop
- Make sure Docker Desktop is running before executing docker commands
- You can start it from the Start menu or system tray

## Setup Steps

### 1. Set Environment Variables

Create a `.env` file in the project root with your OpenAI API key:

```bash
# .env file
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 2. Run with Docker Compose

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up --build -d
```

### 3. Access the Services

- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Vector DB**: http://localhost:6333

### 4. Test the API

```bash
# Upload a document
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"

# Query the documents
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is this document about?", "top_k": 5}'
```

## Services Configuration

### Backend Service
- **Port**: 8000
- **Database**: PostgreSQL (Render cloud database)
- **Vector DB**: Qdrant (containerized)
- **File Storage**: Local volume mount for uploads

### Qdrant Service
- **Port**: 6333
- **Storage**: Persistent volume for vector data
- **Configuration**: Optimized for RAG workloads

## Troubleshooting

1. **Port Conflicts**: Make sure ports 8000 and 6333 are not in use
2. **OpenAI API Key**: Ensure your API key is valid and has sufficient credits
3. **Database Connection**: The PostgreSQL connection is pre-configured for your Render database
4. **File Permissions**: The uploads directory will be created automatically

## Development Mode

The backend runs with `--reload` flag, so code changes will automatically restart the server.
