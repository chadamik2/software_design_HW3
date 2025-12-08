from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class Submission(BaseModel):
    id: int
    student_id: str
    student_name: str
    assignment_id: str
    filename: str
    file_id: str

class Report(BaseModel):
    id: int
    submission_id: int
    assignment_id: str
    student_id: str
    is_plagiarism: bool
    plagiarism_source_submission_id: Optional[int] = None

class SubmitWorkResponse(BaseModel):
    submission: Submission
    report: Optional[Report] = None
    analysis_error: Optional[str] = None

class ReportsListRResponse(BaseModel):
    assignment_id: str
    reports: List[Report]
