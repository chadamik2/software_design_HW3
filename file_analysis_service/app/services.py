import hashlib
from typing import Optional

import requests
from requests import RequestException
from sqlalchemy.orm import Session

from .models import Report
from .plagiarism import check_plagiarism
from .wordcloud import generate_wordcloud_url
from .schemas import AnalysisRequest, ReportRead, ReportCreate


def _compute_content_hash(content: bytes) -> str:
    h = hashlib.sha256()
    h.update(content)
    return h.hexdigest()


def analyze_submission(db: Session, request: AnalysisRequest) -> ReportRead:
    try:
        resp = requests.get(request.file_download_url, timeout=10)
        resp.raise_for_status()
    except RequestException as err:
        raise RuntimeError(f"Failed to download file: {err}") from err

    content: bytes = resp.content or b""
    content_hash = _compute_content_hash(content)

    is_plagiarism, source_submission_id = check_plagiarism(
        db=db,
        assignment_id=request.assignment_id,
        student_id=request.student_id,
        content_hash=content_hash,
    )

    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception:
        text = ""

    wordcloud_url: Optional[str] = None
    if text.strip():
        try:
            wc = generate_wordcloud_url(text=text)
            if wc is not None:
                wordcloud_url = str(wc)
        except Exception:
            wordcloud_url = None

    report_create = ReportCreate(
        submission_id=request.submission_id,
        assignment_id=request.assignment_id,
        student_id=request.student_id,
        content_hash=content_hash,
        is_plagiarism=is_plagiarism,
        plagiarism_source_submission_id=source_submission_id,
        wordcloud_url=wordcloud_url,
    )

    report_data = report_create.model_dump(mode="json")
    report = Report(**report_data)
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportRead.from_orm(report)
