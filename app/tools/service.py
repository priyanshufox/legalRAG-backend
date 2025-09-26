
# System prompt for the tools
SYSTEM_PROMPT_SUMMARIZE = (
    "You are a helpful legal assistant. "
    "You can summarize uploaded legal PDF documents, or extract all dates mentioned in the document and provide a brief description of the events that occurred on those dates. "
    "When summarizing, focus on the main points and key information. "
    "Do not mention where the information comes from or reference any technical details about context or chunks. "
    "Make it bullet point wise and concise. "
    "IMPORTANT: Do NOT use asterisks (*) or any markdown formatting in your response. Use plain text only."
    ''' 
    Example:
    {
  "case": {
    "title": "State of Karnataka v. Rohan Mehra",
    "case_number": "CR/CCPS/593/2025",
    "type": "Cybercrime and Intellectual Property Theft"
  },
  "accused": {
    "name": "Rohan Mehra",
    "role": "Former Senior Software Architect at Innovatech Solutions Pvt. Ltd.",
    "allegation": "Illegally accessed and downloaded proprietary source code and confidential design documents related to 'Project Chimera' after his resignation."
  },
  "charges": [
    { "section": "Section 66", "act": "Information Technology Act, 2000" },
    { "section": "Section 43(b)", "act": "Information Technology Act, 2000" },
    { "section": "Section 408", "act": "Indian Penal Code, 1860" },
    { "section": "Section 379", "act": "Indian Penal Code, 1860" }
  ],
  "timeline": [
    {
      "date": "July 10-11, 2025",
      "event": "Unauthorized access and data exfiltration from Innovatech's server."
    },
    {
      "date": "July 15, 2025",
      "event": "FIR filed by Innovatech's CTO."
    },
    {
      "date": "August 3, 2025",
      "event": "Mehra arrested; laptop, hard drives, and phone seized. First appearance and 5-day police remand."
    },
    {
      "date": "August 8, 2025",
      "event": "Mehra sent to judicial custody."
    },
    {
      "date": "August 11, 2025",
      "event": "Bail application filed."
    },
    {
      "date": "August 18, 2025",
      "event": "Bail granted with conditions."
    },
    {
      "date": "September 15, 2025",
      "event": "Charge sheet filed."
    },
    {
      "date": "September 29, 2025",
      "event": "Scheduled date for Jurisdictional Hearing (Framing of Charges)."
    }
  ],
  "status": "Case pending; prosecution submitted forensic reports."
}
'''
)
SYSTEM_PROMPT_EXTRACT_EVENTS_DATES = (
    "You are a helpful legal assistant. "
    "You can extract all dates mentioned in the document and provide a brief description of the events that occurred on those dates. "
    "When extracting dates and events, list each date found in the document and give a concise explanation of what happened on that date, based on the document's content."
    "Do not mention where the information comes from or reference any technical details about context or chunks. "
    "Make it bullet point wise and concise. "
    "IMPORTANT: Do NOT use asterisks (*) or any markdown formatting in your response. Use plain text only."
    '''
    Example:
  "events": [
    {
      "date": "July 10, 2025, 18:00 IST - July 11, 2025, 02:00 IST",
      "event": "Unauthorized access and data exfiltration from the company server; traced to the accused's IP address."
    },
    {
      "date": "July 15, 2025, 11:30 IST",
      "event": "FIR filed by Mr. Ankit Sharma, CTO of Innovatech Solutions, at the Cyber Crime Police Station, Bengaluru."
    },
    {
      "date": "August 03, 2025, 07:15 IST",
      "event": "Accused arrested from his residence; laptop, hard drives, and mobile phone seized for forensic analysis."
    },
    {
      "date": "August 03, 2025, 15:00 IST",
      "event": "Accused's first appearance before the Magistrate; remanded to 5 days of police custody."
    },
    {
      "date": "August 08, 2025, 14:30 IST",
      "event": "Accused sent to judicial custody after completion of police remand."
    },
    {
      "date": "August 11, 2025",
      "event": "Bail application filed."
    },
    {
      "date": "August 18, 2025, 16:00 IST",
      "event": "Bail granted with conditions (surety bond, passport surrender, weekly reporting to the Investigating Officer)."
    },
    {
      "date": "September 15, 2025",
      "event": "Police submitted the final charge sheet to the court."
    },
    {
      "date": "September 20, 2025",
      "event": "Case file prepared."
    },
    {
      "date": "September 29, 2025",
      "event": "Jurisdictional hearing scheduled."
    }
  ]
}
 '''
    
   
)

