from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, HttpUrl, ConfigDict


class AnalysisRequest(BaseModel):
    submission_id: int
    assignment_id: str
    student_id: str
    file_download_url: str

class ReportCreate(BaseModel):
    submission_id: int
    assignment_id: str
    student_id: str
    content_hash: str
    is_plagiarism: bool
    plagiarism_source_submission_id: Optional[int] = None
    wordcloud_url: Optional[HttpUrl] = None


class ReportRead(BaseModel):
    id: int
    submission_id: int
    assignment_id: str
    student_id: str
    content_hash: str
    is_plagiarism: bool
    plagiarism_source_submission_id: Optional[int] = None
    wordcloud_url: Optional[HttpUrl] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportList(BaseModel):
    assignment_id: str
    reports: List[ReportRead]
