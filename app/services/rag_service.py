# app/services/rag_service.py
from qdrant_client import QdrantClient
from sqlalchemy.orm import Session
from ..utils.embeddings_client import get_embedding
from ..utils.qdrant_client import qdrant
import os
import google.generativeai as genai
from dotenv import load_dotenv
from ..utils.LLMmodel import get_LLM_Response
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINIAI_API_KEY")
CHAT_MODEL = os.getenv("MODEL_FOR_CHAT", "models/gemini-2.5-flash")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)



enhancedQueryPrompt = f"""you're a helpful assistant, you're a part of an advanced RAG pipeline and your job is to
strictly enhance the user query so that the retrieval of chunks from the vectorDB is more accurate.
you don't have to answer or question to the user query, you just have to enhance it for further processes.
if the query feels grammatically wrong, just try to enhance it to make a meaningful query.

Special instructions:
- If the user asks about "this PDF", "this document", or similar references, enhance the query to be more specific about document content
- Include relevant keywords that would help find document content (e.g., if asking about a legal document, include terms like "case", "court", "legal", etc.)
- Make the query more searchable while preserving the original intent
"""

HyDe_Prompt = """you're a part of a RAG pipeline, and your task is to generate a well reasoned hypothetical answer for the user's query (HyDe).

This hypothetical answer will be used further for the retrieval of relevant chunks from the vector database.
So please be very accurate and don't answer the topics you're completely unaware of, just say no there.
For eg: user asks about any real-time data such as date, weather, Politics, etc.
Just simply don't reply to them as you don't have access to all of this.

Special instructions:
- If the user asks about "this PDF" or "this document", generate a hypothetical answer that would be typical for document content
- Include relevant keywords and concepts that would likely appear in legal, business, or other document types
- Make the hypothetical answer detailed enough to help retrieve relevant chunks from the database"""

evaluator_prompt = """You are a chunk relevance evaluator.
your task is to evaluate each retrieved chunk, whether the chunk is relevant to the user query or not.
strictly reply in just "yes" or "no"
and be very strict during the evaluation,
Example:
Query: What is ReactJS, its features, use cases, and benefits in web development?
Here are 3 retrieved chunks.

[
  Document {
    pageContent: 'Version 1.0 \n' +
      "const name = 'Andrew' \n" +
      'const userAge = 27 \n' +
      '... JavaScript object shorthand example ...',
    metadata: { source: 'src/nodejs.pdf', pdf: [Object], loc: [Object] },
    id: '0f430e4b-2c63-494d-a3d7-ad59e3d8bf96'
  },
  Document {
    pageContent: 'Version 1.0 \n' +
      '<!DOCTYPE html> \n' +
      '... Express Handlebars templating example ...',
    metadata: { source: 'src/nodejs.pdf', pdf: [Object], loc: [Object] },
    id: '879441b8-8518-4b38-b001-4a1a9ed6880a'
  },
  Document {
    pageContent: 'Version 1.0 \n' +
      '... Lesson about Node.js basics ...',
    metadata: { source: 'src/nodejs.pdf', pdf: [Object], loc: [Object] },
    id: '6f6ed719-7323-47af-9e87-aa4463bb1761'
  }
]

Output JSON:
{
  "0": "no",
  "1": "no",
  "2": "no"
}
            
reason: bcz these chunks are about nodejs and never talked about reactjs"""





def retrieve_relevant_chunks(query: str, top_k: int = 5, owner: str = None):
    vector = get_embedding(query)
    collection = f"user_{owner or 'global'}"
    # search
    res = qdrant.search(collection_name=collection, query_vector=vector, limit=top_k)
    chunks = []
    for hit in res:
        payload = hit.payload or {}
        text = payload.get("text")
        if text:
            chunks.append(text)
    print(chunks)
    return chunks

async def answer_query(query: str, top_k: int = 5, owner: str = None):

    queryLLM = "gemini-2.5-flash-lite";
    enhanced_query = await get_LLM_Response(queryLLM, enhancedQueryPrompt, query)

    print(enhanced_query)

    # hyde_query = await get_LLM_Response(queryLLM, HyDe_Prompt, query)

    # print(hyde_query)

    new_prompt = f" {enhanced_query} "

    
    chunks = retrieve_relevant_chunks(new_prompt, top_k=top_k, owner=owner)
    # build a simple prompt
    context = "\n\n---\n\n".join(chunks)
    prompt = f"""You are a helpful assistant that answers questions based on the provided information. Use the information below to answer the user's question comprehensively and accurately.

INFORMATION:
{context}

QUESTION:
{query}

INSTRUCTIONS:
- Answer the question based ONLY on the information provided above
- If the information contains relevant details about the topic, use them to provide a complete answer
- Do not say the information doesn't contain details about the topic if relevant content is clearly present
- Be specific and detailed in your response
- If the user asks about "this PDF" or "this document", refer to the content as if it's the document they're asking about
"""
    # model = genai.GenerativeModel(CHAT_MODEL)
    response = await get_LLM_Response(CHAT_MODEL, prompt, query)
    
    
    return {"answer": response, "context_chunks": chunks}
    return {response}