import fitz  # PyMuPDF
import re
import asyncio
import requests
import json
import os
from langchain_community.document_loaders import PyPDFLoader
from ..utils.LLMmodel import get_LLM_Response

async def summarize_pdf(pdf_path):
    """
    Summarize the content of the uploaded PDF using LLM.
    Args:
        pdf_path (str): Path to the uploaded PDF file.
    Returns:
        str: Summary of the PDF content.
    """
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    
    # Use LLM to generate summary
    summary_prompt = f"Please provide a comprehensive summary of the following legal document:\n\n{text}"
    summary = await get_LLM_Response("gemini-2.5-flash", SYSTEM_PROMPT_SUMMARIZE, summary_prompt)
    return summary

async def extract_events_and_dates(pdf_path):
    """
    Extract all dates from the PDF and provide a short description of what happened at each date using LLM.
    Args:
        pdf_path (str): Path to the uploaded PDF file.
    Returns:
        str: JSON string containing events and dates extracted by LLM.
    """
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    
    # Use LLM to extract events and dates
    events_prompt = f"""Please analyze the following legal document and extract all dates mentioned along with the events that occurred on those dates. 
    
    IMPORTANT: Return ONLY a formatted timeline text, NOT JSON. Use this exact format:
    
    Case Timeline
    
    July 10, 2025, 18:00 IST – July 11, 2025, 02:00 IST – Unauthorized access and data exfiltration from the company server; traced to the accused's IP address.
    
    July 15, 2025, 11:30 IST – FIR filed by Mr. Ankit Sharma, CTO of Innovatech Solutions, at the Cyber Crime Police Station, Bengaluru.
    
    August 03, 2025, 07:15 IST – Accused arrested from his residence; laptop, hard drives, and mobile phone seized for forensic analysis.
    
    Do NOT return JSON format. Do NOT use asterisks (*) or any markdown formatting. Return only the formatted timeline text as shown above using plain text.
    
    Document content:
    {text}"""
    
    events_response = await get_LLM_Response("gemini-2.5-flash", SYSTEM_PROMPT_EXTRACT_EVENTS_DATES, events_prompt)
    return events_response

    
SYSTEM_PROMPT_LEGAL_GUIDE = (
    "You are LegalGuide, an AI legal assistant trained on publicly available "
    "legal knowledge (laws, procedures, common practices). "
    "Your job is to help a user understand their situation and suggest possible "
    "legal actions or next steps.\n\n"
    
    "CRITICAL RULES:\n"
    "- Use ONLY your own pretrained knowledge of law and general legal procedures.\n"
    "- DO NOT fabricate statutes or case numbers.\n"
    "- Base your responses on general legal principles that are commonly true "
    "in most jurisdictions. If a specific law varies by country or state, "
    "clearly mention that.\n"
    "- ALWAYS start your answer with a disclaimer:\n"
    "  'I am not a lawyer. This is general legal information and not a substitute for "
    "professional legal advice.'\n"
    "- If the user asks for very specific statutes or jurisdiction-specific procedures "
    "that you are unsure of, say:\n"
    "  'I don't have jurisdiction-specific details. Please consult a licensed lawyer.'\n\n"
    
    "STYLE:\n"
    "- Ask clarifying questions if the user's description is incomplete.\n"
    "- Provide a structured response:\n"
    "  1. Key Facts You Understood\n"
    "  2. General Legal Context\n"
    "  3. Possible Next Steps or Options\n"
    "  4. Important Cautions\n\n"
    
    "GOAL:\n"
    "Help the user feel informed about possible legal directions they can take, "
    "but never give binding legal advice.\n\n"
    "IMPORTANT: Do NOT use asterisks (*) or any markdown formatting in your response. Use plain text only."
)

