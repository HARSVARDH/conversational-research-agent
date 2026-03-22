from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import shutil
import os

from rag_pipeline import process_pdf, ask_question_stream

app = FastAPI(title="Research Paper Agent API")
Instrumentator().instrument(app).expose(app)
class Query(BaseModel):
    session_id: str
    question: str

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        result = process_pdf(file_path)
    finally:
        os.remove(file_path)
        
    return {"message": "PDF processed successfully", "chunks": result["chunks"]}

@app.post("/chat/")
async def chat(query: Query):
    return StreamingResponse(
        ask_question_stream(query.session_id, query.question), 
        media_type="text/event-stream"
    )