from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .schemas import AnalysisRequest, ReportRead
from .models import Report
from .services import analyze_submission

app = FastAPI(
    title="File Analysis Service",
    description="Сервис анализа работ и хранения отчета по антиплагиату",
    version="1.0",
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(engine)


@app.get(
    "/health",
    tags=["health"]
)
def health_check():
    return {"status": "ok"}


@app.post(
    "/internal/analyze",
    response_model=ReportRead,
    tags=["analysis"],
    summary="Внутренний запуск анализа работ"
)
def internal_analyze(
        request: AnalysisRequest,
        db: Session = Depends(get_db)
):
    try:
        report = analyze_submission(db, request)
        return report
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/reports/assignment/{assignment_id}",
    response_model=List[ReportRead],
    tags=["reports"],
    summary="Получить все отчеты по заданию {assigment_id}"
)
def get_reports_by_assignment(
        assignment_id: str,
        db: Session = Depends(get_db)
):
    reports = (
        db.query(Report)
        .filter(Report.assignment_id == assignment_id)
        .order_by(Report.created_at.asc()).all()
    )
    return [ReportRead.from_orm(r) for r in reports]
