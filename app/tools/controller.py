from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
from .service import summarize_pdf, extract_events_and_dates

router = APIRouter()

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

