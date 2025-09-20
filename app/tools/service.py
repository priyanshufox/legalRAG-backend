
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
    summary = await get_LLM_Response("gemini-1.5-flash", SYSTEM_PROMPT_SUMMARIZE, summary_prompt)
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
    
    events_response = await get_LLM_Response("gemini-1.5-flash", SYSTEM_PROMPT_EXTRACT_EVENTS_DATES, events_prompt)
    return events_response