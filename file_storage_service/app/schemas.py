from datetime import datetime
from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    student_id: str
    student_name: str
    assignment_id: str
    filename: str
    file_id: str
    file_path: str


class SubmissionRead(BaseModel):
    id: int
    student_id: str
    student_name: str
    assignment_id: str
    filename: str
    file_id: str
    created_at: datetime

    class Config:
        orm_mode = True