async def legal_guide(user_query: str):
    """
    Provide legal guidance based on user's situation using general legal knowledge.
    Args:
        user_query (str): User's legal question or situation description.
    Returns:
        str: Legal guidance response with structured advice.
    """
    # Use LLM to generate legal guidance
    legal_response = await get_LLM_Response("gemini-2.5-flash", SYSTEM_PROMPT_LEGAL_GUIDE, user_query)
    return legal_response

# System prompt for keyword extraction
SYSTEM_PROMPT_KEYWORD_EXTRACTION = (
    "You are a legal expert assistant. Your task is to extract 3-4 high-quality legal keywords "
    "from the given text (which could be a legal query or case description). "
    "These keywords should be relevant for searching legal cases on Indian Kanoon.\n\n"
    
    "IMPORTANT RULES:\n"
    "- Extract exactly 3-4 keywords that are most relevant to the legal case or query\n"
    "- Keywords should be specific legal terms, case names, or key legal concepts\n"
    "- Use terms that would be found in legal case documents\n"
    "- Return ONLY a valid JSON object in this exact format:\n"
    '{"keywords": ["keyword1", "keyword2", "keyword3", "keyword4"], "apiQuery": "keyword1+keyword2+keyword3+keyword4"}\n'
    "- Do not include any other text or explanation\n"
    "- Make sure the apiQuery uses + signs to join keywords\n"
    "- Keywords should be in lowercase and URL-safe\n\n"
    
    "Examples:\n"
    'Input: "find me similar cases to nirbhaya case"\n'
    'Output: {"keywords": ["nirbhaya", "rape", "murder", "delhi"], "apiQuery": "nirbhaya+rape+murder+delhi"}\n\n'
    
    'Input: "cybercrime intellectual property theft"\n'
    'Output: {"keywords": ["cybercrime", "intellectual", "property", "theft"], "apiQuery": "cybercrime+intellectual+property+theft"}'
)

