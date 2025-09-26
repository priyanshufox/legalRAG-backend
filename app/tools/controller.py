from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import json
from .service import summarize_pdf, extract_events_and_dates, legal_guide, find_similar_cases

router = APIRouter()

class LegalQueryRequest(BaseModel):
    query: str

@router.post("/summarize-pdf")
async def summarize_pdf_endpoint(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        summary = await summarize_pdf(tmp_path)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-events-dates")
async def extract_events_and_dates_endpoint(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        events = await extract_events_and_dates(tmp_path)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/legal-guide")
async def legal_guide_endpoint(request: LegalQueryRequest):
    try:
        legal_advice = await legal_guide(request.query)
        return {"legal_advice": legal_advice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SimilarCasesQueryRequest(BaseModel):
    query: str

@router.post("/similar-cases")
async def similar_cases_endpoint(
    file: UploadFile = File(None),
    query: str = Form(None)
):
    """
    Find similar cases based on either a text query or uploaded PDF file.
    Accepts either:
    1. Multipart form data with PDF file
    2. Multipart form data with 'query' field
    """
    try:
        # Handle PDF file upload
        if file and file.filename:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail="Only PDF files are supported"
                )
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                contents = await file.read()
                tmp.write(contents)
                tmp_path = tmp.name
            
            # Find similar cases using PDF
            result = await find_similar_cases(pdf_path=tmp_path)
            
            # Clean up temporary file
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
                
        elif query:
            # Handle form data query
            result = await find_similar_cases(query=query)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either 'query' in form data or 'file' in form data must be provided"
            )
        
        # Return the result
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/similar-cases-json")
async def similar_cases_json_endpoint(request: SimilarCasesQueryRequest):
    """
    Find similar cases based on a text query sent as JSON.
    Accepts JSON body with 'query' field containing text.
    """
    try:
        result = await find_similar_cases(query=request.query)
        
        # Return the result
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
