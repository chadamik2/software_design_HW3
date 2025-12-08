from typing import List

import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from .clients import file_storage_client, file_analysis_clients
from .schemas import Submission, Report, SubmitWorkResponse, ReportsListRResponse
from .config import settings

app = FastAPI(
    title = "API Gateway - Antiplagiat",
    description="Центральный сервис для системы антиплагиата",
    version="1.0",
)

@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "file_service_url": settings.FILE_SERVICE_URL,
        "analysis_service_url": settings.ANALYSIS_SERVICE_URL,
    }

@app.post(
    "/api/works/submit",
    response_model=SubmitWorkResponse,
    tags=["works"],
    summary="Загрузка работы студента и запуск анализа",
)
async def submit_work(
        student_id: str = Form(...),
        student_name: str = Form(...),
        assignment_id: str = Form(...),
        file: UploadFile = File(...),
):
    try:
        storage_response = file_storage_client.submit_file(
            student_id=student_id,
            student_name=student_name,
            assignment_id=assignment_id,
            file=file,
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    submission = Submission(**storage_response)
    file_download_url = f"{settings.FILE_SERVICE_URL}/files/{submission.file_id}/raw"

    try:
        analysis_response = file_analysis_clients.analyze_submission(
            submission_id=submission.id,
            assignment_id=submission.assignment_id,
            student_id=submission.student_id,
            file_download_url=file_download_url,
        )
        report = Report(**analysis_response)
        return SubmitWorkResponse(
            submission=submission,
            report=report,
            analysis_error=None,
        )
    except requests.RequestException as e:
        return SubmitWorkResponse(
            submission=submission,
            report=None,
            analysis_error=str(e),
        )

@app.get(
    "/api/works/{assignment_id}/reports",
    response_model=ReportsListRResponse,
    tags=["reports"],
    summary="Получить отчеты по всем сдачам для конкретной работы"
)
def get_reports_for_assignment(assignment_id: str):
    try:
        reports_raw = file_analysis_clients.get_reports_for_assignment(assignment_id)
        reports = [Report(**r) for r in reports_raw]
        return ReportsListRResponse(assignment_id=assignment_id, reports=reports)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )