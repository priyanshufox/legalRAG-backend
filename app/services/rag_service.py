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
"""

HyDe_Prompt = """you're a part of a RAG pipeline, and your task is to generate a well reasoned hypothetical answer for the user's query (HyDe).

This hypothetical answer will be used further for the retrieval of relevant chunks from the vector database.
So please be very accurate and don't answer the topics you're completely unaware of, just say no there.
For eg: user asks about any real-time data such as date, weather, Politics, etc.
Just simply don't reply to them as you don't have access to all of this."""

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
    return chunks

async def answer_query(query: str, top_k: int = 5, owner: str = None):

    queryLLM = "gemini-2.5-flash-lite";
    enhanced_query = await get_LLM_Response(queryLLM, enhancedQueryPrompt, query)

    print(enhanced_query)

    hyde_query = await get_LLM_Response(queryLLM, HyDe_Prompt, query)

    print(hyde_query)

    new_prompt = f" {enhanced_query} \n\n {hyde_query} "

    
    chunks = retrieve_relevant_chunks(new_prompt, top_k=top_k, owner=owner)
    # build a simple prompt
    context = "\n\n---\n\n".join(chunks)
    prompt = f"""You are a helpful assistant. Answer the user's question based on the information provided below. Do not mention where the information comes from or reference any technical details about context or chunks.

INFORMATION:
{context}

QUESTION:
{query}

Answer the question naturally and conversationally, as if you simply know this information.
"""
    model = genai.GenerativeModel(CHAT_MODEL)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=500,
            temperature=0.0
        )
    )
    
    # Handle potential content filtering or empty responses
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if candidate.finish_reason == 1:  # STOP - normal completion
            try:
                answer = response.text.strip()
            except Exception:
                answer = "Response generated but could not be accessed. Please try again."
        elif candidate.finish_reason == 2:  # MAX_TOKENS
            try:
                answer = response.text.strip() if response.text else "Response was truncated due to length limits."
            except Exception:
                answer = "Response was truncated due to length limits."
        elif candidate.finish_reason == 3:  # SAFETY
            answer = "I cannot provide a response to this query due to safety concerns."
        elif candidate.finish_reason == 4:  # RECITATION
            answer = "I cannot provide a response to this query due to recitation concerns."
        else:
            answer = "I encountered an issue generating a response. Please try rephrasing your question."
    else:
        answer = "No response generated. Please try again with a different query."
    
    # Clean up any context references that might have slipped through
    import re
    
    # Split on context references and take only the first part
    print(f"Original answer: {answer}")
    
    context_markers = [
        '(Context:', '(context:', 
        '(Context chunks', '(context chunks',
        '(Context chunks starting with',
        '(context chunks starting with'
    ]
    
    for marker in context_markers:
        if marker in answer:
            print(f"Found marker: {marker}")
            answer = answer.split(marker)[0]
            print(f"Cleaned answer: {answer}")
            break
    
    # Clean up extra whitespace and newlines
    answer = re.sub(r'\n+', '\n', answer)
    answer = re.sub(r'\s+', ' ', answer)  # Replace multiple spaces with single space
    answer = answer.strip()
    
    return {"answer": answer, "context_chunks": chunks}

