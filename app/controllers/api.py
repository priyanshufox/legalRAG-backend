# app/controllers/api.py
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import db as db_module
from ..models import schemas, models
from ..services.document_service import save_uploaded_file
from ..services.rag_service import answer_query
from ..utils.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/upload", response_model=schemas.UploadResponse)
async def upload(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # basic validation - allow more file types for MVP
    allowed_types = (
        "text/plain", 
        "application/pdf", 
        "application/msword", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} not supported. Allowed types: {allowed_types}")
    content = await file.read()  # read into memory; for large files streaming is recommended
    # call service with default owner for MVP
    doc, chunks = save_uploaded_file(fileobj=bytes_to_filelike(content), filename=file.filename, db=db, owner="mvp_user")
    return {"message": "File uploaded successfully", "file_id": str(doc.id)}

def bytes_to_filelike(b: bytes):
    from io import BytesIO
    return BytesIO(b)

@router.post("/query", response_model=schemas.QueryResponse)
async def query(
    req: schemas.QueryRequest, 
    db: Session = Depends(get_db)
):
    try:
        out = await answer_query(req.query, top_k=5, owner="mvp_user")
        return {"answer": out["answer"]}
    except Exception as e:
        return {"answer": f"I encountered an error: {str(e)}. Please make sure you have uploaded some documents first.", "sources": []}
