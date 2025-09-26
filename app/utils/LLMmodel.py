import google.generativeai as genai

async def get_LLM_Response(model: str, system_prompt: str, user_query: str):
    # Use ChatML format for the prompt
    chatml_prompt = (
        f"<|system|>\n{system_prompt}\n<|end|>\n"
        f"<|user|>\n{user_query}\n<|end|>\n"
    )
    print(model)
    generative_model = genai.GenerativeModel(model)
    response = await generative_model.generate_content_async(
        chatml_prompt
    )
    
    # Handle potential content filtering or empty responses
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if candidate.finish_reason == 1:  # STOP - normal completion
            try:
                return response.text.strip()
            except Exception:
                return "Response generated but could not be accessed. Please try again."
        elif candidate.finish_reason == 2:  # MAX_TOKENS
            try:
                return response.text.strip() if response.text else "Response was truncated due to length limits."
            except Exception:
                return "Response was truncated due to length limits."
        elif candidate.finish_reason == 3:  # SAFETY
            return "I cannot provide a response to this query due to safety concerns."
        elif candidate.finish_reason == 4:  # RECITATION
            return "I cannot provide a response to this query due to recitation concerns."
        else:
            return "I encountered an issue generating a response. Please try rephrasing your question."
    else:
        return "No response generated. Please try again with a different query."

'''

Create a tool and API endpoint that allows a user to either:
1. Enter a query like: "find me similar cases to nirbhaya case", OR
2. Upload a PDF file describing a case.

The backend must:
- Extract keywords (3–4 high-quality legal keywords) from either the query text
  or from the PDF content.
- Use Google Gemini API to extract these keywords intelligently.
- Call the Indian Kanoon API with the generated keywords to retrieve related
  case information (using this endpoint pattern):
  https://api.indiankanoon.org/search/?formInput=<keywords>&maxcites=20
- Return only the docs array from the Indian Kanoon response.
- Each result should include: title, court/source, publish date, citation,
  and a clickable link to the case (https://indiankanoon.org/doc/{tid}/).

Tech Details:
- Use LangChain’s PyPDFLoader for extracting text from PDFs.
- Use google-generativeai for Gemini calls.
- Securely read Gemini API key from environment variables.
- Handle both input modes (query text or PDF) in a single API endpoint.
- Make sure output is clean JSON for the Next.js frontend.

Steps:
1. Create a FastAPI route /api/similar-cases that accepts either:
   - query (string) in POST JSON body, OR
   - a pdf file in a multipart/form-data request.
2. If a PDF is uploaded:
   - Extract its text using LangChain PyPDFLoader.
3. Send the text/query to Gemini with a system prompt to generate keywords
   in strict JSON:
   {
     "keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
     "apiQuery": "keyword1+keyword2+keyword3+keyword4"
   }
4. Use apiQuery to call the Indian Kanoon API.
5. Return a JSON array of the formatted cases to the frontend.

Also:
- Include an example of .env setup for the Gemini API key.
- Show how to run the FastAPI server locally.
- Include error handling if Gemini returns bad output or Indian Kanoon is down.

USE MODEL: gemini-2.5-flash
dont delete env file or any files from the project
'''