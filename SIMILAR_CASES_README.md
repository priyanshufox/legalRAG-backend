# Similar Cases Tool

This tool allows users to find similar legal cases based on either a text query or an uploaded PDF file. It uses Google Gemini API to extract relevant keywords and then searches the Indian Kanoon API for related cases.

## Features

- **Text Query Support**: Enter a query like "find me similar cases to nirbhaya case"
- **PDF Upload Support**: Upload a PDF file describing a case
- **Intelligent Keyword Extraction**: Uses Gemini 2.5 Flash to extract 3-4 high-quality legal keywords
- **Indian Kanoon Integration**: Searches the Indian Kanoon API for related cases
- **Structured Results**: Returns formatted case information with titles, courts, dates, citations, and links

## API Endpoint

**POST** `/api/tools/similar-cases`

### Input Options

#### Option 1: Text Query (JSON)
```json
{
  "query": "find me similar cases to nirbhaya case"
}
```

#### Option 2: PDF Upload (Multipart Form Data)
- Field name: `file`
- File type: PDF only

### Response Format

```json
{
  "success": true,
  "keywords": ["nirbhaya", "rape", "murder", "delhi"],
  "api_query": "nirbhaya+rape+murder+delhi",
  "cases": [
    {
      "title": "Case Title",
      "court": "Court Name",
      "publish_date": "Date",
      "citation": "Citation",
      "link": "https://indiankanoon.org/doc/{tid}/"
    }
  ],
  "total_cases": 5
}
```

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the project root with:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
cd simple-RAG
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

### Using the Test Script

```bash
# Set your API key
export GEMINI_API_KEY=your_api_key_here

# Run the test
python test_similar_cases.py
```

### Using curl

#### Text Query:
```bash
curl -X POST "http://localhost:8000/api/tools/similar-cases" \
  -H "Content-Type: application/json" \
  -d '{"query": "find me similar cases to nirbhaya case"}'
```

#### PDF Upload:
```bash
curl -X POST "http://localhost:8000/api/tools/similar-cases" \
  -F "file=@path/to/your/case.pdf"
```

## How It Works

1. **Input Processing**: Accepts either text query or PDF file
2. **Text Extraction**: If PDF is uploaded, extracts text using LangChain PyPDFLoader
3. **Keyword Extraction**: Uses Gemini 2.5 Flash to extract 3-4 relevant legal keywords
4. **API Query Formation**: Combines keywords with '+' signs for Indian Kanoon API
5. **Case Search**: Calls Indian Kanoon API with the generated query
6. **Result Formatting**: Formats the response for the frontend with structured case data

## Error Handling

The tool includes comprehensive error handling for:
- Invalid input (missing query/file, wrong file type)
- PDF text extraction failures
- Gemini API errors
- Indian Kanoon API failures
- JSON parsing errors

## Dependencies

- `google-generativeai`: For Gemini API integration
- `langchain-community`: For PDF text extraction
- `requests`: For Indian Kanoon API calls
- `fastapi`: For the API endpoint
- `python-multipart`: For file uploads

## Example Usage

### Frontend Integration (JavaScript)

```javascript
// Text query
const response = await fetch('/api/tools/similar-cases', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'find me similar cases to nirbhaya case'
  })
});

const data = await response.json();
console.log(data.cases);

// PDF upload
const formData = new FormData();
formData.append('file', pdfFile);

const response = await fetch('/api/tools/similar-cases', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.cases);
```

## Notes

- The tool uses the `gemini-2.5-flash` model as specified
- Maximum 20 cases are returned from Indian Kanoon API
- All case links are clickable and point to the full case on Indian Kanoon
- The tool is designed to work with the existing FastAPI application structure
