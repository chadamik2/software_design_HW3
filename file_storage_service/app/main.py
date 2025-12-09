import os
import uuid
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import Submission
from .schemas import SubmissionCreate, SubmissionRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.FILES_DIR, exist_ok=True)
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="File Storing Service",
    description="Сервис для хранения файлов и данных о сдаче",
    version="1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.post(
    "/files/submit",
    response_model=SubmissionRead,
    tags=["files"],
    summary="Сохранить файл и данные о сдаче"
)
async def submit_file(
        student_id: str = Form(...),
        student_name: str = Form(...),
        assignment_id: str = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.FILES_DIR, safe_filename)

    content = await file.read()
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))

    submission_data = SubmissionCreate(
        student_id=student_id,
        student_name=student_name,
        assignment_id=assignment_id,
        filename=file.filename,
        file_id=file_id,
        file_path=file_path,
    )
    submission = Submission(**submission_data.model_dump())

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission


@app.get(
    "/files/{file_id}",
    response_model=SubmissionRead,
    tags=["files"],
    summary="Получить метаданные по file_id"
)
def get_submission_by_file_id(file_id: str, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.file_id == file_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="File not found")
    return submission


@app.get(
    "/files/{file_id}/download",
    response_class=FileResponse,
    tags=["files"],
    summary="Скачать файл по file_id"
)
def download_file(file_id: str, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.file_id == file_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(settings.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=submission.file_path,
        filename=submission.filename,
        media_type="application/octet-stream",
    )