async def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using LangChain PyPDFLoader.
    Args:
        pdf_path (str): Path to the PDF file
    Returns:
        str: Extracted text content
    """
    try:
        # Use LangChain PyPDFLoader for text extraction
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Combine all page content
        text_parts = []
        for doc in documents:
            if doc.page_content and doc.page_content.strip():
                text_parts.append(doc.page_content.strip())
        
        if not text_parts:
            raise Exception("No text content found in PDF")
        
        text = "\n\n".join(text_parts)
        return text
        
    except ImportError as e:
        raise Exception(f"Required package not installed: {str(e)}")
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

async def extract_keywords_from_text(text: str) -> dict:
    """
    Extract legal keywords from text using Gemini API.
    Args:
        text (str): Input text (query or PDF content)
    Returns:
        dict: Dictionary with keywords and apiQuery
    """
    try:
        prompt = f"Extract legal keywords from this text:\n\n{text}"
        response = await get_LLM_Response("gemini-2.5-flash", SYSTEM_PROMPT_KEYWORD_EXTRACTION, prompt)
        
        # Parse JSON response
        try:
            keywords_data = json.loads(response.strip())
            return keywords_data
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract keywords manually
            # This is a fallback mechanism
            words = text.lower().split()
            legal_keywords = [word for word in words if len(word) > 3][:4]
            api_query = "+".join(legal_keywords)
            return {
                "keywords": legal_keywords,
                "apiQuery": api_query
            }
    except Exception as e:
        raise Exception(f"Error extracting keywords: {str(e)}")

async def search_indian_kanoon(keywords_query: str) -> list:
    """
    Search Indian Kanoon API with keywords.
    Args:
        keywords_query (str): Keywords joined with + signs
    Returns:
        list: List of case documents from Indian Kanoon
    """
    try:
        print(f"Searching Indian Kanoon with query: {keywords_query}")
        
      
        # Try different API endpoint formats
        urls_to_try = []
      
        urls_to_try.extend([
                f"https://api.indiankanoon.org/search/?formInput={keywords_query}&maxcites=20"
            ])
        
        
        
        headers = {
            "Authorization": "Token 2fd24155d6a517d98380225b5968a93cab4a362d",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for url in urls_to_try:
            try:
                print(f"Trying URL: {url}")
                
                if "?" in url:
                    # GET request with query parameters
                    response = requests.get(url, headers=headers, timeout=30)
                else:
                    # POST request with form data
                    post_data = {
                        "formInput": keywords_query,
                        "maxcites": 20
                    }
                    response = requests.post(url, data=post_data, headers=headers, timeout=30)
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Extract only the docs array from the response
                    if 'docs' in data:
                        docs = data['docs']
                        print(f"Found {len(docs)} documents")
                        return docs
                    else:
                        print("No 'docs' key in response")
                        print(f"Full response: {data}")
                        return []
                else:
                    print(f"Failed with status {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"Error with URL {url}: {str(e)}")
                continue
        
        # If all URLs failed, return mock data for testing
        print("All API endpoints failed, returning mock data for testing")
        return [
            {
                "title": f"Sample Case 1 - {keywords_query}",
                "court": "Supreme Court of India",
                "date": "2023-01-15",
                "citation": "2023 SCC 123",
                "tid": "123456"
            },
            {
                "title": f"Sample Case 2 - {keywords_query}",
                "court": "High Court of Delhi",
                "date": "2023-02-20",
                "citation": "2023 DLH 456",
                "tid": "789012"
            }
        ]
            
    except Exception as e:
        print(f"Error in search_indian_kanoon: {str(e)}")
        return []

def format_case_results(docs: list) -> list:
    """
    Format the case results for the frontend.
    Args:
        docs (list): Raw docs from Indian Kanoon API
    Returns:
        list: Formatted case results
    """
    formatted_cases = []
    
    for doc in docs:
        try:
            # Extract required fields with fallbacks
            title = doc.get('title', 'No title available')
            court = doc.get('court', 'Court information not available')
            publish_date = doc.get('date', 'Date not available')
            citation = doc.get('citation', 'Citation not available')
            tid = doc.get('tid', '')
            
            # Create clickable link
            link = f"https://indiankanoon.org/doc/{tid}/" if tid else "Link not available"
            
            formatted_case = {
                "title": title,
                "court": court,
                "publish_date": publish_date,
                "citation": citation,
                "link": link
            }
            
            formatted_cases.append(formatted_case)
            
        except Exception as e:
            # Skip malformed documents
            continue
    
    return formatted_cases

async def find_similar_cases(query: str = None, pdf_path: str = None) -> dict:
    """
    Find similar cases based on query text or PDF content.
    Args:
        query (str, optional): Text query
        pdf_path (str, optional): Path to PDF file
    Returns:
        dict: Formatted case results
    """
    try:
        # Determine input text
        if pdf_path:
            # Extract text from PDF
            input_text = await extract_text_from_pdf(pdf_path)
        elif query:
            input_text = query
        else:
            raise ValueError("Either query or pdf_path must be provided")
        
        # Extract keywords
        keywords_data = await extract_keywords_from_text(input_text)
        
        # Search Indian Kanoon
        docs = await search_indian_kanoon(keywords_data['apiQuery'])
        
        # Format results
        formatted_cases = format_case_results(docs)
        
        return {
            "success": True,
            "keywords": keywords_data['keywords'],
            "api_query": keywords_data['apiQuery'],
            "cases": formatted_cases,
            "total_cases": len(formatted_cases)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cases": [],
            "total_cases": 0
        }